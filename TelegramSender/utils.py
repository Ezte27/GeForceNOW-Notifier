import sys
import time
import math
import keyboard
import requests
import pyautogui
import numpy as np
from config import *
from typing import Union
from colorama import Fore
from subprocess import Popen
from PIL import Image, ImageChops

def sendTelegramText(chat_id:str, bot_token:str, msg:str) -> bool:
    url = f"https://api.telegram.org/bot{bot_token}"
    params = {"chat_id": chat_id, "text": msg}
    r = requests.get(url + "/sendMessage", params=params)
    return checkTelegramResponse(r, msg)

def sendTelegramImage(chat_id:str, bot_token:str, img_path:Union[str, Image.Image]) -> bool:
    """
    Send an image to a Telegram chat.

    :param chat_id: The ID of the Telegram chat.
    :type chat_id: str

    :param bot_token: The Telegram bot token.
    :type bot_token: str

    :param img_path: Either a file path (str) or a PIL.Image to be sent.
    :type img_path: Union[str, Image.Image]

    :return: True if the image is sent successfully, False otherwise.
    :rtype: bool
    """
    url = f"https://api.telegram.org/bot{bot_token}"
    params = {"chat_id": chat_id}
    if isinstance(img_path, str):
        # If img_path is a string (file path), open the file and send as photo
        files = {'photo': open(img_path, "rb")}
    elif isinstance(img_path, Image.Image):
        # If img_path is a PIL.Image, convert it to bytes and send as photo
        from io import BytesIO
        img_byte_array = BytesIO()
        img_path.save(img_byte_array, format='PNG')
        img_byte_array.seek(0)
        files = {'photo': img_byte_array}
    else:
        raise ValueError("Unsupported img_path type. Please provide a valid file path or PIL.Image.")
    r = requests.get(url + "/sendPhoto", params=params, files=files)
    return checkTelegramResponse(r, img_path)

def checkTelegramResponse(r, msg):
    # Check if the request was successful (HTTP status code 200) and parse JSON response
    if r.status_code == 200:
        data:dict = r.json()

        # Check if the 'ok' field is True
        if data.get('ok', False):
            print("[LOGS] Telegram message sent!")
            print(f"[LOGS] msg: {msg}")
            return True
        else:
            print(f"[LOGS] Telegram API {Fore.RED}error{Fore.RESET}:", data.get('description', 'Unknown error'))
            print(f"[LOGS] Failed msg: {msg}")
    else:
        print(f"[LOGS] {Fore.RED}Failed{Fore.RESET} to connect to Telegram API. HTTP Status Code:", r.status_code)
        print(f"[LOGS] Failed msg: {msg}")
    return False

def sendGFNNStarted():
    print("[LOGS] Checking Telegram connection...")
    if sendTelegramText(RECEIVER_ID, BOT_TOKEN, CONFIRMATION_MSG):
        print(f"[LOGS] Telegram connection successful! Confirmation sent - Time: {get_time()}")
    else:
        print(f"[LOGS] Telegram connection {Fore.RED}FAILED!{Fore.RESET} Time: {get_time()}")

def take_screenshot(save=False):
    # Take screenshot using pyautogui
    screenshot = pyautogui.screenshot()

    # Write to disk
    if save:
        screenshot.save("screenshots/screenshot.png", format="png")

    return screenshot

def crop_image(img, left, top, right, bottom, grayscale:bool=True):
    # Crop the image
    image = img.crop((left, top, right, bottom))
    
    if grayscale:
        # Convert to grayscale
        image_grayscale = image.convert('L')
        return image_grayscale
    return image
    
def detect_delta_image(new_img:np.array, prev_img:np.array) -> bool:
    """
    Checks if new_image is different to prev_image
    \n\tTrue if different
    \n\tFalse if same
    """
    if prev_img is None:
        prev_img = new_img
    return False if np.array_equal(new_img, prev_img) else True

