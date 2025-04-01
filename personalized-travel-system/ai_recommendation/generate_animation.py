import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple, Union
import sys
import os
import json
import random
import time
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import io
import base64
from datetime import datetime

# 添加项目根目录到系统路径，以便导入backend模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入后端模型和工具
from backend.models.user import User
from backend.models.place import Place
from backend.models.food import Food
from backend.utils.helpers import calculate_distance

# 尝试导入图像生成相关库
try:
    import torch
    from diffusers import StableDiffusionPipeline, DiffusionPipeline
    from diffusers import StableDiffusionImg2ImgPipeline
    DIFFUSION_AVAILABLE = True
except ImportError:
    DIFFUSION_AVAILABLE = False
    print("Warning: diffusers not installed. Using fallback image generation methods.")

try:
    from moviepy.editor import ImageSequenceClip, concatenate_videoclips, TextClip, CompositeVideoClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    print("Warning: moviepy not installed. Using fallback animation methods.")


class TravelAnimationGenerator:
    """旅游动画生成器
    
    使用Stable Diffusion生成旅游相关图像和动画
    """
    
    def __init__(self, use_stable_diffusion: bool = True, model_id: str = "runwayml/stable-diffusion-v1-5"):
        """初始化动画生成器
        
        Args:
            use_stable_diffusion: 是否使用Stable Diffusion模型
            model_id: Stable Diffusion模型ID
        """
        self.use_stable_diffusion = use_stable_diffusion and DIFFUSION_AVAILABLE
        self.model_id = model_id
        self.sd_pipeline = None
        self.img2img_pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu" if DIFFUSION_AVAILABLE else None
        
        # 加载数据
        self.places_data = self._load_places_data()
        self.food_data = self._load_food_data()
        
        # 初始化模型
        if self.use_stable_diffusion:
            self._init_stable_diffusion()
    
    def _init_stable_diffusion(self):
        """初始化Stable Diffusion模型"""
        if not DIFFUSION_AVAILABLE:
            print("Stable Diffusion not available. Using fallback methods.")
            return
        
        try:
            # 加载文生图模型
            self.sd_pipeline = StableDiffusionPipeline.from_pretrained(
                self.model_id,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            )
            self.sd_pipeline = self.sd_pipeline.to(self.device)
            
            # 加载图生图模型
            self.img2img_pipeline = StableDiffusionImg2ImgPipeline.from_pretrained(
                self.model_id,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            )
            self.img2img_pipeline = self.img2img_pipeline.to(self.device)
            
            print(f"Stable Diffusion model loaded on {self.device}")
        except Exception as e:
            print(f"Error loading Stable Diffusion model: {e}")
            self.use_stable_diffusion = False
    
    def _load_places_data(self) -> List[Dict[str, Any]]:
        """加载景点数据
        
        Returns:
            景点数据列表
        """
        try:
            places_file = os.path.join(os.path.dirname(__file__), '..', 'crawler', 'data', 'places', 'all_detailed_places.json')
            with open(places_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading places data: {e}")
            return []
    
    def _load_food_data(self) -> List[Dict[str, Any]]:
        """加载美食数据
        
        Returns:
            美食数据列表
        """
        try:
            food_file = os.path.join(os.path.dirname(__file__), '..', 'crawler', 'data', 'food', 'all_restaurants.json')
            with open(food_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading food data: {e}")
            return []
    
    def generate_place_image(self, place_id: Optional[int] = None, place_name: Optional[str] = None, 
                            prompt: Optional[str] = None, style: str = "realistic") -> Optional[Image.Image]:
        """生成景点图像
        
        Args:
            place_id: 景点ID
            place_name: 景点名称
            prompt: 自定义提示词
            style: 图像风格，可选值：realistic, cartoon, oil_painting, watercolor, sketch
            
        Returns:
            生成的图像
        """
        # 获取景点信息
        place_info = None
        if place_id is not None:
            place_info = next((p for p in self.places_data if p.get("osm_id") == place_id), None)
        elif place_name is not None:
            place_info = next((p for p in self.places_data if p.get("name") == place_name), None)
        
        # 构建提示词
        if prompt is None and place_info is not None:
            prompt = f"A beautiful view of {place_info['name']}, {place_info.get('description', '')}"
        elif prompt is None:
            prompt = "A beautiful tourist attraction in China"
        
        # 添加风格描述
        style_prompts = {
            "realistic": "realistic, detailed, high resolution, 4K, HDR",
            "cartoon": "cartoon style, vibrant colors, simple shapes",
            "oil_painting": "oil painting style, textured, artistic, museum quality",
            "watercolor": "watercolor painting, soft colors, flowing, artistic",
            "sketch": "pencil sketch, black and white, detailed lines"
        }
        
        prompt = f"{prompt}, {style_prompts.get(style, style_prompts['realistic'])}"
        
        # 生成图像
        if self.use_stable_diffusion and self.sd_pipeline is not None:
            try:
                # 使用Stable Diffusion生成图像
                result = self.sd_pipeline(prompt, num_inference_steps=30)
                return result.images[0]
            except Exception as e:
                print(f"Error generating image with Stable Diffusion: {e}")
                return self._generate_fallback_image(prompt)
        else:
            return self._generate_fallback_image(prompt)
    
    def _generate_fallback_image(self, prompt: str) -> Image.Image:
        """生成备用图像
        
        当Stable Diffusion不可用时使用
        
        Args:
            prompt: 提示词
            
        Returns:
            生成的图像
        """
        # 创建一个简单的图像，显示提示词
        width, height = 512, 512
        image = Image.new('RGB', (width, height), color=(random.randint(200, 255), random.randint(200, 255), random.randint(200, 255)))
        draw = ImageDraw.Draw(image)
        
        # 尝试加载字体，如果失败则使用默认字体
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except IOError:
            font = ImageFont.load_default()
        
        # 绘制文本
        text_lines = []
        words = prompt.split()
        current_line = ""
        
        for word in words:
            if len(current_line + word) < 40:
                current_line += word + " "
            else:
                text_lines.append(current_line)
                current_line = word + " "
        
        if current_line:
            text_lines.append(current_line)
        
        y_position = height // 2 - len(text_lines) * 15
        for line in text_lines:
            text_width = draw.textlength(line, font=font)
            draw.text(((width - text_width) // 2, y_position), line, font=font, fill=(0, 0, 0))
            y_position += 30
        
        # 添加一些随机形状作为装饰
        for _ in range(20):
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = random.randint(0, width)
            y2 = random.randint(0, height)
            draw.line((x1, y1, x2, y2), fill=(random.randint(0, 200), random.randint(0, 200), random.randint(0, 200)), width=2)
        
        # 添加模糊效果
        image = image.filter(ImageFilter.GaussianBlur(radius=1))
        
        return image
    
    def apply_style_transfer(self, image: Image.Image, style: str) -> Image.Image:
        """应用风格转换
        
        Args:
            image: 输入图像
            style: 目标风格，可选值：cartoon, oil_painting, watercolor, sketch, vintage
            
        Returns:
            风格转换后的图像
        """
        if self.use_stable_diffusion and self.img2img_pipeline is not None:
            try:
                # 构建风格提示词
                style_prompts = {
                    "cartoon": "cartoon style, vibrant colors, simple shapes",
                    "oil_painting": "oil painting style, textured, artistic, museum quality",
                    "watercolor": "watercolor painting, soft colors, flowing, artistic",
                    "sketch": "pencil sketch, black and white, detailed lines",
                    "vintage": "vintage photo, old film, nostalgic, retro"
                }
                
                prompt = style_prompts.get(style, style_prompts["cartoon"])
                
                # 使用img2img进行风格转换
                result = self.img2img_pipeline(prompt=prompt, image=image, strength=0.75, guidance_scale=7.5)
                return result.images[0]
            except Exception as e:
                print(f"Error applying style transfer with Stable Diffusion: {e}")
                return self._apply_fallback_style_transfer(image, style)
        else:
            return self._apply_fallback_style_transfer(image, style)
    
    def _apply_fallback_style_transfer(self, image: Image.Image, style: str) -> Image.Image:
        """应用备用风格转换
        
        当Stable Diffusion不可用时使用
        
        Args:
            image: 输入图像
            style: 目标风格
            
        Returns:
            风格转换后的图像
        """
        # 使用PIL进行简单的图像处理
        if style == "cartoon":
            # 增加饱和度和对比度
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(1.5)
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.2)
            # 边缘增强
            image = image.filter(ImageFilter.EDGE_ENHANCE_MORE)
        elif style == "oil_painting":
            # 增加纹理感
            image = image.filter(ImageFilter.EMBOSS)
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.3)
        elif style == "watercolor":
            # 柔化图像
            image = image.filter(ImageFilter.BLUR)
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(1.2)
        elif style == "sketch":
            # 转换为灰度并增强边缘
            image = image.convert("L")
            image = image.filter(ImageFilter.FIND_EDGES)
            image = image.filter(ImageFilter.SMOOTH)
        elif style == "vintage":
            # 添加复古效果
            image = image.convert("RGB")
            r, g, b = image.split()
            r = r.point(lambda i: i * 0.9)
            g = g.point(lambda i: i * 0.8)
            b = b.point(lambda i: i * 0.7)
            image = Image.merge("RGB", (r, g, b))
            # 添加噪点
            pixels = image.load()
            for i in range(image.width):
                for j in range(image.height):
                    if random.random() < 0.01:
                        pixels[i, j] = (255, 255, 255)
        
        return image
    
    def generate_travel_animation(self, city: str, num_frames: int = 5, 
                                duration: float = 10.0, output_path: Optional[str] = None) -> Optional[str]:
        """生成旅游动画
        
        Args:
            city: 城市名称
            num_frames: 帧数
            duration: 动画时长（秒）
            output_path: 输出路径，如果为None则返回base64编码的动画
            
        Returns:
            如果output_path为None，返回base64编码的动画，否则返回输出路径
        """
        if not MOVIEPY_AVAILABLE:
            print("MoviePy not available. Cannot generate animation.")
            return None
        
        try:
            # 筛选指定城市的景点
            city_places = [p for p in self.places_data if p.get("city", "") == city]
            if not city_places:
                # 如果找不到指定城市的景点，随机选择景点
                city_places = random.sample(self.places_data, min(num_frames, len(self.places_data)))
            else:
                # 如果景点数量不足，则重复使用
                if len(city_places) < num_frames:
                    city_places = city_places * (num_frames // len(city_places) + 1)
                # 随机选择指定数量的景点
                city_places = random.sample(city_places, min(num_frames, len(city_places)))
            
            # 生成每个景点的图像
            images = []
            for place in city_places:
                # 随机选择一种风格
                style = random.choice(["realistic", "cartoon", "oil_painting", "watercolor"])
                image = self.generate_place_image(place_id=place.get("osm_id"), style=style)
                if image:
                    # 添加景点名称文本
                    draw = ImageDraw.Draw(image)
                    try:
                        font = ImageFont.truetype("arial.ttf", 30)
                    except IOError:
                        font = ImageFont.load_default()
                    
                    text = place.get("name", "")
                    text_width = draw.textlength(text, font=font)
                    draw.text(((image.width - text_width) // 2, image.height - 50), text, font=font, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))
                    
                    # 转换为RGB模式（确保兼容性）
                    if image.mode != "RGB":
                        image = image.convert("RGB")
                    
                    images.append(np.array(image))
            
            if not images:
                print("Failed to generate any images for the animation.")
                return None
            
            # 创建动画
            frame_duration = duration / len(images)
            clip = ImageSequenceClip(images, fps=1/frame_duration)
            
            # 添加标题
            title_text = f"{city}旅游精彩瞬间"
            title_clip = TextClip(title_text, fontsize=30, color='white', bg_color='rgba(0,0,0,0.5)', font="Arial-Bold", size=clip.size)
            title_clip = title_clip.set_duration(2)
            
            # 合并标题和主要内容
            final_clip = concatenate_videoclips([title_clip, clip])
            
            # 保存或返回动画
            if output_path:
                final_clip.write_videofile(output_path, codec="libx264", fps=24)
                return output_path
            else:
                # 生成临时文件并返回base64编码
                temp_file = f"temp_animation_{int(time.time())}.mp4"
                final_clip.write_videofile(temp_file, codec="libx264", fps=24)
                
                with open(temp_file, "rb") as f:
                    video_data = f.read()
                    base64_data = base64.b64encode(video_data).decode("utf-8")
                
                # 删除临时文件
                os.remove(temp_file)
                
                return base64_data
        except Exception as e:
            print(f"Error generating travel animation: {e}")
            return None
    
    def generate_food_tour_animation(self, city: str, num_frames: int = 5, 
                                    duration: float = 10.0, output_path: Optional[str] = None) -> Optional[str]:
        """生成美食之旅动画
        
        Args:
            city: 城市名称
            num_frames: 帧数
            duration: 动画时长（秒）
            output_path: 输出路径，如果为None则返回base64编码的动画
            
        Returns:
            如果output_path为None，返回base64编码的动画，否则返回输出路径
        """
        if not MOVIEPY_AVAILABLE:
            print("MoviePy not available. Cannot generate animation.")
            return None
        
        try:
            # 筛选指定城市的餐厅
            city_restaurants = [r for r in self.food_data if r.get("city", "") == city]
            if not city_restaurants:
                # 如果找不到指定城市的餐厅，随机选择餐厅
                city_restaurants = random.sample(self.food_data, min(num_frames, len(self.food_data)))
            else:
                # 如果餐厅数量不足，则重复使用
                if len(city_restaurants) < num_frames:
                    city_restaurants = city_restaurants * (num_frames // len(city_restaurants) + 1)
                # 随机选择指定数量的餐厅
                city_restaurants = random.sample(city_restaurants, min(num_frames, len(city_restaurants)))
            
            # 生成每个餐厅的图像
            images = []
            for restaurant in city_restaurants:
                # 构建提示词
                cuisine_type = restaurant.get("cuisine_type", "")
                tags = restaurant.get("tags", [])
                if isinstance(tags, list) and tags:
                    food_items = ", ".join(tags[:3])
                elif isinstance(tags, str):
                    food_items = tags.split(",")[0] if "," in tags else tags
                else:
                    food_items = ""
                
                prompt = f"Delicious {cuisine_type} food at {restaurant.get('name', '')}, featuring {food_items}"
                
                # 生成图像
                image = self.generate_place_image(prompt=prompt, style="realistic")
                if image:
                    # 添加餐厅名称文本
                    draw = ImageDraw.Draw(image)
                    try:
                        font = ImageFont.truetype("arial.ttf", 30)
                    except IOError:
                        font = ImageFont.load_default()
                    
                    text = restaurant.get("name", "")
                    text_width = draw.textlength(text, font=font)
                    draw.text(((image.width - text_width) // 2, image.height - 50), text, font=font, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))
                    
                    # 转换为RGB模式（确保兼容性）
                    if image.mode != "RGB":
                        image = image.convert("RGB")
                    
                    images.append(np.array(image))
            
            if not images:
                print("Failed to generate any images for the animation.")
                return None
            
            # 创建动画
            frame_duration = duration / len(images)
            clip = ImageSequenceClip(images, fps=1/frame_duration)
            
            # 添加标题
            title_text = f"{city}美食之旅"
            title_clip = TextClip(title_text, fontsize=30, color='white', bg_color='rgba(0,0,0,0.5)', font="Arial-Bold", size=clip.size)
            title_clip = title_clip.set_duration(2)
            
            # 合并标题和主要内容
            final_clip = concatenate_videoclips([title_clip, clip])
            
            # 保存或返回动画
            if output_path:
                final_clip.write_videofile(output_path, codec="libx264", fps=24)
                return output_path
            else:
                # 生成临时文件并返回base64编码
                temp_file = f"temp_food_animation_{int(time.time())}.mp4"
                final_clip.write_videofile(temp_file, codec="libx264", fps=24)
                
                with open(temp_file, "rb") as f:
                    video_data = f.read()
                    base64_data = base64.b64encode(video_data).decode("utf-8")
                
                # 删除临时文件
                os.remove(temp_file)
                
                return base64_data
        except Exception as e:
            print(f"Error generating food tour animation: {e}")
            return None
    
    def generate_travel_story(self, user_id: Optional[int] = None, city: Optional[str] = None, 
                            num_places: int = 3, output_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """生成旅游故事
        
        Args:
            user_id: 用户ID，用于个性化推荐
            city: 城市名称
            num_places: 包含的景点数量
            output_path: 输出路径，如果为None则返回故事数据
            
        Returns:
            旅游故事数据，包含文本和图像
        """
        try:
            # 选择城市
            if city is None:
                # 随机选择一个城市
                cities = set(p.get("city", "") for p in self.places_data if p.get("city"))
                if cities:
                    city = random.choice(list(cities))
                else:
                    city = "北京"  # 默认城市
            
            # 筛选指定城市的景点
            city_places = [p for p in self.places_data if p.get("city", "") == city]
            if not city_places:
                # 如果找不到指定城市的景点，随机选择景点
                city_places = random.sample(self.places_data, min(num_places, len(self.places_data)))
            else:
                # 随机选择指定数量的景点
                city_places = random.sample(city_places, min(num_places, len(city_places)))
            
            # 为每个景点生成图像
            story_places = []
            for place in city_places:
                # 随机选择一种风格
                style = random.choice(["realistic", "oil_painting", "watercolor"])
                image = self.generate_place_image(place_id=place.get("osm_id"), style=style)
                
                # 转换图像为base64
                if image:
                    buffered = io.BytesIO()
                    image.save(buffered, format="JPEG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()
                    
                    # 构建景点数据
                    place_data = {
                        "id": place.get("osm_id"),
                        "name": place.get("name", ""),
                        "description": place.get("description", ""),
                        "image": img_str,
                        "rating": place.get("rating", 0),
                        "reviews": place.get("reviews", [])[:2]  # 只包含前两条评论
                    }
                    
                    story_places.append(place_data)
            
            # 查找附近的餐厅
            if city_places:
                nearby_restaurants = []
                for place in city_places:
                    lat, lon = place.get("latitude"), place.get("longitude")
                    if lat and lon:
                        # 查找附近的餐厅
                        for restaurant in self.food_data:
                            r_lat, r_lon = restaurant.get("latitude"), restaurant.get("longitude")
                            if r_lat and r_lon:
                                # 计算距离（简化版，实际应使用calculate_distance函数）
                                distance = ((lat - r_lat) ** 2 + (lon - r_lon) ** 2) ** 0.5 * 111  # 粗略转换为公里
                                if distance < 2:  # 2公里内的餐厅
                                    nearby_restaurants.append({
                                        "id": restaurant.get("amap_id"),
                                        "name": restaurant.get("name", ""),
                                        "address": restaurant.get("address", ""),
                                        "rating": restaurant.get("rating", 0),
                                        "price": restaurant.get("price", 0),
                                        "distance": distance
                                    })
                
                # 去重并排序
                unique_restaurants = {}
                for r in nearby_restaurants:
                    if r["id"] not in unique_restaurants:
                        unique_restaurants[r["id"]] = r
                
                nearby_restaurants = sorted(unique_restaurants.values(), key=lambda x: x["rating"], reverse=True)[:3]
            else:
                nearby_restaurants = []
            
            # 构建故事数据
            story_data = {
                "city": city,
                "title": f"{city}精彩一日游",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "places": story_places,
                "restaurants": nearby_restaurants,
                "summary": f"探索{city}的魅力，游览{', '.join([p['name'] for p in story_places])}等著名景点，品尝当地美食。"
            }
            
            # 保存或返回故事数据
            if output_path:
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(story_data, f, ensure_ascii=False, indent=2)
                return output_path
            else:
                return story_data
        except Exception as e:
            print(f"Error generating travel story: {e}")
            return None


# 示例用法
if __name__ == "__main__":
    # 创建动画生成器实例
    generator = TravelAnimationGenerator(use_stable_diffusion=DIFFUSION_AVAILABLE)