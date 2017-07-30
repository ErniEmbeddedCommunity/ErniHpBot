"""includes all the commands."""

from os.path import dirname, basename, isfile
import glob
modules = glob.glob(dirname(__file__)+"/*")
__all__ = [ basename(f) for f in modules if not isfile(f) and not f.endswith('__pycache__')]
print("loaded " + str(__all__) + " commands")


from commands.CommandsBase import command, pattern_command, HandledStatus
from commands import *