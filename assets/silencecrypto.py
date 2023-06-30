'''
 silence-crypto
 standalone crypto library for silence.  can be used individually but is not recommended.
'''

from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA512
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
from settings import KEY_FOLDER, SELF_KEY_FOLDER, TEMP_FOLDER

def GenerateKeypairRSATrue(passphrase):
    key = RSA.generate(4098)
    encrypted_key = key.export_key(passphrase=passphrase, pkcs=8,
                              protection="scryptAndAES256-CBC")

    file_out = open(SELF_KEY_FOLDER+"selfrsatrue.bin", "wb+")
    file_out.write(encrypted_key)
    file_out.close()

    pubkey = key.publickey().export_key()

    file_out = open(SELF_KEY_FOLDER+"selfrsatrue.pub", "wb+")
    file_out.write(pubkey)
    file_out.close()

    return "True key generation complete..."

def GenerateKeypairRSAFalse(passphrase):
    key = RSA.generate(4098)
    encrypted_key = key.export_key(passphrase=passphrase, pkcs=8,
                              protection="scryptAndAES256-CBC")

    file_out = open(SELF_KEY_FOLDER+"selfrsafalse.bin", "wb+")
    file_out.write(encrypted_key)
    file_out.close()

    pubkey = key.publickey().export_key()

    file_out = open(SELF_KEY_FOLDER+"selfrsafalse.pub", "wb+")
    file_out.write(pubkey)
    file_out.close()

    return "False key generation complete..."
    
def UnlockRealRSA(password):
    try:
        key = RSA.import_key(open(SELF_KEY_FOLDER+"selfrsatrue.bin", "rb").read(), passphrase=password)
    except:
        return False
    return True

def UnlockFakeRSA(password):
    try:
        key = RSA.import_key(open(SELF_KEY_FOLDER+"selfrsafalse.bin", "rb").read(), passphrase=password)
    except:
        return False
    return True

def RSACrypt(external_onion, message):
    recipient_key = RSA.import_key(open(KEY_FOLDER.format(external_onion)+"realpub.pub", "rb").read())
    session_key = get_random_bytes(32)

    cipher_rsa = PKCS1_OAEP.new(recipient_key)
    enc_session_key = cipher_rsa.encrypt(session_key)

    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(message.encode('utf-8'))
    file_out = open(TEMP_FOLDER+"encrypted_data.bin", "wb")
    [ file_out.write(x) for x in (enc_session_key, cipher_aes.nonce, tag, ciphertext) ]
    file_out.close()

def RSADecrypt(external_onion, i, passphrase):
    file_in = open(KEY_FOLDER.format(external_onion)+"messages/"+i+"message.bin", "rb")

    private_key = RSA.import_key(open(SELF_KEY_FOLDER+"selfrsatrue.bin", "rb").read(), passphrase=passphrase)

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
    if keystate == "RealKeyUnlocked":
        key = RSA.import_key(open(SELF_KEY_FOLDER+"selfrsatrue.bin", "rb").read(), passphrase=password)
    elif keystate == "FakeKeyUnlocked":
        key = RSA.import_key(open(SELF_KEY_FOLDER+"selfrsafalse.bin", "rb").read(), passphrase=password)
    else:
        return "How tf would you get this to throw an error?"

    h = SHA512.new(bytes(message, 'utf-8'))

    signature = pkcs1_15.new(key).sign(h)
    return signature

def RSACheckSig(external_onion, i, message):
    key = RSA.import_key(open(KEY_FOLDER.format(external_onion)+"realpub.pub").read())

    signature = open(KEY_FOLDER.format(external_onion)+"messages/"+i+"signature.bin", "rb").read()

    h = SHA512.new(message.encode("utf-8"))

    try:
        pkcs1_15.new(key).verify(h, signature)
        return "Valid Signature"
    except (ValueError, TypeError):
        return "Invalid Signature"
