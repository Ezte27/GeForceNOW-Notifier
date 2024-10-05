# from email.message import EmailMessage #
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

import pyautogui
import numpy as np
import cv2

from PIL import Image 
from easyocr import Reader
  
import time, pathlib, os, ctypes

### 
input("Press enter to start GEFORCE NOW notifier.")
time.sleep(0.5)
print("Please make sure that you are on the GeForce NOW window and that it is maximized.")
time.sleep(0.5)
###

# Variables
PARENT_PATH = pathlib.Path(__file__).parent.resolve()
SCREENSHOT_PATH = os.path.join(PARENT_PATH, "screenshots")
SERVER = "smtp.gmail.com"
PORT_NUMBER_TLS = 587
PORT_NUMBER_SSL = 465

# TODO: Add this google password to a .env file
APP_PASSWORD = "llde dekc jhop izdw"

SUBJECT = "GeForce NOW Notifier"
TEST_MSG = f'Subject: {SUBJECT}\n\nEmail Confirmation. Gmail Connection Successful.'

QUEUE_MSG =  "Gamers ahead of you: <h2>#QUEUE#</h2>" # Replace #QUEUE# with number when sending message

SENDER_EMAIL = "estedcg27@gmail.com"
RECEIVER_EMAIL = "estedcg27@gmail.com"

LOOP_TIME = 10 # mins

# Hardcoded
# FOR QUEUE NUMBER: left = 301, top = 275, right = 358, bottom = 306 (from 1440p monitor)
LEFT_CROP_PERCENT   = 0.1393518519
TOP_CROP_PERCENT    = 0.1909722222
RIGHT_CROP_PERCENT  = 0.1657407407
BOTTOM_CROP_PERCENT = 0.2125000000

# Get screen resolution
screensize = (ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1))

LEFT_CROP = screensize[0] * round(LEFT_CROP_PERCENT, 3)
TOP_CROP = screensize[1] * round(TOP_CROP_PERCENT, 3)
RIGHT_CROP = screensize[0] * round(RIGHT_CROP_PERCENT, 3)
BOTTOM_CROP = screensize[1] * round(BOTTOM_CROP_PERCENT, 3)

def establish_connection_msg(receiver_email, msg, sender_email = "estedcg27@gmail.com", app_password = APP_PASSWORD, server = SERVER, port_number_tls = PORT_NUMBER_TLS):
    with smtplib.SMTP(server, port_number_tls) as smtp:
        smtp.ehlo()     # Identify ourselves with the mail server we are using. 
        smtp.starttls() # Encrypt our connection
        smtp.ehlo()     # Reidentify our connection as encrypted with the mail server

        smtp.login(sender_email, app_password) # Use the smtp.login() function to authenticate your account details.

        smtp.sendmail(sender_email, receiver_email, msg) # Send the email using the sendmail() method.
    
    print(f"[LOGS] Email message sent! Established Gmail connection confirmation - Time: {get_time()}")

def take_screenshot(img_name):
    # Take screenshot using pyautogui
    image = pyautogui.screenshot()

    # Convert PIL to np array and from RGB to BGR
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # Write to disk
    cv2.imwrite(f"screenshots/{img_name}.png", image)

def send_screenshot(receiver_email, subject, img_name, sender_email = SENDER_EMAIL, app_password = APP_PASSWORD, server = SERVER, port_number_ssl = PORT_NUMBER_SSL):
    try:
        # Send Image
        message = EmailMessage()                        
        message['Subject'] = subject 
        message['From'] = sender_email                   
        message['To'] = receiver_email                   
        message.set_content(img_name) 

        with open(os.path.join(SCREENSHOT_PATH, f"{img_name}.png"), 'rb') as f:
            image_data = f.read()
            image_type = "png"
            image_name = f.name

        message.add_attachment(image_data, maintype='image', subtype=image_type, filename=image_name)

        with smtplib.SMTP_SSL(server, port_number_ssl) as smtp:
            
            smtp.login(sender_email, app_password)              
            smtp.send_message(message)
        
        print(f"[LOGS] Email message sent! Image attached: {img_name}.png - Time: {get_time()}")

    except Exception as e:
        time.sleep(5)
        print(f"[ERROR] -> {e}")

