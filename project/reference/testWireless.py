#Reference from RPPW Wireless Weather Station by ExplainingComputers

import network
import socket
from time import sleep
from machine import Pin, I2C

ssid = 'xxxxxx' #network name
password = 'xxxx' #Wifi password

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
            <title>Pico W </title>
            <meta http-equiv="refresh" content="10">
            </head>
            <body>
            <p>{reading}</p>
            </body>
            </html>
            """
    return str(html)

def serve(connection):
    #Start a web server
    while True:
        reading = 'Hello'
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        html = webpage(reading)
        client.send(html)
        client.close()
        
try:
    ip = connect()
    connection = open_socket(ip)
    serve(connection)
except KeyboardInterrupt:
    machine.reset()
    
    
    
    
    
    
    
    
    