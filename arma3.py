import os
from shutil import which
import argparse
import configparser
import subprocess
import urllib.parse as urlparse
import shutil

steamcmd_binary = "steamcmd"
tmux_binary = "tmux"
def_config_file = "config.ini"

SERVER_MOD_DIR = "steamapps/workshop/content/107410/"
STEAM_ARMA3_DEDSERVER_CODE = "233780"
STEAM_ARMA3_WORKSHOP_CODE = "107410"

def printSteamHeaderStart():
    print("\n####################")
    print("Starting SteamCMD...")
    print("####################\n")

def printSteamHeaderEnd():
    print("\n####################")
    print("SteamCMD Closed")
    print("####################\n")

def getArmaServer(username, password, dir):
    
    printSteamHeaderStart()

    # automated steamcmd command
    steamcmd_run = subprocess.run(["steamcmd", "+login", username, password, "+force_install_dir", dir, "+app_update", STEAM_ARMA3_DEDSERVER_CODE, "validate", "+quit"])

    printSteamHeaderEnd

    return steamcmd_run.returncode

def getSteamMods(username, password, mod_ids, dir):
    
    printSteamHeaderStart()

    # automated steamcmd command
    mod_requests = []
    for mod_id in mod_ids:
        mod_requests.append("+workshop_download_item")
        mod_requests.append(STEAM_ARMA3_WORKSHOP_CODE)
        mod_requests.append(mod_id)
    
    steamcmd_run = subprocess.run(["steamcmd", "+login", username, password, "+force_install_dir", dir] + mod_requests + ["+quit"])

    printSteamHeaderEnd()

    return steamcmd_run.returncode

def startServer(path, profile, port, mods):
    configPath = profile + "/" + "server.cfg"
    modList = ";".join(mods)
    arma3server_run = subprocess.run(["./arma3server", "-config=" + configPath, "-port="+ port, "-profile="+ profile, "-mod=" + modList], cwd=path)

    return arma3server_run

def lowercase_all(dir):
    # renames all subforders of dir, not including dir itself
    def rename_all(root, items):
        for name in items:
            try:
                os.rename(os.path.join(root, name), os.path.join(root, name.lower()))
            except OSError:
                pass # can't rename it, so what

    # starts from the bottom so paths further up remain valid after renaming
    for root, dirs, files in os.walk(dir, topdown=False):
        rename_all(root, dirs)
        rename_all(root, files)

def getServerPathFromName(name, serverlist):
    SERVER_NAME = None
    for server in serverlist:
        serverconfig = configparser.ConfigParser()
        conffile = server + "/config.ini"
        if not os.path.isfile(conffile):
            return None
        
        serverconfig.read(server + "/config.ini")
        SERVER_DIR = serverconfig['general']['path']
        SERVER_NAME = serverconfig['general']['name']
        if SERVER_NAME == name:
            return SERVER_DIR
    
    return None

