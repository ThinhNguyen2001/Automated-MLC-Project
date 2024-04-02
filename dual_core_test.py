import network
import socket
import utime
import _thread
from machine import Pin, ADC

ssid = 'simplewifi'  # Network name
password = '12345678'  # Wifi password

ssid = 'SHAW-F06F'
password = 'favor8521appear'

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

def serve_webpage():
    global larvae_count, connection
    while True:
        reading = str(larvae_count)
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        html = webpage(reading)
        client.send(html)
        client.close()

def detect_sensor():
    global larvae_count, adc, led
    while True:
        voltage = 3.3 * adc.read_u16() / 65535
        if voltage < 1.0:
            led.value(1)
            larvae_count += 1
            print("Number of larvae detected is: " + str(larvae_count))
        else:
            led.value(0)

####################
try:
    ip = connect()
    connection = open_socket(ip)

    # Initialize variables
    larvae_count = 0
    adc = ADC(Pin(26))
    led = Pin('LED', Pin.OUT)

    # Start web server on core 0
    _thread.start_new_thread(serve_webpage, ())
    detect_sensor()
    # Start sensor detection on core 1
#     _thread.start_new_thread(detect_sensor, ())

    while True:
        pass

except KeyboardInterrupt:
    machine.reset()
