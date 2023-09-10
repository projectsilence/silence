#!/bin/bash

#echo "No specific updates at this time!"

mv temp/install.sh .
rm -rf temp

read -p "Please enter your silence username: " my_var 
echo $my_var >> /usr/share/silence/username.txt