# Import required modules
#define BLYNK_TEMPLATE_ID "TMPL23-29bHyA"
# define BLYNK_TEMPLATE_NAME "IOT"

import network
from machine import Pin, PWM, SoftI2C
import BlynkLib
import uasyncio as asyncio
import time
from lcd_api import LcdApi
from i2c_lcd import I2cLcd

# Connect to Wi-Fi network
wifi_ssid = "Mi 10"
wifi_password = "Diego15122001"

sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect(wifi_ssid, wifi_password)

while not sta_if.isconnected():
    pass

print("Wi-Fi connected:", sta_if.ifconfig())

# Connect to Blynk server
auth_token = "_QD1n6H6Dr5CSuehtobiz69VCfRx1a6T"

blynk = BlynkLib.Blynk(auth_token)

# Define pin numbers
led_pin = 13
# Initialize LED pin
led = Pin(led_pin, Pin.OUT)

#LCD
I2C_ADDR = 0x27 #the address of your LCD I2C device
#in our case, we are using a LDC 20x2
totalRows = 4 
totalColumns = 20


#initialize the SoftI2C method for ESP32 by giving it three arguments.
i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=10000)

#This line is used to initialize the I2C connection for the library by creating an 'lcd' object.
lcd = I2cLcd(i2c, I2C_ADDR, totalRows, totalColumns)


# Sensor pins
s1 = Pin(27, Pin.IN, Pin.PULL_DOWN)  # Sensor 1
s2 = Pin(35, Pin.IN, Pin.PULL_DOWN)  # Sensor 2
s3 = Pin(36, Pin.IN, Pin.PULL_DOWN)  # Sensor 3 - ALTO
s4 = Pin(39, Pin.IN, Pin.PULL_DOWN)  # Sensor 4 - BAJO

# Motor pins
frequency = 240 
duty = 600
duty2 = 600

motorA = PWM(Pin(18, Pin.OUT, Pin.PULL_DOWN), frequency)  # Banda
motorB = PWM(Pin(19, Pin.OUT, Pin.PULL_DOWN), frequency)  # Banda
motorC = PWM(Pin(25, Pin.OUT, Pin.PULL_DOWN), frequency)  # Trocleadora
motorD = PWM(Pin(26, Pin.OUT, Pin.PULL_DOWN), frequency)  # Trocleadora

def motor(on, off):
    motorA.duty(on)
    motorB.duty(off)

def motor_2(on, off):
    motorC.duty(on)
    motorD.duty(off)

async def trocleadora(s3, s4):
    contador = 0
    while contador < 20:
        #Sensor 1 - ALTO
        right_value = s3.value()  # Obtener el valor del sensor derecho IR (0 o 1)
        await asyncio.sleep_ms(100)
        if right_value == 1:
            motor_2(duty2, 0)
            contador += 1
            if contador == 20:
                motor_2(0,duty)
                await asyncio.sleep_ms(500)
                motor_2(0,0)
            

        # Sensor 2 - BAJO
        left_value = s4.value()  # Obtener el valor del sensor izquierdo IR (0 o 1)
        await asyncio.sleep_ms(100)
        if left_value == 1:
            motor_2(0, duty2)
            contador += 1
            if contador == 20:
                motor_2(duty,0)
                await asyncio.sleep_ms(500)
                motor_2(0,0)
            
    await asyncio.sleep_ms(100)  # Esperar 100 milisegundos

async def banda(s1, s2):
    activo = True  # Variable bandera para controlar el bucle while True
    right_value = s1.value()
    while activo:  # Mientras la bandera esté activa
        right_value = s1.value()
        
        if right_value == 1:
            motor(0, 0)
            print(s1.value())
        else:
            while right_value == 0:
                motor(duty, 0)
                print(s1.value())
                left_value = s2.value()
                
                if left_value == 0:
                    print(s2.value())
                    await asyncio.sleep_ms(1250)
                    motor(0, 0)  # Detener la banda transportadora
                    activo = False  # Desactivar la bandera para salir del bucle while True
                    break
                
        await asyncio.sleep_ms(100)
        #break  # Romper el ciclo después de esperar 100 ms

async def banda2(s1):
    activo = True  # Variable bandera para controlar el bucle while True
    right_value = s1.value()
    while activo:        
        motor(0,duty)
        right_value = s1.value()
        if right_value == 0:
            await asyncio.sleep_ms(1250)
            motor(0, 0)
            activo = False  # Desactivar la bandera para salir del bucle while True
            break

async def troceladora_p(s3,s4):
    activo2 = True
    while activo2:
        motor(0,0)
        left_value = s4.value()
        await asyncio.sleep_ms(100)
        if left_value == 1:
            motor_2(0, duty)
            right_value = s3.value()
            await asyncio.sleep_ms(100)
            if right_value == 1:
                motor_2(0, 0)
                activo2 = False 
                break
        right_value = s3.value()
        if right_value == 1:
            motor_2(0, 0)
            activo2 = False 
            break
        
        else:
            break

# Define Blynk virtual pin handlers
@blynk.on("V0")
def v0_handler(value):
    lcd.clear() #Erase all characters or anything written on the screen
    lcd.move_to(0,0) #Move to position based on row and col values
    lcd.putstr("MECATRONICA-SENA") # Send a string of characters to the screen
    lcd.move_to(0,1) #Move to position based on row and col values
    lcd.putstr("FICHA-2449131") # Send a string of characters to the screen
    if int(value[0]) == 1:
        async def run_tasks():
            lcd.clear() #Erase all characters or anything written on the screen
            lcd.move_to(0,0) #Move to position based on row and col values
            lcd.putstr("BANDA TRANSPORTADORA") # Send a string of characters to the screen
            lcd.move_to(0,1) 
            lcd.putstr("EN FUNCIONAMIENTO")
            time.sleep(0.5) #time to show
            await banda(s1,s2)
            lcd.clear() #Erase all characters or anything written on the screen
            lcd.move_to(0,0) #Move to position based on row and col values
            lcd.putstr("TROQUELADORA") # Send a string of characters to the screen
            lcd.move_to(0,1) 
            lcd.putstr("EN FUNCIONAMIENTO")
            time.sleep(0.5) #time to show
            await trocleadora(s3,s4)
            lcd.clear() #Erase all characters or anything written on the screen
            lcd.move_to(0,0) #Move to position based on row and col values
            lcd.putstr("CONTROL CALIDAD") # Send a string of characters to the screen
            lcd.move_to(0,1) 
            lcd.putstr("EN FUNCIONAMIENTO")
            await banda2(s1)
        loop = asyncio.get_event_loop()
        loop.create_task(run_tasks())
        loop.run_forever()
    else:
        led.value(0)


# Start Blynk loop
while True:
    blynk.run()