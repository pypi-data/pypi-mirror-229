import json
import os
import sys
from dotenv import load_dotenv
from logger_local.MessageSeverity import MessageSeverity
from logger_local.LoggerOutputEnum import LoggerOutputEnum

load_dotenv()

LOGGER_CONFIGURATION_JSON = '.logger.json'
LOGGER_MINIMUM_SEVERITY = os.getenv('LOGGER_MINIMUM_SEVERITY')
DEBUG_EVERYTHING = False
LOGGER_JSON = None


class DebugMode:
    @staticmethod
    def init():
        global LOGGER_MINIMUM_SEVERITY
        global LOGGER_JSON
        global DEBUG_EVERYTHING

        if LOGGER_MINIMUM_SEVERITY == None:
            LOGGER_MINIMUM_SEVERITY = 0
        else:
            LOGGER_MINIMUM_SEVERITY = str(LOGGER_MINIMUM_SEVERITY)
            if hasattr(MessageSeverity, LOGGER_MINIMUM_SEVERITY):
                LOGGER_MINIMUM_SEVERITY = MessageSeverity[LOGGER_MINIMUM_SEVERITY].value
            elif LOGGER_MINIMUM_SEVERITY.isdigit():
                LOGGER_MINIMUM_SEVERITY = int(LOGGER_MINIMUM_SEVERITY)
            else:
                raise Exception("LOGGER_MINIMUM_SEVERITY must be a valid LoggerOutputEnum or a number or None")

        try:
            with open(LOGGER_CONFIGURATION_JSON, 'r') as file:
                LOGGER_JSON = json.load(file)
        except FileNotFoundError:
            DEBUG_EVERYTHING = True
        except Exception as exception:
            raise

    @staticmethod
    def is_logger_output(component_id: str, logger_output: LoggerOutputEnum, severity_level: int) -> bool:
        global DEBUG_EVERYTHING
        global LOGGER_MINIMUM_SEVERITY
        global LOGGER_JSON

        # Debug everything that has a severity level higher than the minimum required
        if DEBUG_EVERYTHING:
            result = severity_level >= LOGGER_MINIMUM_SEVERITY
            return result

        severity_level = max(severity_level, LOGGER_MINIMUM_SEVERITY)
        if component_id in LOGGER_JSON:
            output_info = LOGGER_JSON[component_id]
            if logger_output in output_info:
                result = severity_level >= output_info[logger_output]
                return result

        # In case the component does not exist in the logger configuration file or the logger_output was not specified
        result = True
        return result

# Call init() to initialize global variables used in is_logger_output
DebugMode.init()
