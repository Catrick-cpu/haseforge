# haseforge/logger.py

from colorama import init, Fore
from pyfiglet import Figlet

init(autoreset=True)

f = Figlet(font="slant")


def log(msg):
    print(msg)


def banner(text):
    print(Fore.RED + f.renderText(text))