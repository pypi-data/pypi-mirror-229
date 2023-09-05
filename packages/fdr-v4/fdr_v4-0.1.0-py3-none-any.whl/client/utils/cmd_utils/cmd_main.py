# FDR Client Command Methods

# Libraries
import os, sys
from ...utils.utils import *
from ...utils.cmd_utils.cmd_fdr import *
from ...utils.cmd_utils.cmd_doc import *
from ...utils.cmd_utils.cmd_logs import CommandLogs
import threading
import keyboard

key_listener_enabled = False

def initial_command_options():
    """
    Show command options if login is successful
    """
    cprint("\nPress key to choose an FDR action: \n", 'cyan', attrs=['blink', 'bold'])
    print("(d) - Datasets")
    print("(l) - Logout")
    print("(q) - Quit")

    # Start the key listener thread
    global key_listener_enabled
    key_listener_enabled = True
    listener_thread = threading.Thread(target=start_listener)
    listener_thread.start()

def dataset_command_options():
    """
    Show command options for dataset handling
    """
    cprint("\nPress key to choose an FDR action: \n", 'cyan', attrs=['blink', 'bold'])
    print("(o) - Operations")
    print("(d) - Datasets")
    print("(l) - Logout")
    print("(q) - Quit")
    enable_key_listener()

def start_listener():
    """
    Start the key listener
    """
    global key_listener_enabled
    r_pressed = False 
    
    while key_listener_enabled:
        if keyboard.is_pressed('d'):
            cmd_datasets()
            r_pressed = True  
        elif keyboard.is_pressed('l'):
            cmd_logout()
        elif keyboard.is_pressed('q'):
            cmd_exit()
        elif r_pressed and keyboard.is_pressed('o'):  
            cmd_operations()

def enable_key_listener():
    """
    Enable the key listener
    """
    global key_listener_enabled
    key_listener_enabled = True

def disable_key_listener():
    """
    Disable the key listener
    """
    global key_listener_enabled
    key_listener_enabled = False

def cmd_exit():
    """
    Exit FDR client
    """
    clear()
    sys.exit()

def cmd_logout():
    """
    Restart FDR client
    """
    clear()
    os.system(f"{sys.executable} {' '.join(sys.argv)}")
    

def cmd_datasets():
    """
    @GET all datasets
    """
    disable_key_listener()
    clear()
    get_datasets(header_show=True, header_color='cyan')
    dataset_command_options()

def cmd_operations():
    """
    FDR Operations on target dataset
    """
    # history log init
    history = CommandLogs()

    # disable key listener
    disable_key_listener()

    # clear ui
    fdr_clear('FDR Dataset Operations')

    # interactive mode
    while True:
        clear_terminal_input()
        user_input = input("\n>> ")
        history.add_text(user_input[0:])    
        parts = user_input.split()

        if parts:
            command = parts[0].lower()

            if command == 'fdr':
                if len(parts) >= 2:
                    subcommand = parts[1].lower()

                    if subcommand == 'pull':
                        pull_args = parts[2:]  
                        fdr_pull(pull_args)
                    elif subcommand == 'push':
                        # handle fdr push
                        fdr_push()
                    elif subcommand == 'menu':
                        cmd_datasets()
                        break
                    elif subcommand == 'clear':
                        fdr_clear('FDR Dataset Operations')
                    elif subcommand == 'show':
                        get_datasets(header_show=False, header_color='white')
                    elif subcommand == 'doc':
                        fdr_documentation()
                    elif user_input.lower() == 'fdr log':
                        cprint(history.get_history(), "yellow", attrs=['bold'])
                    elif user_input.lower() == 'fdr log --save' or user_input.lower() == 'fdr log -s':
                        # handle fdr logs
                        cprint(history.get_history(), "yellow", attrs=['bold'])
                        folder_path = fdr_log_save()
                        if folder_path is not None:
                            file_path = f'{folder_path}/fdr_logs.txt'
                            with open(file_path, 'w') as file:
                                file.write(f'FDR history:\n\n{history.get_history()}')
                    else:
                        print("Invalid argument")
                else:
                    print("Invalid argument")

            else:
                print("Invalid argument")

    # re-enable key listener
    enable_key_listener()

if __name__ == "__main__":
    initial_command_options()
