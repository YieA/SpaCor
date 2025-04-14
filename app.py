from flask import Flask, request, jsonify, render_template, send_file
import subprocess
import os

app = Flask(__name__)

@app.route('/')
def index():
    # 返回 HTML 文件（假设 index.html 放在 templates 文件夹中）
    return render_template('index.html')

@app.route('/detect_query', methods=['POST'])
def detect_query():
    data = request.get_json()
    nlq = data.get("nlq", "")

    if not nlq.strip():
        return jsonify({"result": "Invalid input."})

    try:
        # 调用 QueryDetectionOne.py 作为子进程
        process = subprocess.Popen(
            ["python", "SpaCor/QueryDetectionOne.py", nlq], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        output, error = process.communicate()

        if error:
            return jsonify({"result": f"Error occurred: {error}"})

        return jsonify({"result": output})

    except Exception as e:
        return jsonify({"result": f"Exception: {str(e)}"})

@app.route('/generate_corpus', methods=['POST'])
def generate_corpus():
    # 获取前端传递的数据
    data = request.get_json()
    corpus = data.get('corpus')
    num = data.get('num')

    # 调用 QueryGeneration.py 脚本并传递参数
    try:
        result = subprocess.run(['python', 'SpaCor/QueryGeneration.py', corpus, num], capture_output=True, text=True)

        # 查看脚本的标准输出
        # print("Subprocess Output:\n", result.stdout)    # 打印输出到终端
        
        if result.stderr:
            print("Subprocess Error:\n", result.stderr) # 打印错误信息
        
        
        # 获取脚本的输出
        generated_content = result.stdout

        return jsonify({'generatedContent': generated_content})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download_csv')
def download_csv():
    # 假设 CSV 文件路径是这样
    file_path = 'SpaCor/knowledge_base/SpaCorOutput.csv'
    
    # 确保文件存在
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "File not found", 404

if __name__ == '__main__':
    app.run(debug=True)
