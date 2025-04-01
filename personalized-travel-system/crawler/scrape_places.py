#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
景点数据爬取脚本

实现功能：
1. 基于已爬取的景点所在城市进行详细景点数据爬取
2. 使用旅游网站API获取景点详细描述、图片和评价
3. 处理和分类景点数据（按类型、特色、适合人群等）
4. 保存为JSON格式，便于导入数据库
5. 为每个城市提供景点推荐
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
from bs4 import BeautifulSoup
import re

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
PLACES_DATA_DIR = os.path.join(DATA_DIR, 'places')

# 确保目录存在
os.makedirs(PLACES_DATA_DIR, exist_ok=True)

# 旅游网站API密钥 (需要替换为实际的API密钥)
XIECHENG_KEY = "YOUR_XIECHENG_KEY_HERE"
MAFENGWO_KEY = "YOUR_MAFENGWO_KEY_HERE"

# 景点类型列表
PLACE_CATEGORIES = [
    "自然风光",
    "历史古迹",
    "博物馆",
    "主题公园",
    "宗教场所",
    "城市地标",
    "文化艺术",
    "休闲娱乐",
    "乡村旅游",
    "海滨海岛",
    "山岳",
    "湖泊",
    "森林",
    "草原",
    "沙漠"
]

# 适合人群
SUITABLE_CROWDS = [
    "家庭亲子",
    "情侣约会",
    "朋友聚会",
    "独自旅行",
    "老年人",
    "摄影爱好者",
    "历史爱好者",
    "自然爱好者",
    "文化爱好者",
    "冒险者"
]

# 最佳游览季节
BEST_SEASONS = [
    "春季",
    "夏季",
    "秋季",
    "冬季",
    "全年皆宜"
]


