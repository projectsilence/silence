sudo systemctl stop tor
sudo systemctl stop nginx
sudo systemctl stop silence.service

sudo rm /etc/nginx/sites-available/silence
sudo rm /etc/nginx/sites-enabled/silence
sudo rm /etc/systemd/system/silence.service
sudo rm /etc/systemd/system/silence.socket

sudo cp ./backup/torrc /etc/tor/torrc

sudo rm -rf ./*