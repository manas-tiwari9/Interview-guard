# InterviewGuard 🛡️

InterviewGuard is an AI-powered proctoring and automated interview platform. It utilizes machine learning models to analyze video feeds in real-time to monitor candidates for suspicious behaviors, ensuring the integrity of remote assessments.

## Features
- **Real-Time AI Monitoring:** Leverages MediaPipe and Ultralytics YOLO to continuously track head posture, facial presence, and the usage of unauthorized devices (like smartphones).
- **Custom UI Architecture:** Built on top of Streamlit with a custom-engineered MJPEG HTML video streaming pipeline to guarantee zero-latency camera feeds.
- **Automated Assessment Generation:** Once the interview concludes, InterviewGuard compiles all tracking evidence into comprehensive PDF and JSON reports.
- **Dynamic Theming:** Configured with a modern "Graphite Slate" dark mode aesthetic that reduces eye strain for candidates.

## Installation

1. **Clone the repository:**
```bash
git clone https://github.com/manas-tiwari9/Interview-guard.git
cd Interview-guard
```

2. **Set up a Python environment (Optional but Recommended):**
```bash
conda create -n interview-guard python=3.11
conda activate interview-guard
```

3. **Install the dependencies:**
```bash
pip install -r requirements.txt
```

## Running the Application

To start the InterviewGuard application, simply run the `app.py` script using Streamlit. 

```bash
streamlit run app.py
```

By default, the application will be hosted on `http://localhost:8501`. 

## Architecture & Privacy
- **Local Inference:** All AI inferences (Face Detection, Phone Detection, Pose Estimation) run directly on your local machine CPU/GPU.
- **Data Protection:** Candidate reports, images, and session recordings are strictly kept local and ignored by Git to protect PII (Personally Identifiable Information).

---
*Developed by Manas Tiwari*
