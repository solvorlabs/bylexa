import os
import json

CONFIG_FILE_PATH = os.path.expanduser("~/.bylexa_config.json")

def save_token(token):
    config = {"user_token": token}
    with open(CONFIG_FILE_PATH, "w") as config_file:
        json.dump(config, config_file)

def load_token():
    try:
        with open(CONFIG_FILE_PATH, "r") as config_file:
            config = json.load(config_file)
            return config.get("user_token")
    except FileNotFoundError:
        return None
