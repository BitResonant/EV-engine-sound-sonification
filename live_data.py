import obd
import time
from pythonosc import udp_client

# --- configuration ---
PORT = "COM8"
BAUD = 115200
# Force protocol 7 (CAN 29-bit) as seen in the recording session, to ensure compatibility with the vLinker and the car's ECU
PROTOCOL = "7"

# configuration OSC for Max MSP
UDP_IP = "127.0.0.1"
UDP_PORT = 5005
client = udp_client.SimpleUDPClient(UDP_IP, UDP_PORT)

def extract_value(response, default=0.0):
    """Return the numeric magnitude of an OBD response, or a default if missing.

    Commands are looked up via dict access and values via getattr so the code
    stays valid regardless of how the obd/pint libraries expose their members.
    """
    if response is None or response.is_null():
        return default
    return getattr(response.value, "magnitude", default)


def run_realtime_obd_to_max():
    print(f"--- Real-Time OBD connection (Port: {PORT}) ---")
    
    # initialize connection
    connection = obd.OBD(PORT, protocol=PROTOCOL, baudrate=BAUD)

    if not connection.is_connected():
        print("Error: Unable to connect to the car. Please check the vLinker and the dashboard.")
        return

    print("Synchronized! Sending data to Max MSP via OSC (Address: /car)")
    print("Press Ctrl+C to stop")

    # Commands to monitor (dict access avoids static-analysis warnings, since
    # obd.commands populates these names dynamically at runtime)
    cmd_rpm = obd.commands["RPM"]
    cmd_load = obd.commands["ENGINE_LOAD"]
    cmd_speed = obd.commands["SPEED"]

    try:
        while True:
            start_loop = time.time()

            # sensor interrogation
            res_rpm = connection.query(cmd_rpm)
            res_load = connection.query(cmd_load)
            res_speed = connection.query(cmd_speed)

            # Extracting numeric values
            rpm = extract_value(res_rpm)
            load = extract_value(res_load)
            speed = extract_value(res_speed)

            # Sending OSC message to Max MSP
            client.send_message("/car", [rpm, load, speed])

            # Debug print to console
            print(f"LIVE -> RPM: {rpm:4.0f} | LOAD: {load:3.1f}% | SPEED: {speed:3.0f}", end='\r')

            # Calculating the waiting time to maintain a constant 20Hz
            # Subtracting the time spent on the query to avoid time drifts
            elapsed = time.time() - start_loop
            wait_time = max(0, 0.05 - elapsed)
            time.sleep(wait_time)

    except KeyboardInterrupt:
        print("\n\nReal-Time Session Terminate.")
    finally:
        connection.close()

if __name__ == "__main__":
    run_realtime_obd_to_max()