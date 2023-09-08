# PyHQ (System) - MessageBox

''' This is the "MessageBox" module. '''

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
import pyautogui

# Function 1 - Alert
def alert(title="", text="", button=""):
    # Checking the Data Type of "title"
    if (isinstance(title, str)):
        # Checking the Data Type of "text"
        if (isinstance(text, str)):
            # Checking the Data Type of "button"
            if (isinstance(button, str)):
                # Displaying the Message Box
                pyautogui.alert(title=title, text=text, button=button)
            else:
                raise TypeError("The 'button' argument must be a string.")
        else:
            raise TypeError("The 'text' argument must be a string.")
    else:
        raise TypeError("The 'title' argument must be a string.")

# Function 2 - Confirm
def confirm(title="", text="", buttons=[]):
    # Checking the Data Type of "title"
    if (isinstance(title, str)):
        # Checking the Data Type of "text"
        if (isinstance(text, str)):
            # Checking the Data Type of "buttons"
            if (isinstance(buttons, list)):
                # Displaying the Message Box
                pyautogui.confirm(title=title, text=text, buttons=buttons)
            else:
                raise TypeError("The 'buttons' argument must be a list.")
        else:
            raise TypeError("The 'text' argument must be a string.")
    else:
        raise TypeError("The 'title' argument must be a string.")

# Function 3 - Prompt
def prompt(title="", text="", default=""):
    # Checking the Data Type of "title"
    if (isinstance(title, str)):
        # Checking the Data Type of "text"
        if (isinstance(text, str)):
            # Checking the Data Type of "default"
            if (isinstance(default, str)):
                # Displaying the Message Box
                return pyautogui.prompt(title=title, text=text, default=default)
            else:
                raise TypeError("The 'default' argument must be a string.")
        else:
            raise TypeError("The 'text' argument must be a string.")
    else:
        raise TypeError("The 'title' argument must be a string.")

# Function 4 - Password
def password(title="", text="", default="", mask="*"):
    # Checking the Data Type of "title"
    if (isinstance(title, str)):
        # Checking the Data Type of "text"
        if (isinstance(text, str)):
            # Checking the Data Type of "default"
            if (isinstance(default, str)):
                # Checking the Data Type of "mask"
                if (isinstance(mask, str)):
                    # Displaying the Message Box
                    return pyautogui.password(title=title, text=text, default=default, mask=mask)
                else:
                    raise TypeError("The 'mask' argument must be a string.")
            else:
                raise TypeError("The 'default' argument must be a string.")
        else:
            raise TypeError("The 'text' argument must be a string.")
    else:
        raise TypeError("The 'title' argument must be a string.")