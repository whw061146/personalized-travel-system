import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple, Union
import sys
import os
from collections import defaultdict

# 添加项目根目录到系统路径，以便导入backend模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入后端模型和工具
from backend.models.user import User
from backend.models.place import Place
from backend.models.food import Food
from backend.utils.helpers import calculate_distance

# 尝试导入科学计算库
try:
    from scipy.sparse import csr_matrix
    from scipy.sparse.linalg import svds
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    print("Warning: scipy not installed. Using fallback similarity methods.")


class CollaborativeFilterRecommender:
    """协同过滤推荐系统
    
    基于用户行为和偏好进行景点和美食推荐
    """
    
    def __init__(self, use_svd: bool = True):
        """初始化推荐器
        
        Args:
            use_svd: 是否使用奇异值分解(SVD)进行矩阵分解，如果为False则使用基础的协同过滤
        """
        self.use_svd = use_svd and SCIPY_AVAILABLE
        self.user_item_matrix = None
        self.user_factors = None
        self.item_factors = None
        self.user_means = None
        self.item_means = None
        self.user_indices = {}
        self.item_indices = {}
        self.items = []
        self.users = []
    
    def _build_user_item_matrix(self, interactions: List[Dict[str, Any]], item_type: str = 'place'):
        """构建用户-物品交互矩阵
        
        Args:
            interactions: 用户与物品的交互记录列表，每个记录包含user_id, item_id和rating
            item_type: 物品类型，'place'或'food'
        """
        # 创建用户和物品的索引映射
        user_ids = set()
        item_ids = set()
        
        for interaction in interactions:
            user_ids.add(interaction['user_id'])
            item_ids.add(interaction['item_id'])
        
        self.users = sorted(list(user_ids))
        self.items = sorted(list(item_ids))
        
        self.user_indices = {user_id: i for i, user_id in enumerate(self.users)}
        self.item_indices = {item_id: i for i, item_id in enumerate(self.items)}
        
        # 创建用户-物品矩阵
        matrix = np.zeros((len(self.users), len(self.items)))
        
        for interaction in interactions:
            user_idx = self.user_indices.get(interaction['user_id'])
            item_idx = self.item_indices.get(interaction['item_id'])
            
            if user_idx is not None and item_idx is not None:
                matrix[user_idx, item_idx] = interaction['rating']
        
        self.user_item_matrix = matrix
        
        # 如果使用SVD，则进行矩阵分解
        if self.use_svd and SCIPY_AVAILABLE:
            self._perform_svd()
    
    def _perform_svd(self, n_factors: int = 20):
        """使用SVD进行矩阵分解
        
        Args:
            n_factors: 潜在因子数量
        """
        if not SCIPY_AVAILABLE:
            print("SVD not available. Using fallback methods.")
            return
        
        # 计算每个用户的平均评分
        self.user_means = np.mean(self.user_item_matrix, axis=1)
        
        # 中心化矩阵
        matrix_centered = self.user_item_matrix - self.user_means.reshape(-1, 1)
        
        # 转换为稀疏矩阵
        matrix_sparse = csr_matrix(matrix_centered)
        
        # 执行SVD
        u, sigma, vt = svds(matrix_sparse, k=min(n_factors, min(matrix_sparse.shape)-1))
        
        # 重构用户和物品因子
        self.user_factors = u
        self.item_factors = vt.T
    
    def _calculate_similarity_user_based(self, user1_idx: int, user2_idx: int) -> float:
        """计算两个用户的相似度
        
        Args:
            user1_idx: 第一个用户的索引
            user2_idx: 第二个用户的索引
            
        Returns:
            两个用户的余弦相似度
        """
        user1_vector = self.user_item_matrix[user1_idx]
        user2_vector = self.user_item_matrix[user2_idx]
        
        # 只考虑两个用户都有评分的物品
        mask = np.logical_and(user1_vector > 0, user2_vector > 0)
        
        if not np.any(mask):
            return 0.0
        
        user1_filtered = user1_vector[mask]
        user2_filtered = user2_vector[mask]
        
        # 计算余弦相似度
        dot_product = np.dot(user1_filtered, user2_filtered)
        norm1 = np.linalg.norm(user1_filtered)
        norm2 = np.linalg.norm(user2_filtered)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _calculate_similarity_item_based(self, item1_idx: int, item2_idx: int) -> float:
        """计算两个物品的相似度
        
        Args:
            item1_idx: 第一个物品的索引
            item2_idx: 第二个物品的索引
            
        Returns:
            两个物品的余弦相似度
        """
        item1_vector = self.user_item_matrix[:, item1_idx]
        item2_vector = self.user_item_matrix[:, item2_idx]
        
        # 只考虑对两个物品都有评分的用户
        mask = np.logical_and(item1_vector > 0, item2_vector > 0)
        
        if not np.any(mask):
            return 0.0
        
        item1_filtered = item1_vector[mask]
        item2_filtered = item2_vector[mask]
        
        # 计算余弦相似度
        dot_product = np.dot(item1_filtered, item2_filtered)
        norm1 = np.linalg.norm(item1_filtered)
        norm2 = np.linalg.norm(item2_filtered)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _predict_rating_user_based(self, user_idx: int, item_idx: int, k: int = 10) -> float:
        """基于用户的协同过滤预测评分
        
        Args:
            user_idx: 用户索引
            item_idx: 物品索引
            k: 考虑的最近邻数量
            
        Returns:
            预测的评分
        """
        # 如果用户已经对该物品有评分，直接返回
        if self.user_item_matrix[user_idx, item_idx] > 0:
            return self.user_item_matrix[user_idx, item_idx]
        
        # 计算用户与其他所有用户的相似度
        similarities = []
        for other_idx in range(len(self.users)):
            if other_idx != user_idx and self.user_item_matrix[other_idx, item_idx] > 0:
                sim = self._calculate_similarity_user_based(user_idx, other_idx)
                similarities.append((other_idx, sim))
        
        # 如果没有相似用户，返回用户的平均评分或默认值
        if not similarities:
            return np.mean(self.user_item_matrix[user_idx][self.user_item_matrix[user_idx] > 0]) or 3.0
        
        # 选择最相似的k个用户
        similarities.sort(key=lambda x: x[1], reverse=True)
        nearest_neighbors = similarities[:k]
        
        # 加权平均预测评分
        weighted_sum = 0
        similarity_sum = 0
        
        for neighbor_idx, similarity in nearest_neighbors:
            weighted_sum += similarity * self.user_item_matrix[neighbor_idx, item_idx]
            similarity_sum += similarity
        
        if similarity_sum == 0:
            return np.mean(self.user_item_matrix[user_idx][self.user_item_matrix[user_idx] > 0]) or 3.0
        
        return weighted_sum / similarity_sum
    
    def _predict_rating_item_based(self, user_idx: int, item_idx: int, k: int = 10) -> float:
        """基于物品的协同过滤预测评分
        
        Args:
            user_idx: 用户索引
            item_idx: 物品索引
            k: 考虑的最近邻数量
            
        Returns:
            预测的评分
        """
        # 如果用户已经对该物品有评分，直接返回
        if self.user_item_matrix[user_idx, item_idx] > 0:
            return self.user_item_matrix[user_idx, item_idx]
        
        # 获取用户评分过的物品
        rated_items = []
        for i in range(self.user_item_matrix.shape[1]):
            if self.user_item_matrix[user_idx, i] > 0:
                rated_items.append(i)
        
        # 如果用户没有评分过任何物品，返回默认值
        if not rated_items:
            return 3.0
        
        # 计算目标物品与用户评分过的物品的相似度
        similarities = []
        for rated_item_idx in rated_items:
            sim = self._calculate_similarity_item_based(item_idx, rated_item_idx)
            similarities.append((rated_item_idx, sim))
        
        # 选择最相似的k个物品
        similarities.sort(key=lambda x: x[1], reverse=True)
        nearest_neighbors = similarities[:k]
        
        # 加权平均预测评分
        weighted_sum = 0
        similarity_sum = 0
        
        for neighbor_idx, similarity in nearest_neighbors:
            weighted_sum += similarity * self.user_item_matrix[user_idx, neighbor_idx]
            similarity_sum += similarity
        
        if similarity_sum == 0:
            return np.mean(self.user_item_matrix[user_idx][self.user_item_matrix[user_idx] > 0]) or 3.0
        
        return weighted_sum / similarity_sum
    
    def _predict_rating_svd(self, user_idx: int, item_idx: int) -> float:
        """使用SVD预测评分
        
        Args:
            user_idx: 用户索引
            item_idx: 物品索引
            
        Returns:
            预测的评分
        """
        if not self.use_svd or not SCIPY_AVAILABLE:
            return self._predict_rating_item_based(user_idx, item_idx)
        
        # 如果用户已经对该物品有评分，直接返回
        if self.user_item_matrix[user_idx, item_idx] > 0:
            return self.user_item_matrix[user_idx, item_idx]
        
        # 使用矩阵分解预测评分
        predicted_rating = self.user_means[user_idx] + np.dot(self.user_factors[user_idx], self.item_factors[item_idx])
        
        # 限制评分范围
        return max(1.0, min(5.0, predicted_rating))
    
    def recommend_places_user_based(self, user: User, places: List[Place], top_n: int = 10) -> List[Dict[str, Any]]:
        """基于用户的协同过滤推荐景点
        
        Args:
            user: 用户对象
            places: 候选景点列表
            top_n: 返回的推荐数量
            
        Returns:
            推荐景点列表，包含预测评分
        """
        # 获取用户索引
        user_idx = self.user_indices.get(user.id)
        
        if user_idx is None:
            return []
        
        # 计算用户对每个景点的预测评分
        place_ratings = []
        for place in places:
            item_idx = self.item_indices.get(place.id)
            
            if item_idx is not None:
                # 预测评分
                predicted_rating = self._predict_rating_user_based(user_idx, item_idx)
                
                place_ratings.append({
                    'place': place,
                    'predicted_rating': predicted_rating
                })
        
        # 按预测评分排序
        place_ratings.sort(key=lambda x: x['predicted_rating'], reverse=True)
        
        # 返回前N个结果
        result = []
        for item in place_ratings[:top_n]:
            place_dict = item['place'].to_dict() if hasattr(item['place'], 'to_dict') else {}
            place_dict.update({
                'predicted_rating': float(item['predicted_rating'])
            })
            result.append(place_dict)
        
        return result
    
    def recommend_places_item_based(self, user: User, places: List[Place], top_n: int = 10) -> List[Dict[str, Any]]:
        """基于物品的协同过滤推荐景点
        
        Args:
            user: 用户对象
            places: 候选景点列表
            top_n: 返回的推荐数量
            
        Returns:
            推荐景点列表，包含预测评分
        """
        # 获取用户索引
        user_idx = self.user_indices.get(user.id)
        
        if user_idx is None:
            return []
        
        # 计算用户对每个景点的预测评分
        place_ratings = []
        for place in places:
            item_idx = self.item_indices.get(place.id)
            
            if item_idx is not None:
                # 预测评分
                predicted_rating = self._predict_rating_item_based(user_idx, item_idx)
                
                place_ratings.append({
                    'place': place,
                    'predicted_rating': predicted_rating
                })
        
        # 按预测评分排序
        place_ratings.sort(key=lambda x: x['predicted_rating'], reverse=True)
        
        # 返回前N个结果
        result = []
        for item in place_ratings[:top_n]:
            place_dict = item['place'].to_dict() if hasattr(item['place'], 'to_dict') else {}
            place_dict.update({
                'predicted_rating': float(item['predicted_rating'])
            })
            result.append(place_dict)
        
        return result
    
    def recommend_foods_user_based(self, user: User, foods: List[Food], top_n: int = 10) -> List[Dict[str, Any]]:
        """基于用户的协同过滤推荐美食
        
        Args:
            user: 用户对象
            foods: 候选美食列表
            top_n: 返回的推荐数量
            
        Returns:
            推荐美食列表，包含预测评分
        """
        # 获取用户索引
        user_idx = self.user_indices.get(user.id)
        
        if user_idx is None:
            return []
        
        # 计算用户对每个美食的预测评分
        food_ratings = []
        for food in foods:
            item_idx = self.item_indices.get(food.id)
            
            if item_idx is not None:
                # 预测评分
                predicted_rating = self._predict_rating_user_based(user_idx, item_idx)
                
                food_ratings.append({
                    'food': food,
                    'predicted_rating': predicted_rating
                })
        
        # 按预测评分排序
        food_ratings.sort(key=lambda x: x['predicted_rating'], reverse=True)
        
        # 返回前N个结果
        result = []
        for item in food_ratings[:top_n]:
            food_dict = item['food'].to_dict() if hasattr(item['food'], 'to_dict') else {}
            food_dict.update({
                'predicted_rating': float(item['predicted_rating'])
            })
            result.append(food_dict)
        
        return result
    
    def recommend_foods_item_based(self, user: User, foods: List[Food], top_n: int = 10) -> List[Dict[str, Any]]:
        """基于物品的协同过滤推荐美食
        
        Args:
            user: 用户对象
            foods: 候选美食列表
            top_n: 返回的推荐数量
            
        Returns:
            推荐美食列表，包含预测评分
        """
        # 获取用户索引
        user_idx = self.user_indices.get(user.id)
        
        if user_idx is None:
            return []
        
        # 计算用户对每个美食的预测评分
        food_ratings = []
        for food in foods:
            item_idx = self.item_indices.get(food.id)
            
            if item_idx is not None:
                # 预测评分
                predicted_rating = self._predict_rating_item_based(user_idx, item_idx)
                
                food_ratings.append({
                    'food': food,
                    'predicted_rating': predicted_rating
                })
        
        # 按预测评分排序
        food_ratings.sort(key=lambda x: x['predicted_rating'], reverse=True)
        
        # 返回前N个结果
        result = []
        for item in food_ratings[:top_n]:
            food_dict = item['food'].to_dict() if hasattr(item['food'], 'to_dict') else {}
            food_dict.update({
                'predicted_rating': float(item['predicted_rating'])
            })
            result.append(food_dict)
        
        return result


