# !/usr/bin/python3
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import time


def main():
    # GPIO port
    switchIn = 36
    switchOut = 18
    flowSensor = 12
    light = 32
    
    # time(s)
    inTime = 15
    waitTime = 10
    outTime = 32
    nextTime = 5

    # 配置GPIO口
    GPIO.setmode(GPIO.BOARD)        # 将GPIO编程方式设置为BOARD模式
    GPIO.setup(switchIn, GPIO.OUT)  # 设置物理引脚负责输出电压
    GPIO.setup(switchOut, GPIO.OUT)
    GPIO.setup(flowSensor, GPIO.IN)
    GPIO.setup(light, GPIO.OUT)
    
    while 1:
        try:
            # 充气过程
            print("start inflation, {} s".format(inTime))
            GPIO.output(switchIn, GPIO.HIGH) # switchIn输出高电平
            GPIO.output(switchOut, GPIO.LOW)
            GPIO.output(light, GPIO.LOW)
            time.sleep(inTime)
            GPIO.output(switchIn, GPIO.LOW) # switchIn输出低电平
            print("waiting for {} s".format(waitTime))
            time.sleep(waitTime)            # 充气后等待
            
            # 放气过程
            print("start deflation, {} s".format(outTime))
            GPIO.output(switchOut, GPIO.HIGH)
            start = time.time()
            while True:
                flow = GPIO.input(flowSensor)       # 读取流量传感器
                if flow:
                    GPIO.output(light, GPIO.HIGH)
                    while True:
                        current = time.time()       # 获取当前时间
                        if (current - start > outTime):
                            break                   # 持续了outTime则break
                current = time.time()
                if (current - start > outTime):
                    print("waiting for {} s".format(nextTime))
                    time.sleep(nextTime)            # 释气后等待
                    break
        except (KeyboardInterrupt, SystemExit):
            GPIO.cleanup()
            break

if __name__ == '__main__':
    main()

