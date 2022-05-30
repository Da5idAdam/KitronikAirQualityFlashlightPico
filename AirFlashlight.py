from PicoAirQuality import KitronikBME688, KitronikOLED, KitronikZIPLEDs, KitronikButton
from time import sleep_ms
from machine import Timer
import time

bme688 = KitronikBME688()
oled = KitronikOLED()
#buzzer = KitronikBuzzer()
zipleds = KitronikZIPLEDs(3)
buttons = KitronikButton()

RED = (255, 0, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)

flashlightState = 0

def checkButtonA(callBackParam):
    global buttonAState
    global flashlightState
    buttonAState = buttonAState <<1 | buttons.buttonA.value() |0xE000
    buttonAState &=0xFFFF
    if(buttonAState == 0xEFFF):
        flashlightState += 1
        if(flashlightState > 2):
            flashlightState = 0
#            print("A: " + str(flashlightState))

def checkButtonB(callBackParam):
    global buttonBState
    global flashlightState
    buttonBState = buttonBState <<1 | buttons.buttonB.value() |0xE000
    buttonBState &=0xFFFF
    if(buttonBState == 0xEFFF):
        flashlightState = 0
#        print("B: " + str(flashlightState))
    
debounceTimerA = Timer()
debounceTimerA.init(period=2, mode=Timer.PERIODIC, callback=checkButtonA)
debounceTimerB = Timer()
debounceTimerB.init(period=2, mode=Timer.PERIODIC, callback=checkButtonB)

buttonAState = 0
buttonBState = 0

def dangerLeds(eCO2Level):
    flashLength = 1
    
    if(eCO2Level >= 400 and eCO2Level < 599):
        zipleds.setLED(0, GREEN)
        flashLength = 33
        
    if(eCO2Level >= 599 and eCO2Level < 999):
        zipleds.setLED(0, YELLOW)
        zipleds.setLED(1, YELLOW)
        flashLength = 66
        
    if(eCO2Level >= 999 and eCO2Level < 2499):
       zipleds.setLED(0, ORANGE)
       zipleds.setLED(1, ORANGE)
       zipleds.setLED(2, ORANGE)
       flashLength = 132
       
    if(eCO2Level >= 2499 and eCO2Level < 2999):
        zipleds.setLED(0, RED)
        zipleds.setLED(1, ORANGE)
        zipleds.setLED(2, ORANGE)
        flashlength = 264
        
    if(eCO2Level >= 2999 and eCO2Level < 3499):
        zipleds.setLED(0, RED)
        zipleds.setLED(1, RED)
        zipleds.setLED(2, ORANGE)
        flashlength = 528
       
    if(eCO2Level >= 3499):
        zipleds.setLED(0, RED)
        zipleds.setLED(1, RED)
        zipleds.setLED(2, RED)
        flashLength = 1056
        
    zipleds.show()
    sleep_ms(flashLength)
    
    for i in range (0, 3):
        zipleds.clear(i)
    zipleds.show()
    

bme688.setupGasSensor()
bme688.calcBaselines()

while True:
    if(flashlightState == 0):
#        print(str(flashlightState))
#        for i in range (0, 3):
#            zipleds.clear(i)
        
        bme688.measureData()
        oled.clear()
    
        oled.drawRect(1, 1, 126, 40, fill=False)
        oled.drawLine(3, 47, 124, 47)
        oled.drawLine(3, 48, 124, 48)
    
        eCO2Level = bme688.readeCO2()
        oled.displayText("CO2: " + str(eCO2Level) + " ppm", 2, 13)
        oled.displayText(str(bme688.readPressure()/100) + " hPa", 3, 18)
        oled.displayText(str(bme688.getAirQualityPercent()) + "%", 6, 100)
        oled.displayText(str(bme688.readHumidity()) + "%", 6, 1)
        oled.displayText(str(bme688.readTemperature()) + "C", 6, 40)
    
        oled.show()
        dangerLeds(eCO2Level)
        sleep_ms(2500)
    
    if(flashlightState != 0):    
        if(flashlightState == 1):
            oled.clear()
#            oled.drawRect(1, 1, 63, 67, fill=True)
            oled.show()
            for i in range (0, 3):
                zipleds.setLED(i, RED)
            
        if(flashlightState == 2):
            oled.clear()
            oled.drawRect(1, 1, 127, 67, fill=True)
            oled.show()
            for i in range (0, 3):
                zipleds.setLED(i, WHITE)
            
        zipleds.show()
    