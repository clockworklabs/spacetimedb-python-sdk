import os
import configparser

# Get the path to the user's home directory
home_dir = os.path.expanduser("~")

# Create a path to the settings file in the user's home directory
settings_path = os.path.join(home_dir, ".spacetime_mud", "settings.ini")

# Create a ConfigParser object and read the settings file (if it exists)
config = configparser.ConfigParser()
if os.path.exists(settings_path):
    config.read(settings_path)
else:
    # Set some default config values
    config["main"] = {        
    }

def set_config(config_in):
    for key, value in config_in:
        config["main"][key] = value
    save()

def get_string(key):
    if key in config["main"]:
        return config["main"][key]
    return None


def set_string(key, value):
    # Update config values at runtime
    config["main"][key] = value
    save()


def save():
    # Write the updated config values to the settings file
    os.makedirs(os.path.dirname(settings_path), exist_ok=True)
    with open(settings_path, "w") as f:
        config.write(f)
