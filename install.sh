#!/usr/bin/env bash
#
# silence
# rootfinlay - Dev
# CryptCod3r - Research Lead

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi

cwd=$(pwd)

read -p "Enter a username for your Silence installation: " my_var 

# Making the Flask project
mkdir /usr/share/silence
echo $my_var >> /usr/share/silence/username.txt
mkdir /usr/share/silence/backup
python3 -m venv /usr/share/silence/virtualenvironment
source "/usr/share/silence/virtualenvironment/bin/activate"
pip3 install gunicorn
pip3 install flask
pip3 install requests
pip3 install pycryptodome
pip3 install pysocks

cp ./assets/silencecrypto.py /usr/share/silence
cp ./assets/settings.py /usr/share/silence
cp ./assets/main.py /usr/share/silence
cp ./assets/wsgi.py /usr/share/silence
cp ./assets/silence.py /usr/bin/silence

cd /usr/share/silence
mkdir ./keys
mkdir ./keys/self
mkdir ./temp
touch ./notifications.sil
touch ./contacts.sil
chmod 777 -R /usr/share/silence
#gunicorn --bind 0.0.0.0:3301 wsgi:app

deactivate

pip3 install gunicorn
pip3 install flask
pip3 install requests
pip3 install pycryptodome
pip3 install pysocks

cd $cwd

useradd --system -g www-data --no-create-home --home-dir=/usr/share/silence --shell=/usr/sbin/nologin silencedaemon
# Tor setup
mkdir backup
cp /etc/tor/torrc ./backup
cp ./setup-utils/torrc /etc/tor/torrc
systemctl restart tor
cat /var/lib/tor/silence_service/hostname >> /usr/share/silence/local_hostname.txt
chown -R silencedaemon:www-data /usr/share/silence

# silence service setup
cp ./setup-utils/silence.socket /etc/systemd/system/silence.socket
cp ./setup-utils/silence.service /etc/systemd/system/silence.service
systemctl enable silence.service
systemctl daemon-reload

cp ./setup-utils/silence /etc/nginx/sites-available/silence
ln -s /etc/nginx/sites-available/silence /etc/nginx/sites-enabled

systemctl restart nginx
systemctl restart silence.service

# Turn off services awaiting start of Silence
systemctl stop tor
systemctl stop nginx

chmod +x /usr/bin/silence

printf "[ Silence Setup ]: DONE \n"
printf "\n"
printf "PLEASE RESTART FOR DAEMON TO WORK EFFECTIVELY!!!\n"
printf "PLEASE RESTART FOR DAEMON TO WORK EFFECTIVELY!!!\n"
printf "PLEASE RESTART FOR DAEMON TO WORK EFFECTIVELY!!!\n"
printf "PLEASE RESTART FOR DAEMON TO WORK EFFECTIVELY!!!\n"
printf "PLEASE RESTART FOR DAEMON TO WORK EFFECTIVELY!!!\n"

# 1033