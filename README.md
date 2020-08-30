# RaspberryBLE_Receive
树莓派接收BLE模块发送的数据（见项目MS5611_BT05_STM32），保存、绘图

## 说明
树莓派中有两个文件main.py与wirelessShow.py。其中，main.py用于控制压气与释气过程，wirelessShow.py用于接收BT05发送的数据，并在屏幕上实时显示出来。这两个文件均使用python3编写，不支持python2环境下运行，并且需要以下第三方库：RPi.GPIO, bluepy, numpy, matplotlib。因此，运行程序前，需要通过如下命令安装这几个库：
```bash
pip3 install RPi.GPIO bluepy numpy matplotlib
```
假设这两个文件的位置均在桌面，则分别执行如下两条命令，以运行这两个python程序。
```bash
python3 ~/Desktop/main.py
python3 ~/Desktop/wirelessShow.py
```
值得注意的是，wirelessShow.py调用了第三方库matplotlib，必须在图像界面才能执行，命令行界面将无法执行这一程序，但是可以执行main.py。
这两个程序并不需要root权限来执行，但根据您的偏好，同样也可以使用root权限以执行，运行前，同样需要如下命令安装第三方库：
```bash
sudo pip3 install RPi.GPIO bluepy numpy matplotlib
```

