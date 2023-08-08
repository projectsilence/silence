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
        self.SELF_KEY_ONE = settings.SELF_KEY_ONE
        self.SELF_KEY_TWO = settings.SELF_KEY_TWO

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


        print("Please sign the session.  Remember, this signed session will be sent to users sending you a message.")
        pass1 = input("Please input the private key password (1/2):\n> ")
        pass2 = input("Please input the private key password (2/2):\n> ")

        if pass1 != pass2:
            print("Passwords do not match..")
            exit()

        if silencecrypto.UnlockRSA(password=pass1, key=self.SELF_KEY_ONE) == False:
            if silencecrypto.UnlockRSA(password=pass1, key=self.SELF_KEY_TWO) == False:
                print("Cannot unlock keys...  Try again..")
                exit()
            else:
                keystate = self.SELF_KEY_TWO
        else:
            keystate = self.SELF_KEY_ONE

        signature = silencecrypto.SessionSigning(password=pass1, keystate=keystate)
        with open("./signedsession.bin", "wb+") as f:
            f.write(signature)

        print("[ Silence ] - Silence Services started..")

    def stop(self):
        os.system('sudo systemctl stop nginx')
        os.system('sudo systemctl stop tor')
        os.system('sudo systemctl stop silence.service')

        if os.path.exists("signedsession.bin") == True:
            os.system("rm -f signedsession.bin")

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
        
        if os.path.exists("signedsession.bin") == False:
            print("Please start the daemon first...")
            exit()

        print("Please be aware that your signed session will be sent to sending a message, choose keys accordingly..")
        realkey = input("Please specify if key 1 or key 2 is to be the real key:\n> ")

        pub1 = base64.b64encode(open(self.SELF_KEY_ONE+".pub", "rb").read())
        pub2 = base64.b64encode(open(self.SELF_KEY_TWO+".pub", "rb").read())

        obj = {
            'pub1' : pub1,
            'pub2' : pub2,
            'init' : realkey,
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
        if cont == "Contact already initiated..":
            print("Connection should already be established..")
            exit()
        elif cont == "Nice try with URL injection.":
            print("Don't URL inject, not cool...")
            exit()
        elif cont == "Contact Initiated!":
            print("Contact initiated, have a nice day!")
            exit()
        else:
            print("Unspecified error")

    def pingtest(self):
        """Onion connection test"""
        parser = argparse.ArgumentParser()
        parser.add_argument("action", choices=["pingtest"])
        parser.add_argument("external_onion", type=str, default="", nargs="*")
        args = parser.parse_args()

        external_onion = ' '.join(args.external_onion).replace("\n", " ").replace("\r", "")

        if os.path.exists("signedsession.bin") == False:
            print("Please start the daemon first...")
            exit()

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
        if os.path.exists("signedsession.bin") == False:
            print("Please start the daemon first...")
            exit()
        
        choice = input("If you wish to use custom keynames, please edit the settings.py file.  Do you want to continue? (y/n):\n> ")
        if choice == "y":
            pass
        elif choice == "n":
            print("Please edit the settings.py file and run again.")
            exit()
        else:
            print("Invalid choice.  y or n only.")
            exit()
        
        passphrase1 = input("Please input a passphrase for the first key:\n> ")
        silencecrypto.GenerateKeypairRSA(passphrase1, name=self.SELF_KEY_ONE)

        passphrase2 = input("Please input a passphrase for the second key:\n> ")
        silencecrypto.GenerateKeypairRSA(passphrase2, name=self.SELF_KEY_TWO)
        print("[ Silence ] - Key generation complete")

    def sendmessage(self):
        """Send a message to a hidden service"""
        parser = argparse.ArgumentParser()
        parser.add_argument("action", choices=["sendmessage"])
        parser.add_argument("external_onion", type=str, default="", nargs="*")
        args = parser.parse_args()

        external_onion = ' '.join(args.external_onion).replace("\n", " ").replace("\r", "")

        if os.path.exists("signedsession.bin") == False:
            print("Please start the daemon first...")
            exit()

        if os.path.exists(self.KEY_FOLDER.format(external_onion)) == False:
            print("External keys not found...  Please initiate contact or check config..")
            exit()

        pass1 = input("Please input the private key password (1/2):\n> ")
        pass2 = input("Please input the private key password (2/2):\n> ")

        if pass1 != pass2:
            print("Passwords do not match..")
            exit()
        
        if silencecrypto.UnlockRSA(password=pass1, key=self.SELF_KEY_ONE) == False:
            if silencecrypto.UnlockRSA(password=pass1, key=self.SELF_KEY_TWO) == False:
                print("Cannot unlock keys...  Try again..")
                exit()
            else:
                keystate = self.SELF_KEY_TWO
        else:
            keystate = self.SELF_KEY_ONE

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
            exit()        
        
        y = session.get(("http://"+external_onion+"/signaturerequest"), headers=headers)
        signatureb = y.text

        if signatureb == "No signed in session...":
            print("\nUser session not signed in, proceed with caution.")
            messagein = input("NO key session signed in.  Please input your message:\n> ")
            keyi = input("Which key would you like to use? REAL or FAKE:\n> ")
            if keyi.upper() == "REAL":
                key = self.KEY_FOLDER.format(external_onion)+"realpub"
            elif keyi.upper() == "FAKE":
                key = self.KEY_FOLDER.format(external_onion)+"fakepub"
            else:
                print("Inalid key, exiting")
                exit()
        else:
            if silencecrypto.SessionCheck(external_onion, signatureb) == "RealKey":
                messagein = input("REAL key session signed in.  Please input your message:\n> ")
                key = self.KEY_FOLDER.format(external_onion)+"realpub"
            elif silencecrypto.SessionCheck(external_onion, signatureb) == "FakeKey":
                messagein = input("FAKE key session signed in.  Please input your message or exit with CNTRL+N:\n> ")
                key = self.KEY_FOLDER.format(external_onion)+"fakepub"
            else:
                print("Invalid signature, exiting...")
                exit()

        signature_b = silencecrypto.RSASign(messagein, pass1, keystate)
        
        if signature_b == "How tf would you get this to throw an error?":
            print("KeyType error...  Not sure how or why this is thrown")
            exit()
        
        signature = base64.b64encode(signature_b)
        silencecrypto.RSACrypt(key, messagein)
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
            os.remove("./temp/encrypted_data.bin")
            print("Message sent")
            exit()
        elif content == "Malformed request..":
            print("Malformed request.  Did you brick the install?")
            exit()
        elif content == "Nice try with URL injection.":
            print("Don't URL inject, not cool...")
            exit()
        else:
            print("Unspecified error...")
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

        signatureb = base64.b64encode(open("./signedsession.bin", "rb").read())
        keyunlocked = silencecrypto.SelfSessionCheck(signatureb)

        if keyunlocked == "Key1":
            keyn = self.SELF_KEY_ONE
        elif keyunlocked == "Key2":
            keyn = self.SELF_KEY_TWO
        else:
            print("Invalid signature, exiting...")
            exit()

        if silencecrypto.UnlockRSA(password=pass1, key=self.SELF_KEY_ONE) == False:
            if silencecrypto.UnlockRSA(password=pass1, key=self.SELF_KEY_TWO) == False:
                print("Cannot unlock keys...  Try again..")
                exit()
            else:
                key = self.SELF_KEY_TWO
        else:
            key = self.SELF_KEY_ONE

        if keyn != key:
            print("Session key and key unlocked don't match..  Exiting..")
            exit()

        mcount = num_files = len([f for f in os.listdir(self.KEY_FOLDER.format(external_onion)+"messages")if os.path.isfile(os.path.join(self.KEY_FOLDER.format(external_onion)+"messages", f))])
        if mcount == 0:
            print("No new messages.")
        mcount = mcount/2

        for i in range(0,int(mcount)):
            message = silencecrypto.RSADecrypt(external_onion, str(i), pass1, key)
            sigcheck = silencecrypto.RSACheckSig(external_onion, str(i), message)
            if sigcheck == "REALKEY: Valid Signature":
                print("\n\n" + message + "  -VALIDSIG-REALKEY")
            elif sigcheck == "FAKEKEY: Valid Signature":
                print("\n\n" + message + "  -VALIDSIG-FAKEKEY  THE SENDER MAY BE COMPROMISED!")
            elif sigcheck == "No valid signatures...":
                print("No valid signatures..")
            else:
                print("Error thrown..")

        if self.MESSAGES_KEPT == "TRUE":
            exit()
        elif self.MESSAGES_KEPT == "FALSE":
            os.system('rm -rf {}'.format(self.KEY_FOLDER.format(external_onion)+"messages"))
            os.mkdir(self.KEY_FOLDER.format(external_onion)+"messages")
            exit()

if __name__ == "__main__":
    handler = Handler()
    handler.handle()
