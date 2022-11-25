import time
import asyncio
from flask import Flask

victim=''

app = Flask(__name__)
f=open("logs","w")
rtt_task=''

async def create_log_entry(epoch,event,rtt):
	f.write("{epoch}::{event}::{RTT}\n")
    return 0

async def measure_rtt(event,sample_density):
	while(True):
		start=time.time()
		request.get(victim+'/json')
		end=time.time()
		create_log_entry(start,event,start-end)
		await asyncio.sleep(sample_density)
	return 0

@app.route("/On/Start",methods=["GET"])
@app.route("/Off/Start",methods=["GET"])
@app.route("/On/Iteration",methods=["GET"])
@app.route("/Off/Iteration",methods=["GET"])
def log_event():
	asyncio.create_task(create_log_entry(time.time(),request.path,-1))
	return "{success:True}"

@app.route("/On/Idle",methods=["GET"])
@app.route("/Off/Idle",methods=["GET"])
@app.route("/On/Burst",methods=["GET"])
@app.route("/Off/Noise",methods=["GET"])
def measure_event():
	if rtt_task != '':
		rtt_task.cancel()
	rtt_task=asyncio.create_task(measure_rtt(request.path,100))
	return "{success:True}"

@app.route("/end",methods=["GET"])
def end():
	f.close()
	return "{success:True}"

'''
async def cancel_me(i,j):
    while(True):
    	print('print')
    	print(i)
    	print(j)
    	await asyncio.sleep(0.1)
    
async def main():
    task = asyncio.create_task(cancel_me(9,10))
    await asyncio.sleep(1)
    task.cancel()

asyncio.run(main())'''