def areImagesEqual(a:Image.Image, b:Image.Image, threshold:int, calibrate_rms=False) -> bool:
    """
    If difference between Images is less than or equal to threshold, the Images are equal. Return True
    """

    func_name = "areImagesEqual"
    display_name = func_name if DEBUG else "LOGS"

    # DEBUG
    if DEBUG:
        a.save(os.path.join(SCREENSHOT_PATH, f"debug/{func_name}_a.png"), "PNG")
        b.save(os.path.join(SCREENSHOT_PATH, f"debug/{func_name}_b.png"), "PNG")

    # Convert images to same format
    a = a.convert('1') # Pure black and white
    b = b.convert('1')

    if a.size != b.size:
        # Handle the size mismatch, e.g., resize the images to the same dimensions.
        print(f"[{display_name}] a and b dont have same dimensions! a.size = {a.size}, b.size = {b.size}")

    # if a.mode != b.mode:
    #     # Handle the mode mismatch, e.g., convert the images to the same mode.
    #     print(f"[{display_name}] a and b dont have same mode! a.mode = {a.mode}, b.mode = {b.mode}")

    #     # Convert images to same format
    #     a = a.convert('1') # Pure black and white
    #     b = b.convert('1')

    #     if a.mode == b.mode:
    #         print(f"[{display_name}] Handled mismatch in modes. a.mode = {a.mode}, b.mode = {b.mode}")
    #     else:
    #         print(f"[{display_name}] fatal error: couldnt handle mismatch in modes.")

    diff = None

    try:
        # Use ImageChops to find the absolute difference between the two images
        diff = ImageChops.difference(a, b)
    except ValueError:
        # Convert images to same format
        a = a.convert('1') # Pure black and white
        b = b.convert('1') # Pure black and white

        # Try again
        try:
            diff = ImageChops.difference(a, b)
        except Exception as e:
            print(f"[{display_name}] {Fore.RED}UNKNOWN ERROR{Fore.RESET} in 'areImagesEqual' method (2): e = {e}")
    except Exception as e:
        print(f"[{display_name}] {Fore.RED}UNKNOWN ERROR{Fore.RESET} in 'areImagesEqual' method (1): e = {e}")

    # Calculate the rms (root mean square) value of the difference
    rms = math.sqrt(sum(map(lambda x: x*x, diff.getdata())) / float(a.size[0] * a.size[1]))
    if calibrate_rms:
        print(f"rms: {rms}")
    # Check if the rms value is below the specified threshold
    return (rms < threshold)

def showWindowOnScreen(window_title:str) -> bool:
    """
    To make specific window show on screen, this function uses a loop to Alt+Tab using pyautogui until the window on screen is the desired one.
    """
    # Alert user searching for window
    alert_user(window_title)

    # Open any window if no window is open
    if pyautogui.getActiveWindowTitle() == "":
        pyautogui.hotkey('alt', 'tab')

    prev_window:str = None
    found_window = False
    i = 0
    # Loop through opened apps using alt + tab
    while True:
        # Check active window title
        active_window_title = pyautogui.getActiveWindowTitle()
        
        # Exit the loop if the desired window is on screen
        if window_title in active_window_title:
            found_window = True
            break 

        # Press Alt + Tab to switch between windows
        pyautogui.keyDown('alt')
        pyautogui.press('tab')
        for _ in range(0, i):
            pyautogui.press('right')
            time.sleep(0.1)
        pyautogui.keyUp('alt')

        # This duration is for laggy computers
        time.sleep(0.1)

        # Check if program is looping over previously seen app to avoid looping all apps again
        if i!=0 and prev_window == active_window_title:
            found_window = False
            break
        prev_window = str(active_window_title)
        i+=1

    # Alert the user window has been found
    alert_user(window_title, status=1) if found_window else alert_user(window_title, status=2)

    return found_window

def maximizeWindow():
    # Give some time for user to focus on the window
    time.sleep(1)

    # Maximize the window by sending the appropriate keyboard shortcut
    pyautogui.hotkey('winleft', 'up')

def get_opened_apps_count() -> int:
    
    # Prepare the user
    print("--------------------------------------------------------------")
    print(f"Counting number of opened apps... {Fore.YELLOW}Please don't touch computer.{Fore.RESET}")
    time.sleep(1)

    # Open any window if no window is open
    if pyautogui.getActiveWindowTitle() == "":
        pyautogui.hotkey('alt', 'tab')

    prev_window:str = None
    i = 0
    # Loop through opened apps using alt + tab
    while True:
        # Check active window title
        active_window_title = pyautogui.getActiveWindowTitle()
        
        # Press Alt + Tab to switch between windows
        pyautogui.keyDown('alt')
        pyautogui.press('tab')
        for _ in range(0, i):
            pyautogui.press('right')
            time.sleep(0.1)
        pyautogui.keyUp('alt')

        # This duration is for laggy computers
        time.sleep(0.1)
        
        # Check if program is looping over previously seen app to avoid looping all apps again
        if i!=0 and prev_window == active_window_title:
            break
        prev_window = str(active_window_title)
        i+=1

    # Alert the user
    print(f"{Fore.GREEN}Finished{Fore.RESET} counting the opened apps.Thank you for your patience.")
    print("--------------------------------------------------------------")
    time.sleep(1)
    return i

