import eventlet

eventlet.monkey_patch()

import time, json
from kafka import KafkaConsumer
from threading import Thread
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect

async_mode = 'eventlet'
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None


def background_thread():
    consumer = KafkaConsumer("test",auto_offset_reset='earliest',
                                 value_deserializer=lambda m: json.loads(m.decode('utf-8')))
    for msg in consumer:
        try:
            print(msg)
            socketio.emit('update',
                          {'data': msg.value,'metadata':msg},
                          namespace='', broadcast=True)
        except Exception as e:
            print(str(e))
        print('emitted')
        time.sleep(1)


@app.route('/')
def index():
    global thread
    if thread is None:
        thread = Thread(target=background_thread)
        thread.daemon = True
        thread.start()
    return render_template('dashboard.html')


@socketio.on('connected', namespace='')
def connected():
    emit('status',
         {'status': 'Connected.'})


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080,debug="true")