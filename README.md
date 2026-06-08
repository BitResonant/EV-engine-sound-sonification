# EV Engine Sound Sonification

Real-time audio engine that uses thermic engine vehicle diagnostic parameters to create a synthesized electric vehicle (EV) engine sound. This system bridges OBD-II vehicle telemetry (RPM, engine load, speed) with Max MSP audio synthesis via OSC communication to create immersive and useful engine sonification.

## MAX/MSP Patch

### Wavetable Module (Melodic Core)

The Wavetable Module establishes the signature melodic and harmonic identity of the vehicle. It comprises a dual-engine architecture operating with distinct lookup tables interpolated in real time.

* **Engine A (Dyad Architecture):** At low speeds, Engine A generates a stable harmonic anchor based on a **major third** dyad. As velocity increases, the interval dynamically expands to a **perfect fifth**. This structural expansion creates a perceived acoustic "hollowness" and vacuum, reducing the sensory satisfaction of acceleration.
* **Engine B (Tetrad Architecture):** Operates on an independent, spectrally richer wavetable configured as a **major seventh** chord. Upon crossing the 100 km/h threshold, the chord transforms into a **minor seventh**, increasing inner-harmonic tension and subjective urgency.

#### Telemetry Mapping Matrix

* **RPM (Revolutions Per Minute):** Maps concurrently to three destinations:
    1. *Wavetable Phase Accumulator Read Position:* Alters the starting phase and scan index.
    2. *Fundamental Frequency:* Scales the lookup-table playback speed via an interpolated geometric mapping function, maintaining a constant proportional relationship with the granular textures to ensure absolute spectral alignment.
    3. *Amplitudinal Balance:* Controls the relative gain of upper extensions against the fundamental. Low RPM prioritizes the fundamental f0, producing a dark, warm, and comforting timbre. High RPM introduces high-frequency brilliance (f > 2 kHz) and a prominent melodic environment.
* **Engine Load:** Modulates the frequency of inter-octave beatings (f_beat) across the modules. This synthesis technique simulates mechanical strain by accelerating a micro-tremolo/amplitude modulation (AM) depth, mapping physical effort directly to perceived acoustic tension.
* **Velocity (Speed):** Controls the crossfade and balance between Engine A and Engine B. Lower velocities ensure complete dominance of the foundational dyad, while high velocities seamlessly transition exposure toward the dense, unresolved tetrad configuration.

### Granular Module (Organic Micro-Synthesis)

The granular module provides organic friction, mechanical "breath," and macroscopic roughness (Δf), breaking the clinical linearity typical of digital EV synthesis.

* **Dynamic Instance Allocation (`poly~` Optimization):** The engine spawns 36 parallel instances of a customized granular voice. To achieve deterministic computational efficiency, individual instances utilize strict **just-in-time (JIT) activation logic**. Voice threads are computed and unmuted *only* for the precise duration of a grain's windowing function (A(t)), and immediately deactivated upon grain termination. This prevents idle CPU pooling and thread serialization overhead.
* **Vectorized Parameter Windowing:** Each voice pulls from a stochastic boundary window updated via low-frequency data arrays, ensuring non-repetitive micro-structural variations.
* **Dynamic Buffer Mapping:** The grains are synthesized from a 22-second reference audio buffer compiled at a mapping scale of 1 s ≡ 10 km/h.
  * *Low Velocity:* Grains are restricted to the early sections of the buffer (0 s ≤ t < 4 s), rich in harmonic, smooth, and warm spectral contents.
  * *High Velocity:* The lookup window shifts to the later stages of the buffer (t > 10 s), consisting of highly inharmonic, dense, and physically "rough" automotive noise profiles.
* **Telemetry Mapping Matrix:**
  * *RPM:* Direct control over grain playback speed and pitch transpose ratios, keeping the micro-acoustic texture perfectly phase-aligned and tuned to the Wavetable Core.
  * *Engine Load:* Directly governs grain trigger density (g_freq) and grain duration (d_g). Low load maps to low-frequency, wide-aperture, overlapping grains (smooth macroscopic envelope). High load switches to high-density, ultra-short grains (d_g < 20 ms), generating acoustic temporal urgency and mimicking high-stress pneumatic/kinetic discharge.

### FX Matrix (Spectral & Spatial Cohesion)

The FX module acts as an electroacoustic glue, merging the discrete digital outputs of the Wavetable and Granular engines into a unified, single acoustic object.

1. **Overdrive & Non-Linear Waveshaping:** Introduces subtle, controlled odd-harmonic distortion. By generating identical, phase-locked upper partials across both synthesis engines, it psychoacoustically fuses the distinct sources into a single perceived sound source.
2. **Resonant Filterbank (Physical Model Simulation):** A specialized multi-channel filter array simulating the acoustic cavity resonances of a physical mechanical chassis. Forcing both engines through identical, static formant peaks establishes a shared structural acoustic profile.
3. **Early Reflections Network:** A localized, low-latency tapped delay line matrix. It places the synthesized audio within a localized spatial frame, ensuring that the driver's auditory cortex perceives the sound as originating from a shared, concrete physical environment rather than disconnected headphones or isolated transducers.

---

## Low-Latency Optimization & Computational Efficiency

The patch has been architected to fit within strict CPU budget allocations:

