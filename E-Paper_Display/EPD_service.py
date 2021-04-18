#!/usr/bin/python3

from PIL import Image

import os
import logging
import socket
import stat

import EPD
import EPDExceptions
import SevenFiveEPD

paths = {
    'frame': '/var/epd/frame.bmp',
    'socket': '/var/run/epd.sock',
    'log': '/var/log/epd.log'
}
epdGID = 1000

display_interface = EPD.DisplayInterface(SevenFiveEPD.commands)
display = EPD.Display(SevenFiveEPD.width, SevenFiveEPD.height, display_interface)

logger = logging.getLogger('EPDService')
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

file_handler = logging.FileHandler(paths['log'])
file_handler.setLevel(logging.WARNING)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

epd_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

try:
    os.remove(paths['socket'])
except OSError:
    pass

epd_socket.bind(paths['socket'])
os.chmod(paths['socket'], stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP | stat.S_IWGRP)
os.chown(paths['socket'], -1, epdGID)
epd_socket.listen(1)

logger.info('Socket ready')

# Waits for connection.
while True:
    connection_socket, connection_address = epd_socket.accept()
    logger.info('New connection')

    try:
        # Executes connection's commands.
        while True:
            command = connection_socket.recv(1)

            if not command:
                break

            if command == b'0': # Init command.
                logger.debug('Initializing display')

                try:
                    display.init()
                except BaseException as exception:
                    logger.error('Initialization failed: ' + str(exception))
                    connection_socket.send(b'1') # Error code.

                    continue

                connection_socket.send(b'0') # Success code.
            elif command == b'1': # Update command.
                logger.debug('Updating display')

                try:
                    frame = Image.open(paths['frame'])
                except IOError as exception:
                    logger.error('Error loading frame file: ' + str(exception))
                    connection_socket.send(b'2') # Frame error code.

                    continue

                try:
                    display.display_frame(frame.load())
                except ValueError as exception:
                    logger.error('Error processing frame: ' + str(exception))
                    connection_socket.send(b'2') # Frame error code.

                    continue
                except EPDExceptions.InvalidDisplayStatusException as exception:
                    logger.debug('Update attempted while display was sleeping')
                    connection_socket.send(b'3') # Display status error code.

                    continue
                except BaseException as exception:
                    logger.error('Update failed: ' + str(exception))
                    connection_socket.send(b'1') # Error code.

                    continue

                connection_socket.send(b'0') # Success code.
            elif command == b'2': # Sleep command.
                logger.debug('Powering off display')

                try:
                    display.sleep()
                except BaseException as exception:
                    logger.error('Powering off failed: ' + str(exception))
                    connection_socket.send(b'1') # Error code.

                    continue

                connection_socket.send(b'0') # Success code.
            else:
                connection_socket.send(b'1') # Error code.
    except BrokenPipeError:
        pass

    connection_socket.close()
    logger.info('Connection closed')
