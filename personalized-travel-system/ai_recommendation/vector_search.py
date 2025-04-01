import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple, Union
import sys
import os
import json
import pickle
from collections import defaultdict

# 添加项目根目录到系统路径，以便导入backend模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  

# 导入后端模型和工具
from backend.models.user import User
from backend.models.place import Place
from backend.models.food import Food
from backend.utils.helpers import calculate_distance

# 尝试导入向量搜索相关库
try:
    from annoy import AnnoyIndex
    ANNOY_AVAILABLE = True
except ImportError:
    ANNOY_AVAILABLE = False
    print("Warning: annoy not installed. Using fallback search methods.")

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("Warning: faiss not installed. Using fallback search methods.")

# 尝试导入NLP相关库，用于特征提取
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


class VectorSearchEngine:
    """向量搜索引擎
    
    实现高效的向量搜索，用于景点和美食推荐
    """
    
    def __init__(self, vector_dim: int = 100, use_bert: bool = False, use_faiss: bool = True):
        """初始化搜索引擎
        
        Args:
            vector_dim: 向量维度
            use_bert: 是否使用BERT进行特征提取
            use_faiss: 是否使用FAISS进行向量搜索，如果为False则使用Annoy
        """
        self.vector_dim = vector_dim
        self.use_bert = use_bert and BERT_AVAILABLE
        self.use_faiss = use_faiss and FAISS_AVAILABLE
        
        # 初始化特征提取模型
        self.word2vec_model = None
        self.bert_model = None
        self.bert_tokenizer = None
        
        if self.use_bert:
            self._init_bert()
        elif WORD2VEC_AVAILABLE:
            self._init_word2vec()
        
        # 初始化索引
        self.place_index = None
        self.food_index = None
        self.place_ids = []
        self.food_ids = []
        self.place_vectors = []
        self.food_vectors = []
        self.place_id_to_index = {}
        self.food_id_to_index = {}
        
        # 缓存向量
        self.place_vector_cache = {}
        self.food_vector_cache = {}
    
    def _init_word2vec(self, vector_size: int = 100):
        """初始化Word2Vec模型"""
        self.vector_dim = vector_size
        # 模拟模型初始化，实际应用中应加载预训练模型
        self.word2vec_model = None
    
    def _init_bert(self):
        """初始化BERT模型"""
        if BERT_AVAILABLE:
            try:
                self.bert_tokenizer = BertTokenizer.from_pretrained('bert-base-chinese')
                self.bert_model = BertModel.from_pretrained('bert-base-chinese')
                # 设置为评估模式
                self.bert_model.eval()
            except Exception as e:
                print(f"Error loading BERT model: {e}")
                self.use_bert = False
    
    def _text_to_vector(self, text: str) -> np.ndarray:
        """将文本转换为向量
        
        Args:
            text: 输入文本
            
        Returns:
            文本的向量表示
        """
        if self.use_bert:
            return self._text_to_vector_bert(text)
        elif WORD2VEC_AVAILABLE and self.word2vec_model is not None:
            return self._text_to_vector_word2vec(text)
        else:
            return self._text_to_vector_fallback(text)
    
    def _text_to_vector_word2vec(self, text: str) -> np.ndarray:
        """使用Word2Vec将文本转换为向量
        
        Args:
            text: 输入文本
            
        Returns:
            文本的向量表示
        """
        if not WORD2VEC_AVAILABLE or self.word2vec_model is None:
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
            return np.zeros(self.vector_dim)
    
    def _text_to_vector_bert(self, text: str) -> np.ndarray:
        """使用BERT将文本转换为向量
        
        Args:
            text: 输入文本
            
        Returns:
            文本的向量表示
        """
        if not BERT_AVAILABLE or self.bert_model is None:
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
        words = text.lower().split()
        vector = np.zeros(self.vector_dim)
        
        # 使用词的哈希值来填充向量
        for word in words:
            hash_val = hash(word) % self.vector_dim
            vector[hash_val] += 1
        
        # 归一化
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        
        return vector
    
    def _get_place_vector(self, place: Place) -> np.ndarray:
        """获取景点的向量表示
        
        Args:
            place: 景点对象
            
        Returns:
            景点的向量表示
        """
        # 检查缓存
        if place.id in self.place_vector_cache:
            return self.place_vector_cache[place.id]
        
        # 组合景点的名称、描述和标签
        text = f"{place.name} {place.description or ''} {' '.join(place.tags or [])}"
        
        # 将文本转换为向量
        vector = self._text_to_vector(text)
        
        # 缓存向量
        self.place_vector_cache[place.id] = vector
        
        return vector
    
    def _get_food_vector(self, food: Food) -> np.ndarray:
        """获取美食的向量表示
        
        Args:
            food: 美食对象
            
        Returns:
            美食的向量表示
        """
        # 检查缓存
        if food.id in self.food_vector_cache:
            return self.food_vector_cache[food.id]
        
        # 组合美食的名称、描述和标签
        text = f"{food.name} {food.description or ''} {' '.join(food.taste_tags or [])} {' '.join(food.signature_dishes or [])}"
        
        # 将文本转换为向量
        vector = self._text_to_vector(text)
        
        # 缓存向量
        self.food_vector_cache[food.id] = vector
        
        return vector
    
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
        
        # 将文本转换为向量
        return self._text_to_vector(text)
    
    def build_place_index(self, places: List[Place]):
        """构建景点索引
        
        Args:
            places: 景点列表
        """
        self.place_ids = [place.id for place in places]
        self.place_id_to_index = {place_id: i for i, place_id in enumerate(self.place_ids)}
        
        # 计算所有景点的向量表示
        self.place_vectors = []
        for place in places:
            vector = self._get_place_vector(place)
            self.place_vectors.append(vector)
        
        # 构建索引
        if self.use_faiss and FAISS_AVAILABLE:
            self._build_faiss_index(self.place_vectors, 'place')
        elif ANNOY_AVAILABLE:
            self._build_annoy_index(self.place_vectors, 'place')
        else:
            print("No vector search library available. Using brute force search.")
    
    def build_food_index(self, foods: List[Food]):
        """构建美食索引
        
        Args:
            foods: 美食列表
        """
        self.food_ids = [food.id for food in foods]
        self.food_id_to_index = {food_id: i for i, food_id in enumerate(self.food_ids)}
        
        # 计算所有美食的向量表示
        self.food_vectors = []
        for food in foods:
            vector = self._get_food_vector(food)
            self.food_vectors.append(vector)
        
        # 构建索引
        if self.use_faiss and FAISS_AVAILABLE:
            self._build_faiss_index(self.food_vectors, 'food')
        elif ANNOY_AVAILABLE:
            self._build_annoy_index(self.food_vectors, 'food')
        else:
            print("No vector search library available. Using brute force search.")
    
    def _build_faiss_index(self, vectors: List[np.ndarray], index_type: str):
        """使用FAISS构建索引
        
        Args:
            vectors: 向量列表
            index_type: 索引类型，'place'或'food'
        """
        if not FAISS_AVAILABLE:
            return
        
        # 将向量转换为numpy数组
        vectors_array = np.array(vectors).astype('float32')
        
        # 创建索引
        index = faiss.IndexFlatL2(vectors_array.shape[1])
        index.add(vectors_array)
        
        # 保存索引
        if index_type == 'place':
            self.place_index = index
        else:
            self.food_index = index
    
    def _build_annoy_index(self, vectors: List[np.ndarray], index_type: str, n_trees: int = 10):
        """使用Annoy构建索引
        
        Args:
            vectors: 向量列表
            index_type: 索引类型，'place'或'food'
            n_trees: 树的数量，增加树的数量可以提高准确性，但会增加构建时间
        """
        if not ANNOY_AVAILABLE or not vectors:
            return
        
        # 创建索引
        index = AnnoyIndex(len(vectors[0]), 'angular')
        
        # 添加向量
        for i, vector in enumerate(vectors):
            index.add_item(i, vector)
        
        # 构建索引
        index.build(n_trees)
        
        # 保存索引
        if index_type == 'place':
            self.place_index = index
        else:
            self.food_index = index
    
    def search_places(self, query_vector: np.ndarray, top_n: int = 10) -> List[Tuple[int, float]]:
        """搜索最相似的景点
        
        Args:
            query_vector: 查询向量
            top_n: 返回的结果数量
            
        Returns:
            景点ID和相似度分数的列表
        """
        if self.use_faiss and FAISS_AVAILABLE and self.place_index is not None:
            return self._search_faiss(query_vector, self.place_index, self.place_ids, top_n)
        elif ANNOY_AVAILABLE and self.place_index is not None:
            return self._search_annoy(query_vector, self.place_index, self.place_ids, top_n)
        else:
            return self._search_brute_force(query_vector, self.place_vectors, self.place_ids, top_n)
    
    def search_foods(self, query_vector: np.ndarray, top_n: int = 10) -> List[Tuple[int, float]]:
        """搜索最相似的美食
        
        Args:
            query_vector: 查询向量
            top_n: 返回的结果数量
            
        Returns:
            美食ID和相似度分数的列表
        """
        if self.use_faiss and FAISS_AVAILABLE and self.food_index is not None:
            return self._search_faiss(query_vector, self.food_index, self.food_ids, top_n)
        elif ANNOY_AVAILABLE and self.food_index is not None:
            return self._search_annoy(query_vector, self.food_index, self.food_ids, top_n)
        else:
            return self._search_brute_force(query_vector, self.food_vectors, self.food_ids, top_n)
    
    def _search_faiss(self, query_vector: np.ndarray, index, ids: List[int], top_n: int) -> List[Tuple[int, float]]:
        """使用FAISS搜索
        
        Args:
            query_vector: 查询向量
            index: FAISS索引
            ids: ID列表
            top_n: 返回的结果数量
            
        Returns:
            ID和相似度分数的列表
        """
        # 将查询向量转换为numpy数组
        query_array = np.array([query_vector]).astype('float32')
        
        # 搜索
        distances, indices = index.search(query_array, top_n)
        
        # 转换结果
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(ids):
                # FAISS返回的是距离，转换为相似度
                similarity = 1.0 / (1.0 + distances[0][i])
                results.append((ids[idx], similarity))
        
        return results
    
    def _search_annoy(self, query_vector: np.ndarray, index, ids: List[int], top_n: int) -> List[Tuple[int, float]]:
        """使用Annoy搜索
        
        Args:
            query_vector: 查询向量
            index: Annoy索引
            ids: ID列表
            top_n: 返回的结果数量
            
        Returns:
            ID和相似度分数的列表
        """
        # 搜索
        indices, distances = index.get_nns_by_vector(query_vector, top_n, include_distances=True)
        
        # 转换结果
        results = []
        for i, idx in enumerate(indices):
            if idx < len(ids):
                # Annoy返回的是角度距离，转换为相似度
                similarity = 1.0 - distances[i] / 2.0
                results.append((ids[idx], similarity))
        
        return results
    
    def _search_brute_force(self, query_vector: np.ndarray, vectors: List[np.ndarray], ids: List[int], top_n: int) -> List[Tuple[int, float]]:
        """暴力搜索
        
        当没有可用的向量搜索库时使用
        
        Args:
            query_vector: 查询向量
            vectors: 向量列表
            ids: ID列表
            top_n: 返回的结果数量
            
        Returns:
            ID和相似度分数的列表
        """
        # 计算所有向量与查询向量的相似度
        similarities = []
        for i, vector in enumerate(vectors):
            # 计算余弦相似度
            dot_product = np.dot(query_vector, vector)
            norm_a = np.linalg.norm(query_vector)
            norm_b = np.linalg.norm(vector)
            
            if norm_a == 0 or norm_b == 0:
                similarity = 0
            else:
                similarity = dot_product / (norm_a * norm_b)
            
            similarities.append((i, similarity))
        
        # 排序并返回前N个结果
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for i, similarity in similarities[:top_n]:
            if i < len(ids):
                results.append((ids[i], similarity))
        
        return results
    
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
        
        # 构建景点索引
        if not self.place_index:
            self.build_place_index(places)
        
        # 搜索最相似的景点
        similar_places = self.search_places(user_vector, top_n)
        
        # 转换结果
        result = []
        for place_id, similarity in similar_places:
            # 查找景点对象
            place = next((p for p in places if p.id == place_id), None)
            if place:
                place_dict = place.to_dict() if hasattr(place, 'to_dict') else {}
                place_dict.update({
                    'similarity': float(similarity)
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
        
        # 构建美食索引
        if not self.food_index:
            self.build_food_index(foods)
        
        # 搜索最相似的美食
        similar_foods = self.search_foods(user_vector, top_n)
        
        # 转换结果
        result = []
        for food_id, similarity in similar_foods:
            # 查找美食对象
            food = next((f for f in foods if f.id == food_id), None)
            if food:
                food_dict = food.to_dict() if hasattr(food, 'to_dict') else {}
                food_dict.update({
                    'similarity': float(similarity)
                })
                result.append(food_dict)
        
        return result
    
    def save_indices(self, place_index_path: str = None, food_index_path: str = None):
        """保存索引
        
        Args:
            place_index_path: 景点索引保存路径
            food_index_path: 美食索引保存路径
        """
        if place_index_path and self.place_index:
            if self.use_faiss and FAISS_AVAILABLE:
                faiss.write_index(self.place_index, place_index_path)
            elif ANNOY_AVAILABLE:
                self.place_index.save(place_index_path)
            
            # 保存ID映射
            with open(f"{place_index_path}.ids", 'wb') as f:
                pickle.dump(self.place_ids, f)
        
        if food_index_path and self.food_index:
            if self.use_faiss and FAISS_AVAILABLE:
                faiss.write_index(self.food_index, food_index_path)
            elif ANNOY_AVAILABLE:
                self.food_index.save(food_index_path)
            
            # 保存ID映射
            with open(f"{food_index_path}.ids", 'wb') as f:
                pickle.dump(self.food_ids, f)
    
    def load_indices(self, place_index_path: str = None, food_index_path: str = None):
        """加载索引
        
        Args:
            place_index_path: 景点索引路径
            food_index_path: 美食索引路径
        """
        if place_index_path and os.path.exists(place_index_path):
            if self.use_faiss and FAISS_AVAILABLE:
                self.place_index = faiss.read_index(place_index_path)
            elif ANNOY_AVAILABLE:
                # 需要知道向量维度
                if self.place_vectors:
                    dim = len(self.place_vectors[0])
                else:
                    dim = self.vector_dim
                self.place_index = AnnoyIndex(dim, 'angular')
                self.place_index.load(place_index_path)
            
            # 加载ID映射
            if os.path.exists(f"{place_index_path}.ids"):
                with open(f"{place_index_path}.ids", 'rb') as f:
                    self.place_ids = pickle.load(f)
                self.place_id_to_index = {place_id: i for i, place_id in enumerate(self.place_ids)}
        
        if food_index_path and os.path.exists(food_index_path):
            if self.use_faiss and FAISS_AVAILABLE:
                self.food_index = faiss.read_index(food_index_path)
            elif ANNOY_AVAILABLE:
                # 需要知道向量维度
                if self.food_vectors:
                    dim = len(self.food_vectors[0])
                else:
                    dim = self.vector_dim
                self.food_index = AnnoyIndex(dim, 'angular')
                self.food_index.load(food_index_path)
            
            # 加载ID映射
            if os.path.exists(f"{food_index_path}.ids"):
                with open(f"{food_index_path}.ids", 'rb') as f:
                    self.food_ids = pickle.load(f)
                self.food_id_to_index = {food_id: i for i, food_id in enumerate(self.food_ids)}


# 提供一个简单的函数接口，方便后端调用
def get_vector_search_recommendations(user_id: int, item_type: str = 'place', top_n: int = 10) -> List[Dict[str, Any]]:
    """获取基于向量搜索的推荐
    
    Args:
        user_id: 用户ID
        item_type: 推荐项目类型，'place'或'food'
        top_n: 返回的推荐数量
        
    Returns:
        推荐项目列表
    """
    # 初始化搜索引擎
    search_engine = VectorSearchEngine(use_bert=BERT_AVAILABLE, use_faiss=FAISS_AVAILABLE)
    
    # 获取用户
    user = User.query.get(user_id)
    if not user:
        return []
    
    if item_type == 'place':
        # 获取所有景点
        places = Place.query.all()
        return search_engine.recommend_places(user, places, top_n)
    elif item_type == 'food':
        # 获取所有美食
        foods = Food.query.all()
        return search_engine.recommend_foods(user, foods, top_n)
    else:
        return []


# 提供一个考虑地理位置的推荐函数
def get_location_aware_vector_recommendations(user_id: int, latitude: float, longitude: float, 
                                           radius: float = 10.0, item_type: str = 'place', 
                                           top_n: int = 10) -> List[Dict[str, Any]]:
    """获取考虑地理位置的基于向量搜索的推荐
    
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
    # 初始化搜索引擎
    search_engine = VectorSearchEngine(use_bert=BERT_AVAILABLE, use_faiss=FAISS_AVAILABLE)
    
    # 获取用户
    user = User.query.get(user_id)
    if not user:
        return []
    
    if item_type == 'place':
        # 获取附近的景点
        nearby_places = Place.get_nearby_places(latitude, longitude, radius)
        
        if nearby_places:
            recommendations = search_engine.recommend_places(user, nearby_places, top_n)
            
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
            recommendations = search_engine.recommend_foods(user, nearby_foods, top_n)
            
            # 添加距离信息
            for item in recommendations:
                item['distance'] = calculate_distance(latitude, longitude, item['latitude'], item['longitude'])
            
            return recommendations
        else:
            return []
    
    else:
        return []