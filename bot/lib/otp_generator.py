"""
Module that just generate new otp code in Thread
"""
import hashlib
from os import urandom
from time import sleep

from lib.settings import REFRESH_TIME
import lib.util

def generate_otp():
    while True:
        # Update global variable for all modulus
        lib.util.otp_code = hashlib.md5(urandom(32)).hexdigest() 
        sleep(REFRESH_TIME)