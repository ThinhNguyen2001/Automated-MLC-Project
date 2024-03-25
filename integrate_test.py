import network
import socket
import utime
from time import sleep
from machine import Pin, I2C, ADC

ssid = 'simplewifi' #network name
password = '12345678' #Wifi password

#ssid = ''
#password = ''


#initialize I2C if necessary

def connect():
    #set Wifi to station interface
    wlan = network.WLAN(network.STA_IF)
    #activate the network interface
    wlan.active(True)
    #connect to Wifi network
    wlan.connect(ssid, password)

    #wait for connection 
    max_wait = 10
    while max_wait > 0:
        # 0   STAT_IDLE -- no connection and no activity
        # 1   STAT_CONNECTING -- connecting in progress
        # -3  STAT_WRONG_PASSWORD -- failed to connect due to incorrect password
        # -2  STAT_NO_AP_FOUND -- failed since no access point replied
        # -1  STAT_CONNECT_FAIL -- failed due to other prob
        # 3   STAT_GOT_IP -- connection successful
        if wlan.status() < 0 or wlan.status() >= 3:
            # connection successful
            break
        max_wait -= 1
        print('waiting for connection... ' + str(max_wait))
        utime.sleep(1)

    # check connection
    if wlan.status() != 3:
        # No connection
        raise RuntimeError('network connection failed')
    else:
        # connection successful
        print('wlan connected')
        status = wlan.ifconfig()
        ip = status[0]
        print('IP address = ' + status[0])
        print('subnet mask = ' + status[1])
        print('gateway  = ' + status[2])
        print('DNS server = ' + status[3])
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
                <meta http-equiv="refresh" content="5">
            </head>
            <body>
            <p>Click the buttons to control the system</p>
            <input type="button" onclick="document.location='/syson'" value="ON"/>
            <p></p>
            <input type="button" onclick="document.location='/sysoff'" value="OFF"/>
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
    larvae_count = 0
    adc = ADC(Pin(26))
    led = Pin('LED', Pin.OUT)
    while True:
        #inner main loop    
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
                
            sleep(0.001)
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
    
    
