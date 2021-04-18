#!/usr/bin/python3

import argparse
import EPDClient

parser = argparse.ArgumentParser()
parser.add_argument('command', help='init | update | sleep')

args = parser.parse_args()

client = EPDClient.EPDClient()
client.connect()

commands = {
    'init': client.init,
    'update': client.update,
    'sleep': client.sleep
}

commands[args.command]()

client.disconnect()
