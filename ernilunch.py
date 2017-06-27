# System functions
import sys
# Timer functions
import time
# Calendar functions
import datetime

# Class wrappers
from Bot_Mock import Bot_wrapper
from BD_Mock  import BD_wrapper

# Global definitions
####################
# Telepot class
bot   = Bot_wrapper()
# Redis class
bd    = BD_wrapper()
# Application thread failsafe
c_end = 1

###########################################################################################################################################
# Telegram bot oriented methods (Testing purposes)                                                                                       ##
###########################################################################################################################################
def hello_msg(msg):
    global bot
    # Retrieve variables
    chat_id = msg['chat']['id']

    ## Send greeting message ##
    bot.send_message(chat_id, 'Wellcome to ERNI Lunch bot, we hope you will make the most of the application')

def talk_back(msg):
    global bot
    # Retrieve variables
    chat_id = msg['chat']['id']
    text    = msg['text']

    ## Repeat what was told
    bot.send_message(chat_id,text)
    

###########################################################################################################################################
## Redis oriented methods (Testing purposes)                                                                                             ##
###########################################################################################################################################

def create_key(msg):
    """ Create key"""
    #Global variables
    global bd

    # Retrieve mensage
    keyname = msg['text']
    keyname = keyname.split(" ")

    if len(keyname) == 2:
        # Create new entry
        bd.createNewEntry(keyname[1])

def get_keys(msg):
    """ Get keys"""
    # Global bd
    global bd
    global bot

    # Retrieve keys with pattern
    keys = bd.get_keys('*')

    chat_id = msg['chat']['id']

    bot.send_message(chat_id,'Keys found are:')
    for key in keys:
        bot.send_message(chat_id, key)

def get_key_value(msg):
    """ Get key value"""
    # Globals
    global bd
    global bot

    # Retrieve and split message
    chat_id = msg['chat']['id']
    param   = msg['text']
    param   = param.split(" ")

    if len(param) == 2:
        values = bd.get_key_value(param[1])

    if len(param) == 3:
        values = bd.get_hash_value(param[1], param[2])

    bot.send_message(chat_id, "Values are:")
    for value in values:
        bot.send_message(chat_id, value)

def set_key_value(msg):
    """ Set key value"""
    # Globals
    global bd
    global bot

    # Retrieve and split message
    chat_id = msg['chat']['id']
    param   = msg['text']
    param   = param.split(" ")

    if len(param) == 4:
        bd.set_hash_value(param[1], param[2], param[3])


###########################################################################################################################################
## Main methods for ERNI lunch application                                                                                               ##
###########################################################################################################################################

def list_groups(msg):
    """ List lunch groups for today"""
    # Globals
    global bd
    global bot

    # Retrieve message parameters
    chat_id = msg['chat']['id']
    
    # Retrieve today's date
    today = str(datetime.datetime.now().day)

    # Format key for search
    today = 'HP_{}_*'.format(today)
    # Search for available times
    keys = bd.get_keys(today)

    # If no group has been found...
    if not keys:
        # ...report to the user
        bot.send_message(chat_id,'No proposal has been found')

    # If any group has been found...
    if keys:
        # ...report that some groups have been found
        bot.send_message(chat_id,'Times available are:')
        # Arrange keys
        keys = sorted(keys)
        
        # For every time available
        for key in keys:
            # Report to the user available times
            bot.send_message(chat_id, tmp[2])

def propose_group(msg):
    """ Propose a new lunch group time"""
    # Globals
    global bd
    global bot

    # Retrieve parameters
    chat_id = msg['chat']['id']
    param   = msg['text']
    param   = param.split(" ")

    try:
        # Check proposed time
        time.strptime(param[1], '%H:%M')
    except ValueError:
        # Report to the user the correct format
        bot.send_message(chat_id,"Time format incorrect, should be HH:MM")
        return

    # Retrieve today's date
    today = str(datetime.datetime.now().day)

    # Format key UPGRADE: Locations
    keyname = 'HP_{}_{}'.format(today,param[1])
    # Retrieve existing keys
    keys    = bd.get_keys(keyname)

    # If a key already exists...
    if keys:
        # ...join the group
        bd.insert_left_list(keyname, chat_id)
        # Report to the user
        bot.send_message(chat_id,"You joined group for %s" % param[1])
        return
    
    # Insert new proposed time
    bd.insert_left_list(keyname, chat_id)
    # Set 8h expiration (Ideas?)
    bd.expire(keyname,8*60*60)
    # Report to the user
    bot.send_message(chat_id,"You proposed group for %s" % param[1])

def how_many_group(msg):
    """ How many people in group"""
    # Globals
    global bd
    global bot

    # Retrieve mensage parameters
    chat_id = msg['chat']['id']
    param   = msg['text']
    param   = param.split(" ")

    try:
        # Check proposed time
        time.strptime(param[1], '%H:%M')
    except ValueError:
        # Report if it is incorrect
        bot.send_message(chat_id,"Time format incorrect, should be HH:MM")
        return
    
    # Retrieve today's date
    today = str(datetime.datetime.now().day)

    # Format search key UPGRADE: Use location
    keyname = 'HP_{}_{}'.format(today,param[1])
    # Retrieve all matching keys from DB
    keys    = bd.get_keys(keyname)

    # If no proposal was found...
    if not keys:
        # ...report it to the user
        bot.send_message(chat_id,'No proposal has been found')
        return
    
    # Retrieve the number of people that joined
    people = bd.get_length(keyname)

    # If only one person proposed...
    if people == 1:
        # ...report it to the user
        bot.send_message(chat_id,'At {} only {} person'.format(param[1],people))
        return

    # Report to the user number of people
    bot.send_message(chat_id,'At {} there are {} people'.format(param[1],people))

