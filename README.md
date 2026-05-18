# EV Engine Sound Sonification

Real-time audio engine that converts electric vehicle (EV) diagnostic parameters into synthesized engine sounds. This project bridges OBD-II vehicle telemetry (RPM, engine load, speed) with Max MSP audio synthesis via OSC communication.

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
- Clean macOS metadata files (.DS_Store)

## Project Structure

**Core Operational Files (Root):**
- `engineV1.maxpat` — Primary audio synthesis engine
- `granular.maxpat` — Granular synthesis module
- `live_data.py` — Real-time OBD-II to OSC bridge
- `Wavetables/` — Audio assets for wavetable synthesis
- `Audio_files/` — Granular synthesis source material

**Setup & Configuration (`setup/`):**
- `requirements.txt` — Python dependencies
- `install_mac.sh`, `install_windows.bat` — Installation scripts

**Data Tools & Algorithm Development (`data-tools/`):**
- `play_data.py` — CSV playback to OSC (for testing without live vehicle)
- `rec_data.py` — OBD-II recording to CSV
- `CSV_files/` — Test datasets (18 recorded driving scenarios)
- `Data Acquisition Protocol.pdf` — OBD-II protocol documentation

## Usage

### Live Operation
Activate the environment and run:
```bash
source .venv/bin/activate
python live_data.py
```

### Testing with Recorded Data
```bash
cd data-tools
python play_data.py CSV_files/01_CAL_Pilot_Run_Check.csv
```

### Recording New Data
```bash
cd data-tools
python rec_data.py
```

## Dependencies

- `python-obd` — OBD-II vehicle communication
- `python-osc` — OSC transport to Max MSP
- `pyserial` — Serial interface
- Max 8 or later (for audio synthesis patches)
