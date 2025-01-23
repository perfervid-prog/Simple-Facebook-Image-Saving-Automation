from fb_post_image_saver import FbPostImageSaver
import time

if __name__ == "__main__":
    total_image = int(input("Enter the number of images you want to save: "))
    file_name = int(input("Starting file name (only number), default is 1: "))
    print("5 seconds left. Move the mouse cursor to the center of the image.")
    time.sleep(5) # Adjust as needed
    saver = FbPostImageSaver(total_image, file_name)
    saver.run()