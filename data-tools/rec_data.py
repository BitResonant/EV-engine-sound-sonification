import obd
import csv
import time
import os

# file name/path configuration
PORT = "COM8"
SAVE_PATH = r"write your save path here"
FILENAME = f"write your file name here"
FULL_PATH = os.path.join(SAVE_PATH, FILENAME)

def run_telemetry_csv():
    # making shure that the folder exists
    if not os.path.exists(SAVE_PATH):
        os.makedirs(SAVE_PATH)

    print(f"--- initializing OBD on {PORT} (Protocol 7) ---")
    connection = obd.OBD(PORT, protocol="7", baudrate=115200)

    if not connection.is_connected():
        print("Error: Cannot connect to the car.")
        return

    print(f"Saving: {FULL_PATH}")
    print("Recording... (Press Ctrl+C to stop)")

    # opening CSV file
    with open(FULL_PATH, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Header: Time, RPM, Load, Speed
        writer.writerow(["timestamp", "rpm", "engine_load", "speed"])

        start_time = time.time()

        try:
            while True:
                # Sensors query
                res_rpm = connection.query(obd.commands.RPM)
                res_load = connection.query(obd.commands.ENGINE_LOAD)
                res_speed = connection.query(obd.commands.SPEED)

                # Data extraaction
                t = round(time.time() - start_time, 3)
                rpm = res_rpm.value.magnitude if not res_rpm.is_null() else 0.0
                load = res_load.value.magnitude if not res_load.is_null() else 0.0
                speed = res_speed.value.magnitude if not res_speed.is_null() else 0.0

                # Writing data into the file and printing on terminal
                writer.writerow([t, rpm, load, speed])
                print(f"[{t}s] RPM: {rpm:4.0f} | LOAD: {load:3.1f}% | SPEED: {speed:3.0f} km/h", end='\r')

                # 20Hz frequency (0.05s)
                time.sleep(0.05)

        except KeyboardInterrupt:
            print(f"\n\nSession stopped. File saved correctly.")
        finally:
            connection.close()

if __name__ == "__main__":
    run_telemetry_csv()
