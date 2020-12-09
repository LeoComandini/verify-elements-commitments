"""
Usage:

    python get_liquid_tx_from_esplora.py 5eeaccb09ef1a50ccfdcbe4e85f47a5d49963b74ccdd05476cd693b2f1ff9945 > data/version0/5eeaccb0.txt

"""

import sys
import requests

BASE_URL="https://blockstream.info/liquid/api/tx/{}/hex"

txid = sys.argv[1]
hex = requests.get(BASE_URL.format(txid)).text
print(hex)
