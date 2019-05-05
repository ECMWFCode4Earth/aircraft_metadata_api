FROM ubuntu:latest
RUN apt-get update
RUN apt-get install python3 -y && apt install python3-pip -y
RUN wget https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-unstable/google-chrome-unstable_74.0.3729.6-1_amd64.deb
RUN dpkg -i ./google-chrome-unstable_74.0.3729.6-1_amd64.deb
RUN apt-get install -f
RUN apt-get update   
RUN apt-get upgrade
