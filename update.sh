if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi

wget https://finlaycampbell.xyz/silence/latest.zip
unzip latest.zip
mv silence/assets/*.py ./app/silence-backend
rm -rf silence 
rm latest.zip
printf "[ SILENCE ]: Updated"