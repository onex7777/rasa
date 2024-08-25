import subprocess
import webbrowser
import os
import warnings

os.environ["SQLALCHEMY_SILENCE_UBER_WARNING"] = "1"
warnings.filterwarnings("ignore")

os.chdir(os.path.dirname(os.path.abspath(__file__ + "/")))

def run():
    # agent 虚拟环境

    # Start your backend server (e.g., Flask)
    tts_server = subprocess.Popen(["python", "tts_asr.py"])

    llm_server = subprocess.Popen(["python", "llm_api.py"])
    # Open the web page in a new browser tab
    # webbrowser.open("http://localhost:5000")

    # Wait for the servers to finish
    tts_server.wait()
    llm_server.wait()


if __name__ == '__main__':
    run()
