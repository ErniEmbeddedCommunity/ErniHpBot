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
def hello_msg(chat_id, text):
  global bot
  
  ## Send greeting message ##
  bot.send_message(chat_id, 'Wellcome to ERNI Lunch bot, we hope you will make the most of the application')

def talk_back(chat_id, text):
  global bot
  
  ## Repeat what was told
  bot.send_message(chat_id,text)
  

###########################################################################################################################################
## Main methods for ERNI lunch application                                                                                               ##
###########################################################################################################################################

# Main menu
###########
def main_menu(chat_id, text):
  # Globals
  global bot

  options = []                                                                           # Array to store buttons
  options.append(bot.new_custombutton('/propose XX:XX'))
  options.append(bot.new_custombutton('/list'))                                          
  
  kb = bot.new_customkeyboard(options,2)                                                 # Create custom keyboard
  bot.send_keyboard(chat_id, 'What would you like to do:', kb)                           # Send custom keyboard to the useer

# Group menu
############
def group_menu(chat_id, text):
  # Globals
  global bot
  global bd

  ptime = text.split(" ")                                                                # Retrieve text parameters

  if len(ptime) == 2:                                                                    # If text contains two parameters
    options = []                                                                         # Array to store buttons
    options.append(bot.new_custombutton('/join %s' % ptime[1]))
    options.append(bot.new_custombutton('/howmany %s' % ptime[1]))
    options.append(bot.new_custombutton('/where %s' % ptime[1]))
    options.append(bot.new_custombutton('/leave %s' % ptime[1]))                         
  
    kb = bot.new_customkeyboard(options,4)                                               # Create custom keyboard
    bot.send_keyboard(chat_id, 'You chose group %s' % ptime[1], kb)                      # Send custom keyboard
    return

  report_error(chat_id, text)                                                            # An erroneous format message

# Where command
###############
def where_group(chat_id, text):
  # Globals
  global bd
  global bot

  today = str(datetime.datetime.now().day)
  ptime = text.split(" ")

  if len(ptime) == 1:
    report_error(chat_id,text)
    return

  group   = 'LOC_HP_{}_{}'.format(today,ptime[1])
  loc_val = bd.get_key_value(group)                                                  # Get appointment in 5 min
  
  loc = 'No location has been set'

  if loc_val is not None:                                                              # There should be only one...
    loc     = 'Group is located at {}'.format(loc_val)

  # TODO FIX
  options=[]
  options.append(bot.new_inlinebutton('A0',     '/loc %s A0' % ptime[1]))
  options.append(bot.new_inlinebutton('Cashier','/loc %s Cashier' % ptime[1]))
  options.append(bot.new_inlinebutton('A2',     '/loc %s A2' % ptime[1]))
  options.append(bot.new_inlinebutton('A3',     '/loc %s A3' % ptime[1]))
  options.append(bot.new_inlinebutton('B0',     '/loc %s B0' % ptime[1]))
  options.append(bot.new_inlinebutton('B1',     '/loc %s B1' % ptime[1]))
  options.append(bot.new_inlinebutton('B2',     '/loc %s B2' % ptime[1]))
  options.append(bot.new_inlinebutton('B3',     '/loc %s B3' % ptime[1]))
  options.append(bot.new_inlinebutton('C0',     '/loc %s C0' % ptime[1]))
  options.append(bot.new_inlinebutton('C1',     '/loc %s C1' % ptime[1]))
  options.append(bot.new_inlinebutton('C2',     '/loc %s C2' % ptime[1]))
  options.append(bot.new_inlinebutton('C3',     '/loc %s C3' % ptime[1]))

  kb = bot.new_inlinekeyboard(options,4)
  bot.send_keyboard(chat_id, loc, kb)
  group_menu(chat_id,text) 

# Locate group
##############
def loc_group(chat_id, text):
  # Globals
  global bd
  global bot

  today = str(datetime.datetime.now().day)
  ptime = text.split(" ")

  group = 'LOC_HP_{}_{}'.format(today,ptime[1])
  
  if len(ptime) == 3:
    bd.set_key_value(group, ptime[2])
    bd.expire(group,60*60)
    bot.send_message(chat_id,'New location is {}'.format(ptime[2]))
    group_menu(chat_id,'{} {}'.format(ptime[0],ptime[1]))
    return

  report_error(chat_id,text)


