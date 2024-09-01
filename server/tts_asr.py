import pyttsx3
import wave
from flask import Flask, send_file, request, jsonify, send_from_directory
import argparse
import json
from funasr import AutoModel
import os
import logging
from pyttsx3.voice import Voice
# os.chdir(os.path.dirname(os.path.abspath(__file__ + "/../")))
app = Flask(__name__)

# 设置日志级别
logger = logging.getLogger(__name__)
logger.setLevel(logging.CRITICAL)
# 解析命令行参数
parser = argparse.ArgumentParser()
parser.add_argument("--host", type=str, default="0.0.0.0", help="host ip, localhost, 0.0.0.0")
parser.add_argument("--port", type=int, default=8888, help="grpc server port")
parser.add_argument("--ngpu", type=int, default=1, help="0 for cpu, 1 for gpu")
parser.add_argument("--root_path", type=str, default=r"D:\Python\Pingan\LLM\model", help="model_path")
args = parser.parse_args()

# 初始化模型
print("asr model loading...")
model_path = os.path.join(args.root_path, "speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch")
vad_model_path = os.path.join(args.root_path, "speech_fsmn_vad_zh-cn-16k-common-pytorch")
punc_model_path = os.path.join(args.root_path, "punc_ct-transformer_zh-cn-common-vocab272727-pytorch")
asr_model = AutoModel(model=model_path, vad_model=vad_model_path, device="cuda",
                      punc_model=punc_model_path, disable_update=True)
print("asr model loaded")

# 热词
param_dict = {"sentence_timestamp": False}
with open("server/hotword.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()
    lines = [line.strip() for line in lines]
hotword = " ".join(lines)
print(f"热词：{hotword}")
param_dict["hotword"] = hotword




@app.route('/tts', methods=['POST'])
def tts():
    text = request.json.get('text')
    engine = pyttsx3.init()
    rate = engine.getProperty('rate')
    # 控制语音播放的速度
    engine.setProperty('rate', rate)
    volume = engine.getProperty('volume')
    # 控制语音播放的音量大小
    engine.setProperty('volume', volume)
    v = Voice(id=3, name='wx', languages='Chinese', age=18, gender='女')
    engine.setProperty('voice', v)
    engine.save_to_file(text, 'server/output.wav')
    engine.say(text)
    engine.runAndWait()

    return jsonify({'audio_url': "/" + 'server/output.wav'})


@app.route('/asr', methods=['POST'])
def asr():
    audio_path = "server/input.wav"
    if os.path.exists(audio_path):
        os.remove(audio_path)
    audio = request.files['audio']
    audio.save(audio_path)
    try:
        response = asr_model.generate(input=audio_path, is_final=True, **param_dict)
        result = response[0]["text"]
        print("result:", result)
    except Exception as e:
        logging.error("Error content: %s \t ", '--e---', e)
        result = ''
    return jsonify({"text": result})


if __name__ == '__main__':
    app.run(port=5003, debug=True)
