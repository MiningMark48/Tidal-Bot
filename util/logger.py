import datetime
import os

class Colors:
    reset = '\033[0m'
    bold = '\033[01m'
    disable = '\033[02m'
    underline = '\033[04m'
    reverse = '\033[07m'
    strike_through = '\033[09m'
    invisible = '\033[08m'

    class FG:
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
    def log(type: str, color: str, msg):
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
            header = f"[{current_form}] [{str(type).upper()}]".ljust(35)

            file.write(f"{header} {msg}\n")

    @staticmethod
    def alert(msg):
        Logger.log('alert', Colors.FG.yellow, msg)

    @staticmethod
    def info(msg):
        Logger.log('info', Colors.FG.light_grey, msg)

    @staticmethod
    def fatal(msg):
        Logger.log('fatal', Colors.FG.red, msg)

    @staticmethod
    def success(msg):
        Logger.log('success', Colors.FG.green, msg)

    @staticmethod
    def warn(msg):
        Logger.log('warn', Colors.FG.purple, msg)

    @staticmethod
    def breakline():
        Logger.log('break', Colors.reset, '')
