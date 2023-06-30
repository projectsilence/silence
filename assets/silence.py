'''
 silence.py
 pretty private messaging service :D

 Credits:
 rootfinlay - Developer, research, tester
 CryptCod3r - Research Lead, tester
 Triponacci - Chorus member, tester
 Cicada3301 - Inspiration.  May emergence be upon us.
'''

import argparse, requests, os, base64, json, datetime
import settings
import silencecrypto

class Handler:
    def __init__(self):
        self.SELF_ADDRESS = settings.SELF_ADDRESS
        self.KEY_FOLDER = settings.KEY_FOLDER
        self.SELF_KEY_FOLDER = settings.SELF_KEY_FOLDER
        self.SILENCE_CLIENT_USER_AGENT = settings.SILENCE_CLIENT_USER_AGENT
        self.TEMP_FOLDER = settings.TEMP_FOLDER
        self.MESSAGES_KEPT = settings.MESSAGES_KEPT

    def handle(self):
        """Interpret the first command line argument, and redirect."""
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "action",
            choices=["daemon", "stop", "full", "lite", "initiate", "pingtest", "genkeys", "sendmessage", "readmessage"],
            help="silenceCORE",
        )
        parser.add_argument("other", nargs="*")
        args = parser.parse_args()

        action = getattr(self, args.action)
        action()

    def daemon(self):
        os.system('sudo systemctl start nginx')
        os.system('sudo systemctl start tor')
        os.system('sudo systemctl start silence.service')

        print("[ Silence ] - Silence Services started..")

    def stop(self):
        os.system('sudo systemctl stop nginx')
        os.system('sudo systemctl stop tor')
        os.system('sudo systemctl stop silence.service')

        print("[ Silence ] - Silence Services stopped..")

    def full(self):
        print("Unimplemented")

    def lite(self):
        print("Unimplemented")

    def initiate(self):
        """Initiate connection with a client"""
        parser = argparse.ArgumentParser()
        parser.add_argument("action", choices=["initiate"])
        parser.add_argument("external_onion", type=str, nargs="*")
        args = parser.parse_args()

        external_onion = ' '.join(args.external_onion).replace("\n", " ").replace("\r", "")
        
        os.mkdir(self.KEY_FOLDER.format(external_onion))
        os.mkdir(self.KEY_FOLDER.format(external_onion)+"messages")

        selfrpub = base64.b64encode(open((self.SELF_KEY_FOLDER+'selfrsatrue.pub'), "rb").read())
        selffpub = base64.b64encode(open((self.SELF_KEY_FOLDER+'selfrsafalse.pub'), "rb").read())

        obj = {
            'rpub' : selfrpub,
            'fpub' : selffpub,
            'init' : 1,
            'oniona' : self.SELF_ADDRESS
        }

        session = requests.session()
        session.proxies = {}
        session.proxies['http'] = 'socks5h://localhost:9050'
        session.proxies['https'] = 'socks5h://localhost:9050'

        headers = {}
        headers['User-agent'] = self.SILENCE_CLIENT_USER_AGENT

        x = session.post(("http://"+external_onion+"/initiate"), params=obj, headers=headers)

        cont = x.text
        if cont == "Contact already initiated..  Try updatekeys":
            print("Connection should already be established..  Try updatekeys..")
            exit()
        
        output = json.loads(cont)
        
        rpub = base64.b64decode(output['rpub'])
        fpub = base64.b64decode(output['fpub'])
        remote_onion = str(output['oniona'])

        with open((self.KEY_FOLDER.format(external_onion)+'realpub.pub'), "wb+") as f:
            f.write(rpub)
        f.close()

        with open((self.KEY_FOLDER.format(external_onion)+'fakepub.pub'), "wb+") as f:
            f.write(fpub)
        f.close()

        print("Contact initiated, have a nice day!")
        

    def pingtest(self):
        """Onion connection test"""
        parser = argparse.ArgumentParser()
        parser.add_argument("action", choices=["pingtest"])
        parser.add_argument("external_onion", type=str, default="", nargs="*")
        args = parser.parse_args()

        external_onion = ' '.join(args.external_onion).replace("\n", " ").replace("\r", "")

        session = requests.session()
        session.proxies = {}
        session.proxies['http'] = 'socks5h://localhost:9050'
        session.proxies['https'] = 'socks5h://localhost:9050'

        headers = {}
        headers['User-agent'] = self.SILENCE_CLIENT_USER_AGENT

        try:
            x = session.get(("http://"+external_onion), headers=headers)            
        except:
            print("Hidden Service is down...  If you are sure this site is up, please check your daemon is running..")
            exit()

        if x.text == 'Silence Server running!':
            print("Silence Service running at: {}".format(external_onion))
        else:
            print("No silence service found at: {}".format(external_onion))

    def genkeys(self):
        """Generates crypto keys"""
        rpassphrase = input("Please input a passphrase for the REAL key:\n> ")
        silencecrypto.GenerateKeypairRSATrue(rpassphrase)

        fpassphrase = input("Please input a passphrase for the FAKE key:\n> ")
        silencecrypto.GenerateKeypairRSAFalse(fpassphrase)
        print("[ Silence ] - Key generation complete")

    def sendmessage(self):
        """Send a message to a hidden service"""
        parser = argparse.ArgumentParser()
        parser.add_argument("action", choices=["sendmessage"])
        parser.add_argument("external_onion", type=str, default="", nargs="*")
        args = parser.parse_args()

        external_onion = ' '.join(args.external_onion).replace("\n", " ").replace("\r", "")

        if os.path.exists(self.KEY_FOLDER.format(external_onion)) == False:
            print("External keys not found...  Please initiate contact or check config..")
            exit()

        pass1 = input("Please input the private key password (1/2):\n> ")
        pass2 = input("Please input the private key password (2/2):\n> ")

        if pass1 != pass2:
            print("Passwords do not match..")
            exit()

        
        if silencecrypto.UnlockRealRSA(pass1) == False:
            if silencecrypto.UnlockFakeRSA(pass1) == False:
                print("Cannot unlock keys...  Try again..")
                exit()
            else:
                keystate = "FakeKeyUnlocked"
        else:
            keystate = "RealKeyUnlocked"

        session = requests.session()
        session.proxies = {}
        session.proxies['http'] = 'socks5h://localhost:9050'
        session.proxies['https'] = 'socks5h://localhost:9050'

        headers = {}
        headers['User-agent'] = self.SILENCE_CLIENT_USER_AGENT
        
        try:
            x = session.get(("http://"+external_onion), headers=headers)            
        except:
            print("Hidden Service is down...  If you are sure this site is up, please check your daemon is running..")
            exit()

        if x.text == 'Silence Server running!':
            print("Silence Service running at: {}".format(external_onion))
        else:
            print("No silence service found at: {}S".format(external_onion))
            exit()        
        
        messagein = input("Please input your message:\n> ")

        signature_b = silencecrypto.RSASign(messagein, pass1, keystate)
        
        if signature_b == "How tf would you get this to throw an error?":
            print("KeyType error...  Not sure how or why this is thrown")
            exit()
        
        signature = base64.b64encode(signature_b)
        silencecrypto.RSACrypt(external_onion, messagein)
        message = base64.b64encode(open(self.TEMP_FOLDER+"encrypted_data.bin", "rb").read())
        timestamp = datetime.datetime.now()

        obj = {
            'oniona' : self.SELF_ADDRESS,
            'message' : message,
            'signature' : signature
        }

        x = session.post(("http://"+external_onion+"/sendmessage"), params=obj, headers=headers)

        content = x.text
        if content == "Thank you for your message!":
            print("Message sent")
            exit()
        elif content == "Malformed request..":
            print("Malformed request.  Did you brick the install?")
            exit()
        else:
            print("HOW?!")
            exit()

    def readmessage(self):
        """Read a message from locale"""
        parser = argparse.ArgumentParser()
        parser.add_argument("action", choices=["readmessage"])
        parser.add_argument("external_onion", type=str, default="", nargs="*")
        args = parser.parse_args()

        external_onion = ' '.join(args.external_onion).replace("\n", " ").replace("\r", "")

        if os.path.exists(self.KEY_FOLDER.format(external_onion)) == False:
            print("External keys not found...  Please initiate contact or check config..")
            exit()

        pass1 = input("Please input the private key password (1/2):\n> ")
        pass2 = input("Please input the private key password (2/2):\n> ")

        if pass1 != pass2:
            print("Passwords do not match..")
            exit()

        mcount = num_files = len([f for f in os.listdir(self.KEY_FOLDER.format(external_onion)+"messages")if os.path.isfile(os.path.join(self.KEY_FOLDER.format(external_onion)+"messages", f))])
        if mcount == 0:
            print("No new messages.")
        mcount = mcount/2

        for i in range(0,int(mcount)):
            message = silencecrypto.RSADecrypt(external_onion, str(i), pass1)
            sigcheck = silencecrypto.RSACheckSig(external_onion, str(i), message)
            if sigcheck == "Valid Signature":
                print("\n\n" + message + "  -VALIDSIG")
            elif sigcheck == "Invalid Signature":
                print("INVALID SIGNATURE.  THIS MESSAGE ISN'T FROM THE ORIGINAL SENDER:  " + message)
            else:
                print("Invalid message...")

        if self.MESSAGES_KEPT == "TRUE":
            exit()
        elif self.MESSAGES_KEPT == "FALSE":
            os.system('rm -rf {}'.format(self.KEY_FOLDER.format(external_onion)+"messages"))
            os.mkdir(self.KEY_FOLDER.format(external_onion)+"messages")
            exit()

if __name__ == "__main__":
    handler = Handler()
    handler.handle()