# List lunch groups for today
#############################
def list_groups(chat_id, text):
  # Globals
  global bd
  global bot

  today = str(datetime.datetime.now().day)                                               # Retrieve today's date

  today = 'HP_{}_*'.format(today)                                                        # Format key for search
  keys = bd.get_keys(today)                                                              # Retrieve all keys (if any)

  if not keys:                                                                           # If no key was found
    bot.send_message(chat_id,'No proposal has been found')                               # ...report to the user
    main_menu(chat_id, text)                                                             # Return to main menu

  if keys:                                                                               # If any key was found...
    keys = sorted(keys)                                                                  # Sort keys (time based)
    hours = []                                                                           # Array to store buttons
    for key in keys:                                                                     # For all found keys
      tmp = key.split("_")                                                               # Retrieve time from found key
      hours.append(bot.new_inlinebutton(tmp[2],'/group %s' % tmp[2]))                    # For every hour create a button
    kb = bot.new_inlinekeyboard(hours,3)                                                 # Create inline keyboard
    bot.send_keyboard(chat_id,'Proposed times:', kb)                                     # Send inline keyboard
    main_menu(chat_id, text)                                                             # Display main menu

# Propose a new lunch group time
################################
def propose_group(chat_id, text):
  # Globals
  global bd
  global bot

  param   = text.split(" ")                                                              # Retrieve parameters  
  ptime = param[1].split(":")
  options = []                                                                           # Prepare options
  
  if ptime[0] == 'XX':                                                                   # Hour to be determined
    
    options.append(bot.new_custombutton('/propose 12:XX'))
    options.append(bot.new_custombutton('/propose 13:XX'))
    options.append(bot.new_custombutton('/propose 14:XX'))

    kb = bot.new_customkeyboard(options, 3)                                              # Prepare options
    bot.send_keyboard(chat_id, 'Chose hour:', kb)                                        # Send options
    return

  if ptime[1] == 'XX':                                                                   # Minutes to be determined
    for i in range(0,60,5):                                                              # For all available minutes (almost)
      phour = '%s:%02d' % (ptime[0], i)                                                  # Prepare label
      options.append(bot.new_custombutton('/propose %s' % phour))                        # Create option

    kb = bot.new_customkeyboard(options, 3)                                              # Create keyboard
    bot.send_keyboard(chat_id, 'Chose minute:', kb)                                      # Send keyboard
    return

  try:
    time.strptime(param[1], '%H:%M')                                                     # Check proposed time
  except ValueError:
    bot.send_message(chat_id,"Time format incorrect, should be HH:MM")                   # Report to the user the correct format
    main_menu(chat_id, text)
    return

  today = str(datetime.datetime.now().day)                                               # Retrieve today's date

  keyname = 'HP_{}_{}'.format(today,param[1])                                            # Format key UPGRADE: Locations
  keys    = bd.get_keys(keyname)                                                         # Retrieve existing keys

  if keys:                                                                               # If a key already exists...
    bd.insert_left_list(keyname, chat_id)                                                # ...join the group
    bot.send_message(chat_id,"You joined group for %s" % param[1])                       # Report to the user
    group_menu(chat_id,'/group %s' % param[1])
    return
  
  bd.insert_left_list(keyname, chat_id)                                                  # Insert new proposed time
  bd.expire(keyname,8*60*60)                                                             # Set 8h expiration (Ideas?)
  bot.send_message(chat_id,"You proposed group for %s" % param[1])                       # Report to the user
  group_menu(chat_id,'/group %s' % param[1])