# 提供一个简单的函数接口，方便后端调用
def get_collaborative_recommendations(user_id: int, item_type: str = 'place', method: str = 'item', top_n: int = 10) -> List[Dict[str, Any]]:
    """获取协同过滤推荐
    
    Args:
        user_id: 用户ID
        item_type: 推荐项目类型，'place'或'food'
        method: 推荐方法，'user'表示基于用户的协同过滤，'item'表示基于物品的协同过滤
        top_n: 返回的推荐数量
        
    Returns:
        推荐项目列表
    """
    # 初始化推荐器
    recommender = CollaborativeFilterRecommender(use_svd=SCIPY_AVAILABLE)
    
    # 获取用户
    user = User.query.get(user_id)
    if not user:
        return []
    
    # 获取用户交互数据
    interactions = []
    
    if item_type == 'place':
        # 这里应该从数据库中获取用户对景点的评分记录
        # 在实际应用中，应该有一个专门的表存储用户对景点的评分
        # 这里使用模拟数据
        
        # 构建用户-物品矩阵
        recommender._build_user_item_matrix(interactions, item_type='place')
        
        # 获取所有景点
        places = Place.query.all()
        
        # 根据方法选择推荐函数
        if method == 'user':
            return recommender.recommend_places_user_based(user, places, top_n)
        else:
            return recommender.recommend_places_item_based(user, places, top_n)
    
    elif item_type == 'food':
        # 这里应该从数据库中获取用户对美食的评分记录
        # 在实际应用中，应该有一个专门的表存储用户对美食的评分
        # 这里使用模拟数据
        
        # 构建用户-物品矩阵
        recommender._build_user_item_matrix(interactions, item_type='food')
        
        # 获取所有美食
        foods = Food.query.all()
        
        # 根据方法选择推荐函数
        if method == 'user':
            return recommender.recommend_foods_user_based(user, foods, top_n)
        else:
            return recommender.recommend_foods_item_based(user, foods, top_n)
    
    else:
        return []


