import os
from shutil import which
import argparse
import configparser
import subprocess

steamcmd_binary = "steamcmd"
tmux_binary = "tmux"
arma3_server_steam_code = "233780"
def_config_file = "config.ini"

def updateConfig():
    return

# load existing config
config = configparser.ConfigParser()
config.read(def_config_file)
if 'steam' in config:
    if 'user' in config['steam']:
        STEAM_USERNAME = config['steam']['user']

    if 'password' in config['steam']:
        STEAM_PASSWORD = config['steam']['password']

if 'state' in config:
    if 'serverlist' in config['state']:
        SERVER_LIST = config['state']['serverlist'].split(",")

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="subcommand")

parser_create = subparsers.add_parser("create", help="create a new arma 3 server instance")
parser_create.add_argument("name", nargs=1, help="Name of server to be created")

parser_update = subparsers.add_parser("update", help="update existing arma 3 server")
parser_update.add_argument("name", nargs=1, help="Name of server to be updated")
parser_update.add_argument("--mods-only", help="Only update mods", action="store_true")
parser_update.add_argument("--server-only", help="Only update server", action="store_true")

#parser.add_argument("delete", nargs="?", help="delete a server instance")
#parser.add_argument("start", nargs="?", help="start a server instance")
#parser.add_argument("stop", nargs="?", help="stop a server instance")
#parser.add_argument("shell", nargs="?", help="access a server instance console")
#parser.add_argument("list", nargs="?", help="list all servers")

args = parser.parse_args()

# Check if steamcmd is available on the system
steamcmd_exists = which(steamcmd_binary) is not None
if not steamcmd_exists:
    print("SteamCMD is not available on this system or is not available in the path.")
    exit(1)

tmux_exists = which(tmux_binary) is not None
if not tmux_exists:
    print("tmux is not available on this system or is not available in the path.")
    exit(1)

if args.subcommand is not None:
    if args.subcommand == 'create':
        if 'STEAM_USERNAME' not in locals():
            STEAM_USERNAME = input("What is your steam username? ")

        if 'STEAM_PASSWORD' not in locals():
            STEAM_PASSWORD = input("What is your steam password? ")

        SERVER_DIR = input("Installation directory for server? ")

        print("####################")
        print("Starting SteamCMD...")
        print("####################")

        steamcmd_run = subprocess.run(["steamcmd", "+login", STEAM_USERNAME, STEAM_PASSWORD, "+force_install_dir", SERVER_DIR, "+app_update", arma3_server_steam_code, "validate", "+quit"])

        print("####################")
        print("SteamCMD Closed")
        print("####################")
        
        if steamcmd_run.returncode == 0:
            print("Server installed successfully")