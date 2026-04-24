from api.client import get_sensor_data

data = get_sensor_data()

print("API Response:", data)

if data is None:
    print("❌ API NOT CONNECTED")