import time
import smbus
  
class Lcd:
  # Define some device parameters
  _I2C_ADDR  = 0x27 # I2C device address
  _WIDTH = 16   # Maximum characters per line
  
  # Define some device constants
  _CHR = 1 # Mode - Sending data
  _CMD = 0 # Mode - Sending command
  
  LINE_1 = 0x80 # LCD RAM address for the 1st line
  LINE_2 = 0xC0 # LCD RAM address for the 2nd line
  
  _BACKLIGHT_ON  = 0x08
  _BACKLIGHT_OFF = 0x00
  
  _ENABLE = 0b00000100 # Enable bit
  
  # Timing constants
  _E_PULSE = 0.0005
  _E_DELAY = 0.0005
  
  #Open I2C interface
  #_bus = smbus.SMBus(0)  # Rev 1 Pi uses 0
  _bus = smbus.SMBus(1) # Rev 2 Pi uses 1
  
  def __init__(self):
    # Initialise display
    self._backlight = self._BACKLIGHT_ON
    self._initialize()

  def __del__(self):
    self._backlight = self._BACKLIGHT_OFF
    self._initialize()
  
  def _initialize(self):
    self._byte(0x33, self._CMD) # 110011 Initialise
    self._byte(0x32, self._CMD) # 110010 Initialise
    self._byte(0x06, self._CMD) # 000110 Cursor move direction
    self._byte(0x0C, self._CMD) # 001100 Display On,Cursor Off, Blink Off 
    self._byte(0x28, self._CMD) # 101000 Data length, number of lines, font size
    self._byte(0x01, self._CMD) # 000001 Clear display
    time.sleep(self._E_DELAY)

  def _byte(self, bits, mode):
    # Send byte to data pins
    # bits = the data
    # mode = 1 for data
    #        0 for command
  
    bits_high = mode | (bits & 0xF0) | self._backlight
    bits_low = mode | ((bits<<4) & 0xF0) | self._backlight
  
    # High bits
    self._bus.write_byte(self._I2C_ADDR, bits_high)
    self._toggle_enable(bits_high)
  
    # Low bits
    self._bus.write_byte(self._I2C_ADDR, bits_low)
    self._toggle_enable(bits_low)
  
  def _toggle_enable(self, bits):
    # Toggle enable
    time.sleep(self._E_DELAY)
    self._bus.write_byte(self._I2C_ADDR, (bits | self._ENABLE))
    time.sleep(self._E_PULSE)
    self._bus.write_byte(self._I2C_ADDR,(bits & ~self._ENABLE))
    time.sleep(self._E_DELAY)
  
  def string(self, message, line):
    # Send string to display
    message = message.ljust(self._WIDTH, ' ')
    self._byte(line, self._CMD)
    for i in range(self._WIDTH):
      self._byte(ord(message[i]), self._CHR)
  
def main():
  while True:
    lcd.string('LCD Control Test',lcd.LINE_1)
    lcd.string('1234567890123456',lcd.LINE_2)
  
    time.sleep(10)
  
if __name__ == '__main__':
  try:
    print('Initialise display')
    lcd = Lcd()
    print('main')
    main()
  except KeyboardInterrupt:
    pass
  finally:
    print('Terminate display')
    del lcd
