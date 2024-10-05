from colorama import Fore
import time
import json
# GFNN = GeForce Now Notifier
class Preferences:
    def __init__(self, path:str) -> None:
        """
        path:str is the path to the preferences.json file where preferences are stored
        """
        self.args = dict()
        self.path = path
    def loadGFNNPreferences(self) -> None:
        # Arguments
        with open(self.path, "rb") as f:
            try:
                self.args = json.load(f)
            except json.decoder.JSONDecodeError:
                self.args:dict = {"sendMethod":"telegram", "openGeForce":True, "sendConfirmation":True, "sendImageConfirmation":True}
            except Exception as e:
                print(f"UNKNOWN ERROR - {e}")
    def editGFNNPreferences(self) -> None:
        editPreferencesFlag = input(f"Edit preferences?({Fore.GREEN}y{Fore.RESET}/{Fore.RED}n{Fore.RESET})")
        if editPreferencesFlag.lower() == "y" or editPreferencesFlag.lower() == "yes":
            time.sleep(0.5)
            print("-----------------------------------------------------------------------")
            time.sleep(0.3)
            print("Preference Editor (type 'help' for help): ")
            time.sleep(0.3)

            # Edit sendMethod
            # sendMethod can either be "telegram", "email", "whatsapp" (from best to worst)
            chose = False
            time.sleep(0.5)
            while not chose:
                i = input(f"Choose a send method: (Current preference: {self.args['sendMethod']})")
                if i.lower() == i.lower() == "telegram":
                    self.args["sendMethod"] = "telegram" 
                    chose = True
                elif i.lower() == i.lower() == "email":
                    self.args["sendMethod"] = "email" 
                    chose = True
                elif i.lower() == i.lower() == "whatsapp":
                    self.args["sendMethod"] = "whatsapp" 
                    chose = True
                elif i == "":
                    print(f"'sendMethod' will not be edited.")
                    chose = True
                elif i.lower() == "h" or i.lower() == "help":
                    print("Available options: telegram, email, whatsapp")
                else:
                    print("Invalid method. To get list of valid methods, please type 'help'.")
            
            # Edit openGeForce
            chose = False
            time.sleep(0.5)
            while not chose:
                i = input(f"At start, should this program open GeForce NOW window? (Current preference: {self.args['openGeForce']})")
                if i.lower() == "yes" or i.lower() == "y":
                    self.args["openGeForce"] = True 
                    chose = True
                elif i.lower() == "no" or i.lower() == "n":
                    self.args["openGeForce"] = False
                    chose = True
                elif i == "":
                    print(f"'openGeForce' will not be edited.")
                    chose = True
                elif i.lower() == "h" or i.lower() == "help":
                    print("Available options: yes, no. If no, then this program assumes that when you hit start, you have already opened the GeForce NOW app.")
                else:
                    print("Invalid input. To get list of valid inputs, please type 'help'.")

            # Edit sendConfirmation
            chose = False
            time.sleep(0.5)
            while not chose:
                i = input(f"Should this program send a message confirming that it has started successfully? (Current preference: {self.args['sendConfirmation']})")
                if i.lower() == "yes" or i.lower() == "y":
                    self.args["sendConfirmation"] = True 
                    chose = True
                elif i.lower() == "no" or i.lower() == "n":
                    self.args["sendConfirmation"] = False
                    chose = True
                elif i == "":
                    print(f"'sendConfirmation' will not be edited.")
                    chose = True
                elif i.lower() == "h" or i.lower() == "help":
                    print("Available options: yes, no (this confirmation is useful when debugging)")
                else:
                    print("Invalid input. To get list of valid inputs, please type 'help'.")
            
            # Edit sendImageConfirmation
            if self.args["sendMethod"] == 'telegram':
                chose = False
                time.sleep(0.5)
                while not chose:
                    i = input(f"Should this program send a screenshot of GeForce NOW screen when it has detected that queue has finished? (Current preference: {self.args['sendImageConfirmation']})")
                    if i.lower() == "yes" or i.lower() == "y":
                        self.args["sendImageConfirmation"] = True 
                        chose = True
                    elif i.lower() == "no" or i.lower() == "n":
                        self.args["sendImageConfirmation"] = False
                        chose = True
                    elif i == "":
                        print(f"'sendImageConfirmation' will not be edited.")
                        chose = True
                    elif i.lower() == "h" or i.lower() == "help":
                        print("Available options: yes, no (these screenshots are useful when debugging)")
                    else:
                        print("Invalid input. To get list of valid inputs, please type 'help'.")
            
            time.sleep(0.3)
            print("-----------------------------------------------------------------------")
            time.sleep(0.5)
    def updateGFNNPreferences(self) -> None:
        with open(self.path, "w") as file:
            json.dump(self.args, file)
    def getGFNNPreferences(self) -> dict:
        return self.args