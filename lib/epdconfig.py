# /*****************************************************************************
# * | File        :	  epdconfig.py
# * | Author      :   Waveshare team
# * | Function    :   Hardware underlying interface
# * | Info        :
# *----------------
# * | This version:   V1.2
# * | Date        :   2022-10-29
# * | Info        :   
# ******************************************************************************
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import os
import logging
import time
from ctypes import CDLL
import spidev
import gpiozero

logger = logging.getLogger(__name__)

class RaspberryPi:
    # Pin definition
    RST_PIN  = 17
    DC_PIN   = 25
    CS_PIN   = 8
    BUSY_PIN = 24
    PWR_PIN  = 18

    def __init__(self):
        self.SPI = None
        self.GPIO_RST_PIN = None
        self.GPIO_DC_PIN = None
        self.GPIO_PWR_PIN = None
        self.GPIO_BUSY_PIN = None
        self.DEV_SPI = None

    def module_init(self, cleanup=False):
        # Initialize GPIO
        self.GPIO_RST_PIN = gpiozero.LED(self.RST_PIN)
        self.GPIO_DC_PIN  = gpiozero.LED(self.DC_PIN)
        self.GPIO_PWR_PIN = gpiozero.LED(self.PWR_PIN)
        self.GPIO_BUSY_PIN = gpiozero.Button(self.BUSY_PIN, pull_up=False)

        self.GPIO_PWR_PIN.on()

        if cleanup:
            find_dirs = [
                os.path.dirname(os.path.realpath(__file__)),
                '/usr/local/lib',
                '/usr/lib',
            ]
            val = int(os.popen('getconf LONG_BIT').read())
            so_filename = ''
            for find_dir in find_dirs:
                if val == 64:
                    so_filename = os.path.join(find_dir, 'DEV_Config_64.so')
                else:
                    so_filename = os.path.join(find_dir, 'DEV_Config_32.so')
                if os.path.exists(so_filename):
                    self.DEV_SPI = CDLL(so_filename)
                    break
            if not self.DEV_SPI:
                raise RuntimeError("Cannot find DEV_Config.so")
            self.DEV_SPI.DEV_Module_Init()
        else:
            self.SPI = spidev.SpiDev()
            self.SPI.open(0, 0)
            self.SPI.max_speed_hz = 4000000
            self.SPI.mode = 0b00

        return 0

    def module_exit(self, cleanup=False):
        logger.debug("Shutting down SPI and GPIO")
        if self.SPI:
            self.SPI.close()

        if self.GPIO_RST_PIN: self.GPIO_RST_PIN.off()
        if self.GPIO_DC_PIN:  self.GPIO_DC_PIN.off()
        if self.GPIO_PWR_PIN: self.GPIO_PWR_PIN.off()

        if cleanup:
            if self.GPIO_RST_PIN: self.GPIO_RST_PIN.close()
            if self.GPIO_DC_PIN:  self.GPIO_DC_PIN.close()
            if self.GPIO_PWR_PIN: self.GPIO_PWR_PIN.close()
            if self.GPIO_BUSY_PIN: self.GPIO_BUSY_PIN.close()

    def digital_write(self, pin, value):
        if pin == self.RST_PIN:
            self.GPIO_RST_PIN.value = value
        elif pin == self.DC_PIN:
            self.GPIO_DC_PIN.value = value
        elif pin == self.PWR_PIN:
            self.GPIO_PWR_PIN.value = value

    def digital_read(self, pin):
        if pin == self.BUSY_PIN:
            return self.GPIO_BUSY_PIN.value
        return 0

    def delay_ms(self, delaytime):
        time.sleep(delaytime / 1000.0)

    def spi_writebyte(self, data):
        if self.SPI:
            self.SPI.writebytes(data)

    def spi_writebyte2(self, data):
        if self.SPI:
            self.SPI.writebytes2(data)

### END OF FILE ###