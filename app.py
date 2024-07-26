import glob
import json
from pathlib import Path

import flask
# import cv2
from flask import Flask, render_template, send_file
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

@app.route("/init/<uuid>", methods=["POST"])
def init_route(uuid):
    args = flask.request.values
    mime_type, timeslice = args["mime_type"], args["timeslice"]

    print("new {}".format(uuid))
    ext = "webm" if mime_type == "video/webm" else "mp4"
    files[uuid] = open(f"videos/{uuid}.{ext}", "wb")
    info[uuid] = {"timeslice": int(timeslice), "segments": []}

    return "", 200

@socketio.on("stop")
def init(uuid):
    files[uuid].close()
    files.pop(uuid)

    with open(f"videos/{uuid}.seg", "w") as file:
        json.dump(info[uuid], file)

    info.pop(uuid)


@app.route("/stop/<uuid>", methods=["POST"])
def stop_route(uuid):
    files[uuid].close()
    files.pop(uuid)

    with open(f"videos/{uuid}.seg", "w") as file:
        json.dump(info[uuid], file)

    info.pop(uuid)
    return "", 200


@socketio.on("frames")
def farmes(uuid, data):
    files[uuid].write(data)
    info[uuid]["segments"].append(len(data))


@app.route("/frames/<uuid>", methods=["POST"])
def frames_route(uuid):
    data = flask.request.data

    files[uuid].write(data)
    info[uuid]["segments"].append(len(data))
    return "", 200


@app.route('/')
def index_page():
    return render_template('index.html')

@app.route("/video/<video_id>")
def result_video(video_id):
    for f in Path().glob(f"videos/{video_id}.*"):
        if f.suffix != ".seg":
            return send_file(f, mimetype=f"video/{f.suffix[1:]}")
    return "", 404


if __name__ == '__main__':
    Path("videos").mkdir(parents=True, exist_ok=True)

    print("strt")
    socketio.run(app, "0.0.0.0", debug=True)
