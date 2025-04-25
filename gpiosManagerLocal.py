
import time
import random
class GpiosManager():
    def __init__(self):
        super().__init__()
        #pines de salidas
        self.cerradura1 = 6
        self.actuador_up = 26
        self.actuador_down = 18
        self.semaforo = 23
        self.validador = 24
        self.electroiman = 25
        self.pulsante_1 = 8
        self.pin_libre3 = 7
        # pines de entradas
        self.sensor_45 = 5
        self.sensor = 22


        
    def turnstileOpen(self):
        return "puerta general abierta" 
    def turnstileBlock(self):
        return "puerta general bloqueada" 
    
    def testLock(self):
        time.sleep(2)
        return 'Cerradura 1 testeada con exito'
    def testArrow(self):
        return 'Luz Led testeada con exito'
    

    def specialDoorOpen(self): 
        return "Puerta especial Abierta"
    
    def specialDoorClose(self):
        return "Puerta Especial Cerrada"
    
    def specialDoorOff(self):
        return "sistema silla de ruedas"
    
    def rebootButton(self):
        return bool(random.randint(0,1))

    def ReadSensor(self):
        return bool(random.randint(0,1))
    def ReadSensor45(self):
        return bool(random.randint(0,1))


    def validador_on(self):
        return bool(random.randint(0,1))
    
    def validador_off(self):
        return bool(random.randint(0,1))

    def restart_validator(self):
        bool(random.randint(0,1))
        time.sleep(5)
        return bool(random.randint(0,1))
    

    def doorOpen(self):
        return "puerta general abierta" 
    
    def doorClose(self):
        return "puerta general cerrada"