def send_queue_info(receiver_email, number:int, msg:str, sender_email = "estedcg27@gmail.com", app_password = APP_PASSWORD, server = SERVER, port_number_tls = PORT_NUMBER_TLS):
    with smtplib.SMTP(server, port_number_tls) as smtp:
        smtp.ehlo()     # Identify ourselves with the mail server we are using. 
        smtp.starttls() # Encrypt our connection
        smtp.ehlo()     # Reidentify our connection as encrypted with the mail server

        smtp.login(sender_email, app_password) # Use the smtp.login() function to authenticate your account details.

        # Creating and attaching html to message
        message = MIMEMultipart()
        message['Subject'] = SUBJECT
        message['From'] = SENDER_EMAIL                   
        message['To'] = RECEIVER_EMAIL  
        message.attach(MIMEText(msg.replace("#QUEUE#", str(number)), 'html'))

        smtp.sendmail(sender_email, receiver_email, message.as_string()) # Send the email using the sendmail() method.
    
    print(f"[LOGS] Email message sent! Sent queue info - Time: {get_time()}")

def get_time() -> str:
    return time.strftime("%H:%M", time.localtime())

def get_et(waiting_time) -> str:
    """
    waiting_time : int (in minutes)
    """
    # Calculate estimated time (et)
    current_time = (time.strftime("%H:%M", time.localtime())).split(":")
    total_time_min = (int(current_time[0])*60) + int(current_time[1]) + waiting_time
    hr_min = str(total_time_min / 60).split(".")
    hrs = int(hr_min[0])
    mins = round(float(f"0.{hr_min[1]}") * 60)
    return f"{hrs}:{mins}"

def crop_screenshot(img_name, left = LEFT_CROP, top = TOP_CROP, right = RIGHT_CROP, bottom = BOTTOM_CROP) -> None:
    img = Image.open(os.path.join(SCREENSHOT_PATH, f"{img_name}.png")) 
    img_cropped = img.crop((left, top, right, bottom))
    
    # Convert to grayscale
    image = img_cropped.convert('L')

    # Write to disk
    image.save(f"screenshots/cropped/{img_name}.png", "PNG")

def get_numbers_in_image(img_name, language="en") -> int:
    # Load the image
    img_path = os.path.join(SCREENSHOT_PATH, f"cropped/{img_name}.png")

    # Create an OCR reader using the specified language
    reader = Reader([language])

    # Perform text recognition on the image
    result = reader.readtext(img_path)

    # Extract and print the recognized text
    recognized_text = result[0][1]

    # Extract the numbers from the text
    numbers = [int(s) for s in recognized_text.split() if s.isdigit()][0]

    # Print the numbers
    print(f"[LOGS] Gamers ahead of you: {numbers}")

    # Return the numbers
    return numbers

def notifier_loop(receiver_email, waiting_time = 10, debug = False):
    i = 0
    while True:
        # Increase i number
        i += 1

        # Generate next screenshot name
        name = f"img_{str(i)}"

        # Take Screenshot
        print(f"[LOGS] Taking screenshot {name}...")
        take_screenshot(name)
        print(f"[LOGS] Screenshot {name} taken. ")

        # time.sleep(1)

        # # Send Screenshot
        # print(f"[LOGS] Sending screenshot {name}...")
        # send_screenshot(receiver_email, subject, name)

        time.sleep(1)
        
        # Crop Screenshot
        crop_screenshot(name)

        time.sleep(1)

        # Get numbers in cropped image
        numbers = get_numbers_in_image(name)

        # Send Queue Info
        send_queue_info(receiver_email, numbers, QUEUE_MSG)

        print(f"[LOGS] Waiting for next queue update (estimated time: {get_et(waiting_time)})...")

        if not debug:
            # Wait for 10 mins before taking next screenshot or sending queue info
            time.sleep(waiting_time * 60)
        else:
            time.sleep(25)

if __name__ == '__main__':
    # Wait 10 seconds
    time.sleep(10)

    # Confirm Gmail connection
    print("[LOGS] Trying to establish Gmail connection...")
    establish_connection_msg(RECEIVER_EMAIL, TEST_MSG)
    print("[LOGS] Established Gmail connection! Check your gmail for confirmation.")
    time.sleep(1)
    print("[LOGS] Initiating GeForce NOW Notifier")

    # Entering infinite loop
    notifier_loop(RECEIVER_EMAIL, waiting_time = LOOP_TIME, debug = False)
