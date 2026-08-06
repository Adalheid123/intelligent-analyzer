echo import os > app.py
echo import re >> app.py
echo import json >> app.py
echo from flask import Flask, request, jsonify >> app.py
echo from flask_cors import CORS >> app.py
echo from openai import OpenAI >> app.py
echo. >> app.py
echo app = Flask(__name__) >> app.py
echo CORS(app) >> app.py
echo. >> app.py
echo DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY') >> app.py
echo DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1" >> app.py
echo. >> app.py
echo if not DEEPSEEK_API_KEY: >> app.py
echo     print("⚠️ 警告: DEEPSEEK_API_KEY 环境变量未设置") >> app.py
echo. >> app.py
echo client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL) >> app.py
echo. >> app.py
echo @app.route('/') >> app.py
echo def index(): >> app.py
echo     return jsonify({"message": "智能体分析器 API 已启动", "status": "running"}) >> app.py
echo. >> app.py
echo @app.route('/analyze', methods=['POST']) >> app.py
echo def analyze(): >> app.py
echo     try: >> app.py
echo         data = request.json >> app.py
echo         text = data.get('text', '') >> app.py
echo         if not text: >> app.py
echo             return jsonify({"success": False, "error": "请提供文本内容"}), 400 >> app.py
echo. >> app.py
echo         prompt = f"""请对以下文本进行深度分析，输出JSON格式结果，包含以下7个字段： >> app.py
echo 1. 情感分析：情感倾向（正向/中性/负向）、情感强度（1-5级）、关键情感词列表 >> app.py
echo 2. 用户意图：意图类型、意图描述 >> app.py
echo 3. 需求紧迫程度：等级（紧急/较急/一般）、评分（1-10） >> app.py
echo 4. 问题分类：类别、子类 >> app.py
echo 5. 推荐处理路径：动作、理由 >> app.py
echo 6. 置信度：评分（0-1）、说明 >> app.py
echo 7. 判断依据：关键信号列表、分析说明 >> app.py
echo 文本内容：{text} >> app.py
echo 请只返回JSON，不要有其他内容。""" >> app.py
echo. >> app.py
echo         response = client.chat.completions.create( >> app.py
echo             model="deepseek-chat", >> app.py
echo             messages=[{"role": "user", "content": prompt}], >> app.py
echo             temperature=0.3 >> app.py
echo         ) >> app.py
echo. >> app.py
echo         result_text = response.choices[0].message.content >> app.py
echo         json_match = re.search(r'\{.*\}', result_text, re.DOTALL) >> app.py
echo         if json_match: >> app.py
echo             result = json.loads(json_match.group()) >> app.py
echo             return jsonify({"success": True, "result": result}) >> app.py
echo         else: >> app.py
echo             return jsonify({"success": False, "error": "JSON解析失败"}), 500 >> app.py
echo. >> app.py
echo     except Exception as e: >> app.py
echo         return jsonify({"success": False, "error": str(e)}), 500 >> app.py
echo. >> app.py
echo @app.route('/analyze/teaching', methods=['POST']) >> app.py
echo def analyze_teaching(): >> app.py
echo     try: >> app.py
echo         data = request.json >> app.py
echo         text = data.get('text', '') >> app.py
echo         if not text: >> app.py
echo             return jsonify({"success": False, "error": "请提供作文内容"}), 400 >> app.py
echo. >> app.py
echo         prompt = f"""请对以下英语作文进行批改，输出JSON格式，包含： >> app.py
echo 1. 语法准确性：评分（0-10）、反馈 >> app.py
echo 2. 词汇丰富度：评分（0-10）、反馈 >> app.py
echo 3. 逻辑连贯性：评分（0-10）、反馈 >> app.py
echo 4. 语用得体性：评分（0-10）、反馈 >> app.py
echo 5. 整体评语 >> app.py
echo 6. 修改优先级：列出3条最重要的修改建议 >> app.py
echo 作文内容：{text} >> app.py
echo 请只返回JSON。""" >> app.py
echo. >> app.py
echo         response = client.chat.completions.create( >> app.py
echo             model="deepseek-chat", >> app.py
echo             messages=[{"role": "user", "content": prompt}], >> app.py
echo             temperature=0.3 >> app.py
echo         ) >> app.py
echo. >> app.py
echo         result_text = response.choices[0].message.content >> app.py
echo         json_match = re.search(r'\{.*\}', result_text, re.DOTALL) >> app.py
echo         if json_match: >> app.py
echo             result = json.loads(json_match.group()) >> app.py
echo             return jsonify({"success": True, "result": result}) >> app.py
echo         else: >> app.py
echo             return jsonify({"success": False, "error": "JSON解析失败"}), 500 >> app.py
echo. >> app.py
echo     except Exception as e: >> app.py
echo         return jsonify({"success": False, "error": str(e)}), 500 >> app.py
echo. >> app.py
echo if __name__ == '__main__': >> app.py
echo     port = int(os.environ.get('PORT', 5000)) >> app.py
echo     app.run(host='0.0.0.0', port=port) >> app.py