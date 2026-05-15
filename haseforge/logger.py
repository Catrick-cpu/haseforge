# haseforge/logger.py

from colorama import init, Fore
from pyfiglet import Figlet
print("init")

if input("Boot Code:") == "1234":
    print("starting")

else:
    print("wrong code, exiting")
    exit(1)
init(autoreset=True)

f = Figlet(font="slant")


def log(msg):
    print(msg)


def banner(text):
    print(Fore.RED + f.renderText(text))