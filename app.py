import datetime

from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


files = {}

@socketio.on("init")
def init(uuid):
    files[uuid] = open(f"{datetime.datetime.now().isoformat()}.webm", "wb")

@socketio.on("frames")
def farmes(uuid, data):
    files[uuid].write(data)

@app.route('/')
def index_page():
    return render_template('index.html')


if __name__ == '__main__':
    socketio.run(app)
