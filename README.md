## 🔧 Raspberry Pi Setup

### 1. Clone the Repository

```bash
git clone https://github.com/varshh219/ThyroSenseX.git
cd ThyroSenseX
```

### 2. Create and Activate Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
python3 -m pip install -r requirements.txt
```

### 4. Verify Model Files

The current ThyroSenseX AI pipeline uses the following trained model files:

```text
model/
├── model.pkl
├── scaler.pkl
└── feature_columns.pkl
```

These files are included in the repository and should be available after cloning.

### 5. Configure Raspberry Pi

Update the Raspberry Pi IP configuration before running the application.

The system uses the Raspberry Pi for:

* 📷 Camera capture
* 🎙️ Voice recording
* 🌡️ Thermal data acquisition
* 📺 OLED result display

Make sure the Raspberry Pi services are running and accessible from the application.

### 6. Run the Application

```bash
python main.py
```

---

## 🔌 Sensor Integration

### 📷 Camera

Connect the Raspberry Pi Camera Module or supported USB camera.

The captured image is processed by the facial feature extraction pipeline.

### 🎙️ Microphone

Connect the microphone and verify that audio recording is working correctly.

The recorded voice sample is processed by the voice feature extraction pipeline.

### 🌡️ Thermal Sensor

Connect the MLX90640 thermal camera module and verify that thermal readings are being received.

The thermal data is processed by the thermal feature extraction pipeline.

### 📺 OLED Display

If an OLED display is connected, ensure that the Raspberry Pi API is running correctly.

The predicted thyroid condition and confidence score are sent to the OLED display.

---

## 🧠 AI Prediction Pipeline

ThyroSenseX combines multiple patient and sensor features:

```text
Patient Information
        │
        ├── Age
        ├── Weight
        └── Gender
              │
              ▼
       Facial Features
              │
              ▼
       Thermal Features
              │
              ▼
        Voice Features
              │
              ▼
       Feature Vector
              │
              ▼
      Machine Learning Model
              │
              ▼
   Thyroid Classification
              │
      ┌───────┼──────────────┐
      ▼       ▼              ▼
   Normal  Hypothyroidism  Hyperthyroidism
```

The prediction is generated from the extracted features and **does not depend on the patient's name or patient ID**.

---

## 🧪 Final System Test

Test the complete workflow:

```text
Doctor Login
     ↓
Patient Selection / Registration
     ↓
Image Capture
     ↓
Thermal Data Capture
     ↓
Voice Recording
     ↓
Feature Extraction
     ↓
AI Model Prediction
     ↓
Result Display
     ↓
Save Scan
     ↓
Generate Report
```

Verify that:

* Patient information is loaded correctly.
* Camera capture works.
* Voice recording works.
* Thermal data is received.
* Features are extracted successfully.
* The trained model generates the prediction.
* The confidence score is displayed.
* The prediction is saved to the database.
* The final report is generated correctly.

---

## 🎯 Goal

The goal is to run the complete **ThyroSenseX AI-IoT thyroid screening system** on Raspberry Pi using real camera, thermal and voice inputs together with the trained machine-learning model.

The system is designed to provide a portable, non-invasive and real-time thyroid screening workflow.
