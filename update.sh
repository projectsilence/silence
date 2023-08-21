if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi

wget https://finlaycampbell.xyz/silence/latest.zip
unzip latest.zip
systemctl stop silence.service
mv ./assets/silencecrypto.py /usr/share/silence
mv ./assets/settings.py /usr/share/silence
mv ./assets/main.py /usr/share/silence
mv ./assets/wsgi.py /usr/share/silence
mv ./assets/silence.py /usr/bin/silence
sudo chmod +x specific.sh
./specific.sh
rm -rf latest 
rm latest.zip
printf "[ SILENCE ]: Updated"