def getModName(dir):
    file = dir + "/mod.cpp"

    with open(file, "r") as meta:
        for line in meta:
            if line.startswith("name"):
                name = line.partition("\"")[2]
                name = name.partition("\"")[0]
                return name

    return ""

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
    # -s parameter
    parser.add_argument("-s", "--save", help="Save steam login info to config file", action="store_true")

    subparsers = parser.add_subparsers(dest="subcommand")

    # Create
    parser_create = subparsers.add_parser("create", help="create a new arma 3 server installation")
    parser_create.add_argument("name", nargs=1, help="Name of server to be created")

    # Delete *
    parser_create = subparsers.add_parser("delete", help="delete arma 3 server installation")
    parser_create.add_argument("name", nargs=1, help="Name of server to be deleted")

    # Update
    parser_update = subparsers.add_parser("update", help="update existing arma 3 server")
    parser_update.add_argument("name", nargs=1, help="Name of server to be updated")
    parser_update.add_argument("--mods-only", help="Only update mods", action="store_true")
    parser_update.add_argument("--server-only", help="Only update server", action="store_true")

    # Mods
    parser_mods = subparsers.add_parser("mods", help="Manage mods for existing arma 3 server")
    parser_mods.add_argument("name", nargs=1, help="Name of server to be modified")
    subparsers_mods = parser_mods.add_subparsers(dest="subtask")
    
    # Mods > Add
    parser_mods_add = subparsers_mods.add_parser("add", help="Add a new mod from the steam workshop")
    parser_mods_add.add_argument("mod", nargs="+", help="URL(s) of mod on steam workshop, or workshop ID")
    
    # Mods > Delete *
    parser_mods_delete = subparsers_mods.add_parser("delete", help="Delete a mod")
    parser_mods_delete.add_argument("mod", nargs="+", help="URL(s) of mod on steam workshop, or workshop ID")
    
    # Mods > List
    parser_mods_list = subparsers_mods.add_parser("list", help="List all mods")

    # Instance
    parser_instance = subparsers.add_parser("instance", help="edit instances within server")
    parser_instance.add_argument("name", nargs=1, help="Name of server to be modified")
    subparsers_instance = parser_instance.add_subparsers(dest="subtask")
    
    # Instance > Add
    parser_instance_add = subparsers_instance.add_parser("add", help="Add a new instance")
    parser_instance_add.add_argument("i_name", nargs=1, help="Name of instance")
    
    # Instance > Mods
    parser_instance_mods = subparsers_instance.add_parser("mods", help="Enable/disable mods on instance")
    parser_instance_mods.add_argument("i_name", nargs=1, help="Name of instance")
    subparsers_instance_mods = parser_instance_mods.add_subparsers(dest="subsubtask")
    
    # Instance > Mods > Enable
    parser_instance_mods_enable = subparsers_instance_mods.add_parser("enable", help="enable a mod")
    parser_instance_mods_enable.add_argument("mod", nargs="+", help="URL(s) of mod on steam workshop, or workshop ID")
    
    # Instance > Mods > Disable
    parser_instance_mods_disable = subparsers_instance_mods.add_parser("disable", help="disable a mod")
    parser_instance_mods_disable.add_argument("mod", nargs="+", help="URL(s) of mod on steam workshop, or workshop ID")
    
    # Instance > Mods > List
    parser_instance_mods_disable = subparsers_instance_mods.add_parser("list", help="List enabled mods")

    # Instance > Delete *
    parser_instance_delete = subparsers_instance.add_parser("delete", help="Delete instance")
    parser_instance_delete.add_argument("i_name", nargs=1, help="Name of instance")
    
    # Instance > Start
    parser_instance_start = subparsers_instance.add_parser("start", help="Start an instance")
    parser_instance_start.add_argument("i_name", nargs=1, help="Name of instance")
    
    # Instance > List
    parser_instance_list = subparsers_instance.add_parser("list", help="list instances")

    args = parser.parse_args()
    #print(args)  # DEBUG

    # Check if steamcmd is available on the system
    steamcmd_exists = which(steamcmd_binary) is not None
    if not steamcmd_exists:
        print("SteamCMD is not available on this system or is not available in the path.")
        exit(1)

    if args.subcommand is not None:
        SERVER_NAME = args.name[0]
        SERVER_DIR = getServerPathFromName(SERVER_NAME)  # will return none if nonexistant
        SERVER_CONF_LOCATION = SERVER_DIR + "/config.ini"

        serverconfig = configparser.ConfigParser()
        if os.path.isfile(SERVER_CONF_LOCATION):
            serverconfig.read(SERVER_CONF_LOCATION)

        if args.subcommand == 'create' or args.subcommand == 'update' or args.subcommand == 'mods':
            if 'STEAM_USERNAME' not in locals():
                STEAM_USERNAME = input("What is your steam username? ")

            if 'STEAM_PASSWORD' not in locals():
                STEAM_PASSWORD = input("What is your steam password? ")

        if args.subcommand == 'create':
            SERVER_DIR = input("Installation directory for server? ")
            SERVER_CONF_LOCATION = SERVER_DIR + "/config.ini"

            # automated steamcmd command
            steam_success = getArmaServer(STEAM_USERNAME, STEAM_PASSWORD, SERVER_DIR)

            if steam_success == 0:
                print("Server installed successfully")
            else:
                exit(steam_success)

            print("Writing server config...")
            
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

            if SERVER_DIR is None:
                print("That server was not found!")
                exit(1)

            def updateMods():
                EXISTING_MODS = serverconfig['server']['mods'].split(",")
                steam_success = getSteamMods(STEAM_USERNAME, STEAM_PASSWORD, EXISTING_MODS, SERVER_DIR)

                if steam_success == 0:
                    print("Mod(s) updated successfully")
                else:
                    exit(steam_success)

            def updateServer():
                steam_success = getArmaServer(STEAM_USERNAME, STEAM_PASSWORD, SERVER_DIR)

                if steam_success == 0:
                    print("Server updated successfully")
                else:
                    exit(steam_success)

            if args.mods_only:
                updateMods()
            elif args.server_only:
                updateServer()
            else:
                updateMods()
                updateServer()

        if args.subcommand == 'delete':
            if SERVER_DIR is None:
                print("That server was not found!")
                exit(1)

            confirm = input("Are you sure you want to delete ALL CONTENTS of " + SERVER_DIR + "? [Y,n] ")
            if confirm == "Y":
                shutil.rmtree(SERVER_DIR)

        if args.subcommand == 'mods':
            if SERVER_DIR is None:
                print("That server was not found!")
                exit(1)

            if args.subtask == 'add':
                mod_id_list = []
                if args.mod is not None:
                    # mods were added
                    for mod_url in args.mod:
                        parsed_url = urlparse.urlparse(mod_url)
                        parsed_list = urlparse.parse_qs(parsed_url.query)
                        if 'id' in parsed_list:
                            mod_id_list.append(parsed_list['id'][0])
                        else:
                            print("No ModID found in URL")
                            exit(1)

                    steam_success = getSteamMods(STEAM_USERNAME, STEAM_PASSWORD, mod_id_list, SERVER_DIR)

                    if steam_success == 0:
                        print("Mod(s) installed successfully")
                    else:
                        exit(steam_success)

                    # lowercase installed mods
                    for mod_id in mod_id_list:
                        path = SERVER_DIR + "/" + SERVER_MOD_DIR + mod_id
                        lowercase_all(path)

                    EXISTING_MODS = serverconfig['server']['mods'].split(",")
                    EXISTING_EXCLUSIVE = list(set(EXISTING_MODS) - set(mod_id_list))
                    NEW_MODS = EXISTING_EXCLUSIVE + mod_id_list
                    NEW_MODS = [string for string in NEW_MODS if string != ""]  # remove empty string from empty set (if they're there)
                    
                    serverconfig['server']['mods'] = ",".join(NEW_MODS)

                    with open(SERVER_CONF_LOCATION, 'w') as serverconfig_file:
                        serverconfig.write(serverconfig_file)

            if args.subtask == 'delete':
                for mod in args.mod:
                    path = SERVER_DIR + "/" + SERVER_MOD_DIR + mod
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                        print("Removed " + mod)

            if args.subtask == 'list':
                EXISTING_MODS = serverconfig['server']['mods'].split(",")

                print("Workshop ID\t\tMod Name")
                for mod in EXISTING_MODS:
                    path = SERVER_DIR + "/" + SERVER_MOD_DIR + mod
                    name = getModName(path)
                    print(mod + "\t\t" + name)

        if args.subcommand == 'instance':
            if args.subtask != 'list':
                INSTANCE_NAME = args.i_name[0]

            if args.subtask == 'add':
                # add new instance

                # get location
                DEF_LOC = SERVER_DIR + "/instances/" + INSTANCE_NAME
                INSTANCE_DIR = input("Location of new isntance [" + DEF_LOC + "]? ")
                if INSTANCE_DIR == "":
                    INSTANCE_DIR = DEF_LOC
                
                # create directory
                if not os.path.exists(INSTANCE_DIR):
                    os.makedirs(INSTANCE_DIR)

                # copy template conf file
                shutil.copyfile("server.cfg.template", INSTANCE_DIR + "/server.cfg")

                serverconfig[INSTANCE_NAME] = {}
                serverconfig[INSTANCE_NAME]['path'] = INSTANCE_DIR
                serverconfig[INSTANCE_NAME]['mods'] = ""
                serverconfig[INSTANCE_NAME]['port'] = "2302"

                with open(SERVER_CONF_LOCATION, 'w') as serverconfig_file:
                    serverconfig.write(serverconfig_file)

                print("Instance created")

            if args.subtask == 'mods':
                # modify instance
                if args.subsubtask == 'enable':
                    if args.mod is not None:
                        # mods to be enabled
                        AVAILABLE_MODS = serverconfig['server']['mods'].split(",")

                        mod_id_list = []
                        for mod_entry in args.mod:
                            if mod_entry in AVAILABLE_MODS:
                                mod_id_list.append(mod_entry)
                            else:
                                parsed_url = urlparse.urlparse(mod_entry)
                                parsed_list = urlparse.parse_qs(parsed_url.query)
                                if 'id' in parsed_list:
                                    modid_found = parsed_list['id'][0]
                                    if modid_found in AVAILABLE_MODS:
                                        mod_id_list.append(modid_found)
                                    else:
                                        print("Mod is not installed on the server")
                                        exit(1)
                                else:
                                    print("Mod is not installed on the server or no ModID found in URL")
                                    exit(1)

                        EXISTING_MODS = serverconfig[INSTANCE_NAME]['mods'].split(",")
                        EXISTING_EXCLUSIVE = list(set(EXISTING_MODS) - set(mod_id_list))
                        NEW_MODS = EXISTING_EXCLUSIVE + mod_id_list
                        NEW_MODS = [string for string in NEW_MODS if string != ""]  # remove empty string from empty set (if they're there)
                        
                        serverconfig[INSTANCE_NAME]['mods'] = ",".join(NEW_MODS)

                        with open(SERVER_CONF_LOCATION, 'w') as serverconfig_file:
                            serverconfig.write(serverconfig_file)
                elif args.subsubtask == 'disable':
                    if args.mod is not None:
                        # mods to be disabled
                        EXISTING_MODS = serverconfig[INSTANCE_NAME]['mods'].split(",")

                        mod_id_list = []
                        for mod_entry in args.mod:
                            if mod_entry in EXISTING_MODS:
                                mod_id_list.append(mod_entry)
                            else:
                                parsed_url = urlparse.urlparse(mod_entry)
                                parsed_list = urlparse.parse_qs(parsed_url.query)
                                if 'id' in parsed_list:
                                    modid_found = parsed_list['id'][0]
                                    if modid_found in EXISTING_MODS:
                                        mod_id_list.append(modid_found)
                                    else:
                                        print("Mod is not installed on the server")
                                        exit(1)
                                else:
                                    print("Mod is not installed on the server or no ModID found in URL")
                                    exit(1)

                        EXISTING_MODS = serverconfig[INSTANCE_NAME]['mods'].split(",")
                        NEW_MODS = list(set(EXISTING_MODS) - set(mod_id_list))
                        NEW_MODS = [string for string in NEW_MODS if string != ""]  # remove empty string from empty set (if they're there)
                        
                        serverconfig[INSTANCE_NAME]['mods'] = ",".join(NEW_MODS)

                        with open(SERVER_CONF_LOCATION, 'w') as serverconfig_file:
                            serverconfig.write(serverconfig_file)
                
                if args.subsubtask == 'list':
                    serverconfig = configparser.ConfigParser()
                    serverconfig.read(SERVER_CONF_LOCATION)
                    EXISTING_MODS = serverconfig[INSTANCE_NAME]['mods'].split(",")

                    print("Workshop ID\t\tMod Name")
                    for mod in EXISTING_MODS:
                        path = SERVER_DIR + "/" + SERVER_MOD_DIR + mod
                        name = getModName(path)
                        print(mod + "\t\t" + name)
            
            if args.subtask == 'start':
                # start an instance

                if INSTANCE_NAME not in serverconfig:
                    print("Instance not found")
                    exit(1)

                INSTANCE_DIR = serverconfig[INSTANCE_NAME]['path']
                INSTANCE_PORT = serverconfig[INSTANCE_NAME]['port']

                INSTANCE_MODS = serverconfig[INSTANCE_NAME]['mods'].split(",")
                INSTANCE_MODS_RELATIVE = [SERVER_MOD_DIR + sub for sub in INSTANCE_MODS]

                startServer(SERVER_DIR, INSTANCE_DIR, INSTANCE_PORT, INSTANCE_MODS_RELATIVE)

            if args.subtask == 'list':
                print("Instance Name\t\tPath")

                for header in serverconfig.keys():
                    if header != "general" and header != "server" and header != "DEFAULT":
                        print(header + "\t\t" + serverconfig[header]['path'])

            if args.subtask == 'delete':
                confirm = input("Are you sure you want to delete ALL CONTENTS of " + INSTANCE_DIR + "? [Y,n] ")
                if confirm == "Y":
                    shutil.rmtree(INSTANCE_DIR)

        # update config
        if args.save:
            config['steam'] = {}
            if 'STEAM_USERNAME' in locals():
                config['steam']['user'] = STEAM_USERNAME

            if 'STEAM_PASSWORD' in locals():
                config['steam']['password'] = STEAM_PASSWORD

        config['state'] = {}
        if 'SERVER_LIST' in locals():
            config['state']['serverlist'] = ",".join(SERVER_LIST)

        with open(def_config_file, 'w') as config_file:
            config.write(config_file)

if __name__ == '__main__':
    main()