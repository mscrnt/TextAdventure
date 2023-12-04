# debug_config.py

import sys
import traceback
from icecream import ic

class DebugConfig:
    DEBUG_LEVELS = {
        'INFO': 1,
        'DEBUG': 2,
        'WARNING': 3,
        'ERROR': 4,
    }

    # Default level
    CURRENT_LEVEL = DEBUG_LEVELS['INFO']

    @staticmethod
    def set_level(level):
        DebugConfig.CURRENT_LEVEL = DebugConfig.DEBUG_LEVELS.get(level, DebugConfig.CURRENT_LEVEL)
        DebugConfig.configure_icecream()

    @staticmethod
    def configure_icecream():
        # Configure icecream based on the debug level
        if DebugConfig.CURRENT_LEVEL >= DebugConfig.DEBUG_LEVELS['DEBUG']:
            ic.enable()
            ic.configureOutput(includeContext=True)
            ic.configureOutput(prefix='DEBUG - ')
            ic.configureOutput(includeContext=True, prefix='DEBUG - ')
            ic.configureOutput(includeContext=True, prefix='DEBUG - ', outputFunction=print)
        else:
            ic.disable()

        # Set custom exception handler
        #sys.excepthook = DebugConfig.handle_exception

    # @staticmethod
    # def handle_exception(exc_type, exc_value, exc_traceback):
    #     if not issubclass(exc_type, KeyboardInterrupt):
    #         ic("Uncaught exception:", {
    #             'type': exc_type, 
    #             'value': exc_value, 
    #             'traceback': traceback.format_tb(exc_traceback)
    #         })

