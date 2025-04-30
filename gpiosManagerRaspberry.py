import os
from gpiozero import Device
from gpiozero import DigitalOutputDevice, DigitalInputDevice
from dotenv import load_dotenv

load_dotenv()

# Detecta entorno desde .env
ENV = os.getenv("TARGET", "PI3")

if ENV == "PI5":
    try:
        from gpiozero.pins.lgpio import LGPIOFactory
        Device.pin_factory = LGPIOFactory()
        print("Usando LGPIOFactory (Raspberry Pi 5)")
    except Exception as e:
        from gpiozero.pins.pigpio import PiGPIOFactory
        Device.pin_factory = PiGPIOFactory()
        print("Fallo LGPIO, usando PiGPIOFactory como respaldo:", e)
else:
    from gpiozero.pins.rpigpio import RPiGPIOFactory
    Device.pin_factory = RPiGPIOFactory()
    print("Usando RPiGPIOFactory (Raspberry Pi 3)")

import time


class GpiosManager():
    def __init__(self):
        # Pines de salida
        self.rightLock = DigitalOutputDevice(6)
        self.leftLock = DigitalOutputDevice(13)
        self.electromagnet = DigitalOutputDevice(24)
        self.arrowLight = DigitalOutputDevice(26)

        # Pines de entrada
        self.sensor = DigitalInputDevice(22, pull_up=True)
        #estado inicial de pines
        self.lock_right.on()
        self.lock_left.on()
        self.electroiman.on()
        self.electromagnet.on()

    def test_all_locks(self):
        self.rightLock.off()
        self.leftLock.off()
        time.sleep(1)
        self.rightLock.on()
        self.leftLock.on()


    def left_lock_open(self):
        self.leftLock.off()
        self.arrowLight.off()
        return "Cerradura Izquierda abierta"

    def left_lock_close(self):
        self.leftLock.on()
        self.arrowLight.on()
        return "Cerradura Izquierda bloqueada"
    
    def rigth_lock_open(self):
        self.rightLock.off()
        self.arrowLight.off()
        return "Cerradura Derecha abierta"

    def rigth_lock_close(self):
        self.rightLock.on()
        self.arrowLight.on()
        return "Cerradura Derecha bloqueada"

    def test_right_lock(self):
        self.rightLock.off()
        time.sleep(1)
        self.rightLock.on()
        return 'Cerradura Derecha testeada con exito'
    
    def test_left_lock(self):
        self.rightLock.off()
        time.sleep(1)
        self.rightLock.on()
        return 'Cerradura Derecha testeada con exito'

    def test_arrow(self):
        self.semaforo.off()
        time.sleep(1)
        self.semaforo.on()
        return 'Luz Led testeada con exito'

    def special_door_open(self):
        self.electromagnet.off()
        self.arrowLight.off()
        return "Puerta especial Abierta"

    def special_door_close(self):
        self.electromagnet.on()
        self.arrowLight.on()
        return "Puerta Especial Cerrada"
    
    def read_sensor(self):
        return self.sensor.value == 0


