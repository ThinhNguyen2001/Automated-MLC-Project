import machine
import utime

# I2C address of the Color 10 Click
COLOR_SENSOR_I2C_ADDR = 0x43

# Register addresses for color data
COLOR_DATA_RED = 0x50
COLOR_DATA_GREEN = 0x51
COLOR_DATA_BLUE = 0x52
COLOR_DATA_CLEAR = 0x53

# Initialize I2C
i2c = machine.I2C(0, scl=machine.Pin(9), sda=machine.Pin(8), freq=100000)

# Function to read 2 bytes from a register and combine them into a single value
def read_color_data(register):
    data = i2c.readfrom_mem(COLOR_SENSOR_I2C_ADDR, register, 2)
    return data[0] | (data[1] << 8)

while True:
    # Read color data
    red = read_color_data(COLOR_DATA_RED)
    green = read_color_data(COLOR_DATA_GREEN)
    blue = read_color_data(COLOR_DATA_BLUE)
    clear = read_color_data(COLOR_DATA_CLEAR)

    # Print color values
    print("Red: {}, Green: {}, Blue: {}, Clear: {}".format(red, green, blue, clear))

    utime.sleep_ms(1000)  # Delay for 1 second
