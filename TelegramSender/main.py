# To activate conda env:
# C:\Users\ested\anaconda3\Scripts\activate.bat
# conda activate ... OR conda env list
import os
import time
import pyautogui
import numpy as np
from utils import *
from config import *
from colorama import Fore
from preferences import Preferences

# updateInQueueImage()
# updateInLoadingImage(os.path.join(IMAGES_PATH, "unfinished/GFN_Loading_game.png"), os.path.join(IMAGES_PATH, "GFN_in_loading.png"))
# updateNetworkErrorImage(os.path.join(IMAGES_PATH, "unfinished/GFN_network_test.png"), os.path.join(IMAGES_PATH, "GFN_network_error.png"))
# updateWrappingSessionImage(os.path.join(IMAGES_PATH, "unfinished/GFN_wrapping_session.png"), os.path.join(IMAGES_PATH, "GFN_wrapping_session.png"))
# sys.exit()

# Preferences for an increased personalization and more user-friendly experience
preferences = Preferences(PREFERENCES_PATH)

### 
time.sleep(0.5)
os.system('cls')
time.sleep(1)
print("-----WELCOME TO-----")
print("GeForce NOW Notifier")
print("--------------------")
time.sleep(0.5)
# Load preferences from preferences.json file
preferences.loadGFNNPreferences()
# If wish, edit preferences
preferences.editGFNNPreferences()
# Update preferences.json file
preferences.updateGFNNPreferences()

if preferences.getGFNNPreferences()["openGeForce"]:
    GAME_NAME = input(f"What game do you want to play? {Fore.CYAN}")
    time.sleep(0.5)
    print(f"{Fore.RESET}{BR_CHAR}")
time.sleep(0.5)

input("Press enter to start GeForce NOW Notifier.")
###

def main_loop(args):

    # Confirm Telegram connection
    if args["sendConfirmation"]:
        sendGFNNStarted()

    print("[LOGS] GeForce NOW Notifier has started.")

    gameON = False # gameON = True when the queue has finished and the game has started. False otherwise.
    prev_img = None
    i=0
    while not gameON:
        i+=1
        ## Check if queue is over
        
        # Take screenshot
        screenshot = take_screenshot()

        # Crop screenshot
        cropped_img = crop_image(screenshot, LEFT_QUEUE_CROP, TOP_QUEUE_CROP, RIGHT_QUEUE_CROP, BOTTOM_QUEUE_CROP)

        # Detect change 
        change = detect_delta_image(np.array(cropped_img), np.array(prev_img))

        # Check for change in screen content (4 Possibilities)
        if change and i!=1:
            # Notify the user and send the screenshot
            sendTelegramText(RECEIVER_ID, BOT_TOKEN, "Change detected!")
            sendTelegramImage(RECEIVER_ID, BOT_TOKEN, screenshot)

            # 1 - Check Network Test
            if checkNetworkTest():
                print("[LOGS] 'Network Test' Error. Notifying user...")
                notify_loop(args=args, error_msg="Network test Error")
            # 2 - Check Wrapping previous session
            elif checkWrappingSession():
                print("[LOGS] 'Wrapping Previous Session' Error. Notifying user...")
                notify_loop(args=args, error_msg="'Wrapping previous session' Error")
            else:
                # 3 - Check Queue finished
                if checkQueueFinished():
                    notify_loop(args=args)
                    gameON = True
                # 4 - Check An unknown error of GeForce NOW or a wrong screenshot (didnt capture the GeForce NOW screen but something else)
                else:
                    print(f"[LOGS] {Fore.RED}UNKNOWN ERROR{Fore.RESET} during queue. Notifier will close.")
                    sendTelegramText(RECEIVER_ID, BOT_TOKEN, QUEUE_ERROR_MSG)

                    # DEBUG
                    try:
                        saveDebugImages(path_to_dir=os.path.join(SCREENSHOT_PATH, f"debug/{i}"), screenshot=screenshot, cropped_image=cropped_img, previous_image=prev_img)
                    except Exception as e:
                        print(f"[LOGS] Error while trying to save debug images. Exception: {e}")
                        pathlib.Path(os.path.join(SCREENSHOT_PATH, f"debug/{i}")).mkdir(parents=True, exist_ok=True)
                        try:
                            saveDebugImages(path_to_dir=os.path.join(SCREENSHOT_PATH, f"debug/{i}"), screenshot=screenshot, cropped_image=cropped_img, previous_image=prev_img)
                        except Exception as e:
                            print(f"[LOGS] ERROR while trying to save debug images. Will save images in screenshots/debug_error directory instead.  Exception: {e}")
                            try:
                                saveDebugImages(path_to_dir=os.path.join(SCREENSHOT_PATH, f"debug_error/{i}"), screenshot=screenshot, cropped_image=cropped_img, previous_image=prev_img)
                            except Exception as e:
                                print(f"[LOGS] Couldn't save images in screenshots/debug_error directory. Debug images will not be saved.  Exception: {e}")

                    # Terminate
                    import sys
                    sys.exit()
        
        # Update prev_img
        prev_img = cropped_img.copy()

        time.sleep(5)

if __name__ == '__main__':

    # Check if GFN is opened. If it is, show GFN window on screen
    isGFNOpen = showWindowOnScreen(WINDOW_TITLE)
    
    ### If GFN is opened:
    if isGFNOpen:
        maximizeWindow()

        ## If it is in queue:
        if isGFNInQueue() and not(isGFNInHome()):
            # Maximize
            maximizeWindow()

        ## If it is at home page:
        # Maximize window, then search for the GAME_NAME and enter its queue
        elif isGFNInHome() and not(isGFNInQueue()):
            # Maximize
            maximizeWindow()
            # Search for the GAME_NAME and enter its queue
            enterGameQueue(GAME_NAME)
        
        else:
            print(f"[LOGS] {Fore.RED}ERROR:{Fore.RESET} isGFNInHome = {isGFNInHome} and isGFNInQueue = {isGFNInQueue}. GFN Window cannot be at both home and queue at the same time.")

    if preferences.getGFNNPreferences()["openGeForce"]:
        ### If GFN is not opened already, open it
        if not isGFNOpen:
            # Open GFN
            openWindow(GEFORCE_EXE_PATH)
            # Maximize
            maximizeWindow()
            # Search for the GAME_NAME and enter its queue
            enterGameQueue(GAME_NAME)
    
    time.sleep(5) # To wait for queue to load

    # By this point, GFN should be in queue, on screen, and maximized.
    if not isGFNInQueue():
        print(f"[LOGS] {Fore.RED}Fatal error!{Fore.RESET} '{GAME_NAME}' is NOT in queue according to function 'isGFNInQueue'.")
    else:
        print(f"[LOGS] '{GAME_NAME}' is now in queue, on screen, and maximized. Time: {get_time()}")

    # Start the GeForceNowNotifier (GFNN) loop for checking queue status
    main_loop(preferences.getGFNNPreferences())