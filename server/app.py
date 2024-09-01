import os, json
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sqlite3
import requests
import warnings
import pyttsx3
from pyttsx3.voice import Voice

os.environ["SQLALCHEMY_SILENCE_UBER_WARNING"] = "1"

warnings.filterwarnings("ignore")


app = Flask(__name__)
CORS(app)

# 简易前端服务
RASA_SERVER_URL = "http://localhost:5005"  # 根据您的 Rasa 服务器配置进行修改
TTS_URL = "http://127.0.0.1:5003/tts"
ASR_URL = "http://127.0.0.1:5003/asr"

"""
假如你是一名资深python专家，请使用python帮我写一个前后端代码。
要求：
1、需要支持接入rasa的api接口http://127.0.0.1:5005进行输入输出展示，同时支持tts和asr的api接口http://127.0.0.1:5003接入的代码；
2、可以支持在界面使用文本输入和支持使用pyaudio采样率为16000进行按键控制开始和停止录音生成，并可播放保存的wav文件，同时被后端使用request.files.get('audio')请求到录音文件，支持语音播报按键，并将所有信息在聊天框展示，界面美观、显示录音的进度条；
3、python实现本地部署TTS的api接口代码；
4、python实现本地部署paraformer的ASR的api接口代码；
5、TTS和ASR使用一个py文件编写代码，前端界面使用一个文件html，集成接口使用一个py文件；
6、一次对话中支持rasa所有间断的输出，并使用TTS进行轮番播报和都在界面展示（例如：rasa首先输出”你好正在帮你查询“，然后在输出查询内容”output“）;
"""


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    message = data.get('message', '')
    response = requests.post(f"{RASA_SERVER_URL}/webhooks/rest/webhook", json={'message': message})
    rasa_responses = response.json()
    # Rasa多轮输出
    try:
        replies = []
        for msg in rasa_responses:
            if 'text' in msg:
                replies.append(msg['text'])
    except:
        replies = "抱歉，我无法理解您的问题。"
    print(rasa_responses)
    return jsonify({'reply': replies})


@app.route('/text_to_speech', methods=['POST'])
def text_to_speech():
    data = request.json
    text = data.get('text', '')
    response = requests.post(TTS_URL, json={'text': text})
    print(response, response.json())
    return jsonify({'audio_url': response.json().get('audio_url', '')})


@app.route('/speech_to_text', methods=['POST'])
def speech_to_text():
    audio_file = request.files.get('audio')
    print(audio_file)
    response = requests.post(ASR_URL, files={'audio': audio_file})
    print(response)
    return jsonify(response.json())


# 获取用户对应session
def get_sessions_by_user(user_id):
    connection = sqlite3.connect("user_sessions.db")
    cursor = connection.cursor()

    cursor.execute("SELECT session_id FROM user_sessions WHERE user_id=?", (user_id,))
    sessions = cursor.fetchall()

    if not sessions:
        connection.close()
        return []

    sessions = [row[0] for row in sessions]
    connection.close()
    return sessions


@app.route("/user_sessions/<user_id>", methods=["GET"])
def get_user_sessions(user_id):
    sessions = get_sessions_by_user(user_id)
    return jsonify({"sessions": sessions})


# 创建新对话
@app.route('/new_conversation/<user_id>/<session_id>', methods=['GET'])
def new_conversation(user_id, session_id):
    conn = sqlite3.connect('user_sessions.db')
    with conn:
        cur = conn.cursor()
        # 检查是否存在相同的 session_id
        cur.execute("SELECT session_id FROM user_sessions WHERE user_id=? AND session_id=?", (user_id, session_id))
        existing_session_id = cur.fetchone()

        # 如果不存在重复的 session_id，则插入新会话
        if not existing_session_id:
            cur.execute("INSERT INTO user_sessions (user_id, session_id) VALUES (?, ?)", (user_id, session_id))
            conn.commit()

    return "OK", 200


# 删除对话（tracker_store.db）
@app.route("/delete_conversation/<session_id>", methods=["DELETE"])
def delete_conversation(session_id):
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect("tracker_store.db")
        cursor = conn.cursor()

        # Delete the conversation from the database
        cursor.execute("DELETE FROM events WHERE sender_id = ?", (session_id,))
        conn.commit()

        # Close the database connection
        conn.close()
        return jsonify({"success": True}), 200
    except Exception as e:
        print(f"Error deleting conversation: {e}")
        return jsonify({"error": "Failed to delete conversation"}), 500


# 删除对话（user_sessions.db）
@app.route("/delete_session/<session_id>", methods=["DELETE"])
def delete_session(session_id):
    try:
        conn = sqlite3.connect('user_sessions.db')
        cur = conn.cursor()
        cur.execute("DELETE FROM user_sessions WHERE session_id = ?", (session_id,))
        conn.commit()
        conn.close()

        return jsonify({"success": True}), 200
    except Exception as e:
        print(f"Error deleting conversation: {e}")
        return jsonify({"error": "Failed to delete session"}), 500


# 获取可用的模型列表
current_script_path = os.path.abspath(__file__)
root_dir = os.path.dirname(current_script_path)
MODELS_DIR = os.path.join(root_dir, "../models")
MODELS_DIR = os.path.abspath(MODELS_DIR)


def get_models_list():
    models = []
    for entry in os.listdir(MODELS_DIR):
        if os.path.isfile(os.path.join(MODELS_DIR, entry)):
            models.append(entry)
    return models


@app.route("/models", methods=["GET"])
def get_models():
    models = get_models_list()
    return jsonify({"models": models})


if __name__ == '__main__':
    app.run(port=5002, debug=True)
