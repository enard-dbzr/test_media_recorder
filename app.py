import base64
import os
from pathlib import Path


import flask
from flask import Flask, render_template, send_file
from flask_socketio import SocketIO

from core.ffmpeg_decoder import FfmpegDecoderCreator
from core.pyav_decoder import AVDecoderCreator
from core.video_aggregator import VideoAggregator
from di import create_aggregator

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


files = {}
info = {}

video_aggregator = create_aggregator()


@socketio.on("init")
def init(uuid, mime_type, timeslice):
    print(f"new", uuid, mime_type, timeslice)
    video_aggregator.start(uuid, mime_type, timeslice)


@app.route("/init/<uuid>", methods=["POST"])
def init_route(uuid):
    args = flask.request.values
    mime_type, timeslice = args["mime_type"], args["timeslice"]

    video_aggregator.start(uuid, mime_type, timeslice)

    return "", 200

@socketio.on("stop")
def init(uuid):
    video_aggregator.stop(uuid)


@app.route("/stop/<uuid>", methods=["POST"])
def stop_route(uuid):
    video_aggregator.stop(uuid)
    return "", 200


@socketio.on("frames")
def farmes(uuid, data):
    video_aggregator.frames(uuid, data)


@app.route("/frames/<uuid>", methods=["POST"])
def frames_route(uuid):
    data = flask.request.data

    video_aggregator.frames(uuid, data)
    return "", 200


@app.route('/')
def index_page():
    return render_template('index.html')

@app.route("/result/<video_id>")
def result_video(video_id):
    for f in Path().glob(f"videos/{video_id}.*"):
        if f.suffix != ".seg":
            return send_file(f, mimetype=f"video/{f.suffix[1:]}")
    return "", 404

@socketio.on("total")
def total_event(video_id):
    res = video_aggregator.get_total(video_id)
    print("sending result", res)
    socketio.emit("total_result",
                  (res["frames"], res["segments_received"], res["first_image"], res["last_image"]))

@app.route("/total/<video_id>")
def total_route(video_id):
    res = video_aggregator.get_total(video_id)
    res["first_image"] = base64.b64encode(res["first_image"]).decode()
    res["last_image"] = base64.b64encode(res["last_image"]).decode()
    return res, 200


if __name__ == '__main__':
    print("strt")
    socketio.run(app, "0.0.0.0", debug=True)
