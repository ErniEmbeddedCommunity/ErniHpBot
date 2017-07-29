"""
This file contais the definition of TUser class and helpers to
abstract the communication with the database
"""
import redis as db
import pickle

CONN = db.StrictRedis()


def redis_decode(inbytes):
    """Helper function to decode bytes from database."""
    return inbytes.decode("utf-8")


class TUser():
    """handles the data for each user"""

    def __init__(self, telegram_user):
        self.id = telegram_user["id"]
        for key, value in telegram_user.items():
            self[key] = value

    def __setattr__(self, name, value):
        if name == "id":
            self.__dict__["id"] = value
            CONN.set("telegram_users_id", value)
            # self.pickle_set("telegram_users_id", value)
        else:
            if isinstance(value, set):
                RedisSet(self.redis_prefix(name), value)
            if isinstance(value, list):
                RedisList(self.redis_prefix(name), value)
            elif isinstance(value, str):
                CONN.set(self.redis_prefix(name), value)
            else:
                raise NotImplementedError(
                    "Type of: " + type(value).__name__ + " is not implemented yet.")

    def __getattr__(self, name):
        # byteValue = self.pickle_get(self.redis_prefix(name))
        # return byteValue
        keytype = CONN.type(self.redis_prefix(name)).decode("utf-8")
        if keytype == "none":
            return None
        elif keytype == "string":
            byte_value = CONN.get(self.redis_prefix(name))
            try:
                float_value = float(byte_value)
                return float_value
            except ValueError:
                pass
            try:
                int_value = int(byte_value)
                return int_value
            except ValueError:
                pass
            str_value = str(byte_value.decode("utf-8"))
            return str_value
        elif keytype == "set":
            return RedisSet(self.redis_prefix(name))
        elif keytype == "list":
            return RedisList(self.redis_prefix(name))
        else:
            raise NotImplementedError(
                "Key type " + str(keytype) + " is not supported.")

    def __dir__(self):
        attr = iter(self)
        return attr

    def __iter__(self):
        long_keys = map(redis_decode, CONN.keys(self.redis_prefix("*")))
        for long_key in long_keys:
            key = long_key[long_key.find('_') + 1:]
            try:
                yield(key, self[key])
            except UnicodeDecodeError as error:
                pass
                # print("invalid key in database: " + key + " " + str(error))

    def __getitem__(self, name):
        return self.__getattr__(name)

    def __setitem__(self, name, value):
        self.__setattr__(name, value)

    def redis_prefix(self, attr):
        """Generates the prefix for a desired attribute."""
        return str(self.id) + "_" + attr
    # pickle was an idea to store the data in the database
    # independently of the data type
    # Now I think it's preferable to use only raw strings
    # to allow external programms to read the database

    @staticmethod
    def pickle_sadd(key, value):
        """NOT IN USE: stores the value as a pickle serialized data."""
        CONN.sadd(key, pickle.dumps(value))

    @staticmethod
    def pickle_set(key, value):
        """NOT IN USE: stores the value as a pickle serialized data."""
        CONN.set(key, pickle.dumps(value))

    @staticmethod
    def pickle_get(key):
        """NOT IN USE: recover the value as a pickle serialized data."""
        value = CONN.get(key)
        if value != None:
            # return value
            return pickle.loads(value)
        else:
            return None


class RedisSet:
    """
    allows the user to interact with redis set as if it were
    a python set.
    """

    def __init__(self, key, setvalues=set()):
        self.key = key
        self._identification_key = "__redis_set__"
        CONN.sadd(key, self._identification_key)
        for value in setvalues:
            self.add(value)

    def add(self, value):
        if value == self._identification_key:
            Exception("this is an internal value.")
        CONN.sadd(self.key, value)

    def remove(self, value):
        if value == self._identification_key:
            Exception("this is an internal value.")
        CONN.srem(self.key, value)

    def clear(self):
        CONN.delete(self.key)
        CONN.sadd(self.key, self._identification_key)

    def __iter__(self):
        members = set(map(redis_decode, CONN.smembers(self.key)))
        members.remove(self._identification_key)
        for member in members:
            yield member

    def __repr__(self):
        return super().__repr__() + " " + self.__str__()

    def __str__(self):
        return "[" + ",".join(map(str, iter(self))) + "]"


class RedisList:
    """
    allows the user to interact with redis list as if it were
    a python list.
    """

    def __init__(self, key, setvalues=list()):
        self.key = key
        self._identification_key = "__redis_list__"
        CONN.lrem(key, 1, self._identification_key)
        CONN.lpush(key, self._identification_key)
        for value in setvalues:
            self.append(value)

    def append(self, value):
        if value == self._identification_key:
            Exception("this is an internal value.")
        CONN.rpush(self.key, value)

    def remove(self, value, count=1):
        if value == self._identification_key:
            Exception("this is an internal value.")
        CONN.lrem(self.key, count, value)

    def rpop(self):
        return redis_decode(CONN.rpop(self.key))

    def lpop(self):
        return redis_decode(CONN.lpop(self.key))

    def rpush(self, value):
        CONN.rpush(self.key, value)

    def lpush(self, value):
        CONN.lpush(self.key, value)

    def clear(self):
        CONN.delete(self.key)
        CONN.lpush(self.key, self._identification_key)

    def __iter__(self):
        # members = list(map(redis_decode, CONN.lrange(self.key, 0, -1)))
        members = self[0:-1]
        members.remove(self._identification_key)
        for member in members:
            yield member

    def __setitem__(self, item, value):
        CONN.lset(self.key, item, value)

    def __delitem__(self, item):
        CONN.lset(self.key, item, self._identification_key)
        CONN.lrem(self.key, -1, self._identification_key)

    def __getitem__(self, index):
        if isinstance(index, slice):
            return list(map(redis_decode, CONN.lrange(self.key, index.start, index.stop)))
        else:
            lrange = CONN.lrange(self.key, index, index)
            return redis_decode(lrange[0])

    def __repr__(self):
        return super().__repr__() + " " + self.__str__()

    def __str__(self):
        return "[" + ",".join(map(str, iter(self))) + "]"
