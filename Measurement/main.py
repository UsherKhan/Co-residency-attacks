import time
import requests
from flask import Flask, request

app = Flask(__name__)
log_file = 'rtt_logs.txt'  # Name of the log file
stop_measurement = False  # Flag to control the measurement loop

def create_log_entry(epoch, event, rtt):
    """
    Creates a log entry with the given epoch, event, and round-trip time (RTT).
    Appends the log entry to the log file.
    """
    log_entry = f"{epoch}::{event}::{rtt}\n"
    with open(log_file, 'a') as f:
        f.write(log_entry)

def measure_rtt(event, sample_density):
    """
    Measures the round-trip time (RTT) by sending requests to the web server.
    The measurement loop runs until the stop_measurement flag is set to True.
    The RTT is calculated and logged for each measurement.
    """
    while not stop_measurement:
        start_time = time.time()
        requests.get(request.host_url)
        end_time = time.time()
        rtt = end_time - start_time
        create_log_entry(start_time, event, rtt)
        time.sleep(sample_density)

@app.route("/start", methods=["GET"])
def start_measurement():
    """
    Starts the RTT measurement.
    Retrieves the event and sample density from the request parameters.
    Calls the measure_rtt function with the provided parameters.
    """
    global stop_measurement
    stop_measurement = False
    event = request.args.get('event', 'Measurement')
    sample_density = float(request.args.get('sample_density', 1.0))
    measure_rtt(event, sample_density)
    return "Measurement started"

@app.route("/stop", methods=["GET"])
def stop_measurement():
    """
    Stops the RTT measurement by setting the stop_measurement flag to True.
    """
    global stop_measurement
    stop_measurement = True
    return "Measurement stopped"

@app.route("/logs", methods=["GET"])
def get_logs():
    """
    Retrieves the contents of the log file and returns it as the response.
    """
    with open(log_file, 'r') as f:
        logs = f.read()
    return logs

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
