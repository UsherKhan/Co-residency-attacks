FROM ubuntu:20.04
RUN apt-get update
RUN apt-get -y install python3
RUN apt-get -y install python3-pip
RUN apt-get -y install python3-requests
RUN pip3 install --pre scapy[complete]
COPY main.py /home/main.py
WORKDIR /home
CMD ["python3","main.py"]