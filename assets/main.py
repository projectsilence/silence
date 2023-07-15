from flask import Flask, jsonify, request
from settings import KEY_FOLDER, SELF_KEY_FOLDER, SELF_ADDRESS
import base64, requests, os

app = Flask(__name__)

base_folder = "keys"

@app.route("/")
def home():
    return "Silence Server running!"

@app.route("/initiate", methods=["POST"])
def initiate():
    if 'pub1' not in request.args or 'pub2' not in request.args or 'init' not in request.args or 'oniona' not in request.args:
        return "Malformed request.."

    external_onion = request.args['oniona']
    fullpath = os.path.normpath(KEY_FOLDER.format(external_onion))

    if not fullpath.startswith(base_folder):
        return "Nice try with URL injection."

    if os.path.exists(fullpath) == True:
            return "Contact already initiated.."

    os.mkdir(fullpath)
    os.mkdir(fullpath+"messages")

    if request.args['init'] == "1":
        rpub = request.args['pub1']
        fpub = request.args['pub2']
    elif request.args['init'] == "2":
        rpub = request.args['pub2']
        fpub = request.args['pub1']

    with open(fullpath+'realpub.pub', "wb+") as f:
        f.write(base64.b64decode(rpub))
    f.close()

    with open(fullpath+'fakepub.pub', "wb+") as f:
        f.write(base64.b64decode(fpub))
    f.close()

    with open("./notifications.sil", "a") as f:
        f.write("New contact:  {}".format(request.args['oniona']))

    return "Contact Initiated!"

@app.route('/sendmessage', methods=["POST"])
def send_message():
    if 'message' not in request.args or 'oniona' not in request.args or 'signature' not in request.args:
        return "Malformed request.."
    
    external_onion = request.args['oniona']
    fullpath = os.path.normpath(KEY_FOLDER.format(external_onion))

    if not fullpath.startswith(base_folder):
        return "Nice try with URL injection."

    mcount = len([f for f in os.listdir(fullpath+"messages")if os.path.isfile(os.path.join(fullpath+"messages", f))])
    if mcount != 0:
        mcount = int(mcount/2)
    
    with open((fullpath+"messages/"+str(int(mcount))+'signature.bin'), "wb+") as f:
        f.write(base64.b64decode(request.args['signature']))
    f.close()

    with open((fullpath+"messages/"+str(int(mcount))+'message.bin'), "wb+") as f:
        f.write(base64.b64decode(request.args['message']))
    f.close()

    return "Thank you for your message!"

@app.route('/signaturerequest', methods=["GET"])
def signature_request():
    if os.path.exists("signedsession.bin") == False:
            return "No signed in session..."
    
    with open("./signedsession.bin", "rb") as f:
        signature = base64.b64encode(f.read())
    f.close()

    return signature

if __name__ == "__main__":
    app.run(port=8080, debug=False)
