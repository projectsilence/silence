####################################
# Settings file for Silence        #
# Change these at your own leisure #
# Just don't brick your install :D #
####################################

SELF_ADDRESS = open("./local_hostname.txt", "r").read().strip("\n")

DEFAULT_SELF_KEY_FOLDER = "./keys/self/"
SELF_KEY_FOLDER = DEFAULT_SELF_KEY_FOLDER # Change this if config is custom

DEFAULT_KEY_FOLDER = "./keys/{}/"#.format(address)
KEY_FOLDER = DEFAULT_KEY_FOLDER#.format(address)   Change this if config is custom

DEFAULT_TEMP_FOLDER = "./temp/"
TEMP_FOLDER = DEFAULT_TEMP_FOLDER # Change this if config is custom

MESSAGES_KEPT = "FALSE" 
MESSAGES_KEPT_FOR = 0 # Zero means forever

SILENCE_CLIENT_USER_AGENT = "silenceCORE/0.1.0"
SILENCE_SERVER_USER_AGENT = "silenceSERVER/0.1.0"