"""
Erni bot launcher
USEFUL DOC http://telepot.readthedocs.io/en/latest/
"""
# System functions
import sys
# Timer functions
import time
# Calendar functions
import datetime

# Class wrappers
from BotMock import BotWrapper
from BDMock  import BDWrapper

# Global definition
####################
# Redis class
BD = BDWrapper()
# Telepot class
BOT = BotWrapper(BD)
# Application thread failsafe
CEND = 1

####################################################################################################
# Telegram bot oriented methods (Testing purposes)                                                ##
####################################################################################################
def hello_msg(chat_id, text):
    """
    Say Hello to new users
    """
    global BOT

    ## Send greeting message ##
    BOT.send_message(chat_id, """
    Wellcome to ERNI Lunch bot,
    we hope you will make the most of the application
    """)

def talk_back(chat_id, text):
    """Echo function"""
    global BOT

    ## Repeat what was told
    BOT.send_message(chat_id, text)

####################################################################################################
## Main methods for ERNI lunch application                                                        ##
####################################################################################################

def main_menu(chat_id, text):
    """ Main menu"""
    # Globals
    global BOT

    # Array to store buttons
    options = []
    options.append(BOT.new_custombutton('/propose XX:XX'))
    options.append(BOT.new_custombutton('/list'))

    # Create custom keyboard
    keyboard = BOT.new_customkeyboard(options, 2)
    # Send custom keyboard to the useer
    BOT.send_keyboard(chat_id, 'What would you like to do:', keyboard)

def group_menu(chat_id, text):
    """ Group menu"""
    # Globals
    global BOT
    global BD

    # Retrieve text parameters
    ptime = text.split(" ")

    # If text contains two parameters
    if len(ptime) == 2:
        # Array to store buttons
        options = []
        options.append(BOT.new_custombutton('/join %s' % ptime[1]))
        options.append(BOT.new_custombutton('/howmany %s' % ptime[1]))
        options.append(BOT.new_custombutton('/where %s' % ptime[1]))
        options.append(BOT.new_custombutton('/leave %s' % ptime[1]))

        # Create custom keyboard
        keyboard = BOT.new_customkeyboard(options, 4)
        # Send custom keyboard
        BOT.send_keyboard(chat_id, 'You chose group %s' % ptime[1], keyboard)
        return

    # An erroneous format message
    report_error(chat_id, text)

def where_group(chat_id, text):
    """ Where command"""
    # Globals
    global BD
    global BOT

    today = str(datetime.datetime.now().day)
    ptime = text.split(" ")

    if len(ptime) == 1:
        report_error(chat_id, text)
        return

    group = 'LOC_HP_{}_{}'.format(today, ptime[1])
    # Get appointment in 5 min
    loc_val = BD.get_key_value(group)

    loc = 'No location has been set'

    # There should be only one...
    if loc_val is not None:
        loc = 'Group is located at {}'.format(loc_val)

    # TODO FIX
    options = []
    options.append(BOT.new_inlinebutton('A0', '/loc %s A0' % ptime[1]))
    options.append(BOT.new_inlinebutton('Cashier', '/loc %s Cashier' % ptime[1]))
    options.append(BOT.new_inlinebutton('A2', '/loc %s A2' % ptime[1]))
    options.append(BOT.new_inlinebutton('A3', '/loc %s A3' % ptime[1]))
    options.append(BOT.new_inlinebutton('B0', '/loc %s B0' % ptime[1]))
    options.append(BOT.new_inlinebutton('B1', '/loc %s B1' % ptime[1]))
    options.append(BOT.new_inlinebutton('B2', '/loc %s B2' % ptime[1]))
    options.append(BOT.new_inlinebutton('B3', '/loc %s B3' % ptime[1]))
    options.append(BOT.new_inlinebutton('C0', '/loc %s C0' % ptime[1]))
    options.append(BOT.new_inlinebutton('C1', '/loc %s C1' % ptime[1]))
    options.append(BOT.new_inlinebutton('C2', '/loc %s C2' % ptime[1]))
    options.append(BOT.new_inlinebutton('C3', '/loc %s C3' % ptime[1]))

    keyboard = BOT.new_inlinekeyboard(options, 4)
    BOT.send_keyboard(chat_id, loc, keyboard)
    group_menu(chat_id, text)

