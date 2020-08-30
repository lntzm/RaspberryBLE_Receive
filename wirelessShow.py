# !/usr/bin/python3
# -*- coding: utf-8 -*-

from bluepy import btle
import time
import matplotlib.pyplot as plt
import numpy as np


class MyDelegate(btle.DefaultDelegate):
    '''
    @brief 监听与处理BLE设备Notification
    @param timeList 要绘制的横坐标列表
    @param dataArray 要绘制的纵坐标numpy array
    '''
    def __init__(self, timeList, dataArray): 
        btle.DefaultDelegate.__init__(self)
        self.timeList = timeList
        self.dataArray = dataArray
                   
    def handleNotification(self, cHandle, data):
        print("Recieved pressure: " + str(data))
        try:
            self.dataArray = refreshList(self.dataArray, data)
            dateStr, self.timeList = refreshTime(self.timeList)
            # 将新接收的数据写入日志文件
            with open('pressure.log', 'a+') as f:       # 追加方式，读写
                f.write(dateStr + ' ' + self.timeList[-1] +
                        ' ' + str(self.dataArray[-1]) + '\n')
            draw(self.timeList, self.dataArray)
        except(ValueError):     # data不能从btyes转化为float，此时无数据，为STM32重启、正在设置BT05导致
            print("STM32 is setting up BT05, waiting for data...")
            time.sleep(0.19)

def refreshList(dataArray, data):
    # 更新当前气压的array，刷新为最近50个数据
    dataArray = np.roll(dataArray, -1)
    dataArray[-1] = data
    return dataArray

def refreshTime(timeList):
    # 更新当前时间，刷新为最近50个数据对应的时间
    now = int(time.time())
    nowStruct = time.localtime(now)
    dateStr = time.strftime("%Y-%m-%d", nowStruct)
    timeStr = time.strftime("%H:%M:%S", nowStruct)
    timeList.remove(timeList[0])
    timeList.insert(len(timeList), timeStr)
    return dateStr, timeList

def draw(timeList, dataArray):
    plt.clf()
    plt.plot(timeList, dataArray)
    plt.xlabel('time')
    plt.ylabel('Air pressure(kPa)')
    tickX = timeList[0: len(timeList): 5]
    plt.xticks(tickX, rotation=60)
    plt.ylim((50, 110))
    press = "Current:{}kPa".format(dataArray[-1])
    plt.title(press)
    plt.pause(0.01)
    
def drawInit(max=1):
    # 默认最大化窗口绘图
    plt.ion()
    plt.figure(1)
    if max:
        # 最大化窗口(Linux)
        mng = plt.get_current_fig_manager()
        mng.resize(*mng.window.maxsize())
        # 最大化窗口(Windows)
        # figManager = plt.get_current_fig_manager()
        # figManager.window.showMaximized()
    
def refreshFile(filename):
    try:
        with open(filename, 'r') as f:     # 读写，指针在开头
            lines = 0
            for index, line in enumerate(f):    # 获取文件行数
                lines += 1

            # 保留文件后1000行，删除早期数据
            f.seek(0,0)               # 文件指针指回开头
            if lines > 1000:          # 保留后1000个数据
                fileData = ""
                for (index, line) in enumerate(f):
                    if (lines - index) > 1000:      # 把后1000行数据copy
                        continue
                    fileData += line
            else:
                return lines
        with open(filename, 'w') as f:      # 覆盖写方式，写入copy的后1000行数据
            f.write(fileData)
        return 1000
    except FileNotFoundError:
        with open(filename, 'w') as f:      # 文件不存在，写方式创建文件
            pass
        return 0

def fileInit(filename):
    # 图像绘制50个点
    lines = refreshFile(filename)
    timeList = ['' for i in range(50)]
    dataArray = np.zeros(50)
    with open(filename, 'r+') as f:     # 读写，指针在开头
        if lines == 0:      # lines为0，是空文件
            pass
        elif lines < 50:      # 小于50行，全部读取，写入对应list/array
            loc = 50 - lines
            for line in f.readlines():
                lineData = line.strip().split(' ')
                timeStr = lineData[1]
                data = float(lineData[2])
                timeList[loc] = timeStr
                dataArray[loc] = data
                loc += 1
        else:               # 否则，读取后50行
            loc = 0
            for index, line in enumerate(f):
                if (lines - index) > 50:
                    continue
                else:
                    lineData = line.strip().split(' ')
                    timeStr = lineData[1]
                    data = float(lineData[2])
                    timeList[loc] = timeStr
                    dataArray[loc] = data
                    loc += 1
    return timeList, dataArray

def listen():
    address = "10:CE:A9:FD:9A:FC"       # 实验用BT05
    # address = "20:CD:39:90:A5:81"     # 远程调试的BT05
    drawInit(1)
    while True:
        timeList, dataArray = fileInit('pressure.log')
        p = btle.Peripheral(address)
        p.setDelegate(MyDelegate(timeList, dataArray))
        while True:
            try:
                if p.waitForNotifications(2.0):
                    # waiting for calling handleNotification()
                    continue
                print("Waiting...")
                time.sleep(0.2)
                continue    # continue 2nd
            except(btle.BTLEDisconnectError):
                print("Connection seems out, reconnecting...")
                time.sleep(0.2)
                break      # jump out the 2nd while, then continue 1st
            except(KeyboardInterrupt, SystemExit):
                return

if __name__ == '__main__':
    listen()
