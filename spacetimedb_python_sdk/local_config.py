""" This is an optional component that allows you to store your settings to a config file.
    In the conext of SpacetimeDB, this is useful for storing the user's auth token so you can 
    connect to the same identity each time you run your program.

    Default settings.ini location is USER_DIR/.spacetime_python_sdk/settings.ini

    Example usage:

    import spacetimedb_python_sdk.local_config as local_config

    # Initialize the config file
    local_config.init()

    # Get the auth token if it exists
    auth_token = local_config.get_string("auth_token")

    ... use auth_token to connect to SpacetimeDB ...

    # When you get your token from SpacetimeDB, save it to the config file
    local_config.set_string("auth_token", auth_token)

    # Next time you run the program, it will load the same token 
""" 

import os
import configparser
import sys

config = None
settings_path = None

def init(config_folder = None, config_file = None, config_root = None, config_defaults = None):
    """
    Initialize the config file

    Format of config defaults is a dictionary of key/value pairs 

    Example:

        import spacetimedb_python_sdk.local_config as local_config

        config_defaults = { "open_ai_key" : "12345" }
        local_config.init(".my_config_folder", config_defaults = config_defaults)
        local_config.get_string("open_ai_key") # returns "12345"

        local_config.set_string("auth_token", auth_token)

    Args:
        config_folder : folder to store the config file in, Default: .spacetime_python_sdk
        config_file : name of the config file, Default: settings.ini
        config_root : root folder to store the config file in, Default: USER_DIR
        config_defaults : dictionary of default values to store in the config file, Default: None
    """

    global config
    global settings_path

    if config_root is None:
        config_root = os.path.expanduser("~")
    if config_folder is None:
        config_folder = ".spacetime_python_sdk"
    if config_file is None:
        config_file = "settings.ini"

    # this allows you to specify a different settings file from the command line
    if "--client" in sys.argv:
        client_index = sys.argv.index("--client")
        config_file_prefix = config_file.split(".")[0]
        config_file_ext = config_file.split(".")[1]
        config_file = "{}_{}.{}".format(config_file_prefix,sys.argv[client_index + 1],config_file_ext)

    settings_path = os.path.join(config_root, config_folder, config_file)

    # Create a ConfigParser object and read the settings file (if it exists)
    config = configparser.ConfigParser()
    if os.path.exists(settings_path):
        config.read(settings_path)
    else:
        # Set some default config values
        config["main"] = {}
        if config_defaults is not None:            
                for key, value in config_defaults.items():
                    config["main"][key] = value

def set_config(config_in):
    global config

    for key, value in config_in:
        config["main"][key] = value
    _save()

def get_string(key):
    global config

    if key in config["main"]:
        return config["main"][key]
    return None

def set_string(key, value):
    global config

    # Update config values at runtime
    config["main"][key] = value
    _save()

def _save():
    global settings_path
    global config

    # Write the updated config values to the settings file
    os.makedirs(os.path.dirname(settings_path), exist_ok=True)
    with open(settings_path, "w") as f:
        config.write(f)