def loc_group(chat_id, text):
    """ Locate group"""
    # Globals
    global BD
    global BOT

    today = str(datetime.datetime.now().day)
    ptime = text.split(" ")

    group = 'LOC_HP_{}_{}'.format(today, ptime[1])

    if len(ptime) == 3:
        BD.set_key_value(group, ptime[2])
        BD.expire(group, 60*60)
        BOT.send_message(chat_id, 'New location is {}'.format(ptime[2]))
        group_menu(chat_id, '{} {}'.format(ptime[0], ptime[1]))
        return

    report_error(chat_id, text)

def list_groups(chat_id, text):
    """ List lunch groups for today"""
    # Globals
    global BD
    global BOT

    # Retrieve today's date
    today = str(datetime.datetime.now().day)

    # Format key for search
    today = 'HP_{}_*'.format(today)
    # Retrieve all keys (if any)
    keys = BD.get_keys(today)

    # If no key was found
    if not keys:
        # ...report to the user
        BOT.send_message(chat_id, 'No proposal has been found')
        # Return to main menu
        main_menu(chat_id, text)

    # If any key was found...
    if keys:
        # Sort keys (time based)
        keys = sorted(keys)
        # Array to store buttons
        hours = []
        # For all found keys
        for key in keys:
            # Retrieve time from found key
            tmp = key.split("_")
            # For every hour create a button
            hours.append(BOT.new_inlinebutton(tmp[2], '/group %s' % tmp[2]))
        # Create inline keyboard
        keyboard = BOT.new_inlinekeyboard(hours, 3)
        # Send inline keyboard
        BOT.send_keyboard(chat_id, 'Proposed times:', keyboard)
        # Display main menu
        main_menu(chat_id, text)

def propose_group(chat_id, text):
    """ Propose a new lunch group time"""
    # Globals
    global BD
    global BOT

    # Retrieve parameters
    param = text.split(" ")
    ptime = param[1].split(":")
    # Prepare options
    options = []

    # Hour to be determined
    if ptime[0] == 'XX':

        options.append(BOT.new_custombutton('/propose 12:XX'))
        options.append(BOT.new_custombutton('/propose 13:XX'))
        options.append(BOT.new_custombutton('/propose 14:XX'))

        # Prepare options
        keyboard = BOT.new_customkeyboard(options, 3)
        # Send options
        BOT.send_keyboard(chat_id, 'Chose hour:', keyboard)
        return

    # Minutes to be determined
    if ptime[1] == 'XX':
        # For all available minutes (almost)
        for i in range(0, 60, 5):
            # Prepare label
            phour = '%s:%02d' % (ptime[0], i)
            # Create option
            options.append(BOT.new_custombutton('/propose %s' % phour))

        # Create keyboard
        keyboard = BOT.new_customkeyboard(options, 3)
        # Send keyboard
        BOT.send_keyboard(chat_id, 'Chose minute:', keyboard)
        return

    try:
    # Check proposed time
        time.strptime(param[1], '%H:%M')
    except ValueError:
        # Report to the user the correct format
        BOT.send_message(chat_id, "Time format incorrect, should be HH:MM")
        main_menu(chat_id, text)
        return

    # Retrieve today's date
    today = str(datetime.datetime.now().day)

    # Format key UPGRADE: Locations
    keyname = 'HP_{}_{}'.format(today, param[1])
    # Retrieve existing keys
    keys = BD.get_keys(keyname)

    # If a key already exists...
    if keys:
        # ...join the group
        BD.insert_left_list(keyname, chat_id)
        # Report to the user
        BOT.send_message(chat_id, "You joined group for %s" % param[1])
        group_menu(chat_id, '/group %s' % param[1])
        return

    # Insert new proposed time
    BD.insert_left_list(keyname, chat_id)
    # Set 8h expiration (Ideas?)
    BD.expire(keyname, 8*60*60)
    # Report to the user
    BOT.send_message(chat_id, "You proposed group for %s" % param[1])
    group_menu(chat_id, '/group %s' % param[1])