def load_osm_places():
    """
    加载已爬取的OSM景点数据
    
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


def fetch_place_details_xiecheng(place_name, city_name):
    """
    使用携程API获取景点详细信息
    
    Args:
        place_name: 景点名称
        city_name: 城市名称
        
    Returns:
        景点详细信息（JSON格式）
    """
    # 这里使用模拟数据，实际应用中应替换为真实API调用
    logger.info(f"正在获取{city_name}的{place_name}详细信息(携程)...")
    
    # 模拟API调用延迟
    time.sleep(0.5)
    
    # 返回模拟数据
    return {
        "name": place_name,
        "description": f"{place_name}是{city_name}著名的旅游景点，吸引了众多游客前来观光。",
        "rating": round(3.5 + (hash(place_name) % 15) / 10, 1),  # 生成3.5-5.0之间的随机评分
        "reviews": [
            {"user": "用户1", "content": f"{place_name}风景优美，值得一游！", "rating": 5},
            {"user": "用户2", "content": f"{place_name}环境不错，但人有点多。", "rating": 4},
            {"user": "用户3", "content": f"去{place_name}的交通很方便，景色也很美。", "rating": 4.5}
        ],
        "images": [
            f"https://example.com/images/{city_name}/{place_name}_1.jpg",
            f"https://example.com/images/{city_name}/{place_name}_2.jpg"
        ],
        "ticket_price": (hash(place_name) % 200) + 50,  # 生成50-250元之间的随机票价
        "opening_hours": "08:00-18:00",
        "best_time": BEST_SEASONS[hash(place_name) % len(BEST_SEASONS)],
        "suitable_for": [SUITABLE_CROWDS[hash(place_name + str(i)) % len(SUITABLE_CROWDS)] for i in range(3)],
        "facilities": ["停车场", "洗手间", "餐厅"] if hash(place_name) % 2 == 0 else ["洗手间", "商店"],
        "tips": f"参观{place_name}时请注意保持安静，不要触摸展品。"
    }


def fetch_place_details_mafengwo(place_name, city_name):
    """
    使用马蜂窝API获取景点详细信息
    
    Args:
        place_name: 景点名称
        city_name: 城市名称
        
    Returns:
        景点详细信息（JSON格式）
    """
    # 这里使用模拟数据，实际应用中应替换为真实API调用
    logger.info(f"正在获取{city_name}的{place_name}详细信息(马蜂窝)...")
    
    # 模拟API调用延迟
    time.sleep(0.5)
    
    # 返回模拟数据
    return {
        "name": place_name,
        "intro": f"{place_name}位于{city_name}，是一处历史悠久的景点。",
        "score": round(4.0 + (hash(place_name + "mfw") % 10) / 10, 1),  # 生成4.0-5.0之间的随机评分
        "comments": [
            {"username": "旅行者A", "text": f"{place_name}非常漂亮，推荐一游！", "score": 5},
            {"username": "旅行者B", "text": f"{place_name}历史文化底蕴深厚。", "score": 4.5}
        ],
        "photos": [
            f"https://mafengwo.com/photos/{city_name}/{place_name}_1.jpg",
            f"https://mafengwo.com/photos/{city_name}/{place_name}_2.jpg",
            f"https://mafengwo.com/photos/{city_name}/{place_name}_3.jpg"
        ],
        "price": (hash(place_name + "mfw") % 150) + 30,  # 生成30-180元之间的随机票价
        "open_time": "09:00-17:30",
        "visit_season": BEST_SEASONS[(hash(place_name + "mfw") % len(BEST_SEASONS))],
        "suitable_crowd": [SUITABLE_CROWDS[hash(place_name + "mfw" + str(i)) % len(SUITABLE_CROWDS)] for i in range(2)],
        "travel_tips": f"1. {place_name}周末人较多，建议工作日前往\n2. 门票可在网上预订有优惠"
    }


def merge_place_details(osm_place, xiecheng_data, mafengwo_data):
    """
    合并来自不同来源的景点数据
    
    Args:
        osm_place: OSM景点基础数据
        xiecheng_data: 携程景点详细数据
        mafengwo_data: 马蜂窝景点详细数据
        
    Returns:
        合并后的景点详细数据
    """
    # 基础信息优先使用OSM数据
    merged_place = {
        "osm_id": osm_place.get("osm_id", ""),
        "name": osm_place.get("name", ""),
        "latitude": osm_place.get("latitude", 0),
        "longitude": osm_place.get("longitude", 0),
        "address": osm_place.get("address", ""),
        "place_type": osm_place.get("place_type", ""),
        "tags": osm_place.get("tags", []),
        "website": osm_place.get("website", ""),
        "contact_phone": osm_place.get("contact_phone", ""),
    }
    
    # 提取城市名称
    city_name = ""
    address = osm_place.get("address", "")
    if address:
        for known_city in ["北京", "上海", "广州", "深圳", "杭州", "成都", "西安", "重庆", "苏州", "厦门", "桂林", "丽江", "三亚", "大理", "拉萨"]:
            if known_city in address:
                city_name = known_city
                break
    
    merged_place["city"] = city_name
    
    # 合并描述信息，优先使用更详细的描述
    xiecheng_desc = xiecheng_data.get("description", "")
    mafengwo_desc = mafengwo_data.get("intro", "")
    osm_desc = osm_place.get("description", "")
    
    descriptions = []
    if len(xiecheng_desc) > 10:
        descriptions.append(xiecheng_desc)
    if len(mafengwo_desc) > 10:
        descriptions.append(mafengwo_desc)
    if len(osm_desc) > 10:
        descriptions.append(osm_desc)
    
    merged_place["description"] = max(descriptions, key=len) if descriptions else ""
    
    # 合并评分，取加权平均
    xiecheng_rating = xiecheng_data.get("rating", 0)
    mafengwo_rating = mafengwo_data.get("score", 0)
    
    if xiecheng_rating > 0 and mafengwo_rating > 0:
        merged_place["rating"] = round((xiecheng_rating + mafengwo_rating) / 2, 1)
    elif xiecheng_rating > 0:
        merged_place["rating"] = xiecheng_rating
    elif mafengwo_rating > 0:
        merged_place["rating"] = mafengwo_rating
    else:
        merged_place["rating"] = 0
    
    # 合并评论
    reviews = []
    if "reviews" in xiecheng_data:
        for review in xiecheng_data["reviews"]:
            reviews.append({
                "user": review.get("user", ""),
                "content": review.get("content", ""),
                "rating": review.get("rating", 0),
                "source": "携程"
            })
    
    if "comments" in mafengwo_data:
        for comment in mafengwo_data["comments"]:
            reviews.append({
                "user": comment.get("username", ""),
                "content": comment.get("text", ""),
                "rating": comment.get("score", 0),
                "source": "马蜂窝"
            })
    
    merged_place["reviews"] = reviews
    merged_place["review_count"] = len(reviews)
    
    # 合并图片
    images = osm_place.get("images", [])
    if "images" in xiecheng_data:
        images.extend(xiecheng_data["images"])
    if "photos" in mafengwo_data:
        images.extend(mafengwo_data["photos"])
    
    merged_place["images"] = list(set(images))  # 去重
    
    # 合并开放时间，优先使用更详细的信息
    opening_hours = osm_place.get("opening_hours", "")
    xiecheng_hours = xiecheng_data.get("opening_hours", "")
    mafengwo_hours = mafengwo_data.get("open_time", "")
    
    if len(xiecheng_hours) > len(opening_hours):
        opening_hours = xiecheng_hours
    if len(mafengwo_hours) > len(opening_hours):
        opening_hours = mafengwo_hours
    
    merged_place["opening_hours"] = opening_hours
    
    # 合并票价，取平均值
    xiecheng_price = xiecheng_data.get("ticket_price", 0)
    mafengwo_price = mafengwo_data.get("price", 0)
    
    if xiecheng_price > 0 and mafengwo_price > 0:
        merged_place["ticket_price"] = round((xiecheng_price + mafengwo_price) / 2)
    elif xiecheng_price > 0:
        merged_place["ticket_price"] = xiecheng_price
    elif mafengwo_price > 0:
        merged_place["ticket_price"] = mafengwo_price
    else:
        merged_place["ticket_price"] = 0
    
    # 合并最佳游览季节
    xiecheng_season = xiecheng_data.get("best_time", "")
    mafengwo_season = mafengwo_data.get("visit_season", "")
    
    if xiecheng_season and mafengwo_season:
        if xiecheng_season == mafengwo_season:
            merged_place["best_season"] = xiecheng_season
        else:
            merged_place["best_season"] = f"{xiecheng_season}、{mafengwo_season}"
    elif xiecheng_season:
        merged_place["best_season"] = xiecheng_season
    elif mafengwo_season:
        merged_place["best_season"] = mafengwo_season
    else:
        merged_place["best_season"] = "全年皆宜"
    
    # 合并适合人群
    suitable_crowds = []
    if "suitable_for" in xiecheng_data:
        suitable_crowds.extend(xiecheng_data["suitable_for"])
    if "suitable_crowd" in mafengwo_data:
        suitable_crowds.extend(mafengwo_data["suitable_crowd"])
    
    merged_place["suitable_crowds"] = list(set(suitable_crowds))  # 去重
    
    # 合并设施信息
    merged_place["facilities"] = xiecheng_data.get("facilities", [])
    
    # 合并旅游贴士
    tips = []
    if "tips" in xiecheng_data and xiecheng_data["tips"]:
        tips.append(xiecheng_data["tips"])
    if "travel_tips" in mafengwo_data and mafengwo_data["travel_tips"]:
        tips.append(mafengwo_data["travel_tips"])
    
    merged_place["travel_tips"] = "\n\n".join(tips)
    
    # 分类景点
    merged_place["category"] = categorize_place(merged_place)
    
    # 计算热度分数
    merged_place["popularity"] = calculate_popularity(merged_place)
    
    return merged_place


def categorize_place(place):
    """
    根据景点信息对景点进行分类
    
    Args:
        place: 景点数据
        
    Returns:
        景点类别
    """
    place_type = place.get("place_type", "")
    tags = place.get("tags", [])
    description = place.get("description", "")
    
    # 根据OSM类型进行初步分类
    if "tourism_museum" in place_type or "museum" in tags:
        return "博物馆"
    elif "tourism_theme_park" in place_type:
        return "主题公园"
    elif "historic_" in place_type or "historic" in tags:
        return "历史古迹"
    elif "natural_" in place_type or any(tag in tags for tag in ["mountain", "peak", "hill"]):
        return "自然风光"
    elif "leisure_park" in place_type or "leisure_garden" in place_type:
        return "休闲娱乐"
    elif "natural_beach" in place_type or "beach" in tags:
        return "海滨海岛"
    elif "natural_peak" in place_type or "mountain" in tags:
        return "山岳"
    elif "natural_water" in place_type or "lake" in tags:
        return "湖泊"
    
    # 根据描述进行进一步分类
    keywords = {
        "自然风光": ["自然", "风景", "风光", "景色", "美景"],
        "历史古迹": ["历史", "古迹", "古代", "遗址", "文物", "古建筑", "古城", "古镇"],
        "博物馆": ["博物馆", "展览", "展品", "文物", "艺术品"],
        "主题公园": ["主题公园", "游乐园", "游乐场", "乐园"],
        "宗教场所": ["寺庙", "庙宇", "教堂", "清真寺", "宗教", "佛教", "道教", "基督教", "伊斯兰教"],
        "城市地标": ["地标", "标志性", "城市", "建筑", "摩天大楼", "塔"],
        "文化艺术": ["文化", "艺术", "表演", "音乐", "戏剧", "舞蹈", "展览"],
        "休闲娱乐": ["休闲", "娱乐", "公园", "花园", "广场"],
        "乡村旅游": ["乡村", "农村", "农家", "田园", "村落"],
        "海滨海岛": ["海滨", "海岛", "海边", "沙滩", "海滩", "珊瑚", "礁石"],
        "山岳": ["山", "峰", "岳", "山脉", "高山", "山峰", "山岳"],
        "湖泊": ["湖", "湖泊", "湖水", "湖畔"],
        "森林": ["森林", "树林", "林区", "原始森林"],
        "草原": ["草原", "草地", "牧场"],
        "沙漠": ["沙漠", "沙丘", "戈壁"]
    }
    
    # 计算每个类别的匹配度
    category_scores = {}
    for category, words in keywords.items():
        score = 0
        for word in words:
            if word in description:
                score += 1
        category_scores[category] = score
    
    # 选择匹配度最高的类别
    if category_scores:
        best_category = max(category_scores.items(), key=lambda x: x[1])
        if best_category[1] > 0:
            return best_category[0]
    
    # 默认分类
    return "自然风光"


def calculate_popularity(place):
    """
    计算景点热度分数
    
    Args:
        place: 景点数据
        
    Returns:
        热度分数(0-100)
    """
    # 基础分数
    base_score = 50
    
    # 根据评分加分
    rating = place.get("rating", 0)
    if rating > 0:
        rating_score = (rating / 5) * 20  # 最高20分
    else:
        rating_score = 0
    
    # 根据评论数加分
    review_count = place.get("review_count", 0)
    if review_count > 0:
        review_score = min(review_count / 10, 15)  # 最高15分
    else:
        review_score = 0
    
    # 根据图片数加分
    image_count = len(place.get("images", []))
    if image_count > 0:
        image_score = min(image_count / 5, 10)  # 最高10分
    else:
        image_score = 0
    
    # 根据描述详细程度加分
    description = place.get("description", "")
    if description:
        desc_score = min(len(description) / 100, 5)  # 最高5分
    else:
        desc_score = 0
    
    # 计算总分
    total_score = base_score + rating_score + review_score + image_score + desc_score
    
    return min(round(total_score), 100)  # 确保不超过100分


def save_to_json(places, filename):
    """
    将景点数据保存为JSON格式
    
    Args:
        places: 景点数据列表
        filename: 输出文件名
    """
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(places, f, ensure_ascii=False, indent=2)
    
    logger.info(f"已保存景点数据到{filename}")


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
    
    # 按景点类别分组并绘制
    for category, group in gdf.groupby("category"):
        group.plot(ax=ax, label=category, markersize=20, alpha=0.6)
    
    # 添加标题和图例
    plt.title("中国主要旅游城市景点分类分布", fontsize=16)
    plt.legend(loc="upper right", fontsize=8)
    
    # 保存图像
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    logger.info(f"已保存可视化地图到{output_file}")


def create_popularity_visualization(places, output_file):
    """
    创建景点热度可视化地图
    
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
    
    # 按热度分组并绘制
    popularity_bins = [0, 60, 70, 80, 90, 100]
    popularity_labels = ["较低", "一般", "较高", "热门", "非常热门"]
    
    gdf["popularity_level"] = pd.cut(gdf["popularity"], bins=popularity_bins, labels=popularity_labels, right=False)
    
    for level, group in gdf.groupby("popularity_level"):
        group.plot(ax=ax, label=level, markersize=group["popularity"] / 5 + 10, alpha=0.6)
    
    # 添加标题和图例
    plt.title("中国主要旅游城市景点热度分布", fontsize=16)
    plt.legend(loc="upper right", fontsize=8)
    
    # 保存图像
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    logger.info(f"已保存热度可视化地图到{output_file}")


