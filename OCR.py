import pyautogui
import win32api
import win32con
import time
from pytesseract import pytesseract
import pyperclip
import translators as ts

pytesseract.tesseract_cmd =  r"D:\programs\Tesseract-OCR\tesseract.exe"

x1,y1,x2,y2=0,0,0,0
while True:
    if win32api.GetAsyncKeyState(win32con.VK_LBUTTON):
        x1,y1=x2,y2
        x2,y2=win32api.GetCursorPos()
        time.sleep(0.1)
    if win32api.GetAsyncKeyState(ord('X')) and x2>x1 and y2>y1:
        pyperclip.copy(
            #ts.server.google(
                pytesseract.image_to_string(
                    pyautogui.screenshot(region=(x1,y1,x2-x1,y2-y1))
                )
            #,from_language='en', to_language='ar')
        )
