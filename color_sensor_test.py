import machine
import utime
from machine import I2C, Pin

COLOR_SENSOR_I2C_ADDR = 0x10

i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=100000)

def write_command(register, data):
    data_bytes = bytearray([data >> 8, data & 0xFF])
    i2c.writeto_mem(COLOR_SENSOR_I2C_ADDR, register, data_bytes)
    
def read_color_data(register):
    data = i2c.readfrom_mem(COLOR_SENSOR_I2C_ADDR, register, 2)
    return data[0] | (data[1] << 8)

def init_sensor():
    configuration = (0 << 15) | (0 << 14) | (0 << 13)| (1 << 12) | (0 << 11)| (1 << 10) | (0 << 6) | (0 << 5)| (1 << 4) | (0 << 0)
    write_command(0x00, configuration)

def rgb_to_hsv(r, g, b):
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    df = mx-mn
    if mx == mn:
        h = 0
    elif mx == r:
        h = (60 * ((g-b)/df) + 360) % 360
    elif mx == g:
        h = (60 * ((b-r)/df) + 120) % 360
    elif mx == b:
        h = (60 * ((r-g)/df) + 240) % 360
    if mx == 0:
        s = 0
    else:
        s = df / mx
    v = mx
    return h, s, v

def get_color_name_hsv(h, s, v):
    if s < 0.2:
        return 'Gray'
    elif v < 0.2:
        return 'Black'
    elif h < 30 or h >= 330:
        return 'Red'
    elif h < 90:
        return 'Yellow'
    elif h < 150:
        return 'Green'
    elif h < 210:
        return 'Cyan'
    elif h < 270:
        return 'Blue'
    elif h < 330:
        return 'Magenta'
    else:
        return 'Red'
    
def adjust_rgb_with_clear_ir(red, green, blue, clear, ir):
    adjusted_r = red * (clear / (ir + 1))
    adjusted_g = green * (clear / (ir + 1))
    adjusted_b = blue * (clear / (ir + 1))
    
    adjusted_r = min(255, max(0, adjusted_r))
    adjusted_g = min(255, max(0, adjusted_g))
    adjusted_b = min(255, max(0, adjusted_b))
    
    return adjusted_r, adjusted_g, adjusted_b

def main_loop():
    init_sensor()
    devices = i2c.scan()
    print("Connected I²C devices:", hex(devices[0]))
    
    while True:
        clear = read_color_data(0x04)  # Clear
        red = read_color_data(0x05)    # Red
        green = read_color_data(0x06)  # Green
        blue = read_color_data(0x07)   # Blue
        ir = read_color_data(0x08)     # IR

        adjusted_r, adjusted_g, adjusted_b = adjust_rgb_with_clear_ir(red, green, blue, clear, ir)
        
        h, s, v = rgb_to_hsv(adjusted_r, adjusted_g, adjusted_b)
        
        color_name = get_color_name_hsv(h, s, v)
        
        print("Detected color:", color_name)
        utime.sleep(1)  

if __name__ == "__main__":
    main_loop()

