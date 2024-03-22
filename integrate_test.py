import network
import socket
from time import sleep
from machine import Pin, I2C, ADC

ssid = 'simplewifi' #network name
password = '12345678' #Wifi password

ssid = 'SHAW-F06F'
password = 'favor8521appear'


#initialize I2C if necessary

def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection')
        sleep(1)
        
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    return ip

def open_socket(ip):
    #open a socket
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    return connection

def webpage(reading):
    #Template HTML
    html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Raspberry Pi Pico Simple LED</title>
                <meta http-equiv="refresh" content="10">
            </head>
            <body>
            <p>Click the buttons to control the system</p>
            <input type="button" onclick="document.location='/ledon'" value="TURN LED ON"/>
            <p></p>
            <input type="button" onclick="document.location='/ledoff'" value="TURN LED OFF"/>
            <p></p>
            <p>Number of larvae is {reading}</p>
            <p>{reading}</p>
            </body>
            </html>
            """
    return str(html)

def serve(connection):
    #Start a web server
    print("Start a web server")
    while True:
        adc = ADC(Pin(26))

        led = Pin('LED', Pin.OUT)
            
        print("*****Photointerruptor Running*****")
        larvae_count = 0
        larvae_detected = False
        switch = True
        while switch:
            
            voltage = 3.3 * adc.read_u16() / 65535
            #print('Voltage is {:.2f}V'.format(voltage))
            #print("Number of larvae detected is: " + str(larvae_count))
            
            if voltage < 1.0:
                led.value(1)
                larvae_count = larvae_count + 1
                print("Number of larvae detected is: " + str(larvae_count))
                switch = False

                    
            else:
                led.value(0)  
                
            sleep(0.2)
        reading = str(larvae_count)
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        html = webpage(reading)
        client.send(html)
        client.close()    


####################
try:
    
    ip = connect()
    connection = open_socket(ip)
    serve(connection)
except KeyboardInterrupt:
    machine.reset()
    
    