def openWindow(path_to_exe:str) -> bool:
    # Open app
    print(f"[LOGS] Opening application...")
    Popen([path_to_exe])
    time.sleep(8)
    print(f"[LOGS] Application opened.")
    return True

def enterGameQueue(game_name:str) -> None:
    print("[LOGS] Entering game queue...")
    time.sleep(5)

    # Click search bar
    # pyautogui.moveTo(1000, 80)
    # time.sleep(0.5)
    # pyautogui.leftClick()
    # time.sleep(1)

    # Go to search bar
    # pyautogui.press("tab")
    # time.sleep(1)
    # pyautogui.press("tab")
    # time.sleep(1)
    # pyautogui.press("enter")
    # time.sleep(1)
    keyboard.send("tab")
    time.sleep(1)
    keyboard.send("tab")
    time.sleep(1)
    keyboard.send("enter")
    time.sleep(1)

    # Type in search bar
    pyautogui.write(game_name, 0.8)
    time.sleep(5)

    # Open the first search result
    # pyautogui.press("enter")
    # time.sleep(1)
    # pyautogui.press("enter")
    # time.sleep(1)
    # pyautogui.press("enter")
    keyboard.send("enter")
    time.sleep(1)
    keyboard.send("enter")
    time.sleep(1)
    keyboard.send("enter")
    time.sleep(1)

    time.sleep(5)   # This sleep() is to wait for GeForce NOW to connect user to queue which usually takes some time
    print("[LOGS] Entered game queue.")

def getWindowTitle() -> Union[str, bool]:
    # Get window title
    active_window_title = pyautogui.getActiveWindowTitle()
    if active_window_title is not None:
        return active_window_title
    else:
        return False

def checkGFNstatus(check_name:str) -> bool:
    """
    Check queue status. Is there a network problem, is it still in queue or has it finished, etc.
    parameter check_name: check_name is the str associated with a specific check. Available options: home, queue, loading, network, wrapping, background ('background' refers to the check for the iconic GFN background when queue is over and the game didnt load correctly.)
    returns bool
    """
    pass


def isGFNInQueue() -> bool:

    # Get window title
    active_window_title = getWindowTitle()
    # AND
    # Get screenshot with text: Looking for the next available rig
    screenshot = pyautogui.screenshot()
    image = screenshot.crop((LEFT_QUEUE_CROP, TOP_QUEUE_CROP, RIGHT_QUEUE_CROP, BOTTOM_QUEUE_CROP)) # Crop the image
    img = isGFNInQueueImageFilter(image)
    gfn_image = Image.open(os.path.join(IMAGES_PATH, "GFN_in_queue.png"))
    
    # Then take the filtered screenshot and compare it to the standard filtered GFN_in_queue.png image
    # If filtered img and GFN_in_queue.png and " on ", then GFN is probably on queue.

    # Check
    if active_window_title and (" on " in active_window_title) and (areImagesEqual(img, gfn_image, QUEUE_IMAGE_DIFF_THRESHOLD)):
        return True
    return False

def isGFNInLoading() -> bool:
    # Get window title
    active_window_title = getWindowTitle()
    # AND
    # Get screenshot with text: Loading...
    screenshot = pyautogui.screenshot()
    image = screenshot.crop((LEFT_LOADING_CROP, TOP_LOADING_CROP, RIGHT_LOADING_CROP, BOTTOM_LOADING_CROP))
    image_filtered = filterImage(image)
    gfn_image = Image.open(os.path.join(IMAGES_PATH, "GFN_in_loading.png"))
    
    # Then take the filtered screenshot and compare it to the standard filtered GFN_in_loading.png image
    # If filtered image and GFN_in_loading.png and " on ", then GFN is probably on loading.
    
    # DEBUG
    if areImagesEqual(image_filtered, gfn_image, IMAGE_DIFF_THRESHOLD):
        print(f"[LOGS] {Fore.GREEN}GFN 'In Loading' Screen has this title: {active_window_title}{Fore.RESET}")

    # Check
    if active_window_title and (" on " in active_window_title) and (areImagesEqual(image_filtered, gfn_image, IMAGE_DIFF_THRESHOLD)):
        return True
    return False

