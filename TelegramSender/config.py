import os
import pathlib
import pyautogui
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv() 

# Paths
PARENT_PATH = pathlib.Path(__file__).parent.resolve()
SCREENSHOT_PATH = os.path.join(PARENT_PATH, "screenshots")
IMAGES_PATH = os.path.join(PARENT_PATH, "assets/images")
PREFERENCES_PATH = os.path.join(PARENT_PATH, "preferences.json")
GEFORCE_EXE_PATH = r"C:\Users\ested\AppData\Local\NVIDIA Corporation\GeForceNOW\CEF\GeForceNOW.exe" # HARDCODED

# Telegram env
BOT_TOKEN = os.getenv('BOT_TOKEN')
RECEIVER_ID = os.getenv('RECEIVER_ID')

# Messages
CONFIRMATION_MSG = "Telegram connection successful! GeForce NOW Notifier has started."
QUEUE_MSG =  "Your game has started! Enjoy playing on GeForce NOW! You have 1 hour."
QUEUE_ERROR_MSG = "Sorry. We have encountered an unknown error during queue. Notifier will self-destruct."

# Loop
LOOP_TIME = 10 # mins

# Window
WINDOW_TITLE = "GeForce NOW"
GAME_NAME = None

# Get screen resolution
screensize = pyautogui.size()

## FOR "LOOKING FOR NEXT RIG" TEXT: left=20, top=50, right=600, bottom=260 (from 2160 x 1440 monitor)
# If you change these values, then use updateInQueueImage in utils.py to apply changes (Uncomment line 13 in main.py)
LEFT_QUEUE_CROP_PERCENT   = 0.0092592593
TOP_QUEUE_CROP_PERCENT    = 0.0347222222 
RIGHT_QUEUE_CROP_PERCENT  = 0.2777777778 
BOTTOM_QUEUE_CROP_PERCENT = 0.1805555556 

LEFT_QUEUE_CROP = screensize[0] * round(LEFT_QUEUE_CROP_PERCENT, 7)
TOP_QUEUE_CROP = screensize[1] * round(TOP_QUEUE_CROP_PERCENT, 7)
RIGHT_QUEUE_CROP = screensize[0] * round(RIGHT_QUEUE_CROP_PERCENT, 7)
BOTTOM_QUEUE_CROP = screensize[1] * round(BOTTOM_QUEUE_CROP_PERCENT, 7)
QUEUE_CROP = (LEFT_QUEUE_CROP, TOP_QUEUE_CROP, RIGHT_QUEUE_CROP, BOTTOM_QUEUE_CROP)

## FOR "Loading..." TEXT: left=20, top=50, right=600, bottom=260 (from 2160 x 1440 monitor)
# If you change these values, then use updateInLoadingImage in utils.py to apply changes (Uncomment line 14 in main.py)
LEFT_LOADING_CROP_PERCENT   = 0.0092592593
TOP_LOADING_CROP_PERCENT    = 0.0647222222 
RIGHT_LOADING_CROP_PERCENT  = 0.1777777778 
BOTTOM_LOADING_CROP_PERCENT = 0.1405555556 

LEFT_LOADING_CROP = screensize[0] * round(LEFT_LOADING_CROP_PERCENT, 7)
TOP_LOADING_CROP = screensize[1] * round(TOP_LOADING_CROP_PERCENT, 7)
RIGHT_LOADING_CROP = screensize[0] * round(RIGHT_LOADING_CROP_PERCENT, 7)
BOTTOM_LOADING_CROP = screensize[1] * round(BOTTOM_LOADING_CROP_PERCENT, 7)
LOADING_CROP = (LEFT_LOADING_CROP, TOP_LOADING_CROP, RIGHT_LOADING_CROP, BOTTOM_LOADING_CROP)

## FOR "Network Test..." TEXT: left=490, top=260, right=1670, bottom=1160 (from 2160 x 1440 monitor)
# If you change these values, then use updateInLoadingImage in utils.py to apply changes (Uncomment line 14 in main.py)

LEFT_NETWORK_CROP_PERCENT   = 490 / 2160
TOP_NETWORK_CROP_PERCENT    = 260 / 1440
RIGHT_NETWORK_CROP_PERCENT  = 1670 / 2160
BOTTOM_NETWORK_CROP_PERCENT = 1160 / 1440

LEFT_NETWORK_CROP = screensize[0] * round(LEFT_NETWORK_CROP_PERCENT, 7)
TOP_NETWORK_CROP = screensize[1] * round(TOP_NETWORK_CROP_PERCENT, 7)
RIGHT_NETWORK_CROP = screensize[0] * round(RIGHT_NETWORK_CROP_PERCENT, 7)
BOTTOM_NETWORK_CROP = screensize[1] * round(BOTTOM_NETWORK_CROP_PERCENT, 7)
NETWORK_CROP = (LEFT_NETWORK_CROP, TOP_NETWORK_CROP, RIGHT_NETWORK_CROP, BOTTOM_NETWORK_CROP)

# Misc
BR_CHAR = "-----------------------------------------------------------------------"
COLOR_FILTER_THRESHOLD = 200
QUEUE_COLOR_FILTER_THRESHOLD = 200 
IMAGE_DIFF_THRESHOLD = 18.0
QUEUE_IMAGE_DIFF_THRESHOLD = 15.0
NETWORK_IMAGE_DIFF_THRESHOLD = 5.0

DEBUG = True