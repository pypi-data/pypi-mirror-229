



# Import the necessary packages
import time,os,json
from consolemenu import *
from consolemenu.items import *
from prettyprinter import cpprint
import inquirer
from datetime import datetime

import configparser
config = configparser.ConfigParser()

CONFIG_DIR = os.path.expanduser("~/")
CONFIG_FILE = os.path.join(CONFIG_DIR, ".shell2_cli_config")

config.read(CONFIG_FILE)
def get_api_key():
    return config['DEFAULT'].get('apikey', None)


from shell2.client import Shell2Client
shell2_client = Shell2Client( get_api_key() )


# Create the menu
menu = ConsoleMenu("shell2.raiden.ai")
# Create some item
# MenuItem is the base class for all items, it doesn't do anything when selected
# menu_item = MenuItem("Menu Item")


def save_json(path,obj):
    with open(path,'w') as fout:
        json.dump(obj, fout)

# SESSIONS #####################################
submenu_sessions = ConsoleMenu("Sessions\ncreate, resume, join or view previous shell2 live chat sessions")
### session new ########################
def fn_sessionNew():
    print('\n\n')
    cpprint({
        'session' : 'create new session',
    })
    timeout = 300
    timeout = input('- timeout in seconds (default 300) > ')
    multiplayer = input('- enable multiplayer (y/n) > ')
    sync_files = input('- transfer the files in current folder to session ? (y/n) > ')
    try:
        timeout = int(timeout)
    except Exception as e:
        timeout = 300
    multiplayer = True if ( multiplayer == 'Y' or multiplayer == 'y' ) else False
    sync_files = True if ( sync_files == 'Y' or sync_files == 'y' ) else False

    cpprint({
        'timeout' : timeout,
        'multiplayer' : multiplayer,
        'sync_files' : sync_files,
    })
    
    
session_new = FunctionItem("Session : Start a new session", fn_sessionNew)
submenu_sessions.append_item(session_new)

### session resume ########################
session_resume = FunctionItem("Session : Resume a previous session", input, ["Enter an input"])
submenu_sessions.append_item(session_resume)

### session join ########################

# <------- use multiplayer url directly
session_join = FunctionItem("Session : Join a multiplayer session", input, ["Enter an input"])
submenu_sessions.append_item(session_join)



### session dump ########################
def fn_sessionPrevious():
    print('############### Previous Sessions ###############')
    response = shell2_client.session.list()
    
    choices_sessions = [ f"{e['sessionId']} | created {str( datetime.fromtimestamp( int(e['timestampCreated']/1000) ) )} | "
        + f"{'done' if e['done'] else 'active'}"
        + f"{'multiplayer | ' if e['multiplayer'] else ''}"
        for e in response['sessions']
    ]
    
    #cpprint(response)
    print('\nChoose a session, the data will be saved under shell2_data/session\n')
    
    questions = [
        inquirer.List(
            "sessionId",
            message="session : ",
            choices=choices_sessions,
        ),
    ]

    choice_sessionId = inquirer.prompt(questions)
    selected_sessionId = choice_sessionId['sessionId'].split(' | ')[0].strip()
    response_session = shell2_client.session.get({"sessionId" : selected_sessionId})
    
    #os.makedirs( os.path.join(os.getcwd(), f'shell2_data/session/{selected_sessionId}') , exist_ok=True)
    #save_json(
    #    os.path.join(os.getcwd(), f'shell2_data/session/{selected_sessionId}/dump.json'),
    #    response_session
    #)
    save_json(
        os.path.join(os.getcwd(), f'session_{selected_sessionId}.json'),
        response_session
    )
    
    cpprint({
        'sessionId' : selected_sessionId,
        'saved' : f"./session_{selected_sessionId}.json"
    })
    
    input('\n< back\n')
session_previous = FunctionItem("Session : View + dump previous sessions", fn_sessionPrevious)
submenu_sessions.append_item(session_previous)
####
submenu_sessions_item = SubmenuItem("Sessions", submenu_sessions, menu=menu)
menu.append_item(submenu_sessions_item)
#############################################




# SEQUENCE #####################################
submenu_sequences = ConsoleMenu("Sequences\nrun a new shell2 sequence or view your previously created sequences")

### sequence run ########################
sequence_run = FunctionItem("Sequence : Run a new sequence", input, ["Enter an input"])
submenu_sequences.append_item(sequence_run)

### settings get ########################
def fn_sequencePrevious():
    print('############### Previous sequences ###############')
    response = shell2_client.sequence.list()
    
    choices_sequences = [ f"{e['sequenceId']} | "
        + f"{'done' if e['done'] else 'running'}"
        + f" | {e['sequence'][0][0:30]} ..."
        for e in response['sequences']
    ]
    
    #cpprint(response)
    print('\nChoose a sequence, the data will be saved under shell2_data/sequence\n')
    
    questions = [
        inquirer.List(
            "sequenceId",
            message="sequence : ",
            choices=choices_sequences,
        ),
    ]

    choice_sequenceId = inquirer.prompt(questions)
    selected_sequenceId = choice_sequenceId['sequenceId'].split(' | ')[0].strip()
    response_sequence = shell2_client.sequence.get({"sequenceId" : selected_sequenceId})
    
    #os.makedirs( os.path.join(os.getcwd(), f'shell2_data/sequence/{selected_sequenceId}') , exist_ok=True)
    #save_json(
    #    os.path.join(os.getcwd(), f'shell2_data/sequence/{selected_sequenceId}/dump.json'),
    #    response_sequence
    #)
    
    save_json(
        os.path.join(os.getcwd(), f'sequenceId_{selected_sequenceId}.json'),
        response_session
    )
    
    cpprint({
        'sequenceId' : selected_sequenceId,
        'saved' : f"./sequenceId_{selected_sequenceId}.json"
    })
    
    input('\n< back\n')
sequence_previous = FunctionItem("Sequence : View + dump previous sequences", fn_sequencePrevious)
submenu_sequences.append_item(sequence_previous)

####
submenu_sequences_item = SubmenuItem("Sequences", submenu_sequences, menu=menu)
menu.append_item(submenu_sequences_item)
#############################################


# SETTINGS #####################################
submenu_settings = ConsoleMenu("Settings\nyou can view and update your shell2 settings below")
### settings get ########################
def fn_settingsGet():
    print('############### Current Settings ###############')
    response = shell2_client.settings.get()
    settings = response['settings']
    cpprint(settings)
    input('\n< back\n')
settings_get = FunctionItem("Settings : Current settings", fn_settingsGet)
submenu_settings.append_item(settings_get)

### settings update ########################
# TBD
#settings_update = FunctionItem("Settings : Update settings", input, ["Enter an input"])
#menu.append_item(settings_update)

####
submenu_settings_item = SubmenuItem("Settings", submenu_settings, menu=menu)
menu.append_item(submenu_settings_item)
#############################################

"""
# A CommandItem runs a console command
command_item = CommandItem("je comonsse l'assession",  "python cliasync.py session")
menu.append_item(command_item)
"""

"""
def lombda():
    user_msg = input('showbob>')
    print('-------->' , user_msg)
    time.sleep(5)
submenu = ConsoleMenu("je_sub_menu")
submenu_function_item = FunctionItem("voir_les_fess", lombda)#, ["bb"])
submenu.append_item(submenu_function_item)

submenu_item = SubmenuItem("Show a submenu", submenu, menu=menu)
menu.append_item(submenu_item)
"""

def main():
    global menu
    menu.show()

if __name__ == '__main__':
    main()