* **Zero-Zipper Noise Interpolation:** All continuous telemetry inputs (Speed, RPM, Load) are smoothed at vector level using linear and exponential ramp generators (`line~`) to eliminate quantization artifacts and parameter-induced aliasing.
* **Memory Footprint:** The granular buffer size is strictly capped at 22 seconds, utilizing single-precision floating-point arrays (`buffer~`) entirely residency-cached in RAM to minimize memory controller page faults and bus latency.


## Prerequisites

Before installation, ensure you have:

* **Hardware**: Vehicle with OBD-II diagnostics support + vLinker serial adapter
* **Software**:
  * Python 3.7 or later
  * Max 8 or later (for audio synthesis patches)
* **Connectivity**: USB serial port available (e.g., `COM8` on Windows, `/dev/ttyUSB0` on macOS/Linux)

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

* Create a Python virtual environment at `.venv/`
* Install dependencies from `setup/requirements.txt`
* Remove macOS metadata files (`.DS_Store`) to keep repository clean

## Project Structure

**Core Operational Files (Root):**

* `engineV1.maxpat` — Primary audio synthesis engine with hybrid wavetable and effects processing
* `granular.maxpat` — Granular synthesis module for textured soundscapes
* `live_data.py` — Real-time OBD-II to OSC bridge (connects vehicle to Max MSP)
* `live_data_universal.py` — Universal OBD-II to OSC bridge with automatic protocol and serial port detection
* `Wavetables/` — Audio assets for wavetable synthesis layers
* `Audio_files/` — Granular synthesis source material

**Setup & Configuration (`setup/`):**

* `requirements.txt` — Python package dependencies
* `install_mac.sh` — Automated macOS setup script
* `install_windows.bat` — Automated Windows setup script

**Data Tools & Algorithm Development (`data-tools/`):**

* `play_data.py` — CSV playback to OSC (for testing without a live vehicle)
* `rec_data.py` — OBD-II data recording to CSV files
* `CSV_files/` — Test datasets (18 recorded driving scenarios)
* `Data Acquisition Protocol.pdf` — OBD-II protocol documentation and signal specifications

## Usage

### Live Operation with Vehicle

For most vehicles, use `live_data_universal.py` to automatically detect both the serial port and the OBD protocol.

If you want to rely on auto-detection, leave `PORT = None` in `live_data_universal.py`:

```python
PORT = None                 # Automatic serial port detection
BAUD = 115200               # Standard baud rate for vLinker
```

If the script cannot connect automatically, it will print detected serial ports and ask you to manually set `PORT`:

```python
PORT = "COM8"              # Serial port override (Windows)
# or
PORT = "/dev/ttyUSB0"      # Serial port override (macOS/Linux)
```

Then activate the environment and start the real-time bridge:

```bash
source .venv/bin/activate
python live_data_universal.py
```

If you still need the original fixed-port version, `live_data.py` can be used as before with explicit `PORT`, `BAUD`, and `PROTOCOL` settings.

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

* **timestamp** — Elapsed time in seconds (starts at 0.0)
* **rpm** — Engine RPM (0–8000 typical range)
* **engine_load** — Engine load percentage (0–100%)
* **speed** — Vehicle speed in km/h

## Test Datasets

The `data-tools/CSV_files/` folder contains 18 pre-recorded driving scenarios:

* **Calibration (CAL)**: Idle, steady cruising at various speeds, power cycle startup
* **Dynamics (DYN)**: Acceleration, coast-down, direction changes, parking maneuvers
* **Stress (STR)**: Uphill/downhill driving, highway max speed, traction load spikes
* **Environment (ENV)**: Center and suburban driving profiles

Use these datasets to validate algorithm behavior across diverse driving conditions.

## Dependencies

* `python-obd>=0.7.1` — OBD-II protocol communication with vehicle ECU
* `python-osc>=1.8.0` — Open Sound Control (OSC) client for Max MSP integration
* `pyserial>=3.5` — Serial port communication for vLinker adapter
* `Max 8+` — Audio synthesis and real-time signal processing (not installed by pip)

## Troubleshooting

**"Unable to connect to the car"**

* Verify vLinker is powered and connected to the USB port
* Check `PORT` configuration matches your serial port (use Device Manager on Windows, `ls /dev/tty*` on macOS/Linux)
* Ensure vehicle is in "on" or "ready" state (not off)

**"error: File not found"** (in play_data.py)

* Verify `CSV_PATH` and `FILENAME` are correct and file exists
* Use absolute paths if relative paths aren't working

**OSC messages not reaching Max MSP**

* Verify Max patch is listening on port `5005`
* Confirm `UDP_IP = "127.0.0.1"` in Python script (localhost)
* Check firewall isn't blocking UDP on port 5005

## Development Workflow

1. **Prototype**: Use recorded CSV data with `play_data.py` to iterate on the Max algorithm
2. **Validate**: Test with live vehicle using `live_data.py` on different driving scenarios
3. **Record**: Capture new test cases with `rec_data.py` for future validation
4. **Refine**: Return to step 1 with new recordings

## Notes

* The project uses **Protocol 7 (CAN 29-bit)** hardcoded for vLinker compatibility
* Data sampling frequency is **20 Hz** (50ms intervals) for both recording and playback
* OSC messages are sent to address `/car` with payload `[rpm, load, speed]`
* All Python scripts require the virtual environment activated: `source .venv/bin/activate`
