# Silence

## Precursor
Running the install script will change your Tor files, nginx sites and create system services under the name "silence". This shouldn't affect most people, but be dilligent when running the install script. The script is made to be as user-friendly as possible, it is encouraged to install the components yourself if you have the knowhow.

Local encryption laws may apply. Please check and abide by the laws setout by your country. Moral laws also apply, please use this service for good and do no harm. I am not liable for your choices.

Silence is still in an open beta, and is a proof of concept. If you find any bugs or have any questions please contact me at finlay.business@proton.me

Thank you.

## Installation & Running Silence
```console

# Clone the repo
$ git clone https://github.com/projectsilence/silence

# Run the install script
$ cd silence
$ chmod +x install.sh
$ sudo ./install.sh

# Run Silence (regular mode)
$ silence # Not implemented yet

# Run silence daemon
$ silence daemon

# Initiate contact with another silence user
$ silence initiate (onion url)

# Send a message to a contact
$ silence sendmessage (onion url)

# Read a message from a contact
$ silence readmessage (onion url)

```

## Updating Silence
```console
# Make the update script executable
$ sudo chmod +x update.sh 

# Run the update script
$ sudo ./update.sh
```
