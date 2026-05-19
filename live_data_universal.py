import obd
import time
from pythonosc import udp_client

try:
    from serial.tools import list_ports
except ImportError:
    list_ports = None

# --- configuration ---
PORT = None  # Set to a specific port (e.g. "COM8" or "/dev/ttyUSB0") to override auto-detection
BAUD = 115200

# configuration OSC for Max MSP
UDP_IP = "127.0.0.1"
UDP_PORT = 5005
client = udp_client.SimpleUDPClient(UDP_IP, UDP_PORT)

# OBD Protocols to try (most common first)
# Protocol descriptions:
# 0: Auto (lets the adapter determine)
# 1: SAE J1850 PWM
# 2: SAE J1850 VPW
# 3: ISO 9141-2
# 4: ISO 14230-4 KWP (5 baud init)
# 5: ISO 14230-4 KWP (Fast init)
# 6: ISO 15765-4 CAN (11-bit, 250k) - Common in older/Asian cars
# 7: ISO 15765-4 CAN (29-bit, 250k) - Common in European cars
# 8: ISO 15765-4 CAN (11-bit, 500k)
# 9: ISO 15765-4 CAN (29-bit, 500k) - Common in newer cars
PROTOCOLS_TO_TRY = ["0", "7", "6", "9", "8", "5", "4", "3", "2", "1"]

def attempt_connection(port, baudrate, protocol):
    """Attempt to connect with a specific protocol"""
    try:
        print(f"  Trying protocol {protocol}...", end=" ")
        connection = obd.OBD(port, protocol=protocol, baudrate=baudrate, timeout=5)
        
        if connection.is_connected():
            print(f"✓ Connected!")
            return connection
        else:
            print("✗ Failed to connect")
            return None
    except Exception as e:
        print(f"✗ Error: {str(e)[:50]}")
        return None

def find_and_connect(port, baudrate):
    """Try multiple protocols until one works"""
    print(f"\n--- Auto-Detecting OBD Protocol (Port: {port}) ---\n")
    
    for protocol in PROTOCOLS_TO_TRY:
        connection = attempt_connection(port, baudrate, protocol)
        if connection:
            return connection
    
    print("\n✗ Could not establish connection with any protocol.")
    print("  Please check:")
    print("  - OBD cable is properly connected")
    print("  - Car is powered on")
    print("  - USB/COM port is correct")
    return None


def get_candidate_ports():
    """Return likely candidate serial ports for OBD adapters."""
    if list_ports is None:
        return []

    ports = [comport.device for comport in list_ports.comports()]
    candidates = []
    for port in ports:
        if port.startswith("COM"):
            candidates.append(port)
        elif "/dev/ttyUSB" in port or "/dev/ttyACM" in port:
            candidates.append(port)
        elif port.startswith("/dev/cu.") or port.startswith("/dev/tty."):
            candidates.append(port)

    return candidates if candidates else ports


def scan_ports_and_connect(baudrate):
    """Try all detected serial ports until one connects."""
    print("\n--- Auto-Detecting OBD Port ---\n")

    ports = get_candidate_ports()
    if not ports:
        if list_ports is None:
            print("✗ Automatic port detection is unavailable because pyserial is not installed.")
            print("  Install it with: pip install pyserial")
        else:
            print("✗ No serial ports detected.")
        return None

    print(f"Detected ports: {', '.join(ports)}")
    for port in ports:
        connection = find_and_connect(port, baudrate)
        if connection:
            return connection

    return None


def run_realtime_obd_to_max():
    # Find and connect to OBD
    if PORT:
        print(f"Using configured port: {PORT}")
        connection = find_and_connect(PORT, BAUD)
        if not connection:
            print("\nAttempting automatic port scan instead...")
            connection = scan_ports_and_connect(BAUD)
    else:
        connection = scan_ports_and_connect(BAUD)

    if not connection:
        print("\n✗ Unable to connect automatically to any port.")
        if list_ports is not None:
            ports = get_candidate_ports()
            if ports:
                print(f"  Detected ports: {', '.join(ports)}")
        print("  Please manually set the PORT variable in live_data_universal.py to the correct serial port.")
        print("  Example: PORT = \"COM8\" or PORT = \"/dev/ttyUSB0\"")
        return

    print("\n✓ Synchronized! Sending data to Max MSP via OSC (Address: /car)")
    print("  Press Ctrl+C to stop\n")

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
        print("\n\nReal-Time Session Terminated.")
    finally:
        connection.close()

if __name__ == "__main__":
    run_realtime_obd_to_max()
