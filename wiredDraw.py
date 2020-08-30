# !/usr/bin/python3
# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np
from MS5611 import MS5611


def getData(sensor, data):
    data = np.roll(data, -1)
    sensor.read()
    data[-1] = sensor.pressureAdj
    return data

def getTime(t):
    maxT = t[-1]
    t = np.roll(t, -1)
    t[-1] = maxT + 1
    return t

def draw():
    sensor = MS5611(1, 0x77, 1)
    plt.ion()
    plt.figure(1)
    
    # 图像绘制50个点
    t = np.linspace(-49, 0)
    data = np.zeros(50)
    
    # 最大化窗口(Linux)
    mng = plt.get_current_fig_manager()
    mng.resize(*mng.window.maxsize())
    # 最大化窗口(Windows)
    # figManager = plt.get_current_fig_manager()
    # figManager.window.showMaximized()

    while True:
        try:
            plt.clf()
            # t, data = fakeData(t, data)
            data = getData(sensor, data)
            # sensor.printResults()
            t = getTime(t)
            plt.plot(t, data)
            plt.xlabel('time(s)')
            plt.ylabel('Air pressure(kPa)')
            plt.ylim((100, 101))
            press = "Current:{:.2f}kPa".format(data[-1])
            plt.text(t[-10], 101, press)
            plt.pause(0.1)
        except (KeyboardInterrupt, SystemExit):
            break

if __name__ == '__main__':
    draw()
