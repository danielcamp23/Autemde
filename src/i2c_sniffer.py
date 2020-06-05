import RPi.GPIO as GPIO
import pigpio

class I2CSniffer:
    def __init__(self, SDA, SCL, read_cb):
        self.gpio_sda = SDA
        self.gpio_scl = SCL
        
        self.gSCL = SCL
        self.gSDA = SDA
        
        self.finish = read_cb
        self.FALLING = 0
        self.RISING = 1
        self.STEADY = 2
        
        self.in_data = False
        self.byte = 0
        self.bit = 0
        self.oldSCL = 1
        self.oldSDA = 1
        
        self.transact = ""
        
    def sniff(self):
        self.pi = pigpio.pi()
        self.pi.set_mode(self.gpio_scl, pigpio.INPUT)
        self.pi.set_mode(self.gpio_sda, pigpio.INPUT)
        self.cbA = self.pi.callback(self.gpio_scl, pigpio.EITHER_EDGE, self._cb)
        self.cbB = self.pi.callback(self.gpio_sda, pigpio.EITHER_EDGE, self._cb)
        
    def stop(self):
        self.cbA.cancel()
        self.cbB.cancel()
        self.pi.stop()

    def _parse(self, SCL, SDA):
        if SCL != self.oldSCL:
            self.oldSCL = SCL
            if SCL:
                xSCL = self.RISING
            else:
                xSCL = self.FALLING
        else:
            xSCL = self.STEADY

        if SDA != self.oldSDA:
             self.oldSDA = SDA
             if SDA:
                xSDA = self.RISING
             else:
                xSDA = self.FALLING
        else:
            xSDA = self.STEADY

        if xSCL == self.RISING:
            if self.in_data:
                if self.bit < 8:
                    self.byte = (self.byte << 1) | SDA
                    self.bit += 1
                else:
                    self.transact += '{:02X}'.format(self.byte)
                    if SDA:
                        self.transact += '-'
                    else:
                        self.transact += '+'
                    self.bit = 0
                    self.byte = 0

        elif xSCL == self.STEADY:
            if xSDA == self.RISING:
                if SCL:
                    self.in_data = False
                    self.byte = 0
                    self.bit = 0
                    self.transact += ']' # STOP
                    #print (self.transact)
                    self.finish(self.transact)
                    self.transact = ""

            if xSDA == self.FALLING:
                if SCL:
                    self.in_data = True
                    self.byte = 0
                    self.bit = 0
                    self.transact += '[' # START

    def _cb(self, gpio, level, tick):
        """
          Check which line has altered state (ignoring watchdogs) and
          call the parser with the new state.
        """
        SCL = self.oldSCL
        SDA = self.oldSDA

        if gpio == self.gSCL:
            if level == 0:
                SCL = 0
            elif level == 1:
                SCL = 1

        if gpio == self.gSDA:
            if level == 0:
                SDA = 0
            elif level == 1:
                SDA = 1

        self._parse(SCL, SDA)

    def cancel(self):
        """Cancel the I2C callbacks."""
        self.cbA.cancel()
        self.cbB.cancel()
