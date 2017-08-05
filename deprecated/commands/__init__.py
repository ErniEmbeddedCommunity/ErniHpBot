"""includes all the commands."""

from os.path import dirname, basename, isfile
import glob
modules = glob.glob(dirname(__file__) + "/*")
__all__ = [basename(f) for f in modules if not isfile(f)
           and not f.endswith('__pycache__')]
print("loaded " + str(__all__) + " commands")

# __all__ = ['tools']
from commands.CommandsBase import BaseCommand, PatternCommand, HandledStatus, ChatType, KeyboardCommand
from commands import *
