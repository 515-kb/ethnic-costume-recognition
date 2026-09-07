#!/usr/bin/env python3
"""
Ethnic Costume Recognition - 民族服饰智能识别系统
基于多模态大模型（Qwen-VL-Plus）的民族服饰图像识别 Web 演示系统
支持 55 个民族服饰类别识别
"""

import os
import json
import base64
import uuid
import re
import time
from flask import Flask, render_template, request, jsonify, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'ethnic-costume-recognition-dev')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ========== 加载类别数据 ==========
CLASSES_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'classes.json')
with open(CLASSES_PATH, 'r', encoding='utf-8') as f:
    CLASSES_DATA = json.load(f)

CLASS_NAMES = [c['name'] for c in CLASSES_DATA['classes']]
CLASS_NAMES_EN = [c['name_en'] for c in CLASSES_DATA['classes']]
CLASSES_LIST_TEXT = "、".join(CLASS_NAMES)

# ========== 多模态大模型推理引擎 ==========
def get_inference_client():
    """获取推理客户端（懒加载，避免启动时必须有API key）"""
    api_key = os.environ.get('DASHSCOPE_API_KEY', '')
    if not api_key:
        return None
    from openai import OpenAI
    return OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

def run_ethnic_costume_recognition(image_base64, mime_type):
    """
    使用多模态大模型识别民族服饰
    返回识别结果JSON
    """
    client = get_inference_client()
    if client is None:
        raise RuntimeError(
            "未配置 DASHSCOPE_API_KEY 环境变量，无法进行识别。"
            "请设置环境变量后重试。"
        )

    system_prompt = f"""你是一个专业的民族服饰图像识别专家。
请分析图片中的人物服饰，判断其属于中国哪个民族的传统服饰。

可识别的民族类别（共{len(CLASS_NAMES)}个）：
{CLASSES_LIST_TEXT}

请严格按照以下JSON格式返回，不要有其他内容：
{{
    "predicted_class": "民族名称（中文，如维吾尔族）",
    "predicted_class_en": "英文名（如Uyghur）",
    "confidence": 0.95,
    "analysis": "从服饰的色彩、纹样、款式、材质、配饰等角度进行专业分析",
    "features": ["特征1", "特征2", "特征3", "特征4"]
}}

注意：
- confidence范围0.70-0.99，保留4位小数
- analysis要具体描述服饰的视觉特征，不要泛泛而谈
- features列出4-6个具体的服饰视觉特征
- 如果图片中没有明显的民族服饰，predicted_class填"未识别"，confidence低于0.5
- 只输出JSON，不要有任何解释文字"""

    resp = client.chat.completions.create(
        model="qwen-vl-plus",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/{mime_type};base64,{image_base64}"
                        }
                    },
                    {
                        "type": "text",
                        "text": "请识别图中人物所穿的民族服饰。"
                    }
                ]
            }
        ],
        temperature=0.3,
    )
    return resp.choices[0].message.content


def parse_model_output(raw_text):
    """解析模型输出的JSON"""
    try:
        json_match = re.search(r'\{[\s\S]*\}', raw_text)
        if json_match:
            return json.loads(json_match.group())
    except (json.JSONDecodeError, Exception):
        pass
    return {
        "predicted_class": "解析失败",
        "predicted_class_en": "Unknown",
        "confidence": 0.0,
        "analysis": raw_text,
        "features": []
    }


# ========== 工具函数 ==========
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_sample_images():
    """获取示例图片列表"""
    sample_images = []
    samples_dir = os.path.join(os.path.dirname(__file__), 'static', 'images', 'samples')
    if not os.path.exists(samples_dir):
        return sample_images
    for fname in sorted(os.listdir(samples_dir)):
        if fname.lower().endswith(('.jpg', '.jpeg', '.png')):
            ethnic_key = fname.split('_')[0].lower()
            label_map = {
                'uyghur': '维吾尔族服饰',
                'kazakh': '哈萨克族服饰',
                'mongolian': '蒙古族服饰',
                'miao': '苗族服饰',
            }
            sample_images.append({
                'filename': fname,
                'label': label_map.get(ethnic_key, fname),
                'path': f'images/samples/{fname}'
            })
    return sample_images


