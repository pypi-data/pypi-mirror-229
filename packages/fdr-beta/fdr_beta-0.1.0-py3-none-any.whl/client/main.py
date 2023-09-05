# FDR Main Client Module

# Libraries
from .utils.utils import *
from .utils.login import *
from .utils.cmd_utils.cmd_main import *
from pwinput import pwinput
import multiprocessing

# FDR Client Method
def fdr_client():

    # Welcome message
    welcome_message()

    # Login
    un = input("Username: ")
    pw = pwinput("Password: ")
    
    if auth(un, pw) == 200:

        # cmd options after login
        initial_command_options()

    else:
        auth_denied()

# Main Executable
if __name__ == "__main__":

    # import multiprocessing freeze
    multiprocessing.freeze_support()

    # run client
    fdr_client()