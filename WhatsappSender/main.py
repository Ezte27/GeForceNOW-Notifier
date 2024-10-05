import pywhatkit
import pathlib, os, time, keyboard

import pyautogui
import numpy as np
import cv2

### 
input("Press enter to start GEFORCE NOW notifier.")
###

# Variables
PARENT_PATH = pathlib.Path(__file__).parent.resolve()
SCREENSHOT_PATH = os.path.join(PARENT_PATH, "screenshots")
receiver = '+18494561618'
wait_time = 50
close_time = 15
window_time = 10
test_img = "test_screenshot"
debug = True if input("Debug? (y/n)") == 'y' else False

def establish_connection(receiver, wait_time, close_time):
    pywhatkit.sendwhatmsg_instantly(receiver, 'Connection has been established.', wait_time = wait_time, tab_close = False)
    _make_sure_to_send()
    _close_tab(close_time)

def take_screenshot(img_name):
    # Take screenshot using pyautogui
    image = pyautogui.screenshot()

    # Convert PIL to np array and from RGB to BGR
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # Write to disk
    cv2.imwrite(f"screenshots/{img_name}.png", image)

def send_screenshot(img_name, screenshot_path, receiver, wait_time, close_time):
    try:
        # Send Picture
        pywhatkit.sendwhats_image(receiver, os.path.join(screenshot_path, f"{img_name}.png"), caption = img_name, wait_time = wait_time, tab_close = False)
        _make_sure_to_send()
        _close_tab(close_time)
    except Exception as e:
        time.sleep(5)
        fatal_error(wait_time, close_time)
        print(f"ERROR: {e}")

def fatal_error(receiver, wait_time, close_time):
    pywhatkit.sendwhatmsg_instantly(receiver, 'Fatal Error! Closing program.', wait_time = wait_time, tab_close = False)
    _make_sure_to_send()
    _close_tab(close_time)

def test_send_screenshot(img_name, screenshot_path, receiver, wait_time, close_time):
    try:
        # Send Picture
        pywhatkit.sendwhats_image(receiver, os.path.join(screenshot_path, f"{img_name}.png"), caption = "Test Screenshot", wait_time = wait_time, tab_close = False)
        _make_sure_to_send()
        _close_tab(close_time)
    except Exception as e:
        time.sleep(5)
        fatal_error(receiver, wait_time, close_time)
        print(f"ERROR in TEST: {e}")

def notifier_start_msg(receiver, wait_time, close_time):
    pywhatkit.sendwhatmsg_instantly(receiver, 'GeForce NOW Notifier started!', wait_time = wait_time, tab_close = False)
    _make_sure_to_send()
    _close_tab(close_time)

def notifier_loop(receiver, wait_time, close_time, screenshot_path, debug = False):
    i = 0
    while True:
        # Generate next screenshot name
        name = f"img_{str(i)}"

        time.sleep(1)

        # Take Screenshot
        print(f"[LOGS] Taking screenshot {name}...")
        take_screenshot(name)
    
        # Send Screenshot
        print(f"[LOGS] Sending screenshot {name}...")
        send_screenshot(name, screenshot_path, receiver, wait_time, close_time)

        # Increase i number
        i += 1

        print("[LOGS] Waiting...")
        # Wait for 30 mins before taking next screenshot
        # time.sleep(1800)
        # Wait for 15 mins before taking next screenshot
        # time.sleep(900)
        if not debug:
            # Wait for 10 mins before taking next screenshot
            time.sleep(600)
        else:
            time.sleep(25)

def _make_sure_to_send():
    time.sleep(3)
    pyautogui.moveTo(1040, 670)
    time.sleep(1)
    pyautogui.click()
    time.sleep(1)
    pyautogui.press('enter')

def _close_tab(close_time):
    time.sleep(close_time)
    keyboard.press_and_release('ctrl+w')
    time.sleep(1)

if __name__ == '__main__':
    # Wait 15 seconds and then
    time.sleep(15)
    # Start Program

    # Establish Whatsapp connection
    print("[LOGS] Trying to establish Whatsapp connection...")
    establish_connection(receiver, wait_time, close_time)
    print("[LOGS] Established Whatsapp connection!")
    time.sleep(window_time)
    # print("[LOGS] Testing screenshot functionality...")
    # take_screenshot(test_img)
    # time.sleep(2)
    # test_send_screenshot(test_img, SCREENSHOT_PATH, receiver, wait_time, close_time)
    # print("[LOGS] Screenshot functionality successful!")
    # time.sleep(window_time)
    print("[LOGS] Initiating GeForce NOW Notifier")
    notifier_start_msg(receiver, wait_time, close_time)
    time.sleep(window_time)

    # Entering infinite loop
    notifier_loop(receiver, wait_time, close_time, SCREENSHOT_PATH, debug=debug)
