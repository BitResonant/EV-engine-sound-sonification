# EV Engine Sound Sonification

Real-time audio engine that uses thermic engine vehicle diagnostic parameters to create a synthesized electric vehicle (EV) engine sound. This system bridges OBD-II vehicle telemetry (RPM, engine load, speed) with Max MSP audio synthesis via OSC communication to create immersive and useful engine sonification.

## Prerequisites

Before installation, ensure you have:

- **Hardware**: Vehicle with OBD-II diagnostics support + vLinker serial adapter
- **Software**:
  - Python 3.7 or later
  - Max 8 or later (for audio synthesis patches)
- **Connectivity**: USB serial port available (e.g., `COM8` on Windows, `/dev/ttyUSB0` on macOS/Linux)

## Installation

### macOS

```bash
bash setup/install_mac.sh
```

### Windows

```cmd
setup\install_windows.bat
```

The installer will:
- Create a Python virtual environment at `.venv/`
- Install dependencies from `setup/requirements.txt`
- Remove macOS metadata files (`.DS_Store`) to keep repository clean

## Project Structure

**Core Operational Files (Root):**

- `engineV1.maxpat` — Primary audio synthesis engine with hybrid wavetable and effects processing
- `granular.maxpat` — Granular synthesis module for textured soundscapes
- `live_data.py` — Real-time OBD-II to OSC bridge (connects vehicle to Max MSP)
- `Wavetables/` — Audio assets for wavetable synthesis layers
- `Audio_files/` — Granular synthesis source material

**Setup & Configuration (`setup/`):**

- `requirements.txt` — Python package dependencies
- `install_mac.sh` — Automated macOS setup script
- `install_windows.bat` — Automated Windows setup script

**Data Tools & Algorithm Development (`data-tools/`):**

- `play_data.py` — CSV playback to OSC (for testing without a live vehicle)
- `rec_data.py` — OBD-II data recording to CSV files
- `CSV_files/` — Test datasets (18 recorded driving scenarios)
- `Data Acquisition Protocol.pdf` — OBD-II protocol documentation and signal specifications

## Usage

### Live Operation with Vehicle

Before running, configure your hardware connection in `live_data.py`:

```python
PORT = "COM8"              # Serial port (change to your vLinker port)
BAUD = 115200             # Standard baud rate for vLinker
PROTOCOL = "7"            # CAN 29-bit protocol (specific to your vehicle)
```

Then activate the environment and start the real-time bridge:

```bash
source .venv/bin/activate
python live_data.py
```

The system will connect to your vehicle and stream telemetry to Max MSP at `127.0.0.1:5005` via OSC.

### Testing with Recorded Data (No Vehicle Required)

Use pre-recorded test datasets to develop and refine the Max algorithm without a live vehicle connection.

**Step 1:** Configure `data-tools/play_data.py` with a CSV file path:

```python
CSV_PATH = r"./CSV_files"           # Folder containing CSV files
FILENAME = "01_CAL_Pilot_Run_Check.csv"  # Choose any test dataset
```

**Step 2:** Run the playback:

```bash
cd data-tools
python play_data.py
```

The system will replay recorded telemetry data at original timing to Max MSP.

### Recording New Vehicle Data

To capture fresh telemetry for testing and validation:

**Step 1:** Configure `data-tools/rec_data.py` with your vehicle port and save location:

```python
PORT = "COM8"              # Serial port (same as live_data.py)
SAVE_PATH = r"./CSV_files"  # Where to save recorded CSV
FILENAME = f"my_recording.csv"  # Unique filename
```

**Step 2:** Start recording:

```bash
cd data-tools
python rec_data.py
```

Press `Ctrl+C` to stop recording. The CSV file will be saved in `SAVE_PATH` with timestamp, RPM, engine load, and speed columns.

## Data Format

All CSV files use the following structure:

```
timestamp,rpm,engine_load,speed
0.000,850,15.3,0
0.050,850,15.3,0
0.100,860,16.1,2
...
```

- **timestamp** — Elapsed time in seconds (starts at 0.0)
- **rpm** — Engine RPM (0–8000 typical range)
- **engine_load** — Engine load percentage (0–100%)
- **speed** — Vehicle speed in km/h

## Test Datasets

The `data-tools/CSV_files/` folder contains 18 pre-recorded driving scenarios:

- **Calibration (CAL)**: Idle, steady cruising at various speeds, power cycle startup
- **Dynamics (DYN)**: Acceleration, coast-down, direction changes, parking maneuvers
- **Stress (STR)**: Uphill/downhill driving, highway max speed, traction load spikes
- **Environment (ENV)**: Center and suburban driving profiles

Use these datasets to validate algorithm behavior across diverse driving conditions.

## Dependencies

- `python-obd>=0.7.1` — OBD-II protocol communication with vehicle ECU
- `python-osc>=1.8.0` — Open Sound Control (OSC) client for Max MSP integration
- `pyserial>=3.5` — Serial port communication for vLinker adapter
- `Max 8+` — Audio synthesis and real-time signal processing (not installed by pip)

## Troubleshooting

**"Unable to connect to the car"**
- Verify vLinker is powered and connected to the USB port
- Check `PORT` configuration matches your serial port (use Device Manager on Windows, `ls /dev/tty*` on macOS/Linux)
- Ensure vehicle is in "on" or "ready" state (not off)

**"error: File not found"** (in play_data.py)
- Verify `CSV_PATH` and `FILENAME` are correct and file exists
- Use absolute paths if relative paths aren't working

**OSC messages not reaching Max MSP**
- Verify Max patch is listening on port `5005`
- Confirm `UDP_IP = "127.0.0.1"` in Python script (localhost)
- Check firewall isn't blocking UDP on port 5005

## Development Workflow

1. **Prototype**: Use recorded CSV data with `play_data.py` to iterate on the Max algorithm
2. **Validate**: Test with live vehicle using `live_data.py` on different driving scenarios
3. **Record**: Capture new test cases with `rec_data.py` for future validation
4. **Refine**: Return to step 1 with new recordings

## Notes

- The project uses **Protocol 7 (CAN 29-bit)** hardcoded for vLinker compatibility
- Data sampling frequency is **20 Hz** (50ms intervals) for both recording and playback
- OSC messages are sent to address `/car` with payload `[rpm, load, speed]`
- All Python scripts require the virtual environment activated: `source .venv/bin/activate`