# ========== 页面路由 ==========
@app.route('/')
def index():
    """首页"""
    return render_template('index.html',
                           total_classes=CLASSES_DATA['total'],
                           api_configured=bool(os.environ.get('DASHSCOPE_API_KEY', '')))


@app.route('/detection')
def detection():
    """在线识别页面"""
    return render_template('detection.html',
                           sample_images=get_sample_images(),
                           total_classes=CLASSES_DATA['total'])


@app.route('/dataset')
def dataset():
    """数据集介绍页面"""
    return render_template('dataset.html', classes_data=CLASSES_DATA)


@app.route('/about')
def about():
    """技术说明页面"""
    return render_template('about.html')


# ========== API 路由 ==========
@app.route('/api/health')
def api_health():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'api_configured': bool(os.environ.get('DASHSCOPE_API_KEY', '')),
        'total_classes': CLASSES_DATA['total']
    })


@app.route('/api/classes')
def api_classes():
    """获取所有类别"""
    return jsonify(CLASSES_DATA)


@app.route('/api/detect', methods=['POST'])
def api_detect():
    """上传图片进行识别"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': '未上传图片'}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': '未选择文件'}), 400
        if not allowed_file(file.filename):
            return jsonify({'error': '不支持的文件格式'}), 400

        filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        with open(filepath, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')

        ext = filename.rsplit('.', 1)[1].lower()
        mime_map = {'jpg': 'jpeg', 'jpeg': 'jpeg', 'png': 'png',
                    'gif': 'gif', 'webp': 'webp', 'bmp': 'bmp'}
        mime_type = mime_map.get(ext, 'jpeg')

        start_time = time.time()
        raw_output = run_ethnic_costume_recognition(image_data, mime_type)
        elapsed = time.time() - start_time

        result = parse_model_output(raw_output)
        result['image_url'] = f'/static/uploads/{filename}'
        result['inference_time'] = round(elapsed, 2)

        return jsonify(result)

    except RuntimeError as e:
        return jsonify({'error': str(e)}), 503
    except Exception as e:
        return jsonify({'error': f'识别失败: {str(e)}'}), 500


@app.route('/api/detect_sample', methods=['POST'])
def api_detect_sample():
    """识别示例图片"""
    try:
        data = request.get_json()
        sample_path = data.get('sample_path', '')

        full_path = os.path.join(os.path.dirname(__file__), 'static', sample_path)
        if not os.path.exists(full_path):
            return jsonify({'error': '示例图片不存在'}), 404

        with open(full_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')

        ext = full_path.rsplit('.', 1)[1].lower()
        mime_map = {'jpg': 'jpeg', 'jpeg': 'jpeg', 'png': 'png',
                    'gif': 'gif', 'webp': 'webp'}
        mime_type = mime_map.get(ext, 'jpeg')

        start_time = time.time()
        raw_output = run_ethnic_costume_recognition(image_data, mime_type)
        elapsed = time.time() - start_time

        result = parse_model_output(raw_output)
        result['image_url'] = f'/static/{sample_path}'
        result['inference_time'] = round(elapsed, 2)

        return jsonify(result)

    except RuntimeError as e:
        return jsonify({'error': str(e)}), 503
    except Exception as e:
        return jsonify({'error': f'识别失败: {str(e)}'}), 500


if __name__ == '__main__':
    print("=" * 60)
    print("  民族服饰智能识别系统")
    print(f"  支持类别: {CLASSES_DATA['total']} 个民族")
    print(f"  API Key 已配置: {'是' if os.environ.get('DASHSCOPE_API_KEY') else '否（请设置 DASHSCOPE_API_KEY 环境变量）'}")
    print("  访问地址: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)