# 提供一个考虑地理位置的推荐函数
def get_location_aware_collaborative_recommendations(user_id: int, latitude: float, longitude: float, 
                                                   radius: float = 10.0, item_type: str = 'place', 
                                                   method: str = 'item', top_n: int = 10) -> List[Dict[str, Any]]:
    """获取考虑地理位置的协同过滤推荐
    
    Args:
        user_id: 用户ID
        latitude: 当前纬度
        longitude: 当前经度
        radius: 搜索半径（公里）
        item_type: 推荐项目类型，'place'或'food'
        method: 推荐方法，'user'表示基于用户的协同过滤，'item'表示基于物品的协同过滤
        top_n: 返回的推荐数量
        
    Returns:
        推荐项目列表
    """
    # 初始化推荐器
    recommender = CollaborativeFilterRecommender(use_svd=SCIPY_AVAILABLE)
    
    # 获取用户
    user = User.query.get(user_id)
    if not user:
        return []
    
    # 获取用户交互数据
    interactions = []
    
    if item_type == 'place':
        # 获取附近的景点
        nearby_places = Place.get_nearby_places(latitude, longitude, radius)
        
        if nearby_places:
            # 构建用户-物品矩阵
            recommender._build_user_item_matrix(interactions, item_type='place')
            
            # 根据方法选择推荐函数
            if method == 'user':
                recommendations = recommender.recommend_places_user_based(user, nearby_places, top_n)
            else:
                recommendations = recommender.recommend_places_item_based(user, nearby_places, top_n)
            
            # 添加距离信息
            for item in recommendations:
                item['distance'] = calculate_distance(latitude, longitude, item['latitude'], item['longitude'])
            
            return recommendations
        else:
            return []
    
    elif item_type == 'food':
        # 获取附近的美食
        nearby_foods = Food.get_nearby_foods(latitude, longitude, radius)
        
        if nearby_foods:
            # 构建用户-物品矩阵
            recommender._build_user_item_matrix(interactions, item_type='food')
            
            # 根据方法选择推荐函数
            if method == 'user':
                recommendations = recommender.recommend_foods_user_based(user, nearby_foods, top_n)
            else:
                recommendations = recommender.recommend_foods_item_based(user, nearby_foods, top_n)
            
            # 添加距离信息
            for item in recommendations:
                item['distance'] = calculate_distance(latitude, longitude, item['latitude'], item['longitude'])
            
            return recommendations
        else:
            return []