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

def run_realtime_obd_to_max():
    print(f"--- Real-Time OBD connection (Port: {PORT}) ---")
    
    # initialization connection
    connection = obd.OBD(PORT, protocol=PROTOCOL, baudrate=BAUD)

    if not connection.is_connected():
        print("Error: Unable to connect to the car. Please check the vLinker and the dashboard.")
        return

    print("Synchronized! Sending data to Max MSP via OSC (Address: /car)")
    print("Press Ctrl+C to stop")

    # Commands to monitor
    cmd_rpm = obd.commands.RPM
    cmd_load = obd.commands.ENGINE_LOAD
    cmd_speed = obd.commands.SPEED

    try:
        while True:
            start_loop = time.time()

            # sensor interrogation
            res_rpm = connection.query(cmd_rpm)
            res_load = connection.query(cmd_load)
            res_speed = connection.query(cmd_speed)

            # Extracting numeric values
            rpm = res_rpm.value.magnitude if not res_rpm.is_null() else 0.0
            load = res_load.value.magnitude if not res_load.is_null() else 0.0
            speed = res_speed.value.magnitude if not res_speed.is_null() else 0.0

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