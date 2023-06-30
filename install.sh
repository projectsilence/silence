#!/usr/bin/env bash
#
# silence
# rootfinlay - Dev
# CryptCod3r - Research Lead
# Triponacci - Chorus Member

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi

printf 'Have you edited the files according to the README.md file?  Failing to will result in a non-working Silence installation. (y/n)? \n'
old_stty_cfg=$(stty -g)
stty raw -echo ; answer=$(head -c 1) ; stty $old_stty_cfg
if [ "$answer" != "${answer#[Yy]}" ];then
    printf '[ Silence Setup ]: Starting setup \n'
else
    printf '\n'
    exit
fi

# Making the Flask project
mkdir ./app
python3 -m venv ./app/virtualenvironment
source "./app/virtualenvironment/bin/activate"
pip3 install gunicorn
pip3 install flask
pip3 install requests
pip3 install pycryptodome
mkdir ./app/silence-backend

cp ./assets/*.py ./app/silence-backend

cd ./app/silence-backend
mkdir ./keys
mkdir ./keys/self
#gunicorn --bind 0.0.0.0:3301 wsgi:app

deactivate

pip3 install gunicorn
pip3 install flask
pip3 install requests
pip3 install pycryptodome

cd ../..
# Tor setup
mkdir backup
cp /etc/tor/torrc ./backup
cp ./setup-utils/torrc /etc/tor/torrc
systemctl start tor
systemctl restart tor
cat /var/lib/tor/silence_service/hostname >> ./app/silence-backend/local_hostname.txt

# silence service setup
cp ./setup-utils/silence.socket /etc/systemd/system/silence.socket
cp ./setup-utils/silence.service /etc/systemd/system/silence.service
systemctl enable silence.service
systemctl daemon-reload
systemctl start silence.service

cp ./setup-utils/silence /etc/nginx/sites-available/silence
ln -s /etc/nginx/sites-available/silence /etc/nginx/sites-enabled

systemctl restart nginx
systemctl restart silence.service

# Turn off services awaiting start of Silence
systemctl stop silence.service
systemctl stop tor
systemctl stop nginx


printf "[ Silence Setup ]: DONE \n"

# 1033