def main():
    """
    主函数
    """
    logger.info("开始爬取景点详细数据...")
    
    # 加载OSM景点数据
    osm_places, cities = load_osm_places()
    
    if not osm_places or not cities:
        logger.error("未找到OSM景点数据，请先运行 scrape_osm.py")
        return
        
    logger.info(f"从OSM数据中加载了{len(osm_places)}个景点和{len(cities)}个城市")
    
    all_detailed_places = []
    
    # 遍历景点获取详细信息
    for place in tqdm(osm_places, desc="处理景点"):
        place_name = place.get("name", "")
        if not place_name:
            continue
            
        # 提取城市名称
        city_name = ""
        address = place.get("address", "")
        if address:
            for known_city in ["北京", "上海", "广州", "深圳", "杭州", "成都", "西安", "重庆", "苏州", "厦门", "桂林", "丽江", "三亚", "大理", "拉萨"]:
                if known_city in address:
                    city_name = known_city
                    break
        
        if not city_name:
            # 使用最近的城市
            from math import radians, sin, cos, sqrt, atan2
            
            def haversine(lat1, lon1, lat2, lon2):
                # 计算两点之间的距离（公里）
                R = 6371  # 地球半径（公里）
                dLat = radians(lat2 - lat1)
                dLon = radians(lon2 - lon1)
                a = sin(dLat/2) * sin(dLat/2) + cos(radians(lat1)) * cos(radians(lat2)) * sin(dLon/2) * sin(dLon/2)
                c = 2 * atan2(sqrt(a), sqrt(1-a))
                return R * c
            
            min_dist = float('inf')
            nearest_city = None
            
            for city in cities:
                dist = haversine(place["latitude"], place["longitude"], city["lat"], city["lon"])
                if dist < min_dist:
                    min_dist = dist
                    nearest_city = city["name"]
            
            if min_dist <= 100:  # 如果在100公里范围内
                city_name = nearest_city
            else:
                city_name = "未知城市"
        
        # 获取携程数据
        xiecheng_data = fetch_place_details_xiecheng(place_name, city_name)
        
        # 获取马蜂窝数据
        mafengwo_data = fetch_place_details_mafengwo(place_name, city_name)
        
        # 合并数据
        detailed_place = merge_place_details(place, xiecheng_data, mafengwo_data)
        
        all_detailed_places.append(detailed_place)
        
        # 避免请求过于频繁
        time.sleep(0.5)
    
    # 保存所有数据
    if all_detailed_places:
        logger.info(f"共获取{len(all_detailed_places)}个景点详细数据")
        
        # 按城市分组保存
        city_places = {}
        for place in all_detailed_places:
            city = place.get("city", "未知城市")
            if city not in city_places:
                city_places[city] = []
            city_places[city].append(place)
        
        for city, places in city_places.items():
            city_filename = f"{city}_detailed_places"
            city_json = os.path.join(PLACES_DATA_DIR, f"{city_filename}.json")
            city_geojson = os.path.join(PLACES_DATA_DIR, f"{city_filename}.geojson")
            
            save_to_json(places, city_json)
            save_to_geojson(places, city_geojson)
            
            logger.info(f"已保存{city}的{len(places)}个景点详细数据")
        
        # 保存为JSON和GeoJSON
        all_json = os.path.join(PLACES_DATA_DIR, "all_detailed_places.json")
        all_geojson = os.path.join(PLACES_DATA_DIR, "all_detailed_places.geojson")
        
        save_to_json(all_detailed_places, all_json)
        save_to_geojson(all_detailed_places, all_geojson)
        
        # 创建分类可视化地图
        category_visualization_file = os.path.join(PLACES_DATA_DIR, "places_category_visualization.png")
        create_visualization(all_detailed_places, category_visualization_file)
        
        # 创建热度可视化地图
        popularity_visualization_file = os.path.join(PLACES_DATA_DIR, "places_popularity_visualization.png")
        create_popularity_visualization(all_detailed_places, popularity_visualization_file)
        
        logger.info(f"已保存所有景点详细数据到{all_json}")
    else:
        logger.warning("未获取到任何景点详细数据")
    
    logger.info("景点详细数据爬取完成")


if __name__ == "__main__":
    main()