## How many people in group
###########################
def how_many_group(chat_id, text):
  # Globals
  global bd
  global bot

  param   = text.split(" ")

  try:
    time.strptime(param[1], '%H:%M')                                                     # Check proposed time
  except ValueError:
    bot.send_message(chat_id,"Time format incorrect, should be HH:MM")                   # Report if it is incorrect
    main_menu(chat_id, text)
    return
  
  today = str(datetime.datetime.now().day)                                               # Retrieve today's date

  keyname = 'HP_{}_{}'.format(today,param[1])                                            # Format search key UPGRADE: Use location
  keys    = bd.get_keys(keyname)                                                         # Retrieve all matching keys from DB

  if not keys:                                                                           # If no proposal was found...
    bot.send_message(chat_id,'No proposal has been found')                               # ...report it to the user
    main_menu(chat_id, text)
    return
  
  people = bd.get_length(keyname)                                                        # Retrieve the number of people that joined

  if people == 1:                                                                        # If only one person proposed...
    bot.send_message(chat_id,'At {} only {} person'.format(param[1],people))             # ...report it to the user
    group_menu(chat_id, '/group %s' % param[1])
    return

  bot.send_message(chat_id,'At {} there are {} people'.format(param[1],people))          # Report to the user number of people
  group_menu(chat_id, '/group %s' % param[1])


## Join lunch time group
########################
def join_group(chat_id, text):
  # Globals
  global bd
  global bot

  param   = text.split(" ")

  if len(param) != 0:
    report_error(chat_id, text)
  
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
    main_menu(chat_id, text)
    return

  bd.insert_left_list(keyname, chat_id)                                                 # Add user to key list
  bot.send_message(chat_id,'You have joined the {} group'.format(param[1]))             # Report to the user
  group_menu(chat_id, '/group %s' % param[1])

## Leave lunch time group
#########################
def leave_group(chat_id, text):
  # Globals
  global bd
  global bot

  today = str(datetime.datetime.now().day)                                              # Retrieve today's date
  ptime = text.split(" ")

  keyname = 'HP_{}_{}'.format(today,ptime[1])                                           # Create key format UPGRADE: Use different locations
  keys    = bd.get_keys(keyname)                                                        # Retrieve all keys in DB

  if not keys:                                                                          # If no key was found for today...
    bot.send_message(chat_id,'No proposal has been found')                              # ...inform the user

  for key in keys:                                                                      # Check for all keys retrieved from today
    res = bd.remove_from_list(key, chat_id)                                             # Remove element from list
    if res is not 0:                                                                    # If at least one element was removed
      proposal = key.split("_")                                                         # Get time from key
      bot.send_message(chat_id,'You have been removed from {}'.format(proposal[2]))     # Announced removed time

  main_menu(chat_id, text)

# Emergency shutdown
####################
def end_execution(chat_id, text):
  # Retrieve variables
  global c_end
  global bot
  
  bot.send_message(chat_id,'Performing arakiri')                                        # Report to user
  print 'I die alone'                                                                   # Report to console
  c_end = 0                                                                             # Kill thread loop

# Report error message
######################
def report_error(chat_id, text):
  global bot

  bot.send_message(chat_id,'This is an error')                                          # Report to the user

###########################################################################################################################################
# List of user available commands                                                                                                        ##
###########################################################################################################################################
commands = { '/start':    main_menu,                                                    # /start should always be available
             '/hello':    hello_msg,                                                    # Send greeting message
             '/main':     main_menu,                                                    # Main menu of application
             '/group':    group_menu,                                                   # Actions regarding one group
             '/where':    where_group,
             '/loc':      loc_group,
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

  text = '/error'                                                              # Be on safe side

  flavor = bot.get_flavor(msg)                                                 # Retrieve message flavor

  if flavor is 'chat':                                                         # If it is a 'chat' message...
    chat_id = msg['chat']['id']                                                # Retrieve parameters
    text    = msg['text']

  if flavor is 'callback_query':                                               # If it is a 'callback_query'...
    msg_id  = msg['id']
    chat_id = msg['from']['id']                                                # Retrieve parameters
    text    = msg['data']
    bot.send_reply(msg_id,'processing')

    #bot.send_message(chat_id, text)

  command = text.split(" ")                                                    # Divide message text

  if command[0] not in commands:                                               # If command is not understood...
    command[0] = '/error'                                                      # ...mark it as an error

  commands[command[0]](chat_id, text)                                          # Execute command based on dictionary


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
