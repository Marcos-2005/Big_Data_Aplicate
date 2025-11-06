import requests
import time
from datetime import datetime, timedelta

ORION_URLS = {
    "Sensor_Agua_1": "http://localhost:1026/v2/entities/Sensor_Agua_1/attrs",
    "Sensor_Temperatura_1": "http://localhost:1026/v2/entities/Sensor_Temperatura_1/attrs",
    "Sensor_CO2_1": "http://localhost:1026/v2/entities/Sensor_CO2_1/attrs"
}

valores_iniciales = {
    "Sensor_Agua_1": {"temperatura": 20.0, "conductividad": 100.0, "turbidez": 1.0, "bateria": 50.0},
    "Sensor_Temperatura_1": {"temperatura": 18.0, "humedad_relativa": 40.0, "bateria": 60.0},
    "Sensor_CO2_1": {"co2": 400.0, "bateria": 70.0}
}

incrementos = {
    "Sensor_Agua_1": {"temperatura": 0.1, "conductividad": 0.5, "turbidez": 0.05, "bateria": 0.2},
    "Sensor_Temperatura_1": {"temperatura": 0.05, "humedad_relativa": 0.1, "bateria": 0.2},
    "Sensor_CO2_1": {"co2": 1.0, "bateria": 0.2}
}

NUM_ITER = 400   
DELAY = 0.05     

tiempo_actual = datetime.utcnow()

print("\n⏳ Iniciando carga de datos masiva...\n")

for i in range(NUM_ITER):
    for sensor, url in ORION_URLS.items():
        payload = {}

        for attr, valor in valores_iniciales[sensor].items():
            payload[attr] = {"value": valor}
            valores_iniciales[sensor][attr] += incrementos[sensor][attr]

        payload["Tiempo"] = {"value": tiempo_actual.isoformat() + "Z"}

        r = requests.patch(url, json=payload)

        print(f"[{i+1}/{NUM_ITER}] {sensor} -> {r.status_code}")

    tiempo_actual += timedelta(seconds=1)

    time.sleep(DELAY)

print("\n Carga masiva completada correctamente.\n")
