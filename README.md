# Real-Time Neon Gesture Vision Engine

A computer vision project that tracks both hands in real time using MediaPipe and renders stunning neon laser effects — including finger laser strings, a spinning vortex portal, and explosion particles — all powered by OpenCV.

---

## Features

- **Laser Strings** — Neon beams connect matching fingertips of both hands
- **Vortex Portal** — Spinning energy portal appears between your palms
- **Explosion Particles** — Collision effect when hands come together
- **Two-Hand Detection** — Effects only trigger when both hands are visible
- **1280×720 HD Webcam** — Wide frame for max detection range

---

## Project Structure

```
Neon-hand-reactor/
│
├── hand_overlay.py          # Main application
├── hand_landmarker.task     # Auto-downloaded on first run
├── requirements.txt         # Python dependencies
├── README.md                # This file
└── venv/                    # Virtual environment (not uploaded to GitHub)
```

---

## How to Run

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/Neon-hand-reactor.git
cd Neon-hand-reactor
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> `hand_landmarker.task` is **automatically downloaded on the first run** using this code, include it at the top of `hand_overlay.py`:

```python
import urllib.request
import os

MODEL_PATH = "hand_landmarker.task"
MODEL_URL  = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"

if not os.path.exists(MODEL_PATH):
    print("Downloading hand_landmarker.task...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    print("Download complete.")
```

### 4. Run the app

```bash
python hand_overlay.py
```

Press **ESC** to quit.

---

## How to Use

| Gesture | Effect |
|---|---|
| Show both hands to camera | Laser strings connect your fingertips |
| Move hands apart/together | Vortex portal scales between palms |
| Bring wrists close together | 💥 Explosion particle burst! |

---


## License

MIT License — free to use and modify.
---