def how_many_group(chat_id, text):
    """ How many people in group"""
    # Globals
    global BD
    global BOT

    param = text.split(" ")

    try:
        # Check proposed time
        time.strptime(param[1], '%H:%M')
    except ValueError:
        # Report if it is incorrect
        BOT.send_message(chat_id, "Time format incorrect, should be HH:MM")
        main_menu(chat_id, text)
        return

    # Retrieve today's date
    today = str(datetime.datetime.now().day)

    # Format search key UPGRADE: Use location
    keyname = 'HP_{}_{}'.format(today, param[1])
    # Retrieve all matching keys from DB
    keys = BD.get_keys(keyname)

    # If no proposal was found...
    if not keys:
        # ...report it to the user
        BOT.send_message(chat_id, 'No proposal has been found')
        main_menu(chat_id, text)
        return

    # Retrieve the number of people that joined
    people = BD.get_length(keyname)

    # If only one person proposed...
    if people == 1:
    # ...report it to the user
        BOT.send_message(chat_id, 'At {} only {} person'.format(param[1], people))
        group_menu(chat_id, '/group %s' % param[1])
        return

    # Report to the user number of people
    BOT.send_message(chat_id, 'At {} there are {} people'.format(param[1], people))
    group_menu(chat_id, '/group %s' % param[1])

def join_group(chat_id, text):
    """ Join lunch time group"""
    # Globals
    global BD
    global BOT

    param = text.split(" ")

    #if len(param) != 0: pyLint C1801
    if param:
        report_error(chat_id, text)

    try:
        # Check proposed time format
        time.strptime(param[1], '%H:%M')
    except ValueError:
        # Incorrect format was proposed
        BOT.send_message(chat_id, "Time format incorrect, should be HH:MM")
    return

    # Retrieve today's date
    today = str(datetime.datetime.now().day)

    # Create label format UPGRADE: Different locations
    keyname = 'HP_{}_{}'.format(today, param[1])
    # Retrieve all matching keys from DB
    keys = BD.get_keys(keyname)

    # If no appointment is found...
    if not keys:
        # ...report to the user
        BOT.send_message(chat_id, 'No proposal has been found')
        main_menu(chat_id, text)
        return

    # Add user to key list
    BD.insert_left_list(keyname, chat_id)
    # Report to the user
    BOT.send_message(chat_id, 'You have joined the {} group'.format(param[1]))
    group_menu(chat_id, '/group %s' % param[1])

def leave_group(chat_id, text):
    """ Leave lunch time group"""
    # Globals
    global BD
    global BOT

    # Retrieve today's date
    today = str(datetime.datetime.now().day)
    ptime = text.split(" ")

    # Create key format UPGRADE: Use different locations
    keyname = 'HP_{}_{}'.format(today, ptime[1])
    # Retrieve all keys in DB
    keys = BD.get_keys(keyname)

    # If no key was found for today...
    if not keys:
        # ...inform the user
        BOT.send_message(chat_id, 'No proposal has been found')

        # Check for all keys retrieved from today
        for key in keys:
            # Remove element from list
            res = BD.remove_from_list(key, chat_id)
            # If at least one element was removed
            if res is not 0:
                # Get time from key
                proposal = key.split("_")
                # Announced removed time
                BOT.send_message(chat_id, 'You have been removed from {}'.format(proposal[2]))

        main_menu(chat_id, text)

def end_execution(chat_id, text):
    """ Emergency shutdown"""
    # Retrieve variables
    global CEND
    global BOT

    # Report to user
    BOT.send_message(chat_id, 'Performing arakiri')
    # Report to console
    print('I die alone')
    # Kill thread loop
    CEND = 0

