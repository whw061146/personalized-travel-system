from flask import Blueprint, request, jsonify, current_app, url_for, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime
import requests
import json
import numpy as np
from PIL import Image
import io

# 导入数据库和模型
from models import db
from models.user import User

# 创建AI生成内容蓝图
aigc_bp = Blueprint('aigc', __name__)

# 配置上传和生成图像的保存路径
UPLOAD_FOLDER = os.path.join(current_app.root_path, 'static', 'generated_images')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 允许的图片扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@aigc_bp.route('/generate-image', methods=['POST'])
@jwt_required()
def generate_image():
    """使用Stable Diffusion生成旅游图像
    
    Request Body:
        prompt: 图像生成提示词
        style: 图像风格 (realistic, anime, painting, etc.)
        size: 图像尺寸 (512x512, 768x768, etc.)
    
    Returns:
        生成的图像URL
    """
    # 获取当前用户ID
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({
            'status': 'error',
            'message': '用户不存在'
        }), 404
    
    # 获取请求数据
    data = request.get_json()
    
    if not data or 'prompt' not in data:
        return jsonify({
            'status': 'error',
            'message': '缺少必要参数：prompt'
        }), 400
    
    prompt = data.get('prompt')
    style = data.get('style', 'realistic')
    size = data.get('size', '512x512')
    
    try:
        # 这里应该调用Stable Diffusion API或本地模型
        # 由于实际环境中可能没有Stable Diffusion，这里使用模拟数据
        # 在实际应用中，应该使用transformers库加载和运行Stable Diffusion模型
        
        # 模拟生成图像过程
        # 生成随机图像（实际应用中应替换为Stable Diffusion生成的图像）
        width, height = map(int, size.split('x'))
        random_image = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
        img = Image.fromarray(random_image)
        
        # 生成唯一文件名并保存图像
        filename = f"{uuid.uuid4()}.png"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        img.save(file_path)
        
        # 构建图像URL
        image_url = url_for('static', filename=f'generated_images/{filename}', _external=True)
        
        return jsonify({
            'status': 'success',
            'data': {
                'image_url': image_url,
                'prompt': prompt,
                'style': style,
                'size': size
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'图像生成失败: {str(e)}'
        }), 500

@aigc_bp.route('/text-to-image', methods=['POST'])
@jwt_required()
def text_to_image():
    """文本到图像生成功能
    
    Request Body:
        text: 描述文本
        style: 图像风格
        location: 位置信息（可选）
    
    Returns:
        生成的图像URL
    """
    # 获取当前用户ID
    current_user_id = get_jwt_identity()
    
    # 获取请求数据
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({
            'status': 'error',
            'message': '缺少必要参数：text'
        }), 400
    
    text = data.get('text')
    style = data.get('style', 'photo')
    location = data.get('location', '')
    
    try:
        # 构建提示词
        prompt = f"A {style} of {text}"
        if location:
            prompt += f" in {location}"
        
        # 调用图像生成API（这里复用上面的生成逻辑）
        # 生成随机图像（实际应用中应替换为Stable Diffusion生成的图像）
        width, height = 512, 512
        random_image = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
        img = Image.fromarray(random_image)
        
        # 生成唯一文件名并保存图像
        filename = f"{uuid.uuid4()}.png"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        img.save(file_path)
        
        # 构建图像URL
        image_url = url_for('static', filename=f'generated_images/{filename}', _external=True)
        
        return jsonify({
            'status': 'success',
            'data': {
                'image_url': image_url,
                'prompt': prompt,
                'style': style
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'文本到图像生成失败: {str(e)}'
        }), 500

@aigc_bp.route('/generate-animation', methods=['POST'])
@jwt_required()
def generate_animation():
    """生成旅游动画
    
    Request Body:
        location: 位置名称
        style: 动画风格
        duration: 动画时长（秒）
    
    Returns:
        生成的动画URL
    """
    # 获取当前用户ID
    current_user_id = get_jwt_identity()
    
    # 获取请求数据
    data = request.get_json()
    
    if not data or 'location' not in data:
        return jsonify({
            'status': 'error',
            'message': '缺少必要参数：location'
        }), 400
    
    location = data.get('location')
    style = data.get('style', 'realistic')
    duration = data.get('duration', 5)
    
    try:
        # 这里应该调用动画生成API或本地模型
        # 由于实际环境中可能没有动画生成模型，这里使用模拟数据
        # 在实际应用中，应该使用适当的库生成动画
        
        # 模拟生成动画过程（实际应用中应替换为真实动画生成）
        # 这里只返回一个模拟的URL
        animation_url = url_for('static', filename=f'generated_animations/sample.mp4', _external=True)
        
        return jsonify({
            'status': 'success',
            'data': {
                'animation_url': animation_url,
                'location': location,
                'style': style,
                'duration': duration
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'动画生成失败: {str(e)}'
        }), 500

@aigc_bp.route('/style-transfer', methods=['POST'])
@jwt_required()
def style_transfer():
    """图像风格转换
    
    Request Body:
        image_file: 原始图像文件
        style: 目标风格
    
    Returns:
        转换后的图像URL
    """
    # 获取当前用户ID
    current_user_id = get_jwt_identity()
    
    # 检查是否有文件上传
    if 'image_file' not in request.files:
        return jsonify({
            'status': 'error',
            'message': '没有上传图像文件'
        }), 400
    
    file = request.files['image_file']
    style = request.form.get('style', 'painting')
    
    # 检查文件名是否为空
    if file.filename == '':
        return jsonify({
            'status': 'error',
            'message': '未选择文件'
        }), 400
    
    # 检查文件类型
    if not allowed_file(file.filename):
        return jsonify({
            'status': 'error',
            'message': f'不支持的文件类型，允许的类型: {", ".join(ALLOWED_EXTENSIONS)}'
        }), 400
    
    try:
        # 保存原始图像
        original_filename = secure_filename(file.filename)
        original_path = os.path.join(UPLOAD_FOLDER, original_filename)
        file.save(original_path)
        
        # 读取图像并应用风格转换
        # 这里应该调用风格转换模型
        # 由于实际环境中可能没有风格转换模型，这里使用模拟数据
        
        # 模拟风格转换（实际应用中应替换为真实风格转换）
        img = Image.open(original_path)
        # 简单处理：根据风格应用不同的滤镜
        if style == 'painting':
            # 模拟绘画风格
            img = img.convert('RGB')
        elif style == 'sketch':
            # 模拟素描风格
            img = img.convert('L')
            img = img.convert('RGB')
        
        # 生成唯一文件名并保存转换后的图像
        styled_filename = f"styled_{uuid.uuid4()}.png"
        styled_path = os.path.join(UPLOAD_FOLDER, styled_filename)
        img.save(styled_path)
        
        # 构建图像URL
        styled_url = url_for('static', filename=f'generated_images/{styled_filename}', _external=True)
        
        return jsonify({
            'status': 'success',
            'data': {
                'original_url': url_for('static', filename=f'generated_images/{original_filename}', _external=True),
                'styled_url': styled_url,
                'style': style
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'风格转换失败: {str(e)}'
        }), 500