import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple, Union
import sys
import os

# 添加项目根目录到系统路径，以便导入backend模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入后端模型和工具
from backend.models.user import User
from backend.models.place import Place
from backend.models.food import Food
from backend.utils.helpers import calculate_distance

# 尝试导入NLP相关库，如果不存在则提供备用方案
try:
    from gensim.models import Word2Vec
    from gensim.models.doc2vec import Doc2Vec, TaggedDocument
    WORD2VEC_AVAILABLE = True
except ImportError:
    WORD2VEC_AVAILABLE = False
    print("Warning: gensim not installed. Using fallback similarity methods.")

try:
    import torch
    from transformers import BertModel, BertTokenizer
    BERT_AVAILABLE = True
except ImportError:
    BERT_AVAILABLE = False
    print("Warning: transformers not installed. Using fallback similarity methods.")


class ContentBasedRecommender:
    """基于内容的推荐系统
    
    使用文本特征和用户偏好进行景点和美食推荐
    """
    
    def __init__(self, use_bert: bool = False):
        """初始化推荐器
        
        Args:
            use_bert: 是否使用BERT模型，如果为False则使用Word2Vec或备用方法
        """
        self.use_bert = use_bert and BERT_AVAILABLE
        self.word2vec_model = None
        self.bert_model = None
        self.bert_tokenizer = None
        
        # 初始化模型
        if self.use_bert:
            self._init_bert()
        elif WORD2VEC_AVAILABLE:
            self._init_word2vec()
    
    def _init_word2vec(self, vector_size: int = 100):
        """初始化Word2Vec模型"""
        # 这里应该加载预训练模型或训练新模型
        # 在实际应用中，应该使用预训练好的模型
        self.vector_size = vector_size
        # 模拟模型初始化
        self.word2vec_model = None
    
    def _init_bert(self):
        """初始化BERT模型"""
        # 加载预训练的BERT模型和分词器
        # 在实际应用中，应该使用预训练好的模型
        if BERT_AVAILABLE:
            try:
                self.bert_tokenizer = BertTokenizer.from_pretrained('bert-base-chinese')
                self.bert_model = BertModel.from_pretrained('bert-base-chinese')
                # 设置为评估模式
                self.bert_model.eval()
            except Exception as e:
                print(f"Error loading BERT model: {e}")
                self.use_bert = False
    
    def _text_to_vector_word2vec(self, text: str) -> np.ndarray:
        """使用Word2Vec将文本转换为向量
        
        Args:
            text: 输入文本
            
        Returns:
            文本的向量表示
        """
        if not WORD2VEC_AVAILABLE or self.word2vec_model is None:
            # 备用方法：使用简单的词袋模型
            return self._text_to_vector_fallback(text)
        
        # 分词
        words = text.lower().split()
        
        # 获取每个词的向量并计算平均值
        word_vectors = []
        for word in words:
            if word in self.word2vec_model.wv:
                word_vectors.append(self.word2vec_model.wv[word])
        
        if word_vectors:
            return np.mean(word_vectors, axis=0)
        else:
            # 如果没有词向量，返回零向量
            return np.zeros(self.vector_size)
    
    def _text_to_vector_bert(self, text: str) -> np.ndarray:
        """使用BERT将文本转换为向量
        
        Args:
            text: 输入文本
            
        Returns:
            文本的向量表示
        """
        if not BERT_AVAILABLE or self.bert_model is None:
            # 备用方法
            return self._text_to_vector_fallback(text)
        
        try:
            # 对文本进行编码
            inputs = self.bert_tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
            
            # 不计算梯度
            with torch.no_grad():
                outputs = self.bert_model(**inputs)
            
            # 使用[CLS]标记的输出作为文本的向量表示
            return outputs.last_hidden_state[:, 0, :].numpy()[0]
        except Exception as e:
            print(f"Error in BERT encoding: {e}")
            return self._text_to_vector_fallback(text)
    
    def _text_to_vector_fallback(self, text: str) -> np.ndarray:
        """备用的文本向量化方法
        
        当Word2Vec和BERT都不可用时使用
        
        Args:
            text: 输入文本
            
        Returns:
            文本的向量表示
        """
        # 简单的词频统计
        # 在实际应用中，应该使用更复杂的方法
        words = text.lower().split()
        # 创建一个简单的向量，长度为100
        vector = np.zeros(100)
        
        # 使用词的哈希值来填充向量
        for i, word in enumerate(words):
            hash_val = hash(word) % 100
            vector[hash_val] += 1
        
        # 归一化
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        
        return vector
    
    def _calculate_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """计算两个向量的余弦相似度
        
        Args:
            vec1: 第一个向量
            vec2: 第二个向量
            
        Returns:
            两个向量的余弦相似度
        """
        # 计算余弦相似度
        dot_product = np.dot(vec1, vec2)
        norm_a = np.linalg.norm(vec1)
        norm_b = np.linalg.norm(vec2)
        
        if norm_a == 0 or norm_b == 0:
            return 0
        
        return dot_product / (norm_a * norm_b)
    
    def _get_place_vector(self, place: Place) -> np.ndarray:
        """获取景点的向量表示
        
        Args:
            place: 景点对象
            
        Returns:
            景点的向量表示
        """
        # 组合景点的名称、描述和标签
        text = f"{place.name} {place.description or ''} {' '.join(place.tags or [])}"
        
        # 使用选定的方法将文本转换为向量
        if self.use_bert:
            return self._text_to_vector_bert(text)
        else:
            return self._text_to_vector_word2vec(text)
    
    def _get_food_vector(self, food: Food) -> np.ndarray:
        """获取美食的向量表示
        
        Args:
            food: 美食对象
            
        Returns:
            美食的向量表示
        """
        # 组合美食的名称、描述和标签
        text = f"{food.name} {food.description or ''} {' '.join(food.taste_tags or [])} {' '.join(food.signature_dishes or [])}"
        
        # 使用选定的方法将文本转换为向量
        if self.use_bert:
            return self._text_to_vector_bert(text)
        else:
            return self._text_to_vector_word2vec(text)
    
    def _get_user_preference_vector(self, user: User) -> np.ndarray:
        """获取用户偏好的向量表示
        
        Args:
            user: 用户对象
            
        Returns:
            用户偏好的向量表示
        """
        # 组合用户的旅游偏好和美食偏好
        preferences = []
        if user.travel_preferences:
            preferences.extend(user.travel_preferences)
        if user.food_preferences:
            preferences.extend(user.food_preferences)
        
        text = " ".join(preferences)
        
        # 使用选定的方法将文本转换为向量
        if self.use_bert:
            return self._text_to_vector_bert(text)
        else:
            return self._text_to_vector_word2vec(text)
    
    def recommend_places(self, user: User, places: List[Place], top_n: int = 10) -> List[Dict[str, Any]]:
        """为用户推荐景点
        
        Args:
            user: 用户对象
            places: 候选景点列表
            top_n: 返回的推荐数量
            
        Returns:
            推荐景点列表，包含相似度分数
        """
        # 获取用户偏好向量
        user_vector = self._get_user_preference_vector(user)
        
        # 计算每个景点与用户偏好的相似度
        place_similarities = []
        for place in places:
            place_vector = self._get_place_vector(place)
            similarity = self._calculate_similarity(user_vector, place_vector)
            
            # 考虑用户的预算偏好
            budget_match = 1.0
            if hasattr(place, 'ticket_price') and place.ticket_price is not None and user.budget_level is not None:
                # 简单的预算匹配逻辑
                max_budget = user.budget_level * 100  # 假设每个预算等级对应100元
                if place.ticket_price > max_budget:
                    budget_match = max(0.5, 1.0 - (place.ticket_price - max_budget) / max_budget)
            
            # 综合评分
            score = similarity * budget_match
            
            place_similarities.append({
                'place': place,
                'similarity': similarity,
                'score': score
            })
        
        # 按分数排序
        place_similarities.sort(key=lambda x: x['score'], reverse=True)
        
        # 返回前N个结果
        result = []
        for item in place_similarities[:top_n]:
            place_dict = item['place'].to_dict() if hasattr(item['place'], 'to_dict') else {}
            place_dict.update({
                'similarity': float(item['similarity']),
                'score': float(item['score'])
            })
            result.append(place_dict)
        
        return result
    
    def recommend_foods(self, user: User, foods: List[Food], top_n: int = 10) -> List[Dict[str, Any]]:
        """为用户推荐美食
        
        Args:
            user: 用户对象
            foods: 候选美食列表
            top_n: 返回的推荐数量
            
        Returns:
            推荐美食列表，包含相似度分数
        """
        # 获取用户偏好向量
        user_vector = self._get_user_preference_vector(user)
        
        # 计算每个美食与用户偏好的相似度
        food_similarities = []
        for food in foods:
            food_vector = self._get_food_vector(food)
            similarity = self._calculate_similarity(user_vector, food_vector)
            
            # 考虑用户的预算偏好
            budget_match = 1.0
            if hasattr(food, 'price_level') and food.price_level is not None and user.budget_level is not None:
                # 简单的预算匹配逻辑
                if food.price_level > user.budget_level:
                    budget_match = max(0.5, 1.0 - (food.price_level - user.budget_level) / 5.0)
            
            # 综合评分
            score = similarity * budget_match
            
            food_similarities.append({
                'food': food,
                'similarity': similarity,
                'score': score
            })
        
        # 按分数排序
        food_similarities.sort(key=lambda x: x['score'], reverse=True)
        
        # 返回前N个结果
        result = []
        for item in food_similarities[:top_n]:
            food_dict = item['food'].to_dict() if hasattr(item['food'], 'to_dict') else {}
            food_dict.update({
                'similarity': float(item['similarity']),
                'score': float(item['score'])
            })
            result.append(food_dict)
        
        return result


