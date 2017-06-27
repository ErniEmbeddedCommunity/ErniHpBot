import sys                   # System functions
import time                  # Timer functions
import datetime              # Calendar functions

# Class wrappers
from Bot_Mock import Bot_wrapper
from BD_Mock  import BD_wrapper

# Global definitions
####################
bot   = Bot_wrapper()                                                          # Telepot class
bd    = BD_wrapper()                                                           # Redis class
c_end = 1                                                                      # Application thread failsafe

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

# Create key
#############
def create_key(msg):
  #Global variables
  global bd

  # Retrieve mensage
  keyname = msg['text']
  keyname = keyname.split(" ")

  if len(keyname) == 2:
    # Create new entry
    bd.createNewEntry(keyname[1])

# Get keys
##########
def get_keys(msg):
  # Global bd
  global bd
  global bot

  # Retrieve keys with pattern
  keys = bd.get_keys('*')

  chat_id = msg['chat']['id']

  bot.send_message(chat_id,'Keys found are:')
  for key in keys:
    bot.send_message(chat_id, key)

# Get key value
###############
def get_key_value(msg):
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

# Set key value
###############
def set_key_value(msg):
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

# List lunch groups for today
#############################
def list_groups(msg):
  # Globals
  global bd
  global bot

  chat_id = msg['chat']['id']                                                            # Retrieve message parameters
  
  today = str(datetime.datetime.now().day)                                               # Retrieve today's date

  today = 'HP_{}_*'.format(today)                                                        # Format key for search
  keys = bd.get_keys(today)                                                              # Search for available times

  if not keys:                                                                           # If no group has been found...
    bot.send_message(chat_id,'No proposal has been found')                               # ...report to the user

  if keys:                                                                               # If any group has been found...
    bot.send_message(chat_id,'Times available are:')                                     # ...report that some groups have been found
    keys = sorted(keys)                                                                  # Arrange keys
    
    for key in keys:                                                                     # For every time available
      bot.send_message(chat_id, tmp[2])                                                  # Report to the user available times
    
# Propose a new lunch group time
################################
def propose_group(msg):
  # Globals
  global bd
  global bot

  chat_id = msg['chat']['id']                                                            # Retrieve parameters
  param   = msg['text']
  param   = param.split(" ")

  try:
    time.strptime(param[1], '%H:%M')                                                     # Check proposed time
  except ValueError:
    bot.send_message(chat_id,"Time format incorrect, should be HH:MM")                   # Report to the user the correct format
    return

  today = str(datetime.datetime.now().day)                                               # Retrieve today's date

  keyname = 'HP_{}_{}'.format(today,param[1])                                            # Format key UPGRADE: Locations
  keys    = bd.get_keys(keyname)                                                         # Retrieve existing keys

  if keys:                                                                               # If a key already exists...
    bd.insert_left_list(keyname, chat_id)                                                # ...join the group
    bot.send_message(chat_id,"You joined group for %s" % param[1])                       # Report to the user
    return
  
  bd.insert_left_list(keyname, chat_id)                                                  # Insert new proposed time
  bd.expire(keyname,8*60*60)                                                             # Set 8h expiration (Ideas?)
  bot.send_message(chat_id,"You proposed group for %s" % param[1])                       # Report to the user

## How many people in group
###########################
def how_many_group(msg):
  # Globals
  global bd
  global bot

  chat_id = msg['chat']['id']                                                            # Retrieve mensage parameters
  param   = msg['text']
  param   = param.split(" ")

  try:
    time.strptime(param[1], '%H:%M')                                                     # Check proposed time
  except ValueError:
    bot.send_message(chat_id,"Time format incorrect, should be HH:MM")                   # Report if it is incorrect
    return
  
  today = str(datetime.datetime.now().day)                                               # Retrieve today's date

  keyname = 'HP_{}_{}'.format(today,param[1])                                            # Format search key UPGRADE: Use location
  keys    = bd.get_keys(keyname)                                                         # Retrieve all matching keys from DB

  if not keys:                                                                           # If no proposal was found...
    bot.send_message(chat_id,'No proposal has been found')                               # ...report it to the user
    return
  
  people = bd.get_length(keyname)                                                        # Retrieve the number of people that joined

  if people == 1:                                                                        # If only one person proposed...
    bot.send_message(chat_id,'At {} only {} person'.format(param[1],people))             # ...report it to the user
    return

  bot.send_message(chat_id,'At {} there are {} people'.format(param[1],people))          # Report to the user number of people


## Join lunch time group
########################
def join_group(msg):
  # Globals
  global bd
  global bot

  chat_id = msg['chat']['id']                                                           # Retrieve mensage parameters
  param   = msg['text']
  param   = param.split(" ")
  
  try:
    time.strptime(param[1], '%H:%M')                                                    # Check proposed time format
  except ValueError:
    bot.send_message(chat_id,"Time format incorrect, should be HH:MM")                  # Incorrect format was proposed
    return
  
  
  today = str(datetime.datetime.now().day)                                              # Retrieve today's date

  keyname = 'HP_{}_{}'.format(today,param[1])                                           # Create label format UPGRADE: Different locations
  keys    = bd.get_keys(keyname)                                                        # Retrieve all matching keys from DB

  if not keys:                                                                          # If no appointment is found...
    bot.send_message(chat_id,'No proposal has been found')                              # ...report to the user
    return

  bd.insert_left_list(keyname, chat_id)                                                 # Add user to key list
  bot.send_message(chat_id,'You have joined the {} group'.format(param[1]))             # Report to the user

