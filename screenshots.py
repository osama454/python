import pyautogui
from win32api import *
from win32con import *
import win32con
import time
i=0
while True:
    if GetAsyncKeyState(ord('X')):
        myScreenshot = pyautogui.screenshot()
        myScreenshot.save(rf'images\\{i}.jpg')
        i+=1
        time.sleep(3)