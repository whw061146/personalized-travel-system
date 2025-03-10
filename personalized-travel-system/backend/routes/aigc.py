from flask import Blueprint, request, jsonify
from backend.models import db, AIGCContent, User
import openai  # 假设使用 OpenAI API 进行文本生成
from PIL import Image
import io
import base64

# AIGC 生成内容 Blueprint
aigc_bp = Blueprint('aigc', __name__)

# 生成 AI 旅游日记（基于文本生成）
@aigc_bp.route('/generate-diary', methods=['POST'])
def generate_diary():
    data = request.get_json()
    user_id = data.get('user_id')
    prompt = data.get('prompt')
    
    if not user_id or not prompt:
        return jsonify({'error': '缺少必要参数'}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    # 调用 OpenAI API 进行文本生成
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "你是一个旅游博主，请撰写一篇精彩的游记。"},
                  {"role": "user", "content": prompt}]
    )
    generated_text = response["choices"][0]["message"]["content"]
    
    # 存储生成内容
    new_content = AIGCContent(user_id=user_id, content=generated_text)
    db.session.add(new_content)
    db.session.commit()
    
    return jsonify({'generated_diary': generated_text}), 200

# 生成 AI 旅游图片（基于图像生成）
@aigc_bp.route('/generate-image', methods=['POST'])
def generate_image():
    data = request.get_json()
    user_id = data.get('user_id')
    prompt = data.get('prompt')
    
    if not user_id or not prompt:
        return jsonify({'error': '缺少必要参数'}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    # 这里假设调用 Stable Diffusion API 生成图像
    image = Image.new('RGB', (512, 512), (255, 255, 255))  # 这里使用占位图像，实际应调用 AI 生成
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    encoded_image = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
    
    return jsonify({'generated_image': encoded_image}), 200
