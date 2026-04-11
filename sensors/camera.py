import cv2, time, numpy as np

def capture_face_image(preview_seconds=3):
    """Opens webcam, shows preview, captures frame."""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return None
    start, frame = time.time(), None
    while True:
        ret, frame = cap.read()
        if not ret: break
        elapsed   = time.time() - start
        remaining = max(0, preview_seconds - int(elapsed))
        display   = frame.copy()
        cv2.putText(display,
            f'Capturing in {remaining}s — look at camera',
            (20, 40), cv2.FONT_HERSHEY_SIMPLEX,
            0.7, (79, 141, 255), 2)
        h, w = display.shape[:2]
        cx, cy = w//2, h//2
        cv2.rectangle(display,
            (cx-100, cy-130), (cx+100, cy+130),
            (79, 141, 255), 2)
        cv2.imshow('ThyroSenseX — Face Scan', display)
        cv2.waitKey(1)
        if elapsed >= preview_seconds: break
    cap.release()
    cv2.destroyAllWindows()
    return frame
