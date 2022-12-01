FROM ubuntu:20.04
RUN apt-get update
RUN apt-get -y install python3
RUN apt-get -y install python3-pip
RUN pip3 install flask
RUN pip3 install requests
COPY main.py /home/main.py
WORKDIR /home
EXPOSE 8080
CMD ["python3","main.py"]