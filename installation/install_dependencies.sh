sudo apt update
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-armv7l.sh
bash Miniconda3-latest-Linux-armv7l.sh
conda create --name AI_Smart_Home
conda activate AI_Smart_Home
sudo apt-get install portaudio19-dev python3-dev
sudo apt install bluetooth bluez bluez-tools rfkill
sudo apt install pulseaudio pulseaudio-module-bluetooth