def isGFNInHome() -> bool:
    #TODO: Add another check to see if in home page by taking a screenshot of a section of the GFN window that appears only when at home page.
    # Get window title
    active_window_title = getWindowTitle()
    # AND
    # Get screenshot
    screenshot = pyautogui.screenshot()
    image = screenshot.crop((LEFT_LOADING_CROP, TOP_LOADING_CROP, RIGHT_LOADING_CROP, BOTTOM_LOADING_CROP))
    image_filtered = filterImage(image)
    gfn_image = Image.open(os.path.join(IMAGES_PATH, "unfinished/GFN_in_home.png"))
    
    # Check
    if active_window_title and (active_window_title == WINDOW_TITLE): #and (areImagesEqual(image_filtered, gfn_image, IMAGE_DIFF_THRESHOLD)):
        return True
    return False

def checkNetworkTest() -> bool:
    # Get window title
    active_window_title = getWindowTitle()
    # AND
    # Get screenshot with text: Network Test...
    screenshot = pyautogui.screenshot()
    image = screenshot.crop((LEFT_NETWORK_CROP, TOP_NETWORK_CROP, RIGHT_NETWORK_CROP, BOTTOM_NETWORK_CROP))
    image_filtered = filterImage(image)
    gfn_image = Image.open(os.path.join(IMAGES_PATH, "GFN_network_error.png"))
    
    # Then take the filtered screenshot and compare it to the standard filtered GFN_network_error.png image
    # If filtered image and GFN_network_error.png and " on ", then GFN has probably a problem with network connectivity.

    # Check
    if active_window_title and (active_window_title == WINDOW_TITLE) and (areImagesEqual(image_filtered, gfn_image, NETWORK_IMAGE_DIFF_THRESHOLD)):
        if DEBUG:
            image.save(os.path.join(SCREENSHOT_PATH, "debug/network_crp_img.png"), "PNG") # DEBUG
            gfn_image.save(os.path.join(SCREENSHOT_PATH, "debug/network_gfn_img.png"), "PNG") # DEBUG
        return True
    return False

def checkWrappingSession() -> bool:
    # Get window title
    active_window_title = getWindowTitle()
    # AND
    # Get screenshot with text: Wrapping previous session...
    screenshot = Image.open(os.path.join(IMAGES_PATH, "unfinished/GFN_wrapping_session.png")) # pyautogui.screenshot()
    image = screenshot.crop((LEFT_QUEUE_CROP, TOP_QUEUE_CROP, RIGHT_QUEUE_CROP, BOTTOM_QUEUE_CROP))
    image_filtered = filterImage(image)
    gfn_image = Image.open(os.path.join(IMAGES_PATH, "GFN_wrapping_session.png"))
    
    # Then take the filtered screenshot and compare it to the standard filtered GFN_wrapping_session.png image
    # If filtered image and GFN_wrapping_session.png and " on ", then GFN is probably wrapping the previous session, which usually just takes a minute or two.
    
    # DEBUG
    if DEBUG:
        if areImagesEqual(image_filtered, gfn_image, IMAGE_DIFF_THRESHOLD):
            print(f"[LOGS] {Fore.GREEN}GFN 'Wrapping Session' Screen has this title: {active_window_title}{Fore.RESET}")

    # Check
    if active_window_title and (" on " in active_window_title) and (areImagesEqual(image_filtered, gfn_image, IMAGE_DIFF_THRESHOLD)):
        if DEBUG:
            image.save(os.path.join(SCREENSHOT_PATH, "debug/wrapping_crp_img.png"), "PNG") # DEBUG
            gfn_image.save(os.path.join(SCREENSHOT_PATH, "debug/wrapping_gfn_img.png"), "PNG") # DEBUG
        return True
    return False

def isGameBackground() -> bool:
    # See screenshots/screenshot.png for clarity
    # TODO:
    return False

def isGFNInQueueImageFilter(image:Image) -> Image:
    # Get image size
    width, height = image.size

    # Iterate through each pixel
    for x in range(width):
        for y in range(height):
            # Get pixel value
            pixel = image.getpixel((x, y))

            # Check if under threshold
            if (pixel[0] < QUEUE_COLOR_FILTER_THRESHOLD) or (pixel[1] < QUEUE_COLOR_FILTER_THRESHOLD) or (pixel[2] < QUEUE_COLOR_FILTER_THRESHOLD):
                # Set pixel to pure black
                image.putpixel((x, y), (0, 0, 0))
            else:
                # Set pixel to pure white
                image.putpixel((x, y), (255, 255, 255))
    
    # Return modified image
    return image

