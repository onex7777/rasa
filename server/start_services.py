import subprocess
import webbrowser
import os
import warnings

os.environ["SQLALCHEMY_SILENCE_UBER_WARNING"] = "1"
warnings.filterwarnings("ignore")

os.chdir(os.path.dirname(os.path.abspath(__file__ + "/../")))


def run():
    # rasa-cn 虚拟环境
    # Start your backend server (e.g., Flask)
    # Start your backend server (e.g., Flask)
    tts_server = subprocess.Popen(["python", "server/tts_asr.py"])

    llm_server = subprocess.Popen(["python", "server/llm_api.py"])
    # Start Rasa action server
    action_server = subprocess.Popen(["rasa", "run", "actions"])
    # Start Rasa server
    rasa_server = subprocess.Popen(["rasa", "run", "--enable-api", "--cors", "*", "--log-file", "log/rasa.log"])

    # Start Rasa server
    http_server = subprocess.Popen(["python", "-m", "http.server"])
    # Start your backend server (e.g., Flask)
    backend_server = subprocess.Popen(["python", "server/app.py"])

    test_server = subprocess.Popen(["python", "server/test.py"])
    # Open the web page in a new browser tab
    # webbrowser.open("http://localhost:5000")

    # Wait for the servers to finish

    tts_server.wait()
    llm_server.wait()
    http_server.wait()
    action_server.wait()
    rasa_server.wait()
    backend_server.wait()
    test_server.wait()


def interactive():
    # Start Rasa action server

    llm_server = subprocess.Popen(["python", "server/llm_api.py"])
    action_server = subprocess.Popen(["rasa", "run", "actions", "--port", "5055", "--actions", "actions", "--debug"])

    interactive_server = subprocess.Popen(["rasa", "interactive", "-m", "models/20240818-143050-jet-skua.tar.gz",
                                           "--endpoints", "endpoints.yml", "--config", "-config.yml"])

    llm_server.wait()
    action_server.wait()
    interactive_server.wait()


if __name__ == '__main__':
    run()
