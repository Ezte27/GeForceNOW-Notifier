import time
from colorama import Fore
from utils import *
from config import *

def test_areImagesEqual(image_type="queue") -> bool:
    print(f"'areImagesEqual' test running ({image_type})...")
    screenshot_types = {"queue": "GFN_in_queue_debug_4.png", "loading":"GFN_Loading_game.png", "network":"GFN_network_test.png", "wrapping":"GFN_wrapping_session.png"}
    gfn_image_types = {"queue": "GFN_in_queue.png", "loading":"GFN_in_loading.png", "network": "GFN_network_error.png", "wrapping": "GFN_wrapping_session.png",}
    crop_types = {"queue": QUEUE_CROP, "loading": LOADING_CROP, "network": NETWORK_CROP, "wrapping": QUEUE_CROP}

    screenshot = Image.open(os.path.join(IMAGES_PATH, f"unfinished/{screenshot_types[image_type]}"))
    image = screenshot.crop(crop_types[image_type]) # Crop the image
    img = isGFNInQueueImageFilter(image)
    gfn_image = Image.open(os.path.join(IMAGES_PATH, gfn_image_types[image_type]))

    try:
        areImagesEqual(img, gfn_image, 1, "test")
        print(f"'areImagesEqual' test {Fore.GREEN}passed{Fore.RESET}.")
        return True
    except Exception as e:
        print(f"'areImagesEqual' test {Fore.RED}failed{Fore.RESET}. Exception: {e}")
        return False

def test_all_areImagesEqual():
    areImagesEqual_types = ["queue", "loading", "network", "wrapping"]
    for i in areImagesEqual_types:
        test_areImagesEqual(i)
        time.sleep(0.5)

def run_all_tests():
    print("Running all tests...")
    time.sleep(0.5)
    # test_all_areImagesEqual()
    test_areImagesEqual("queue")

if __name__ == '__main__':
    run_all_tests()