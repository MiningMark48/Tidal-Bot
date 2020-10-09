import datetime
import os


class Colors:
    """
    Colors used for logging to console.
    """

    reset = '\033[0m'
    bold = '\033[01m'
    disable = '\033[02m'
    underline = '\033[04m'
    reverse = '\033[07m'
    strike_through = '\033[09m'
    invisible = '\033[08m'

    class FG:
        """
        Foreground colors
        """

        black = '\033[30m'
        red = '\033[31m'
        green = '\033[32m'
        orange = '\033[33m'
        blue = '\033[34m'
        purple = '\033[35m'
        cyan = '\033[36m'
        light_grey = '\033[37m'
        dark_grey = '\033[90m'
        light_red = '\033[91m'
        light_green = '\033[92m'
        yellow = '\033[93m'
        light_blue = '\033[94m'
        pink = '\033[95m'
        light_cyan = '\033[96m'

    class BG:
        """
        Background colors
        """

        black = '\033[40m'
        red = '\033[41m'
        green = '\033[42m'
        orange = '\033[43m'
        blue = '\033[44m'
        purple = '\033[45m'
        cyan = '\033[46m'
        light_grey = '\033[47m'


class Logger:

    @staticmethod
    def log(typ: str, color: str, msg):
        """
        Logs a message to console and saves to a log file.

        :param typ: Beginning log tag, in brackets
        :param color: Color of log text
        :param msg:  Message to log to console
        """

        # Print to console
        print(f"{color}{msg}{Colors.reset}")

        # Write to file
        current_time = datetime.datetime.now()

        filename = f'logs/{current_time.strftime("%m%y")}.log'
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError:
                raise

        with open(filename, 'a') as file:
            current_form = current_time.strftime("%m/%d/%y %r")
            header = f"[{current_form}] [{str(typ).upper()}]".ljust(35)

            file.write(f"{header} {msg}\n")

    @staticmethod
    def alert(msg):
        """
        Logs a message to console (Yellow FG)

        :param msg: Message to log to console
        """

        Logger.log('alert', Colors.FG.yellow, msg)

    @staticmethod
    def info(msg):
        """
        Logs a message to console (Light Grey FG)

        :param msg: Message to log to console
        """

        Logger.log('info', Colors.FG.light_grey, msg)

    @staticmethod
    def fatal(msg):
        """
        Logs a message to console (RED FG)

        :param msg: Message to log to console
        """

        Logger.log('fatal', Colors.FG.red, msg)

    @staticmethod
    def success(msg):
        """
        Logs a message to console (Green FG)

        :param msg: Message to log to console
        """

        Logger.log('success', Colors.FG.green, msg)

    @staticmethod
    def warn(msg):
        """
        Logs a message to console (Purple FG)

        :param msg: Message to log to console
        """

        Logger.log('warn', Colors.FG.purple, msg)

    @staticmethod
    def breakline():
        """
        Empty log message, acts as a break line.
        """
        
        Logger.log('lnbrk', Colors.reset, '')