def report_error(chat_id, text):
    """ Report error message"""
    global BOT

    # Report to the user
    BOT.send_message(chat_id, 'This is an error')

####################################################################################################
# List of user available commands                                                                 ##
####################################################################################################
# /start should always be available
COMMANDS = {'/start':    main_menu,
            # Send greeting message
            '/hello':    hello_msg,
            # Main menu of application
            '/main':     main_menu,
            # Actions regarding one group
            '/group':    group_menu,
            '/where':    where_group,
            '/loc':      loc_group,
            # List all available groups for today
            '/list':     list_groups,
            # Create or join a lunch group
            '/propose':  propose_group,
            # Join a lunch group
            '/join':     join_group,
            # How many members requested to join lunch time
            '/howmany':  how_many_group,
            # Be removed from all lunch groups
            '/leave':    leave_group,
            # Emergency stop for script
            '/die':      end_execution,
            # Error found
            '/error':    report_error}

###################################################################################################
# Thread loop methods (Telegram bot and ERNI Lunch application)                                  ##
###################################################################################################

def call_out(now):
    """ Function to advise of incomming lunch time"""
    # Globals
    global BD
    global BOT

    # Retrieve day
    today = now.day
    # Hour
    hour = now.hour
    # Minute
    minute = now.minute

    # Test proposed time
    try:
        # Generate lunch time in 5 min
        pro_time = '{:02}:{:02}'.format(hour, minute+5)
        # Check correct time format
        time.strptime(pro_time, '%H:%M')
        # No issue found, advance 5 min
        minute = minute+5
    except ValueError:
        # TODO: This should take into account 24h clock and day/month/year
        hour = hour + 1
        # Advance 5 min into next hour
        minute = (minute + 5)%60

    # Compose appointment name
    keyname = 'HP_{}_{:02}:{:02}'.format(today, hour, minute)
    # Get appointment in 5 min
    keys = BD.get_keys(keyname)

    # No appointment is found
    if not keys:
        return

    # There should be only one...
    for key in keys:
        # Compose check mark
        check = 'CHECKED_HP_{}_{:2}:{:2}'.format(today, hour, minute)
        # Ask check mark
        res = BD.get_keys(check)
        # If there is no mark
        if not res:
            attendees = BD.get_list_value(keyname)
            # For each attendee
            for attendee in attendees:
            # Send a message
                BOT.send_message(attendee, 'Lunch is in 5 min')

            # Add flag
            BD.insert_left_list(check, 0)
            # Add expiration (1 min)
            BD.expire(check, 60)

def proc_mess(msg):
    """ Method used to process each message received"""

    # Be on safe side
    text = '/error'

    # Retrieve message flavor
    flavor = BOT.get_flavor(msg)

    # If it is a 'chat' message...
    if flavor == 'chat':
        # Retrieve parameters
        chat_id = msg['chat']['id']
        text = msg['text']

    # If it is a 'callback_query'...
    if flavor == 'callback_query':
        msg_id = msg['id']
        # Retrieve parameters
        chat_id = msg['from']['id']
        text = msg['data']
        BOT.send_reply(msg_id, 'processing')

    #bot.send_message(chat_id, text)

    # Divide message text
    command = text.split(" ")

    # If command is not understood...
    if command[0] not in COMMANDS:
        # ...mark it as an error
        command[0] = '/error'

    # Execute command based on dictionary
    COMMANDS[command[0]](chat_id, text)

####################################################################################################
# Operation loop (Main thread loop execution)                                                     ##
####################################################################################################

# Attach message processing method to bot
#########################################
# Attach handling message method to bot
BOT.add_handle(proc_mess)

# While python process is not called to end
###########################################
# Thread failsafe
while CEND:
    ## Check if any lunch proposal is due
    call_out(datetime.datetime.now())
    ## Sleep for 5 secs
    time.sleep(5)
