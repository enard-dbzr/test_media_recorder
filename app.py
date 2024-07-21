import json
from pathlib import Path

# import cv2
from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


files = {}
info = {}

@socketio.on("init")
def init(uuid, mime_type, timeslice):
    print("new {}".format(uuid))
    ext = "webm" if mime_type == "video/webm" else "mp4"
    files[uuid] = open(f"videos/{uuid}.{ext}", "wb")
    info[uuid] = {"timeslice": int(timeslice), "segments": []}

@socketio.on("stop")
def init(uuid):
    files[uuid].close()
    files.pop(uuid)

    with open(f"videos/{uuid}.seg", "w") as file:
        json.dump(info[uuid], file)

    info.pop(uuid)



@socketio.on("frames")
def farmes(uuid, data):
    files[uuid].write(data)
    info[uuid]["segments"].append(len(data))


@app.route('/')
def index_page():
    return render_template('index.html')


if __name__ == '__main__':
    Path("videos").mkdir(parents=True, exist_ok=True)

    print("strt")
    socketio.run(app, "0.0.0.0")
