import numpy as np


def read_thermal(simulate=True):
    """
    Reads thermal data from MLX90640 sensor.
    Returns: 24x32 numpy array of temperatures in Celsius.

    On laptop : simulate=True  → generates realistic fake data
    On Pi     : simulate=False → reads real I2C sensor data
    """

    if simulate:
        return _simulate_thermal()
    else:
        return _read_real_sensor()


def _simulate_thermal():
    """
    Generates realistic fake thermal data for laptop testing.
    Simulates a neck thermal scan with slight hotspot.
    """

    print("Simulating thermal data (laptop mode)...")

    # Base neck temperature ~33-36°C
    base_temp = np.random.uniform(33.0, 36.5)

    # Generate 24x32 temperature matrix
    temp_matrix = np.random.normal(
        loc=base_temp,
        scale=0.6,
        size=(24, 32)
    ).astype(np.float32)

    # Add thyroid region hotspot (center of neck)
    hotspot_intensity = np.random.uniform(0.0, 2.0)
    temp_matrix[8:16, 10:22] += hotspot_intensity

    # Add slight left-right asymmetry
    asymmetry = np.random.uniform(-0.5, 0.5)
    temp_matrix[:, :16] += asymmetry

    print(f"Thermal simulation complete ✓")
    print(f"  Mean temp : {np.mean(temp_matrix):.2f} °C")
    print(f"  Max temp  : {np.max(temp_matrix):.2f} °C")
    print(f"  Min temp  : {np.min(temp_matrix):.2f} °C")

    return temp_matrix


def _read_real_sensor():
    """
    Reads real data from MLX90640 via I2C on Raspberry Pi.
    Only runs on Pi — will be activated in Step 9.
    """

    try:
        import board
        import busio
        import adafruit_mlx90640

        i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)
        mlx = adafruit_mlx90640.MLX90640(i2c)
        mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ

        frame = [0] * 768  # 24x32 = 768 pixels
        mlx.getFrame(frame)

        temp_matrix = np.array(frame).reshape((24, 32))
        print("Real thermal data read successfully ✓")
        return temp_matrix

    except Exception as e:
        print(f"ERROR reading thermal sensor: {e}")
        print("Falling back to simulation...")
        return _simulate_thermal()