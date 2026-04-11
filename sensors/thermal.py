import numpy as np

def read_thermal(simulate=True):
    """Returns 24x32 numpy array of temperatures."""
    if simulate:
        return _simulate_thermal()
    return _read_real_sensor()

def _simulate_thermal():
    base  = np.random.uniform(33.0, 36.5)
    mat   = np.random.normal(base, 0.6, (24,32)).astype(np.float32)
    mat[8:16, 10:22] += np.random.uniform(0.0, 2.0)
    mat[:, :16]      += np.random.uniform(-0.5, 0.5)
    return mat

def _read_real_sensor():
    # Pi only — real MLX90640 via I2C
    try:
        import board, busio, adafruit_mlx90640
        i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)
        mlx = adafruit_mlx90640.MLX90640(i2c)
        mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ
        frame = [0] * 768
        mlx.getFrame(frame)
        return np.array(frame).reshape((24, 32))
    except Exception as e:
        print(f'Thermal sensor error: {e} — using simulation')
        return _simulate_thermal()