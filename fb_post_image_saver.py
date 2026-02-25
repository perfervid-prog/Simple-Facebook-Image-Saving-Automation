import pyautogui
import time
import os

class FbPostImageSaver:
    def __init__(self, total_image, save_path, file_name_start=1, delay=1.0, callback=None):
        self.total_image = total_image
        self.save_path = save_path
        self.file_name_start = file_name_start
        self.delay = delay
        self.callback = callback
        self.is_running = True

    def stop(self):
        self.is_running = False

    def run(self):
        # Fail-safe: Mouse to corner to abort
        pyautogui.FAILSAFE = True
        
        for i in range(self.total_image):
            if not self.is_running:
                break
                
            current_file_num = self.file_name_start + i
            base_name = f"{current_file_num}.jpg"
            full_path = os.path.join(self.save_path, base_name)
            
            # Duplicate handling
            counter = 1
            while os.path.exists(full_path):
                full_path = os.path.join(self.save_path, f"{current_file_num}_{counter}.jpg")
                counter += 1
            
            if self.callback:
                self.callback(i + 1, self.total_image, f"Saving {file_name}...")

            # Step 1: Right click on the image
            x, y = pyautogui.position()
            pyautogui.rightClick(x, y)
            time.sleep(self.delay * 0.8) 
            
            # Step 2: Use "v" shortcut to "Save image as..." (Works in Chrome/Edge/Brave)
            pyautogui.press('v')
            time.sleep(self.delay * 1.5) # Wait for "Save As" dialog
            
            # Step 3: Type the full absolute path
            pyautogui.write(full_path)
            time.sleep(0.5)
            
            # Step 4: Press enter to save
            pyautogui.press('enter')
            time.sleep(self.delay) 
            
            # Step 5: Move to next image
            pyautogui.press('right')
            time.sleep(self.delay) 
        
        if self.callback:
            if not self.is_running:
                self.callback(self.total_image, self.total_image, "Process stopped.")
            else:
                self.callback(self.total_image, self.total_image, "All images saved successfully!")
