#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
OpenStreetMap数据爬取脚本

实现功能：
1. 爬取OpenStreetMap地理数据和地图数据
2. 获取道路和设施数据（道路、建筑物等）
3. 处理和清洗地理数据
4. 保存为GeoJSON、Shapefile等适用格式
5. 爬取至少200个景点数据并制作可视化地图
"""

import os
import json
import time
import logging
import requests
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point, LineString, Polygon
from datetime import datetime
from tqdm import tqdm

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 定义数据存储路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
OSM_DATA_DIR = os.path.join(DATA_DIR, 'osm')

# 确保目录存在
os.makedirs(OSM_DATA_DIR, exist_ok=True)

# 定义中国主要旅游城市列表（包含经纬度信息）
CITIES = [
    {"name": "北京", "lat": 39.9042, "lon": 116.4074},
    {"name": "上海", "lat": 31.2304, "lon": 121.4737},
    {"name": "广州", "lat": 23.1291, "lon": 113.2644},
    {"name": "深圳", "lat": 22.5431, "lon": 114.0579},
    {"name": "杭州", "lat": 30.2741, "lon": 120.1551},
    {"name": "成都", "lat": 30.5728, "lon": 104.0668},
    {"name": "西安", "lat": 34.3416, "lon": 108.9398},
    {"name": "重庆", "lat": 29.4316, "lon": 106.9123},
    {"name": "苏州", "lat": 31.2990, "lon": 120.5853},
    {"name": "厦门", "lat": 24.4798, "lon": 118.0894},
    {"name": "桂林", "lat": 25.2736, "lon": 110.2907},
    {"name": "丽江", "lat": 26.8721, "lon": 100.2236},
    {"name": "三亚", "lat": 18.2524, "lon": 109.5119},
    {"name": "大理", "lat": 25.6065, "lon": 100.2679},
    {"name": "拉萨", "lat": 29.6500, "lon": 91.1000},
]

# 定义景点类型
PLACE_TYPES = [
    "tourism=attraction",
    "tourism=museum",
    "tourism=gallery",
    "tourism=theme_park",
    "tourism=zoo",
    "tourism=viewpoint",
    "historic=monument",
    "historic=castle",
    "historic=ruins",
    "historic=archaeological_site",
    "historic=memorial",
    "natural=beach",
    "natural=peak",
    "natural=volcano",
    "natural=water",
    "natural=bay",
    "leisure=park",
    "leisure=garden",
]


def fetch_osm_data(query, city_name, city_lat, city_lon, radius=5000):
    """
    使用Overpass API获取OSM数据
    
    Args:
        query: OSM查询字符串
        city_name: 城市名称
        city_lat: 城市纬度
        city_lon: 城市经度
        radius: 搜索半径（米）
        
    Returns:
        OSM数据（JSON格式）
    """
    overpass_url = "https://overpass-api.de/api/interpreter"
    
    # 构建Overpass QL查询
    overpass_query = f"""
    [out:json];
    (
        node[{query}](around:{radius},{city_lat},{city_lon});
        way[{query}](around:{radius},{city_lat},{city_lon});
        relation[{query}](around:{radius},{city_lat},{city_lon});
    );
    out body;
    >;
    out skel qt;
    """
    
    logger.info(f"正在获取{city_name}的{query}数据...")
    
    try:
        response = requests.get(overpass_url, params={"data": overpass_query})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"获取{city_name}的{query}数据失败: {e}")
        # 如果请求失败，等待一段时间后重试
        time.sleep(10)
        try:
            response = requests.get(overpass_url, params={"data": overpass_query})
            response.raise_for_status()
            return response.json()
        except:
            logger.error(f"重试获取{city_name}的{query}数据失败")
            return {"elements": []}


def process_place_data(osm_data):
    """
    处理OSM景点数据
    
    Args:
        osm_data: OSM API返回的JSON数据
        
    Returns:
        处理后的景点数据列表
    """
    places = []
    
    for element in osm_data.get("elements", []):
        # 只处理节点和区域
        if element["type"] not in ["node", "way", "relation"]:
            continue
            
        # 获取标签
        tags = element.get("tags", {})
        if not tags:
            continue
            
        # 提取基本信息
        name = tags.get("name") or tags.get("name:en") or tags.get("name:zh")
        if not name:
            continue
            
        # 确定位置坐标
        if element["type"] == "node":
            lat = element.get("lat")
            lon = element.get("lon")
        else:
            # 对于区域和关系，使用中心点坐标
            center = element.get("center", {})
            lat = center.get("lat")
            lon = center.get("lon")
            
        if not lat or not lon:
            continue
            
        # 确定景点类型
        place_type = None
        for key in ["tourism", "historic", "natural", "leisure"]:
            if key in tags:
                place_type = f"{key}_{tags[key]}"
                break
                
        if not place_type:
            continue
            
        # 提取其他信息
        description = tags.get("description") or ""
        address = tags.get("addr:full") or ""
        if not address and "addr:city" in tags:
            address_parts = []
            for addr_part in ["addr:country", "addr:province", "addr:city", "addr:district", "addr:street", "addr:housenumber"]:
                if addr_part in tags:
                    address_parts.append(tags[addr_part])
            address = ", ".join(address_parts)
            
        website = tags.get("website") or ""
        phone = tags.get("phone") or tags.get("contact:phone") or ""
        opening_hours = tags.get("opening_hours") or ""
        
        # 提取图片URL
        image_url = tags.get("image") or ""
        
        # 构建标签列表
        tag_list = []
        for key in ["historic", "tourism", "natural", "leisure", "amenity"]:
            if key in tags:
                tag_list.append(tags[key])
                
        # 添加其他可能的标签
        for key in tags:
            if key.startswith("subject") or key == "heritage":
                tag_list.append(tags[key])
                
        # 构建景点数据
        place = {
            "osm_id": element.get("id"),
            "name": name,
            "description": description,
            "latitude": float(lat),
            "longitude": float(lon),
            "address": address,
            "place_type": place_type,
            "tags": tag_list,
            "website": website,
            "contact_phone": phone,
            "opening_hours": opening_hours,
            "images": [image_url] if image_url else [],
            "rating": 0.0,  # 默认评分
            "review_count": 0,  # 默认评价数量
            "popularity": 0,  # 默认热度
        }
        
        places.append(place)
    
    return places


def save_to_geojson(places, filename):
    """
    将景点数据保存为GeoJSON格式
    
    Args:
        places: 景点数据列表
        filename: 输出文件名
    """
    # 创建GeoJSON特征集合
    features = []
    
    for place in places:
        # 创建几何对象
        geometry = {
            "type": "Point",
            "coordinates": [place["longitude"], place["latitude"]]
        }
        
        # 创建属性
        properties = {k: v for k, v in place.items() if k not in ["latitude", "longitude"]}
        
        # 创建特征
        feature = {
            "type": "Feature",
            "geometry": geometry,
            "properties": properties
        }
        
        features.append(feature)
    
    # 创建特征集合
    feature_collection = {
        "type": "FeatureCollection",
        "features": features
    }
    
    # 保存到文件
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(feature_collection, f, ensure_ascii=False, indent=2)
    
    logger.info(f"已保存GeoJSON数据到{filename}")


def save_to_shapefile(places, filename):
    """
    将景点数据保存为Shapefile格式
    
    Args:
        places: 景点数据列表
        filename: 输出文件名
    """
    # 创建DataFrame
    df = pd.DataFrame(places)
    
    # 创建几何列
    geometry = [Point(xy) for xy in zip(df["longitude"], df["latitude"])]
    
    # 创建GeoDataFrame
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
    
    # 删除冗余列
    if "latitude" in gdf.columns and "longitude" in gdf.columns:
        gdf = gdf.drop(["latitude", "longitude"], axis=1)
    
    # 保存到文件
    gdf.to_file(filename, driver="ESRI Shapefile", encoding="utf-8")
    
    logger.info(f"已保存Shapefile数据到{filename}")


def create_visualization(places, output_file):
    """
    创建景点分布可视化地图
    
    Args:
        places: 景点数据列表
        output_file: 输出文件名
    """
    # 创建GeoDataFrame
    df = pd.DataFrame(places)
    geometry = [Point(xy) for xy in zip(df["longitude"], df["latitude"])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
    
    # 创建地图
    fig, ax = plt.subplots(figsize=(15, 10))
    
    # 按景点类型分组并绘制
    for place_type, group in gdf.groupby("place_type"):
        group.plot(ax=ax, label=place_type, markersize=20, alpha=0.6)
    
    # 添加标题和图例
    plt.title("中国主要旅游城市景点分布", fontsize=16)
    plt.legend(loc="upper right", fontsize=8)
    
    # 保存图像
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    logger.info(f"已保存可视化地图到{output_file}")


def main():
    """
    主函数
    """
    logger.info("开始爬取OpenStreetMap数据...")
    
    all_places = []
    
    # 遍历城市和景点类型
    for city in tqdm(CITIES, desc="处理城市"):
        city_places = []
        
        for place_type in tqdm(PLACE_TYPES, desc=f"处理{city['name']}的景点类型", leave=False):
            # 获取OSM数据
            osm_data = fetch_osm_data(
                query=place_type,
                city_name=city["name"],
                city_lat=city["lat"],
                city_lon=city["lon"],
                radius=10000  # 10公里半径
            )
            
            # 处理数据
            places = process_place_data(osm_data)
            city_places.extend(places)
            
            # 避免请求过于频繁
            time.sleep(2)
        
        # 保存城市数据
        if city_places:
            city_filename = f"{city['name']}_places"
            city_geojson = os.path.join(OSM_DATA_DIR, f"{city_filename}.geojson")
            city_shapefile = os.path.join(OSM_DATA_DIR, f"{city_filename}.shp")
            
            save_to_geojson(city_places, city_geojson)
            save_to_shapefile(city_places, city_shapefile)
            
            all_places.extend(city_places)
    
    # 保存所有数据
    if all_places:
        logger.info(f"共获取{len(all_places)}个景点数据")
        
        # 确保至少有200个景点
        if len(all_places) < 200:
            logger.warning(f"获取的景点数量不足200个，实际获取了{len(all_places)}个")
        
        # 保存为GeoJSON和Shapefile
        all_geojson = os.path.join(OSM_DATA_DIR, "all_places.geojson")
        all_shapefile = os.path.join(OSM_DATA_DIR, "all_places.shp")
        
        save_to_geojson(all_places, all_geojson)
        save_to_shapefile(all_places, all_shapefile)
        
        # 创建可视化地图
        visualization_file = os.path.join(OSM_DATA_DIR, "places_visualization.png")
        create_visualization(all_places, visualization_file)
        
        # 保存为JSON格式（用于数据库导入）
        json_file = os.path.join(OSM_DATA_DIR, "places.json")
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(all_places, f, ensure_ascii=False, indent=2)
        
        logger.info(f"已保存所有景点数据到{json_file}")
    else:
        logger.warning("未获取到任何景点数据")
    
    logger.info("OpenStreetMap数据爬取完成")


if __name__ == "__main__":
    main()