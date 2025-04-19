import sys
from colorama import Fore, Style


def msg(msg: str, prefix="•"):
    """Write a nicely formatted message with a leading bullet point to the console."""

    str = prefix + " " + msg if prefix != "" else msg
    print(str)


def info(msg: str, suffix: str = "", prefix: str = "  →"):
    """Write an indented info string with a cyan arrow to the console."""

    str = Fore.CYAN + prefix + Style.RESET_ALL + " " + msg if prefix != "" else msg
    if suffix != "":
        str += Fore.LIGHTBLACK_EX + suffix + Style.RESET_ALL
    print(str)


def success(msg: str, suffix: str = "", prefix: str = "✓"):
    """Write a success message with a green check mark to the console."""

    str = Fore.GREEN + prefix + Style.RESET_ALL + " " + msg if prefix != "" else msg
    if suffix != "":
        str += Fore.LIGHTBLACK_EX + suffix + Style.RESET_ALL
    print(str)


def error(msg: str, suffix: str = "", prefix: str = "  ✗"):
    """Write an error message with a red cross to the console."""

    str = Fore.RED + prefix + Style.RESET_ALL + " " + msg if prefix != "" else msg
    if suffix != "":
        str += Fore.LIGHTBLACK_EX + suffix + Style.RESET_ALL
    print(str)
