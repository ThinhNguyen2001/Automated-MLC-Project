import network
import socket
import utime
import _thread
from machine import Pin, ADC
import time

# ssid = 'simplewifi'  # Network name
# password = '12345678'  # Wifi password

ssid = 'ece492_test' #network name
password = 'ETLCE3011xxt' #Wifi password

# ssid = 'SHAW-F06F'
# password = 'favor8521appear'

# Initialize I2C if necessary

def connect():
    # Set Wifi to station interface
    wlan = network.WLAN(network.STA_IF)
    # Activate the network interface
    wlan.active(True)
    # Connect to Wifi network
    wlan.connect(ssid, password)

    # Wait for connection
    max_wait = 10
    while max_wait > 0:
        if wlan.isconnected():
            # Connection successful
            break
        max_wait -= 1
        print('waiting for connection... ' + str(max_wait))
        utime.sleep(1)

    # Check connection
    if not wlan.isconnected():
        # No connection
        raise RuntimeError('network connection failed')
    else:
        # Connection successful
        print('wlan connected')
        status = wlan.ifconfig()
        ip = status[0]
        print('IP address = ' + status[0])
        print('subnet mask = ' + status[1])
        print('gateway  = ' + status[2])
        print('DNS server = ' + status[3])
        return ip

def open_socket(ip):
    # Open a socket
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    print('listening on', address)
    return connection

def webpage(reading):
    # Template HTML
    html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Raspberry Pi Pico Simple LED</title>
                <meta http-equiv="refresh" content="1"/> 
            </head>
            <body>
            <p>Click the buttons to control the system</p>
            <input type="button" onclick="document.location='syson'" value="ON"/>
            <p></p>
            <input type="button" onclick="document.location='sysoff'" value="OFF"/>
            <p></p>
            <p>Number of larvae is {reading}</p>
            <p>{reading}</p>
            </body>
            </html>
            """
    return str(html)

lock = _thread.allocate_lock()

def detect_sensor():
    global i
    global larvae_count
    
    while True:
        with lock:  # 获取锁
            i += 1
#         print(f"\rThis is the {i} cycle in detect......")
        led.on()
        time.sleep(0.188)
        led.off()
        
        voltage = 3.3 * adc.read_u16() / 65535
        if voltage < 1.0:
            with lock:  # 在更改i之前获取锁
                larvae_count += 1
            led2.value(1)
            print("Number of larvae detected is: " + str(larvae_count))
        else:
            led2.value(0)
            
        time.sleep(0.188)

        

def serve_webpage():
    global i
    global larvae_count
    last_served_i = -1  # 记录上一次服务的i值
    
    while True:
        with lock:  # 获取锁来读取i的当前值
            current_i = i
        if current_i != last_served_i:
#             print(f"\rTh89is is the {current_i} cycle......")
            reading = str(larvae_count)
            client = connection.accept()[0]
            request = client.recv(1024)
            html = webpage(reading)
            client.send(html)
            client.close()
            last_served_i = current_i  # 更新已服务的i值
        time.sleep(1)  # 稍作延时，减轻CPU负担
   

####################
try:
   
    ip = connect()
    connection = open_socket(ip)

    # Initialize variables
    larvae_count = 0
    i = 0
    adc = ADC(Pin(26))
    led = Pin('LED', Pin.OUT)
    led2 = Pin('GP16', Pin.OUT)

    # Start web server on core 0
    _thread.start_new_thread(serve_webpage, ())
#     _thread.start_new_thread(serve_webpage, ())
    detect_sensor()
           

except KeyboardInterrupt:
    machine.reset()