# 提供一个简单的函数接口，方便后端调用
def get_content_based_recommendations(user_id: int, item_type: str = 'place', top_n: int = 10) -> List[Dict[str, Any]]:
    """获取基于内容的推荐
    
    Args:
        user_id: 用户ID
        item_type: 推荐项目类型，'place'或'food'
        top_n: 返回的推荐数量
        
    Returns:
        推荐项目列表
    """
    # 初始化推荐器
    recommender = ContentBasedRecommender(use_bert=BERT_AVAILABLE)
    
    # 获取用户
    user = User.query.get(user_id)
    if not user:
        return []
    
    if item_type == 'place':
        # 获取所有景点
        places = Place.query.all()
        return recommender.recommend_places(user, places, top_n)
    elif item_type == 'food':
        # 获取所有美食
        foods = Food.query.all()
        return recommender.recommend_foods(user, foods, top_n)
    else:
        return []


# 提供一个考虑地理位置的推荐函数
def get_location_aware_recommendations(user_id: int, latitude: float, longitude: float, 
                                      radius: float = 10.0, item_type: str = 'place', 
                                      top_n: int = 10) -> List[Dict[str, Any]]:
    """获取考虑地理位置的基于内容的推荐
    
    Args:
        user_id: 用户ID
        latitude: 当前纬度
        longitude: 当前经度
        radius: 搜索半径（公里）
        item_type: 推荐项目类型，'place'或'food'
        top_n: 返回的推荐数量
        
    Returns:
        推荐项目列表
    """
    # 初始化推荐器
    recommender = ContentBasedRecommender(use_bert=BERT_AVAILABLE)
    
    # 获取用户
    user = User.query.get(user_id)
    if not user:
        return []
    
    if item_type == 'place':
        # 获取附近的景点
        nearby_places = Place.get_nearby_places(latitude, longitude, radius, limit=50)
        recommendations = recommender.recommend_places(user, nearby_places, top_n)
        
        # 添加距离信息
        for item in recommendations:
            item['distance'] = calculate_distance(latitude, longitude, item['latitude'], item['longitude'])
        
        return recommendations
    elif item_type == 'food':
        # 获取附近的美食
        nearby_foods = Food.get_nearby_foods(latitude, longitude, radius, limit=50)
        recommendations = recommender.recommend_foods(user, nearby_foods, top_n)
        
        # 添加距离信息
        for item in recommendations:
            item['distance'] = calculate_distance(latitude, longitude, item['latitude'], item['longitude'])
        
        return recommendations
    else:
        return []