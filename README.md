## 🔧 Steps to Follow (Raspberry Pi Side)

1. Clone the repository:

```bash
git clone https://github.com/varshh219/ThyroSenseX
cd ThyroSenseX
```

2. Create and activate virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

4. Add model files:

* Place the following inside `model/` folder:

  * thyroid_model.pkl
  * scaler.pkl
  * feature_columns.pkl
  * cnn_model.h5 (if used)

5. Run the application:

```bash
python main.py
```

---

## 🔌 Integration Work

6. Update camera:

* Edit `sensors/camera.py`
* Capture face image using Pi Camera / USB cam

7. Update microphone:

* Edit `sensors/microphone.py`
* Record voice input properly

8. Update thermal sensor:

* Edit `sensors/thermal.py`
* Replace dummy values with real readings (if sensor available)

---

## 🧪 Final Check

9. Test full flow:

* Login → Register Patient → Capture Data → Predict → Result → Report

---

## 🎯 Goal

Ensure the GUI runs on Raspberry Pi and uses real sensor inputs for prediction.
