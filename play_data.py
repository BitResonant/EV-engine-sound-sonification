import csv
import time
import os
from pythonosc import udp_client

# --- Configuration ---
CSV_PATH = r"C:\Users\matte\Desktop\audio_ux\EV_UX\CSV_files"
FILENAME = "08_DYN_Acc_100_Percent.csv"
FULL_PATH = os.path.join(CSV_PATH, FILENAME)

# OSC
UDP_IP = "127.0.0.1"
UDP_PORT = 5005

# Client OSC
client = udp_client.SimpleUDPClient(UDP_IP, UDP_PORT)

def play_csv_to_max_osc():
    if not os.path.exists(FULL_PATH):
        print(f"Error: File not found in {FULL_PATH}")
        return

    print(f"--- OSC Session begin: {FILENAME} ---")
    print(f"Sending data to Max {UDP_IP}:{UDP_PORT}")

    with open(FULL_PATH, mode='r') as file:
        reader = csv.DictReader(file)
        last_time = 0

        for row in reader:
            # reading data from CSV file
            current_time = float(row['timestamp'])
            rpm = float(row['rpm'])
            load = float(row['engine_load'])
            speed = float(row['speed'])

            # Logic to maintain original recording speed
            sleep_time = current_time - last_time
            if sleep_time > 0:
                time.sleep(sleep_time)

            # Sending OSC with /car address, sending rpm, load and speed data
            client.send_message("/car", [rpm, load, speed])

            print(f"T: {current_time:.2f}s | OSC -> /car {rpm:.0f} {load:.1f} {speed:.0f}", end='\r')
            last_time = current_time

    print("\n--- Session completed ---")

if __name__ == "__main__":
    play_csv_to_max_osc()
