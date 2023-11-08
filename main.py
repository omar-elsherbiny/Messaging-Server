#IMPORTS
import csv
import base64
from random import randint
from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit

app = Flask(__name__)
app.config['SECRET'] = "!2007!"
socketio = SocketIO(app, cors_allowed_origins='*')
clients={}

def write_2_csv(data, file='saved.csv', fields=['user_id', 'user', 'message']):
    with open(file, 'a+', encoding='UTF-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writerow(data)
        
def read_csv(file='saved.csv', fields=['user_id', 'user', 'message']):
    with open(file, 'r', encoding='UTF-8') as f:
        reader = csv.DictReader(f, fieldnames=fields)
        data_read={}
        for ind,row in enumerate(reader):
            if row['message'][:10] == 'file_ref;;':
                data_read[ind]=[row['user'], read_voice_note(row['message']), int(row['user_id'])]
            else:
                data_read[ind]=[row['user'], row['message'], int(row['user_id'])]
        return data_read

def download_voice_note(data_string):
    raw_data_string=data_string.replace('data:audio/mp3;;base64,','')
    base64_bytes = raw_data_string.encode('ascii')
    message_bytes = base64.b64decode(base64_bytes)
    #message = message_bytes.decode('ascii')
    path_num=randint(0,9999)
    with open(f'static/voice_notes/voice_{path_num}.mp3', 'wb') as f:
        f.write(message_bytes)
    return ['data_b64;;'+raw_data_string, 'file_ref;;voice_'+str(path_num)]

def read_voice_note(path):
    raw_name=path.replace('file_ref;;','')
    message_bytes=''
    try:
        with open(f'static/voice_notes/{raw_name}.mp3', 'rb') as f:
            message_bytes=f.read()
    except Exception as e:
        print('[Error]=>',e)
        return 'data_b64;;'+'ZXJyb3I='
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')
    return 'data_b64;;'+base64_message

@socketio.on('message')
def handle_msg(msg):
    smsg=msg.split('*')
    if smsg[0] != '[User connected]' and smsg[0] != '[User config]':
        if smsg[2][:23] == 'data:audio/mp3;;base64,':
            print(f'Recieved message: data:audio/mp3;;base64,')
            p=download_voice_note(smsg[2])
            send([smsg[1], p[0], smsg[0]], broadcast=True)
            write_2_csv({'user_id':smsg[0], 'user':smsg[1], 'message':p[1]})
        else:
            print(f'Recieved message: {msg}')
            send([smsg[1], smsg[2], smsg[0]], broadcast=True)
            write_2_csv({'user_id':smsg[0], 'user':smsg[1], 'message':smsg[2]})
    else:
        print(f'Recieved message: {msg}')
        if smsg[0] == '[User config]':
            clients[smsg[1]]=smsg[2]
        else:
            emit('History', read_csv())
        emit('UserDict', clients)

@socketio.on('disconnect')
def test_disconnect():
    print('[User disconnected]')

@app.route('/')
def index():
    return render_template('index.html')

if __name__=='__main__':
    h=['localhost','192.168.1.5'][0]
    print(f'[Server started on {h}:9999]')
    socketio.run(app, host=h, port=698)# "http://localhost:5000" "192.168.1.15"
 