def filterImage(image:Image) -> Image:
    # Get image size
    width, height = image.size

    # Iterate through each pixel
    for x in range(width):
        for y in range(height):
            # Get pixel value
            pixel = image.getpixel((x, y))

            # Check if under threshold
            if (pixel[0] < COLOR_FILTER_THRESHOLD) or (pixel[1] < COLOR_FILTER_THRESHOLD) or (pixel[2] < COLOR_FILTER_THRESHOLD):
                # Set pixel to pure black
                image.putpixel((x, y), (0, 0, 0))
            else:
                # Set pixel to pure white
                image.putpixel((x, y), (255, 255, 255))
    
    # Return modified image
    return image

def updateInQueueImage() -> None:
    # Go to GFN queue for this
    input("When you have opened GFN and entered a game queue, hit enter to update queue image.")
    print("Dont touch your computer now.")
    time.sleep(2)
    if showWindowOnScreen(WINDOW_TITLE):
        time.sleep(1)

        # Take screenshot
        screenshot = pyautogui.screenshot()
        # Crop the image
        image = screenshot.crop((LEFT_QUEUE_CROP, TOP_QUEUE_CROP, RIGHT_QUEUE_CROP, BOTTOM_QUEUE_CROP)) 
        # Apply filter
        img = isGFNInQueueImageFilter(image)
        # Save the new image and delete the old one
        img.save(os.path.join(IMAGES_PATH, "GFN_in_queue_.png"), "png")

def updateInLoadingImage(img_path:str, save_path:str) -> None:
    screenshot = Image.open(img_path)
    image = screenshot.crop((LEFT_LOADING_CROP, TOP_LOADING_CROP, RIGHT_LOADING_CROP, BOTTOM_LOADING_CROP))
    image_filtered = filterImage(image)
    image_filtered.save(save_path)

def updateNetworkErrorImage(img_path:str, save_path:str) -> None:
    screenshot = Image.open(img_path)
    image = screenshot.crop((LEFT_NETWORK_ERROR_CROP, TOP_NETWORK_ERROR_CROP, RIGHT_NETWORK_ERROR_CROP, BOTTOM_NETWORK_ERROR_CROP))
    image_filtered = filterImage(image)
    image_filtered.save(save_path)

def updateWrappingSessionImage(img_path:str, save_path:str) -> None:
    screenshot = Image.open(img_path)
    image = screenshot.crop((LEFT_QUEUE_CROP, TOP_QUEUE_CROP, RIGHT_QUEUE_CROP, BOTTOM_QUEUE_CROP))
    image_filtered = filterImage(image)
    image_filtered.save(save_path)

def alert_user(app_name:str, status=0) -> None:
    """
    status parameter can either be:
    \n0: Searching
    \n1: Found
    \n2: Not Found
    """
    if status==1:
        msg = f"{app_name} {Fore.GREEN}has been found!{Fore.RESET} Thanks for your patience."
        print(msg)
        print("-" * len(msg))
    elif status==2:
        msg = f"{app_name} {Fore.RED}has NOT been found!{Fore.RESET} Sorry for your patience."
        print(msg)
        print("-" * len(msg))
    else:
        # Prepare the user
        msg = f"Searching for {app_name}... {Fore.YELLOW}Please do not touch computer.{Fore.RESET}"
        print("-" * len(msg))
        print(msg)
        time.sleep(2.5)

def get_time() -> str:
    return time.strftime("%H:%M", time.localtime())

def checkQueueFinished() -> bool:
    # TODO: Add more checks
    if isGFNInLoading() or isGameBackground():
        return True
    elif isGFNInQueue():
        return False
    elif isGFNInHome():
        return False
    return True

def notify_loop(iterations=5, args=None, error_msg=None) -> None:
    msg = QUEUE_MSG if error_msg is None else error_msg

    time.sleep(5)

    if (args is not None) and args["sendImageConfirmation"]:
        sendTelegramImage(RECEIVER_ID, BOT_TOKEN, take_screenshot())
        time.sleep(1.5)

    for i in range(1, iterations):
        sendTelegramText(RECEIVER_ID, BOT_TOKEN, msg) if i == 1 else sendTelegramText(RECEIVER_ID, BOT_TOKEN, ".")
        time.sleep(5)

def saveDebugImages(path_to_dir:str, screenshot:Image, cropped_image:Image, previous_image:Image) -> None:
    path_to_dir = path_to_dir.removeprefix("/")
    screenshot.save(os.path.join(path_to_dir, "screenshot.png"), "PNG")
    cropped_image.save(os.path.join(path_to_dir, "cropped_img.png"), "PNG")
    previous_image.save(os.path.join(path_to_dir, "prev_img.png"), "PNG")