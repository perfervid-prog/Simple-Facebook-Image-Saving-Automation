import pyautogui
import time

class FbPostImageSaver:
    def __init__(self, total_image, file_name_start=1):
        self.total_image = total_image
        self.file_name = file_name_start

    def run(self):
        file_name = self.file_name if (self.file_name != 1) else 1
        for i in range(1, self.total_image + 1):
            x, y = pyautogui.position() #gets the cursor position
            pyautogui.rightClick(x, y) #right click
            pyautogui.moveTo(x + 20, y + 60) # move the cursor down to click on save as image option
            pyautogui.click()
            time.sleep(1)
            pyautogui.write(str(file_name) if i == 1 else file_name + i - 1) # write the file name i
            pyautogui.moveTo(x-2, y - 1) # again move the cursor up 
            pyautogui.press('enter') # press enter
            time.sleep(1)
            pyautogui.press('right') # move to next image
            time.sleep(1)