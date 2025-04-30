import time
from gpiosManagerRaspberry import GpiosManager
try:
    gpios = GpiosManager()

    while True:
        if gpios.ReadSensor():
            print("Sensor1 activado")
        else:
            print("Sensor1 desactivado")
        if gpios.ReadSensor45():
            print("Sensor2 activado")
        else:
            print("Sensor2 desactivado")
        time.sleep(0.5)
except KeyboardInterrupt:
    print("\n🛑 Interrumpido por el usuario.")
finally:
    pass
