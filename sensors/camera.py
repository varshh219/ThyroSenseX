import cv2
import numpy as np


def capture_face_image(preview_seconds=3):
    """
    Opens webcam, shows live preview, captures one frame.
    Returns: numpy BGR image array, or None if failed.

    On laptop : uses webcam (cv2.VideoCapture(0))
    On Pi     : swap to picamera2 (Step 9 - deployment)
    """

    cap = cv2.VideoCapture(0)  # 0 = default webcam

    if not cap.isOpened():
        print("ERROR: Could not open camera.")
        return None

    print(f"Camera open — hold still, capturing in {preview_seconds} seconds...")

    import time
    start = time.time()
    frame = None

    while True:
        ret, frame = cap.read()
        if not ret:
            print("ERROR: Could not read frame.")
            break

        # Show countdown on preview window
        elapsed   = time.time() - start
        remaining = max(0, preview_seconds - int(elapsed))
        display   = frame.copy()

        cv2.putText(
            display,
            f"Capturing in {remaining}s — look at camera",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (79, 141, 255),
            2
        )

        # Draw face guide box in center
        h, w = display.shape[:2]
        cx, cy = w // 2, h // 2
        cv2.rectangle(
            display,
            (cx - 100, cy - 130),
            (cx + 100, cy + 130),
            (79, 141, 255),
            2
        )

        cv2.imshow("ThyroSenseX — Face Scan", display)
        cv2.waitKey(1)

        if elapsed >= preview_seconds:
            break

    cap.release()
    cv2.destroyAllWindows()

    if frame is not None:
        print("Face image captured successfully!")
        return frame

    print("ERROR: No frame captured.")
    return None


def save_face_image(image, path="temp_face.jpg"):
    """Save captured face image to disk."""
    if image is not None:
        cv2.imwrite(path, image)
        print(f"Face image saved to {path}")
        return path
    return None