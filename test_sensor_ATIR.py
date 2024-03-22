from machine import Pin, ADC
import time

adc = ADC(Pin(26))

led = Pin('LED', Pin.OUT)
    
print("*****Photointerruptor Running*****")
larvae_count = 0
larvae_detected = False
while True:
    
    voltage = 3.3 * adc.read_u16() / 65535
    #print('Voltage is {:.2f}V'.format(voltage))
    #print("Number of larvae detected is: " + str(larvae_count))
    
    if voltage < 1.0:
        led.value(1)
        larvae_count = larvae_count + 1
        print("Number of larvae detected is: " + str(larvae_count))

            
    else:
        led.value(0)  
        
    time.sleep(0.188)
    
