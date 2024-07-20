import time
import datetime
import io
from threading import Thread

from flask import Flask, render_template
from flask_socketio import SocketIO
from matplotlib import pyplot as plt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


files = {}
bytes_files = {}

@socketio.on("init")
def init(uuid, mime_type):
    print("new {}".format(uuid))
    ext = "webm" if mime_type == "video/webm" else "mp4"
    files[uuid] = open(f"{datetime.datetime.now().isoformat()}.{ext}", "wb")
    bytes_files[uuid] = io.BytesIO()

    # Thread(target=frames_view, args=(bytes_files[uuid],)).start()

@socketio.on("stop")
def init(uuid):
    files[uuid].close()
    files.pop(uuid)


@socketio.on("frames")
def farmes(uuid, data):
    files[uuid].write(data)

    pos = bytes_files[uuid].tell()

    bytes_files[uuid].seek(0, 2)
    bytes_files[uuid].write(data)
    bytes_files[uuid].seek(pos)

    plt.show()

@app.route('/')
def index_page():
    return render_template('index.html')


def frames_view(file):
    print("imp")
    from av import open as avopen
    print("done")

    time.sleep(3)
    video = avopen(file, format="webm")

    while True:
        for packet in video.demux():
            for frame in packet.decode():
                if packet.stream.type == 'video':
                    print(packet)
                    print(frame)
                    img = frame.to_ndarray(format='bgr24')
                    time.sleep(1)
                    plt.imshow(img)
                    plt.pause(1)



if __name__ == '__main__':
    bytes_files[1] = io.BytesIO()

    print("strt")
    socketio.run(app, "0.0.0.0")
