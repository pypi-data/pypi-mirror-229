# PyHQ (System) - Brightness

''' This is the "Brightness" module. '''

'''
Copyright 2023 Aniketh Chavare

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

# Imports
import platform
import screen_brightness_control as sbc

# Function 1 - Max
def max():
    # Checking the OS
    if (platform.uname().system in ["Windows", "Linux"]):
        # Setting the Brightness
        sbc.set_brightness(100)
    else:
        raise Exception("This function only works on Windows and Linux.")

# Function 2 - Min
def min():
    # Checking the OS
    if (platform.uname().system in ["Windows", "Linux"]):
        # Setting the Brightness
        sbc.set_brightness(0)
    else:
        raise Exception("This function only works on Windows and Linux.")

# Function 3 - Set
def set(value, display=0):
    # Checking the OS
    if (platform.uname().system in ["Windows", "Linux"]):
        # Checking the Data Type of "value"
        if (isinstance(value, (int, float))):
            # Checking the Data Type of "display"
            if (isinstance(display, (int, str))):
                # Setting the Brightness
                sbc.set_brightness(value, display=display)
            else:
                raise TypeError("The 'display' argument must be an integer.")
        else:
            raise TypeError("The 'value' argument must be an integer or a float.")
    else:
        raise Exception("This function only works on Windows and Linux.")

# Function 4 - Fade
def fade(final, start=None, interval=0.01, increment=1, blocking=True):
    # Checking the OS
    if (platform.uname().system in ["Windows", "Linux"]):
        # Checking the Data Type of "final"
        if (isinstance(final, (int, float))):
            # Checking the Data Type of "start"
            if (isinstance(start, (int, float)) or (start == None)):
                # Checking the Data Type of "interval"
                if (isinstance(interval, (int, float))):
                    # Checking the Data Type of "increment"
                    if (isinstance(increment, (int, float))):
                        # Checking the Data Type of "blocking"
                        if (isinstance(blocking, bool)):
                            # Setting the Brightness
                            sbc.fade_brightness(final, start=start, interval=interval, increment=increment, blocking=blocking)
                        else:
                            raise TypeError("The 'blocking' argument must be a boolean.")
                    else:
                        raise TypeError("The 'increment' argument must be an integer or a float.")
                else:
                    raise TypeError("The 'interval' argument must be an integer or a float.")
            else:
                raise TypeError("The 'start' argument must be an integer or a float.")
        else:
            raise TypeError("The 'final' argument must be an integer or a float.")
    else:
        raise Exception("This function only works on Windows and Linux.")

# Function 5 - Get
def get():
    # Checking the OS
    if (platform.uname().system in ["Windows", "Linux"]):
        # Returning the Data
        return {"Brightness": sbc.get_brightness(), "Monitors": list()}
    else:
        raise Exception("This function only works on Windows and Linux.")

# Function 6 - List
def list(info=False):
    # Checking the OS
    if (platform.uname().system in ["Windows", "Linux"]):
        # Checking the Data Type of "info"
        if (isinstance(info, bool)):
            # Checking the Value of "info"
            if (info):
                # Returning the Data
                return sbc.list_monitors_info()
            else:
                # Returning the Data
                return sbc.list_monitors()
        else:
             raise TypeError("The 'info' argument must be a boolean.")
    else:
        raise Exception("This function only works on Windows and Linux.")