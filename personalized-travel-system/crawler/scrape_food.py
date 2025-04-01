#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
美食数据爬取脚本

实现功能：
1. 基于已爬取的景点所在城市进行美食数据爬取
2. 使用高德地图API获取餐厅信息和评价
3. 处理和分类美食数据（按菜系、价格等）
4. 保存为JSON格式，便于导入数据库
5. 为每个城市的景点周边提供美食推荐
"""

import os
import json
import time
import logging
import requests
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point
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
FOOD_DATA_DIR = os.path.join(DATA_DIR, 'food')

# 确保目录存在
os.makedirs(FOOD_DATA_DIR, exist_ok=True)

# 高德地图API密钥 (需要替换为实际的API密钥)
AMAP_KEY = "3ff7baa4c830d1d94161bd0fb904b978"

# 美食类型列表
FOOD_TYPES = [
    "中餐",
    "西餐",
    "日料",
    "韩餐",
    "火锅",
    "烧烤",
    "小吃",
    "甜点",
    "咖啡厅",
    "茶馆",
    "素食",
    "清真",
    "海鲜",
    "自助餐",
    "特色菜"
]

# 价格区间
PRICE_RANGES = [
    {"name": "经济实惠", "min": 0, "max": 50},
    {"name": "中等价位", "min": 50, "max": 100},
    {"name": "高档餐厅", "min": 100, "max": 200},
    {"name": "豪华餐厅", "min": 200, "max": 10000}
]


def load_places_data():
    """
    加载已爬取的景点数据
    
    Returns:
        景点数据列表和城市列表
    """
    places_file = os.path.join(OSM_DATA_DIR, "places.json")
    
    if not os.path.exists(places_file):
        logger.error(f"景点数据文件 {places_file} 不存在，请先运行 scrape_osm.py")
        return [], []
    
    try:
        with open(places_file, "r", encoding="utf-8") as f:
            places = json.load(f)
            
        # 提取城市信息
        cities = []
        for place in places:
            address = place.get("address", "")
            city_name = None
            
            # 从地址中提取城市名称
            if address:
                parts = address.split(", ")
                for part in parts:
                    if part in [city["name"] for city in cities]:
                        city_name = part
                        break
                    
                    # 检查是否包含常见城市名称
                    for known_city in ["北京", "上海", "广州", "深圳", "杭州", "成都", "西安", "重庆", "苏州", "厦门", "桂林", "丽江", "三亚", "大理", "拉萨"]:
                        if known_city in part:
                            city_name = known_city
                            break
                            
                    if city_name:
                        break
            
            # 如果无法从地址提取，使用经纬度查找最近的城市
            if not city_name and "latitude" in place and "longitude" in place:
                from math import radians, sin, cos, sqrt, atan2
                
                def haversine(lat1, lon1, lat2, lon2):
                    # 计算两点之间的距离（公里）
                    R = 6371  # 地球半径（公里）
                    dLat = radians(lat2 - lat1)
                    dLon = radians(lon2 - lon1)
                    a = sin(dLat/2) * sin(dLat/2) + cos(radians(lat1)) * cos(radians(lat2)) * sin(dLon/2) * sin(dLon/2)
                    c = 2 * atan2(sqrt(a), sqrt(1-a))
                    return R * c
                
                # 定义中国主要旅游城市列表（包含经纬度信息）
                known_cities = [
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
                
                min_dist = float('inf')
                nearest_city = None
                
                for city in known_cities:
                    dist = haversine(place["latitude"], place["longitude"], city["lat"], city["lon"])
                    if dist < min_dist:
                        min_dist = dist
                        nearest_city = city["name"]
                
                if min_dist <= 100:  # 如果在100公里范围内
                    city_name = nearest_city
            
            if city_name and city_name not in [city["name"] for city in cities]:
                cities.append({
                    "name": city_name,
                    "lat": place.get("latitude"),
                    "lon": place.get("longitude")
                })
        
        return places, cities
    except Exception as e:
        logger.error(f"加载景点数据失败: {e}")
        return [], []


def fetch_amap_food_data(city_name, lat, lon, food_type=None, radius=3000, page=1):
    """
    使用高德地图API获取餐厅数据
    
    Args:
        city_name: 城市名称
        lat: 纬度
        lon: 经度
        food_type: 美食类型
        radius: 搜索半径（米）
        page: 页码
        
    Returns:
        餐厅数据（JSON格式）
    """
    amap_url = "https://restapi.amap.com/v3/place/around"
    
    # 构建查询参数
    params = {
        "key": AMAP_KEY,
        "location": f"{lon},{lat}",
        "keywords": food_type if food_type else "餐厅|美食",
        "radius": radius,
        "offset": 25,  # 每页结果数
        "page": page,
        "extensions": "all"  # 返回详细信息
    }
    
    logger.info(f"正在获取{city_name}的{food_type if food_type else '美食'}数据 (第{page}页)...")
    
    try:
        response = requests.get(amap_url, params=params)
        response.raise_for_status()
        result = response.json()
        
        # 检查API返回状态
        if result.get("status") != "1":
            logger.error(f"API请求失败: {result.get('info')}")
            return {"pois": []}
            
        return result
    except requests.exceptions.RequestException as e:
        logger.error(f"获取{city_name}的美食数据失败: {e}")
        # 如果请求失败，等待一段时间后重试
        time.sleep(5)
        try:
            response = requests.get(amap_url, params=params)
            response.raise_for_status()
            return response.json()
        except:
            logger.error(f"重试获取{city_name}的美食数据失败")
            return {"pois": []}


def process_food_data(amap_data, city_name):
    """
    处理高德地图API返回的餐厅数据
    
    Args:
        amap_data: 高德地图API返回的JSON数据
        city_name: 城市名称
        
    Returns:
        处理后的餐厅数据列表
    """
    restaurants = []
    
    for poi in amap_data.get("pois", []):
        # 提取基本信息
        name = poi.get("name")
        if not name:
            continue
            
        # 提取位置信息
        location = poi.get("location", "").split(",")
        if len(location) != 2:
            continue
            
        try:
            lon = float(location[0])
            lat = float(location[1])
        except ValueError:
            continue
            
        # 提取地址
        address = poi.get("address", "")
        
        # 提取联系电话
        phone = poi.get("tel", "")
        
        # 提取营业时间
        opening_hours = poi.get("business_hours", "")
        
        # 提取评分
        rating = 0.0
        if "biz_ext" in poi and "rating" in poi["biz_ext"]:
            rating_value = poi["biz_ext"]["rating"]
            try:
                if isinstance(rating_value, (int, float)):
                    rating = float(rating_value)
                elif isinstance(rating_value, str):
                    rating = float(rating_value)
                elif isinstance(rating_value, list) and len(rating_value) > 0:
                    # 如果rating是列表，取第一个元素
                    if isinstance(rating_value[0], (int, float, str)):
                        rating = float(rating_value[0])
            except (ValueError, TypeError, IndexError):
                pass
                
        # 提取价格
        price = 0
        if "biz_ext" in poi and "cost" in poi["biz_ext"]:
            cost = poi["biz_ext"]["cost"]
            if isinstance(cost, (int, float)):
                price = int(cost)
            elif isinstance(cost, str):
                try:
                    price = int(float(cost))
                except (ValueError, TypeError):
                    pass
            elif isinstance(cost, list) and len(cost) > 0:
                # 如果cost是列表，取第一个元素或计算平均值
                try:
                    if isinstance(cost[0], (int, float, str)):
                        price = int(float(cost[0]))
                    # 如果需要计算平均值，可以取消下面的注释
                    # price = int(sum(float(c) for c in cost if isinstance(c, (int, float, str))) / len(cost))
                except (ValueError, TypeError, IndexError):
                    pass
                
        # 确定价格区间
        price_range = "未知"
        for range_info in PRICE_RANGES:
            if range_info["min"] <= price <= range_info["max"]:
                price_range = range_info["name"]
                break
                
        # 提取标签
        tags = []
        if "dining_type" in poi:
            tags.append(poi["dining_type"])
            
        if "tag" in poi:
            tags.extend([tag.strip() for tag in poi["tag"].split(";")] if poi["tag"] else [])
            
        # 提取图片URL
        photos = []
        if "photos" in poi:
            for photo in poi["photos"]:
                if "url" in photo:
                    photos.append(photo["url"])
                    
        # 构建餐厅数据
        restaurant = {
            "amap_id": poi.get("id", ""),
            "name": name,
            "latitude": lat,
            "longitude": lon,
            "address": address,
            "city": city_name,
            "phone": phone,
            "opening_hours": opening_hours,
            "rating": rating,
            "price": price,
            "price_range": price_range,
            "tags": tags,
            "photos": photos,
            "cuisine_type": poi.get("dining_type", ""),
            "review_count": int(poi.get("biz_ext", {}).get("rating_count", "0") or "0"),
            "popularity": int(poi.get("biz_ext", {}).get("popularity", "0") or "0"),
        }
        
        restaurants.append(restaurant)
    
    return restaurants


def save_to_json(restaurants, filename):
    """
    将餐厅数据保存为JSON格式
    
    Args:
        restaurants: 餐厅数据列表
        filename: 输出文件名
    """
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=2)
    
    logger.info(f"已保存餐厅数据到{filename}")


def save_to_geojson(restaurants, filename):
    """
    将餐厅数据保存为GeoJSON格式
    
    Args:
        restaurants: 餐厅数据列表
        filename: 输出文件名
    """
    # 创建GeoJSON特征集合
    features = []
    
    for restaurant in restaurants:
        # 创建几何对象
        geometry = {
            "type": "Point",
            "coordinates": [restaurant["longitude"], restaurant["latitude"]]
        }
        
        # 创建属性
        properties = {k: v for k, v in restaurant.items() if k not in ["latitude", "longitude"]}
        
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


def create_visualization(restaurants, output_file):
    """
    创建餐厅分布可视化地图
    
    Args:
        restaurants: 餐厅数据列表
        output_file: 输出文件名
    """
    # 创建GeoDataFrame
    df = pd.DataFrame(restaurants)
    geometry = [Point(xy) for xy in zip(df["longitude"], df["latitude"])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
    
    # 创建地图
    fig, ax = plt.subplots(figsize=(15, 10))
    
    # 按价格区间分组并绘制
    for price_range, group in gdf.groupby("price_range"):
        group.plot(ax=ax, label=price_range, markersize=20, alpha=0.6)
    
    # 添加标题和图例
    plt.title("中国主要旅游城市餐厅分布", fontsize=16)
    plt.legend(loc="upper right", fontsize=8)
    
    # 保存图像
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    logger.info(f"已保存可视化地图到{output_file}")


def main():
    """
    主函数
    """
    logger.info("开始爬取美食数据...")
    
    # 加载景点数据
    places, cities = load_places_data()
    
    if not places or not cities:
        logger.error("未找到景点数据，请先运行 scrape_osm.py")
        return
        
    logger.info(f"从景点数据中提取了{len(cities)}个城市")
    
    all_restaurants = []
    
    # 遍历城市和美食类型
    for city in tqdm(cities, desc="处理城市"):
        city_restaurants = []
        
        for food_type in tqdm(FOOD_TYPES, desc=f"处理{city['name']}的美食类型", leave=False):
            page = 1
            total_restaurants = 0
            max_pages = 5  # 限制每种类型最多爬取5页
            
            while page <= max_pages:
                # 获取高德地图数据
                amap_data = fetch_amap_food_data(
                    city_name=city["name"],
                    lat=city["lat"],
                    lon=city["lon"],
                    food_type=food_type,
                    radius=5000  # 5公里半径
                )
                
                # 处理数据
                restaurants = process_food_data(amap_data, city["name"])
                
                if not restaurants:
                    break
                    
                city_restaurants.extend(restaurants)
                total_restaurants += len(restaurants)
                
                # 检查是否有更多页
                if len(restaurants) < 25:  # 每页最多25条结果
                    break
                    
                page += 1
                
                # 避免请求过于频繁
                time.sleep(1)
            
            logger.info(f"已获取{city['name']}的{food_type}类型餐厅{total_restaurants}个")
        
        # 保存城市数据
        if city_restaurants:
            city_filename = f"{city['name']}_restaurants"
            city_json = os.path.join(FOOD_DATA_DIR, f"{city_filename}.json")
            city_geojson = os.path.join(FOOD_DATA_DIR, f"{city_filename}.geojson")
            
            save_to_json(city_restaurants, city_json)
            save_to_geojson(city_restaurants, city_geojson)
            
            all_restaurants.extend(city_restaurants)
    
    # 保存所有数据
    if all_restaurants:
        logger.info(f"共获取{len(all_restaurants)}个餐厅数据")
        
        # 保存为JSON和GeoJSON
        all_json = os.path.join(FOOD_DATA_DIR, "all_restaurants.json")
        all_geojson = os.path.join(FOOD_DATA_DIR, "all_restaurants.geojson")
        
        save_to_json(all_restaurants, all_json)
        save_to_geojson(all_restaurants, all_geojson)
        
        # 创建可视化地图
        visualization_file = os.path.join(FOOD_DATA_DIR, "restaurants_visualization.png")
        create_visualization(all_restaurants, visualization_file)
        
        logger.info(f"已保存所有餐厅数据到{all_json}")
    else:
        logger.warning("未获取到任何餐厅数据")
    
    logger.info("美食数据爬取完成")


if __name__ == "__main__":
    main()