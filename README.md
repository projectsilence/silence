# Silence

## Precursor
Running the install script will change your Tor files, nginx sites and create system services under the name "silence".  This shouldn't affect most people, but be dilligent when running the install script.
The script is made to be as user-friendly as possible, it is encouraged to install the components yourself if you have the knowhow.

Local encryption laws may apply.  Please check and abide by the laws setout by your country.  Moral laws also apply, please use this service for good and do no harm.  I am not liable for your choices.

Silence is still in an open beta, if you find any bugs or have any questions please contact me at finlay.business@proton.me

Thank you.

## Modifying the setup files
```text

# silence

server {
       listen 127.0.0.1:8080 default_server;  <---  Only change this line if you changed your torrc port
       server_name silence;

       location / {
         include proxy_params;
         proxy_pass http://unix:/home/CHANGEME/silence/app/silence_backend/silence.sock;  <---  CHANGE THIS LINE TO YOUR SILENCE PATH
         allow 127.0.0.1;
         deny all;
       }
     }

# silence.service

[Unit]
Description=silence service
Requires=silence.socket
After=network.target

[Service]
User=CHANGEME   <--  CHANGE THIS LINE TO YOUR USERNAME
Group=www-data
WorkingDirectory=/home/CHANGEME/silence/app/silence-backend/ <---  CHANGE THIS LINE TO YOUR SILENCE PATH
Environment="PATH=/home/CHANGEME/silence/app/virtualenvironment/bin" <---  CHANGE THIS LINE TO YOUR SILENCE PATH
ExecStart=/home/CHANGEME/silence/app/virtualenvironment/bin/gunicorn --access-logfile - --workers 3 --bind unix:/home/CHANGEME/silence/app/silence_backend/silence.sock wsgi:app <---  CHANGE THIS LINE TO YOUR SILENCE PATH

[Install]
WantedBy=multi-user.target

# silence.socket

[Unit]
Description=silence socket

[Socket]
ListenStream=/home/CHANGEME/silence/app/silence_backend/silence.sock <---  CHANGE THIS LINE TO YOUR SILENCE PATH

[Install]
WantedBy=sockets.target

# torrc 

Only change this if you know what you're doing.

```

## Installation & Running Silence
```console

# Clone the repo
$ git clone https://github.com/rfdevelopments/silence

# Run the install script
$ cd silence
$ chmod +x install.sh
$ ./install.sh

# Locate the silence files
$ cd app/silence-backend

# Run silence daemon
$ python3 silence.py daemon

# Generate the silence keys
$ python3 silence.py genkeys

# Pingtest a silence onion to see if it's online
$ python3 silence.py pingtest (onion)

# Initiate a connection with the onion
$ python3 silence.py initiate (onion)

# Send a message to an onion
$ python3 silence.py sendmessage (onion)

# Read a message from an onion
$ python3 silence.py readmessage (onion)

# Stop the daemon
$ python3 silence.py stop

```
