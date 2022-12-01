import time
import asyncio
import requests
import logging
from threading import Thread, Lock
from flask import Flask, request
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

victim='http://127.0.0.1:8080/'

app = Flask(__name__)
f=open("logs","w")
run_lock=Lock()
stop=False
worker=''

def create_log_entry(epoch,event,rtt):
	print("{epoch}::{event}::{RTT}".format(epoch=epoch,event=event,RTT=rtt))
	f.write("{epoch}::{event}::{RTT}\n".format(epoch=epoch,event=event,RTT=rtt))
	return 0

def measure_rtt(event,sample_density):
	while(True):
		start=time.time()
		requests.get(victim)
		end=time.time()
		create_log_entry(start,event,end-start)
		run_lock.acquire()
		global stop
		if stop:
			run_lock.release()
			return 0
		run_lock.release()
		time.sleep(sample_density)
	return 0

@app.route("/On/Start",methods=["GET"])
@app.route("/Off/Start",methods=["GET"])
@app.route("/On/Iteration",methods=["GET"])
@app.route("/Off/Iteration",methods=["GET"])
def log_event():
	#asyncio.create_task(create_log_entry(time.time(),request.path,-1))
	create_log_entry(time.time(),request.path,-1)
	return "{success:True}"

@app.route("/On/Idle",methods=["GET"])
@app.route("/Off/Idle",methods=["GET"])
@app.route("/On/Burst",methods=["GET"])
@app.route("/Off/Noise",methods=["GET"])
def measure_event():
	global worker
	run_lock.acquire()
	global stop
	stop = True
	run_lock.release()
	if worker!='':
		worker.join()
	run_lock.acquire()
	worker=Thread(target=measure_rtt,args=(request.path,1,))
	stop = False
	run_lock.release()
	worker.start()
	return "{success:True}"

@app.route("/end",methods=["GET"])
def end():
	global worker
	run_lock.acquire()
	global stop
	stop = True
	run_lock.release()
	worker.join()
	f.close()
	return "{success:True}"

if __name__ == "__main__":
	app.run(debug=True,host="0.0.0.0",port=8080)