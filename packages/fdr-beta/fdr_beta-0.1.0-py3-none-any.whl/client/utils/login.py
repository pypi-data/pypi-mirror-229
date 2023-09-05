# FDR Client Login 

# Libraries
from ..utils.utils import clear
from time import sleep
import sys, os

def auth(un:str, pw:str):
    """
    Login per FDR user 
    """
    if un=="user" and pw=="pass":
        return 200
    else:
        return 404

def auth_denied():
    """
    Message & reload FDR client if auth fails
    """
    print("\nAuthentication failed, restarting FaradAI Client in:")
    for i in range(3):
        print(f'{3-i}')
        sleep(1)
    # clear terminal
    clear()
    # restart script
    os.system(f"{sys.executable} {' '.join(sys.argv)}")