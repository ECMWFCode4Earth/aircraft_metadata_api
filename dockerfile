FROM ubuntu:latest
RUN apt-get update
RUN apt-get install python3 -y && apt install python3-pip -y
RUN apt-get install wget -y
RUN wget https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-unstable/google-chrome-unstable_75.0.3770.18-1_amd64.deb
RUN apt-get install libappindicator3-1 -y
RUN apt-get update   
RUN apt-get upgrade -y
RUN apt-get install fonts-liberation -y
RUN apt-get install libasound2 -y
RUN apt-get install libnspr4 -y
RUN apt-get install libnss3 -y
RUN apt-get install libx11-xcb1 -y
RUN apt-get install libxss1 -y
RUN apt-get install lsb-release -y
RUN apt-get install xdg-utils -y
RUN dpkg -i ./google-chrome-unstable_75.0.3770.18-1_amd64.deb
RUN apt-get install -f 
RUN apt install python3-pip
RUN mkdir api 
WORKDIR ${PWD}/api
ADD . .
ENV PYTHONPATH="$PYTHONPATH:${PWD}"
RUN pip3 install -r requirements.txt
RUN pip3 install pytest


