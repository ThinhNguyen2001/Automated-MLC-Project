import network
import socket
import utime
from time import sleep
from machine import Pin, I2C, ADC

ssid = 'simplewifi' #network name
password = '12345678' #Wifi password

ssid = 'SHAW-F06F'
password = 'favor8521appear'

# ssid = 'ece492_test' #network name
# password = 'ETLCE3011xxt' #Wifi password




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
    print('listening on', address)
    return connection

def webpage(num_larvae, state):
    #Template HTML
    html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Raspberry Pi Pico Simple LED</title>

            </head>
            <body>
            <form action="./lighton">
            <input type="submit" value="Light on" />
            </form>
            <form action="./lightoff">
            <input type="submit" value="Light off" />
            </form>
            <p>LED is {state}</p>
            <p>Number of larvae is {num_larvae}</p>
            </body>
            </html>
            """
    return str(html)

def serve(connection):
    #Start a web server
    state = 'OFF'
    led = Pin('LED', Pin.OUT)
    led.value(0)
    larvae_count = 0
    adc = ADC(Pin(26))
#     led = Pin('LED', Pin.OUT)
    while True:
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        start = utime.ticks_ms()
        
        #Photointerruptor function
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
        
        try:
            request = request.split()[1]
        except IndexError:
            pass
        if request == '/lighton?':
            led.value(1)
            larvae_count = larvae_count + 1
            print("Number of larvae detected is: " + str(larvae_count))
            state = 'ON'
        elif request =='/lightoff?':
            led.value(0)
            state = 'OFF'
        num_larvae = str(larvae_count)
        html = webpage(num_larvae, state)
        client.send(html)
        client.close() 
        print('request took ' + str(utime.ticks_ms() - start) + "ms")

####################
try:

    ip = connect()
    connection = open_socket(ip)
    serve(connection)
except KeyboardInterrupt:
    machine.reset()
    
    


