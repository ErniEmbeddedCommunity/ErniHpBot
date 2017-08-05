"""
Data base connection
"""
import string
import sys

import redis


class BDWrapper:
    """Helper functions to connect to the database"""
    DB = None
    @classmethod
    def getDB(cls):
        if cls.DB is None:
            cls.createDBConnection()
        return cls.DB

    @classmethod
    def createDBConnection(cls):
        if cls.DB is None:
            cls.DB = BDWrapper()

    def __init__(self):
        self.__conn = redis.Redis()
        print('I am BD')

    def __enter__(self):
        print('I enter')

    def __exit__(self, exc_type, exc_value, traceback):
        print('BD is going to die')

    @staticmethod
    def sayhello():
        print('Hello world')

    def create_new_entry(self, keyname):

        fields = {"field1":"Hola", "field2":"qtal"}

        self.__conn.hmset(keyname, fields)

        test = self.__conn.hmget(keyname, "field1")
        test2 = self.__conn.hmget(keyname, "field2")

        print(test)
        print(test2)

    def get_key_value(self, keyname):
        """ Get key value """
        values = self.__conn.get(keyname)

        return values

    def set_key_value(self, keyname, value):
        self.__conn.set(keyname, value)

    def get_hash_value(self, keyname, field):
        """ Get hash value """
        values = self.__conn.hmget(keyname, field)

        return values

    def set_hash_value(self, keyname, field, value):
        """Set hash value"""
        self.__conn.hset(keyname, field, value)

    ###################################################################
    ## NEW DEFINITIONS BASED ON LISTS                                ##
    ###################################################################

    def get_keys(self, keypattern):
        """ Retrieve keys with pattern"""
        keys = self.__conn.keys(keypattern)

        return keys

    def insert_left_list(self, keyname, value):
        """ Insert new entry into list"""
        temp = self.__conn.lrange(keyname, 0, -1)

        if len(temp) is not 0:
            temp = self.__conn.lrem(keyname, value)

        self.__conn.lpush(keyname, value)

    def get_length(self, keyname):
        """ Check length"""
        return self.__conn.llen(keyname)

    def get_list_value(self, keyname):
        """ Retrieve list value"""
        return self.__conn.lrange(keyname, 0, -1)

    def remove_from_list(self, keyname, value):
        """ Remove element from list"""
        # Remove from list
        res = self.__conn.lrem(keyname, value)

        # Check if list is empty
        if not self.__conn.llen(keyname):
            self.__conn.delete(keyname)

        return res

    def expire(self, keyname, exptime):
        """Set to 8 hours expiring"""
        self.__conn.expire(keyname, exptime)
