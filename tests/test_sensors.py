import sys
sys.path.append(".")

from sensors.camera     import capture_face_image
from sensors.microphone import record_voice
from sensors.thermal    import read_thermal


def test_camera():
    print("\n── Testing Camera ──────────────────")
    image = capture_face_image(preview_seconds=3)
    if image is not None:
        print(f"✓ Image shape: {image.shape}")
    else:
        print("✗ Camera test failed")
    return image


def test_microphone():
    print("\n── Testing Microphone ──────────────")
    path = record_voice(duration=4)
    if path:
        print(f"✓ Audio saved: {path}")
    else:
        print("✗ Microphone test failed")
    return path


def test_thermal():
    print("\n── Testing Thermal ─────────────────")
    matrix = read_thermal(simulate=True)
    if matrix is not None:
        print(f"✓ Thermal matrix shape: {matrix.shape}")
    else:
        print("✗ Thermal test failed")
    return matrix


if __name__ == "__main__":
    print("═══ ThyroSenseX Sensor Tests ═══")

    img    = test_camera()
    audio  = test_microphone()
    thermal = test_thermal()

    print("\n═══ Results ═══")
    print(f"Camera    : {'✓ PASS' if img     is not None else '✗ FAIL'}")
    print(f"Microphone: {'✓ PASS' if audio   is not None else '✗ FAIL'}")
    print(f"Thermal   : {'✓ PASS' if thermal is not None else '✗ FAIL'}")