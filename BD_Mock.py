import sys
import string
import redis


class BD_wrapper:
  def __init__(self):
  	self.__conn = redis.Redis()
  	print 'I am BD'

  def __enter__(self):
    print 'I enter'

  def __exit__(self, exc_type, exc_value, traceback):
    print 'BD is going to die'

  def sayhello(self):
    print 'Hello world'

  def createNewEntry(self, keyname):

    fields = {"field1":"Hola","field2":"qtal"}

    self.__conn.hmset(keyname, fields)

    test  = self.__conn.hmget(keyname, "field1")
    test2 = self.__conn.hmget(keyname, "field2")

    print test
    print test2

  

  #################
  # Get key value #
  #################
  def get_key_value(self, keyname):
	values = self.__conn.get(keyname)

	return (values)

  def set_key_value(self, keyname, value):
    self.__conn.set(keyname,value)


  ##################
  # Get hash value #
  ##################
  def get_hash_value(self, keyname, field):
	values = self.__conn.hmget(keyname,field)

	return (values)

  ## Set hash value
  def set_hash_value(self, keyname, field, value):
  	self.__conn.hset(keyname,field,value)
  
  ###################################################################
  ## NEW DEFINITIONS BASED ON LISTS                                ##
  ###################################################################

  ## Retrieve keys with pattern
  #############################
  def get_keys(self, keypattern):
    keys = self.__conn.keys(keypattern)

    return (keys)

  ## Insert new entry into list
  #############################
  def insert_left_list(self, keyname, value):
    temp = self.__conn.lrange(keyname, 0, -1)

    if len(temp) is not 0:
      temp = self.__conn.lrem(keyname,value)

    self.__conn.lpush(keyname,value)

  ## Check length
  ###############
  def get_length(self, keyname):
  	return self.__conn.llen(keyname)

  ## Retrieve list value
  ######################
  def get_list_value(self, keyname):
    return self.__conn.lrange(keyname, 0, -1)

  ## Remove element from list
  ###########################
  def remove_from_list(self, keyname, value):
  	# Remove from list
  	res = self.__conn.lrem(keyname, value)

  	# Check if list is empty
  	if not self.__conn.llen(keyname):
  	  self.__conn.delete(keyname)

  	return res

  def expire(self, keyname,exptime):
    self.__conn.expire(keyname, exptime)  # Set to 8 hours expiring
