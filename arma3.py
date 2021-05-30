import os
from shutil import which
import argparse
import configparser
import subprocess

steamcmd_binary = "steamcmd"
tmux_binary = "tmux"
def_config_file = "config.ini"

def getArmaServer(username, password, dir):
    arma3_server_steam_code = "233780"
    print("\n####################")
    print("Starting SteamCMD...")
    print("####################\n")

    # automated steamcmd command
    steamcmd_run = subprocess.run(["steamcmd", "+login", username, password, "+force_install_dir", dir, "+app_update", arma3_server_steam_code, "validate", "+quit"])

    print("\n####################")
    print("SteamCMD Closed")
    print("####################\n")

    return steamcmd_run.returncode

def getServerPathFromName(name, serverlist):
    SERVER_NAME = None
    for server in serverlist:
        serverconfig = configparser.ConfigParser()
        serverconfig.read(server + "/config.ini")
        SERVER_DIR = serverconfig['general']['path']
        SERVER_NAME = serverconfig['general']['name']
        if SERVER_NAME == name:
            return SERVER_DIR
    
    return None

def main():
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

    # Handle cli arguments
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="subcommand")

    parser_create = subparsers.add_parser("create", help="create a new arma 3 server instance")
    parser_create.add_argument("name", nargs=1, help="Name of server to be created")

    parser_update = subparsers.add_parser("update", help="update existing arma 3 server")
    parser_update.add_argument("name", nargs=1, help="Name of server to be updated")
    parser_update.add_argument("--mods-only", help="Only update mods", action="store_true")
    parser_update.add_argument("--server-only", help="Only update server", action="store_true")

    parser_modify = subparsers.add_parser("modify", help="modify existing arma 3 server")
    parser_modify.add_argument("name", nargs=1, help="Name of server to be modified")
    parser_modify.add_argument("-m", "--mod", nargs="?", help="Add mod (by steam workshop URL) to server", action="append")
    parser_modify.add_argument("-p", "--port", type=int, help="Set port of server")

    #parser.add_argument("delete", nargs="?", help="delete a server instance")
    #parser.add_argument("start", nargs="?", help="start a server instance")
    #parser.add_argument("stop", nargs="?", help="stop a server instance")
    #parser.add_argument("shell", nargs="?", help="access a server instance console")
    #parser.add_argument("list", nargs="?", help="list all servers")

    args = parser.parse_args()
    #print(args)  # DEBUG

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
        if args.subcommand == 'create' or args.subcommand == 'update':
            if 'STEAM_USERNAME' not in locals():
                STEAM_USERNAME = input("What is your steam username? ")

            if 'STEAM_PASSWORD' not in locals():
                STEAM_PASSWORD = input("What is your steam password? ")

        if args.subcommand == 'create':
            SERVER_DIR = input("Installation directory for server? ")
            SERVER_NAME = args.name[0]
            SERVER_CONF_LOCATION = SERVER_DIR + "/config.ini"

            # automated steamcmd command
            steam_success = getArmaServer(STEAM_USERNAME, STEAM_PASSWORD, SERVER_DIR)

            if steam_success == 0:
                print("Server installed successfully")
            else:
                exit(steam_success)

            print("Writing server config...")
            
            serverconfig = configparser.ConfigParser()
            serverconfig['general'] = {}
            serverconfig['general']['name'] = SERVER_NAME
            serverconfig['general']['path'] = SERVER_DIR
            serverconfig['server'] = {}
            serverconfig['server']['mods'] = ""

            with open(SERVER_CONF_LOCATION, 'w') as serverconfig_file:
                serverconfig.write(serverconfig_file)

            if 'SERVER_LIST' not in locals():
                SERVER_LIST = []
                SERVER_LIST.append(SERVER_DIR)

        if args.subcommand == 'update':
            if 'SERVER_LIST' not in locals():
                print("No servers are available!")
                exit(1)

            SERVER_DIR = getServerPathFromName(args.name[0], SERVER_LIST)

            if SERVER_DIR is None:
                print("That server was not found!")
                exit(1)

            steam_success = getArmaServer(STEAM_USERNAME, STEAM_PASSWORD, SERVER_DIR)

            if steam_success == 0:
                print("Server updated successfully")
            else:
                exit(steam_success)

        if args.subcommand == 'modify':
            SERVER_DIR = getServerPathFromName(args.name[0], SERVER_LIST)

            if SERVER_DIR is None:
                print("That server was not found!")
                exit(1)

        # update config
        config['steam'] = {}
        config['state'] = {}
        if 'STEAM_USERNAME' in locals():
            config['steam']['user'] = STEAM_USERNAME

        if 'STEAM_PASSWORD' in locals():
            config['steam']['password'] = STEAM_PASSWORD

        if 'SERVER_LIST' in locals():
            config['state']['serverlist'] = ",".join(SERVER_LIST)

        with open(def_config_file, 'w') as config_file:
            config.write(config_file)

if __name__ == '__main__':
    main()