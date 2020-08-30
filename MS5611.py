# !/usr/bin/python3
# -*- coding:utf-8 -*-


## Usage:
##
## sensor = MS5611()
## sensor.setElevationFt(1420)
## sensor.read()
## sensor.printResults()
##
## Alternatively all the values can be passed into the initialize function
## sensor = MS5611(0,   0x76, 432.8    )
##                 bus, i2c,  elevation
## sensor.read()
## sensor.printResults()


import time
import math
from smbus import SMBus

class MS5611:
    '''
    Driver for reading temperature/pressure MS5611 Pressure Sensor.
    @params bus: can be set as 0 or 1 in rasberry3B+,
                 0 means port SDA.0 while 1 means port SDA.1 in pi
    @params i2c: the address of i2c, i2c is 0x77 when CSB<-->GND, 0x76 when CSB<-->3V3
    @params elevation: height
    '''
    def __init__(self, bus = 1, i2c = 0x77, elevation = 0):
        self.bus = SMBus(bus)
        self.i2c = i2c
        self.elevation = elevation

    def read(self):
        ## Get raw pressure
        self.bus.write_byte(self.i2c, 0x48)
        time.sleep(0.05)

        D1 = self.bus.read_i2c_block_data(self.i2c, 0x00)
        D1 = D1[0] * 65536 + D1[1] * 256.0 + D1[2]
        time.sleep(0.05)

        ## Get raw temperature
        self.bus.write_byte(self.i2c, 0x58)
        time.sleep(0.05)
        D2 = self.bus.read_i2c_block_data(self.i2c, 0x00)
        D2 = D2[0] * 65536 + D2[1] * 256.0 + D2[2]
        time.sleep(0.05)

        
        ## Read Constants from Sensor
        if hasattr(self, 'C1'):
            C1 = self.C1
        else:
            C1 = self.bus.read_i2c_block_data(self.i2c, 0xA2) #Pressure Sensitivity
            C1 = C1[0] * 256.0 + C1[1]
            self.C1 = C1
            time.sleep(0.05)

        if hasattr(self, 'C2'):
            C2 = self.C2
        else:
            C2 = self.bus.read_i2c_block_data(self.i2c, 0xA4) #Pressure Offset
            C2 = C2[0] * 256.0 + C2[1]
            self.C2 = C2
            time.sleep(0.05)

        if hasattr(self, 'C3'):
            C3 = self.C3
        else:
            C3 = self.bus.read_i2c_block_data(self.i2c, 0xA6) #Temperature coefficient of pressure sensitivity
            C3 = C3[0] * 256.0 + C3[1]
            self.C3 = C3
            time.sleep(0.05)

        if hasattr(self, 'C4'):
            C4 = self.C4
        else:
            C4 = self.bus.read_i2c_block_data(self.i2c, 0xA8) #Temperature coefficient of pressure offset
            C4 = C4[0] * 256.0 + C4[1]
            self.C4 = C4
            time.sleep(0.05)

        if hasattr(self, 'C5'):
            C5 = self.C5
        else:
            C5 = self.bus.read_i2c_block_data(self.i2c, 0xAA) #Reference temperature
            C5 = C5[0] * 256.0 + C5[1]
            self.C5 = C5
            time.sleep(0.05)

        if hasattr(self, 'C6'):
            C6 = self.C6
        else:
            C6 = self.bus.read_i2c_block_data(self.i2c, 0xAC) #Temperature coefficient of the temperature
            C6 = C6[0] * 256.0 + C6[1]
            self.C6 = C6
            time.sleep(0.05)

        
        ## These are the calculations provided in the datasheet for the sensor.
        dT = D2 - C5 * 2**8
        TEMP = 2000 + dT * C6 / 2**23

        ## Set Values to class to be used elsewhere
        self.tempC = TEMP/100.0
        self.tempK = TEMP/100.0 + 273.15

        ## These calculations are all used to produce the final pressure value
        OFF = C2 * 2**16 + (C4 * dT) / 2**7
        SENS = C1 * 2**15 + (C3 * dT) / 2**8
        P = (D1 * SENS / 2**21 - OFF) / 2**15
        self.pressure = P/1000.0

        ## Calculate an offset for the pressure.  This is required so that the readings are correct.
        ##   Equation can be found here: http://en.wikipedia.org/wiki/Barometric_formula
        altOffset = math.exp( (-9.80665 * 0.0289644 * self.elevation) / (8.31432 * self.tempK) )
        self.pressureAdj = ( P/altOffset ) / 1000.0 

    def getTempC(self):
        return self.tempC

    def getPressure(self):
        return self.pressure

    def getPressureAdj(self):
        return self.pressureAdj

    def printResults(self):
        print("Temperature:", round(self.tempC, 2), "C")

        print("Pressure Absolute:", round(self.pressure, 2), "kPa")
        print("         Adjusted:", round(self.pressureAdj, 2), "kPa")
