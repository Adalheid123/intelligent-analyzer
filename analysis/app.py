import os
import re
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
from faster_whisper import WhisperModel

app = Flask(__name__)
CORS(app)

DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"

if not DEEPSEEK_API_KEY:
    print("⚠️ 警告: DEEPSEEK_API_KEY 环境变量未设置")

openai.api_key = DEEPSEEK_API_KEY
openai.base_url = DEEPSEEK_BASE_URL

# ============================================================
# 加载 faster-whisper 语音识别模型（更轻量，兼容性更好）
# ============================================================
print("🔄 正在加载 faster-whisper 模型...")
whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
print("✅ faster-whisper 模型加载完成！")

# ============================================================
# 路由：根路径
# ============================================================
@app.route('/')
def index():
    return jsonify({"message": "智能体分析器 API 已启动", "status": "running"})

# ============================================================
# 路由：通用文本分析（7个字段）
# ============================================================
@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        text = data.get('text', '')
        if not text:
            return jsonify({"success": False, "error": "请提供文本内容"}), 400

        prompt = f"""请对以下文本进行深度分析，输出JSON格式结果，包含以下7个字段：

1. 情感分析：情感倾向（正向/中性/负向）、情感强度（1-5级）、关键情感词列表
2. 用户意图：意图类型、意图描述
3. 需求紧迫程度：等级（紧急/较急/一般）、评分（1-10）
4. 问题分类：类别、子类
5. 推荐处理路径：动作、理由
6. 置信度：评分（0-1）、说明
7. 判断依据：关键信号列表、分析说明

文本内容：{text}

请只返回JSON，不要有其他内容。"""

        response = openai.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        result_text = response.choices[0].message.content
        json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            return jsonify({"success": True, "result": result})
        else:
            return jsonify({"success": False, "error": "JSON解析失败"}), 500

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ============================================================
# 路由：教学批改（英语作文四维分析）
# ============================================================
@app.route('/analyze/teaching', methods=['POST'])
def analyze_teaching():
    try:
        data = request.json
        text = data.get('text', '')
        if not text:
            return jsonify({"success": False, "error": "请提供作文内容"}), 400

        prompt = f"""请对以下英语作文进行批改，输出JSON格式，包含：

1. 语法准确性：评分（0-10）、反馈
2. 词汇丰富度：评分（0-10）、反馈
3. 逻辑连贯性：评分（0-10）、反馈
4. 语用得体性：评分（0-10）、反馈
5. 整体评语
6. 修改优先级：列出3条最重要的修改建议

作文内容：{text}

请只返回JSON。"""

        response = openai.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        result_text = response.choices[0].message.content
        json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            return jsonify({"success": True, "result": result})
        else:
            return jsonify({"success": False, "error": "JSON解析失败"}), 500

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ============================================================
# 路由：faster-whisper 语音识别
# ============================================================
@app.route('/transcribe', methods=['POST'])
def transcribe():
    try:
        if 'audio' not in request.files:
            return jsonify({"success": False, "error": "没有找到音频文件"}), 400

        audio_file = request.files['audio']
        temp_path = "/tmp/temp_audio.wav"
        audio_file.save(temp_path)

        segments, info = whisper_model.transcribe(temp_path, language="zh")
        result_text = "".join([seg.text for seg in segments])
        os.remove(temp_path)

        return jsonify({"success": True, "text": result_text})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ============================================================
# 启动
# ============================================================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
