from flask import Flask, jsonify, request
from settings import KEY_FOLDER, SELF_KEY_FOLDER, SELF_ADDRESS
import base64, requests, os

app = Flask(__name__)   

@app.route("/")
def home():
    return "Silence Server running!"

@app.route("/initiate", methods=["POST"])
def initiate():
    if 'rpub' not in request.args and 'fpub' not in request.args and 'init' not in request.args and 'oniona' not in request.args:
        return "Malformed request.."

    os.mkdir(KEY_FOLDER.format(request.args['oniona']))
    os.mkdir(KEY_FOLDER.format(request.args['oniona'])+"messages")

    with open((KEY_FOLDER.format(str(request.args['oniona']))+'realpub.pub'), "wb+") as f:
        f.write(base64.b64decode(request.args['rpub']))
    f.close()

    with open((KEY_FOLDER.format(str(request.args['oniona']))+'fakepub.pub'), "wb+") as f:
        f.write(base64.b64decode(request.args['fpub']))
    f.close()

    selfrpub = base64.b64encode(open((SELF_KEY_FOLDER+'selfrsatrue.pub'), "rb").read())
    selffpub = base64.b64encode(open((SELF_KEY_FOLDER+'selfrsafalse.pub'), "rb").read())

    return_dict = {
        'rpub' : selfrpub.decode('utf-8'),
        'fpub' : selffpub.decode('utf-8'),
        'init' : 2,
        'oniona' : SELF_ADDRESS
    }

    return return_dict

@app.route('/sendmessage', methods=["POST"])
def send_message():
    if 'message' not in request.args and 'oniona' not in request.args and 'signature' not in request.args:
        return "Malformed request.."
    
    mcount = num_files = len([f for f in os.listdir(KEY_FOLDER.format(request.args['oniona'])+"messages")if os.path.isfile(os.path.join(path, f))])
    if mcount != 0:
        mcount = mcount/2
    
    with open((KEY_FOLDER.format(str(request.args['oniona']))+"messages/"+str(int(mcount))+'signature.bin'), "wb+") as f:
        f.write(base64.b64decode(request.args['signature']))
    f.close()

    with open((KEY_FOLDER.format(str(request.args['oniona']))+"messages/"+str(int(mcount))+'message.bin'), "wb+") as f:
        f.write(base64.b64decode(request.args['message']))
    f.close()

    return "Thank you for your message!"

if __name__ == "__main__":
    app.run(port=8080, debug=False)
