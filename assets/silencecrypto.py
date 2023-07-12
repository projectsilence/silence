'''
 silence-crypto
 standalone crypto library for silence.  can be used individually but is not recommended.
'''

from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA512
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
from settings import KEY_FOLDER, SELF_KEY_FOLDER, TEMP_FOLDER, SELF_KEY_ONE, SELF_KEY_TWO
import base64

def GenerateKeypairRSA(passphrase, name):
    key = RSA.generate(4098)
    encrypted_key = key.export_key(passphrase=passphrase, pkcs=8,
                              protection="scryptAndAES256-CBC")

    file_out = open(name+".bin", "wb+")
    file_out.write(encrypted_key)
    file_out.close()

    pubkey = key.publickey().export_key()

    file_out = open(name+".pub", "wb+")
    file_out.write(pubkey)
    file_out.close()

    return "True key generation complete..."
    
def UnlockRSA(password, key): 
    try:
        key = RSA.import_key(open(key+".bin", "rb").read(), passphrase=password)
    except:
        return False
    return True

def RSACrypt(key, message):
    recipient_key = RSA.import_key(open(key+".pub", "rb").read())
    session_key = get_random_bytes(32)

    cipher_rsa = PKCS1_OAEP.new(recipient_key)
    enc_session_key = cipher_rsa.encrypt(session_key)

    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(message.encode('utf-8'))
    file_out = open(TEMP_FOLDER+"encrypted_data.bin", "wb")
    [ file_out.write(x) for x in (enc_session_key, cipher_aes.nonce, tag, ciphertext) ]
    file_out.close()

def RSADecrypt(external_onion, i, passphrase, key):
    file_in = open(KEY_FOLDER.format(external_onion)+"messages/"+i+"message.bin", "rb")

    private_key = RSA.import_key(open(key+".bin", "rb").read(), passphrase=passphrase)

    enc_session_key, nonce, tag, ciphertext = \
        [ file_in.read(x) for x in (private_key.size_in_bytes(), 16, 16, -1) ]
    file_in.close()

    cipher_rsa = PKCS1_OAEP.new(private_key)
    session_key = cipher_rsa.decrypt(enc_session_key)

    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
    data = cipher_aes.decrypt_and_verify(ciphertext, tag)
    out = data.decode("utf-8")
    return out

def RSASign(message, password, keystate):
    key = RSA.import_key(open(keystate+".bin", "rb").read(), passphrase=password)

    h = SHA512.new(bytes(message, 'utf-8'))

    signature = pkcs1_15.new(key).sign(h)
    return signature

def RSACheckSig(external_onion, i, message):
    key1 = RSA.import_key(open(KEY_FOLDER.format(external_onion)+"realpub.pub").read())
    key2 = RSA.import_key(open(KEY_FOLDER.format(external_onion)+"fakepub.pub").read())

    signature = open(KEY_FOLDER.format(external_onion)+"messages/"+i+"signature.bin", "rb").read()

    h = SHA512.new(message.encode("utf-8"))

    try:
        pkcs1_15.new(key1).verify(h, signature)
        return "REALKEY: Valid Signature"
    except (ValueError, TypeError):
        pass
    try:
        pkcs1_15.new(key2).verify(h, signature)
        return "FAKEKEY: Valid Signature"
    except (ValueError, TypeError):
        return "No valid signatures..."

def SessionSigning(password, keystate):
    key = RSA.import_key(open(keystate+".bin", "rb").read(), passphrase=password)

    h = SHA512.new(bytes("SessionSigned", 'utf-8'))

    signature = pkcs1_15.new(key).sign(h)
    return signature

def SessionCheck(external_onion, signatureb):
    key1 = RSA.import_key(open(KEY_FOLDER.format(external_onion)+"realpub.pub").read())
    key2 = RSA.import_key(open(KEY_FOLDER.format(external_onion)+"fakepub.pub").read())

    signature = base64.b64decode(signatureb)

    h = SHA512.new(bytes("SessionSigned", "utf-8"))

    try:
        pkcs1_15.new(key1).verify(h, signature)
        return "RealKey"
    except (ValueError, TypeError):
        pass
    
    try:
        pkcs1_15.new(key2).verify(h, signature)
        return "FakeKey"
    except (ValueError, TypeError):
        return "No valid signatures..."

def SelfSessionCheck(signatureb):
    key1 = RSA.import_key(open(SELF_KEY_FOLDER+"key1.pub").read())
    key2 = RSA.import_key(open(SELF_KEY_FOLDER+"key2.pub").read())

    signature = base64.b64decode(signatureb)

    h = SHA512.new(bytes("SessionSigned", "utf-8"))

    try:
        pkcs1_15.new(key1).verify(h, signature)
        return "Key1"
    except (ValueError, TypeError):
        pass
    
    try:
        pkcs1_15.new(key2).verify(h, signature)
        return "Key2"
    except (ValueError, TypeError):
        return "No valid signatures..."