## Leave lunch time group
#########################
def leave_group(msg):
  # Globals
  global bd
  global bot

  chat_id = msg['chat']['id']                                                           # Retrieve message parameters
  
  today = str(datetime.datetime.now().day)                                              # Retrieve today's date

  keyname = 'HP_{}_*'.format(today)                                                     # Create key format UPGRADE: Use different locations
  keys    = bd.get_keys(keyname)                                                        # Retrieve all keys in DB

  if not keys:                                                                          # If no key was found for today...
    bot.send_message(chat_id,'No proposal has been found')                              # ...inform the user

  for key in keys:                                                                      # Check for all keys retrieved from today
    res = bd.remove_from_list(key, chat_id)                                             # Remove element from list
    if res is not 0:                                                                    # If at least one element was removed
      proposal = key.split("_")                                                         # Get time from key
      bot.send_message(chat_id,'You have been removed from {}'.format(proposal[2]))     # Announced removed time

# Emergency shutdown
####################
def end_execution(msg):
  # Retrieve variables
  global c_end
  global bot
  
  chat_id = msg['chat']['id']                                                           # Retrieve parameters

  bot.send_message(chat_id,'Performing arakiri')                                        # Report to user
  print 'I die alone'                                                                   # Report to console
  c_end = 0                                                                             # Kill thread loop

# Report error message
######################
def report_error(msg):
  global bot

  chat_id = msg['chat']['id']                                                           # Retrieve message parameters

  bot.send_message(chat_id,'This is an error')                                          # Report to the user

###########################################################################################################################################
# List of user available commands                                                                                                        ##
###########################################################################################################################################
commands = { '/hello':    hello_msg,                                                    # Send greeting message
             '/list':     list_groups,                                                  # List all available groups for today
             '/propose':  propose_group,                                                # Create or join a lunch group
             '/join':     join_group,                                                   # Join a lunch group
             '/howmany':  how_many_group,                                               # How many members requested to join lunch time             
             '/leave':    leave_group,                                                  # Be removed from all lunch groups
             '/die':      end_execution,                                                # Emergency stop for script
             '/error':    report_error}                                                 # Error found

###########################################################################################################################################
# Thread loop methods (Telegram bot and ERNI Lunch application)                                                                          ##
###########################################################################################################################################

## Function to advise of incomming lunch time
#############################################
def call_out(now):
  # Globals
  global bd
  global bot

  today = now.day                                                              # Retrieve day
  h     = now.hour                                                             # Hour
  m     = now.minute                                                           # Minute
  
  try:                                                                         # Test proposed time
    proTime = '{:02}:{:02}'.format(h, m+5)                                     # Generate lunch time in 5 min
    time.strptime(proTime, '%H:%M')                                            # Check correct time format
    m = m+5                                                                    # No issue found, advance 5 min
  except ValueError:
    h =  h + 1                                                                 # TODO: This should take into account 24h clock and day/month/year
    m = (m + 5)%60                                                             # Advance 5 min into next hour

  keyname = 'HP_{}_{:02}:{:02}'.format(today,h,m)                              # Compose appointment name
  keys = bd.get_keys(keyname)                                                  # Get appointment in 5 min

  if not keys:                                                                 # No appointment is found
    return

  for key in keys:                                                             # There should be only one...
    check = 'CHECKED_HP_{}_{:2}:{:2}'.format(today,h,m)                        # Compose check mark
    res   = bd.get_keys(check)                                                 # Ask check mark
    if not res:                                                                # If there is no mark
      attendees = bd.get_list_value(keyname)
      for attendee in attendees:                                               # For each attendee
        bot.send_message(attendee,'Lunch is in 5 min')                         # Send a message

      bd.insert_left_list(check, 0)                                            # Add flag
      bd.expire(check,60)                                                      # Add expiration (1 min)

## Method used to process each message received
###############################################
def proc_mess(msg):

  flavor = bot.get_flavor(msg)                                                 # Retrieve message flavor

  if flavor is 'chat':                                                         # If it is a 'chat' message
    message = msg['text']                                                      # Retrieve the message text

    command = message.split(" ")                                               # Extract commands and parameters

    if command[0] not in commands:                                             # If command is not understood...
      command[0] = '/error'                                                    # ...mark it as an error

    commands[command[0]](msg)                                                  # Execute command based on dictionary




###########################################################################################################################################
# Operation loop (Main thread loop execution)                                                                                            ##
###########################################################################################################################################

# Attach message processing method to bot
#########################################
bot.add_handle(proc_mess)                                                      # Attach handling message method to bot

# While python process is not called to end
###########################################
while c_end:                                                                   # Thread failsafe
  call_out(datetime.datetime.now())                                            ## Check if any lunch proposal is due
  time.sleep(5)                                                                ## Sleep for 5 secs
