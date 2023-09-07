#
#  Copyright (c) 2018-2023 Renesas Inc.
#  Copyright (c) 2018-2023 EPAM Systems Inc.
#

import random
import string
from pathlib import Path

from rich.console import Console

CONTENT_ENCRYPTION_ALGORITHM = 'aes256_cbc'
DOWNLOADS_PATH = Path.home() / '.aos' / 'downloads'
AOS_DISKS_PATH = DOWNLOADS_PATH
NODE0_IMAGE_FILENAME = 'aos-vm-node0-genericx86-64.wic.vmdk'
NODE1_IMAGE_FILENAME = 'aos-vm-node1-genericx86-64.wic.vmdk'

DISK_IMAGE_DOWNLOAD_URL = 'https://aos-prod-cdn-endpoint.azureedge.net/vm/aos-vm.tar.gz?' \
                          '0b4236c906d1ed48a8cc1a56f430c214019bfe0901e4158abb916b2d52ebb8f' \
                          'f756d5e49e81daf5fcfd134b1b426c11367e9088538cfada40cc92efff6e990'



console = Console()
error_console = Console(stderr=True, style='red')
allow_print = True

def print_message(formatted_text, end="\n", ljust: int = 0):
    if allow_print:
        if ljust > 0:
            formatted_text = formatted_text.ljust(ljust)
        console.print(formatted_text, end=end)

def print_left(formatted_text, ljust=60):
    print_message(formatted_text, end='', ljust = ljust)

def print_done():
    print_message('[green]DONE')

def print_success(message):
    print_message(f'[green]{str(message)}')

def print_error(message):
    if allow_print:
        error_console.print(message)

def generate_random_password() -> str:
    """
    Generate random password from letters and digits.

    Returns:
        str: Random string password
    """
    dictionary = string.ascii_letters + string.digits
    password_length = random.randint(10, 15)
    return ''.join(random.choice(dictionary) for _ in range(password_length))
