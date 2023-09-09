# PyHQ (Fun) - Init

''' This is the __init__.py file. '''

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
import json
import random
import pyjokes
import requests
import randfacts

# Function 1 - Joke
def joke(type="random"):
    # Variables
    joke_types = ["random", "general", "programming", "knock-knock"]
    programming_joke_random = random.choice([1, 2])
    api_endpoint = "https://official-joke-api.appspot.com/jokes/{0}"

    # Checking the Data Type of "type"
    if (isinstance(type, str)):
        # Checking the Value of "type"
        if (type in joke_types):
            # Fetching and Returning the Joke
            if (type == "random"):
                # Fetching the Joke
                try:
                    response = json.loads(requests.get(api_endpoint.format("random")).text)
                except requests.ConnectionError:
                    raise ConnectionError("A connection error occurred. Please try again.")
                except:
                    raise Exception("Something went wrong. Please try again.")

                # Deleting Unwanted Keys
                del response["type"]
                del response["id"]

                # Returning the Joke
                return response["setup"] + " " + response["punchline"]
            elif (type in ["general", "knock-knock"]):
                # Fetching the Joke
                try:
                    response = json.loads(requests.get(api_endpoint.format(type + "/random")).text)[0]
                except requests.ConnectionError:
                    raise ConnectionError("A connection error occurred. Please try again.")
                except:
                    raise Exception("Something went wrong. Please try again.")

                # Deleting Unwanted Keys
                del response["type"]
                del response["id"]

                # Returning the Joke
                return response["setup"] + " " + response["punchline"]
            elif (type == "programming"):
                # Checking the Value of "programming_joke_random"
                if (programming_joke_random == 1):
                    # Fetching the Joke
                    try:
                        response = json.loads(requests.get(api_endpoint.format(type + "/random")).text)[0]
                    except requests.ConnectionError:
                        raise ConnectionError("A connection error occurred. Please try again.")
                    except:
                        raise Exception("Something went wrong. Please try again.")

                    # Deleting Unwanted Keys
                    del response["type"]
                    del response["id"]

                    # Returning the Joke
                    return response["setup"] + " " + response["punchline"]
                elif (programming_joke_random == 2):
                    # Returning the Joke
                    return pyjokes.get_joke()
        else:
            raise Exception("The 'type' argument must be either 'random', 'general', 'programming', or 'knock-knock'.")
    else:
        raise TypeError("The 'type' argument must be a string.")

# Function 2 - Fact
def fact(filter=True, unsafe=False):
    # Variables
    parameters = ["filter", "unsafe"]

    # Parameters & Data Types
    paramaters_data = {
        "filter": [bool, "a boolean"],
        "unsafe": [bool, "a boolean"]
    }

    # Checking the Data Types
    for parameter in parameters:
        if (isinstance(eval(parameter), paramaters_data[parameter][0])):
            pass
        else:
            raise Exception("The '{0}' argument must be {1}.".format(parameter, paramaters_data[parameter][1]))

    # Returning the Fact
    return randfacts.get_fact(filter_enabled=filter, only_unsafe=unsafe)

# Function 3 - Bored
def bored():
    # Fetching and Returning the Data
    try:
        return json.loads(requests.get("https://boredapi.com/api/activity").text)
    except requests.ConnectionError:
        raise ConnectionError("A connection error occurred. Please try again.")
    except:
        raise Exception("Something went wrong. Please try again.")