def join_group(msg):
    """ Join lunch time group"""
    # Globals
    global bd
    global bot

    # Retrieve mensage parameters
    chat_id = msg['chat']['id']
    param   = msg['text']
    param   = param.split(" ")
    
    try:
        # Check proposed time format
        time.strptime(param[1], '%H:%M')
    except ValueError:
        # Incorrect format was proposed
        bot.send_message(chat_id,"Time format incorrect, should be HH:MM")
        return
    
    
    # Retrieve today's date
    today = str(datetime.datetime.now().day)

    # Create label format UPGRADE: Different locations
    keyname = 'HP_{}_{}'.format(today,param[1])
    # Retrieve all matching keys from DB
    keys    = bd.get_keys(keyname)

    # If no appointment is found...
    if not keys:
        # ...report to the user
        bot.send_message(chat_id,'No proposal has been found')
        return

    # Add user to key list
    bd.insert_left_list(keyname, chat_id)
    # Report to the user
    bot.send_message(chat_id,'You have joined the {} group'.format(param[1]))

def leave_group(msg):
    """ Leave lunch time group"""
    # Globals
    global bd
    global bot

    # Retrieve message parameters
    chat_id = msg['chat']['id']
    
    # Retrieve today's date
    today = str(datetime.datetime.now().day)

    # Create key format UPGRADE: Use different locations
    keyname = 'HP_{}_*'.format(today)
    # Retrieve all keys in DB
    keys    = bd.get_keys(keyname)

    # If no key was found for today...
    if not keys:
        # ...inform the user
        bot.send_message(chat_id,'No proposal has been found')

    # Check for all keys retrieved from today
    for key in keys:
        # Remove element from list
        res = bd.remove_from_list(key, chat_id)
        # If at least one element was removed
        if res is not 0:
            # Get time from key
            proposal = key.split("_")
            # Announced removed time
            bot.send_message(chat_id,'You have been removed from {}'.format(proposal[2]))

def end_execution(msg):
    """ Emergency shutdown"""
    # Retrieve variables
    global c_end
    global bot
    
    # Retrieve parameters
    chat_id = msg['chat']['id']

    # Report to user
    bot.send_message(chat_id,'Performing arakiri')
    # Report to console
    print ('I die alone')
    # Kill thread loop
    c_end = 0

def report_error(msg):
    """ Report error message"""
    global bot

    # Retrieve message parameters
    chat_id = msg['chat']['id']

    # Report to the user
    bot.send_message(chat_id,'This is an error')

###########################################################################################################################################
# List of user available commands                                                                                                        ##
###########################################################################################################################################
# Send greeting message
commands = { '/hello':    hello_msg,
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

###########################################################################################################################################
# Thread loop methods (Telegram bot and ERNI Lunch application)                                                                          ##
###########################################################################################################################################

def call_out(now):
    """ Function to advise of incomming lunch time"""
    # Globals
    global bd
    global bot

    # Retrieve day
    today = now.day
    # Hour
    h     = now.hour
    # Minute
    m     = now.minute
    
    # Test proposed time
    try:
        # Generate lunch time in 5 min
        proTime = '{:02}:{:02}'.format(h, m+5)
        # Check correct time format
        time.strptime(proTime, '%H:%M')
        # No issue found, advance 5 min
        m = m+5
    except ValueError:
        # TODO: This should take into account 24h clock and day/month/year
        h =  h + 1
        # Advance 5 min into next hour
        m = (m + 5)%60

    # Compose appointment name
    keyname = 'HP_{}_{:02}:{:02}'.format(today,h,m)
    # Get appointment in 5 min
    keys = bd.get_keys(keyname)

    # No appointment is found
    if not keys:
        return

    # There should be only one...
    for key in keys:
        # Compose check mark
        check = 'CHECKED_HP_{}_{:2}:{:2}'.format(today,h,m)
        # Ask check mark
        res   = bd.get_keys(check)
        # If there is no mark
        if not res:
            attendees = bd.get_list_value(keyname)
            # For each attendee
            for attendee in attendees:
                # Send a message
                bot.send_message(attendee,'Lunch is in 5 min')

            # Add flag
            bd.insert_left_list(check, 0)
            # Add expiration (1 min)
            bd.expire(check,60)

def proc_mess(msg):
    """ Method used to process each message received"""

    # Retrieve message flavor
    flavor = bot.get_flavor(msg)

    # If it is a 'chat' message
    if flavor is 'chat':
        # Retrieve the message text
        message = msg['text']

        # Extract commands and parameters
        command = message.split(" ")

        # If command is not understood...
        if command[0] not in commands:
            # ...mark it as an error
            command[0] = '/error'

        # Execute command based on dictionary
        commands[command[0]](msg)




###########################################################################################################################################
# Operation loop (Main thread loop execution)                                                                                            ##
###########################################################################################################################################

# Attach message processing method to bot
#########################################
# Attach handling message method to bot
bot.add_handle(proc_mess)

# While python process is not called to end
###########################################
# Thread failsafe
while c_end:
    ## Check if any lunch proposal is due
    call_out(datetime.datetime.now())
    ## Sleep for 5 secs
    time.sleep(5)
