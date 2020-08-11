"""
Manages individual submarines, including their subsystems.
"""

from random import choice, random, shuffle
from consts import GAME_SPEED

from discord import File as DFile

import math, datetime

MAX_SPEED = 4

subsystems = ["power", "comms", "movement", "puzzles", "scan", "inventory"]

class Submarine():
    def __init__(self, name, channels, x, y):
        # To avoid circular dependencies.
        # The one dependency is that Scan and Comms need the list of available
        # subs, but that needs this class, which needs Scan and Comms.
        from power import PowerManager
        from scan import ScanSystem
        from comms import CommsSystem
        from puzzles import EngineeringPuzzles
        from movement import MovementControls
        from inventory import Inventory

        self.name = name
        self.channels = channels
        self.power = PowerManager(self)
        self.comms = CommsSystem(self)
        self.movement = MovementControls(self, x, y)
        self.puzzles = EngineeringPuzzles(self)
        self.scan = ScanSystem(self)
        self.inventory = Inventory(self)

    def status_message(self, loop):
        message = (
            f"Status for **{self.name}**\n"
            f"------------------------------------\n\n"
        )
        
        message += self.movement.status(loop)
        message += self.power.status()
        message += self.inventory.status()

        return message + "\nNo more to report."
    
    async def send_message(self, content, channel, filename=None):
        fp = None
        if filename:
            fp = DFile(filename)
        if self.channels[channel]:
            await self.channels[channel].send(content, file=fp)
            return True
        return False
    
    async def send_to_all(self, content):
        for channel in self.channels:
            await self.channels[channel].send(content)
        return True
    
    def to_dict(self):
        """
        Converts this submarine instance to a serialisable dictionary.
        We just use self.__dict__ and then convert things as necessary.
        """
        dictionary = self.__dict__.copy()

        # self.channels: convert channels to their IDs.
        ids = {}
        for channel in self.channels:
            ids[channel] = self.channels[channel].id
        dictionary["channels"] = ids

        # Each subsystem needs to be turned into a dict, and then have its
        # parent reference removed.
        for subsystem in subsystems:
            dictionary[subsystem] = self.__getattribute__(subsystem).__dict__.copy()
            dictionary[subsystem]["sub"] = None

        return dictionary
    
def sub_from_dict(dictionary, client):
    """
    Creates a submarine from a serialised dictionary.
    """
    newsub = Submarine("", {}, 0, 0)

    # self.channels: turn channel IDs into their objects.
    channels = dictionary["channels"]
    for channel in channels:
        channels[channel] = client.get_channel(channels[channel])
    
    # Subsystems need to be remade into their classes.
    for subsystem in subsystems:
        # First, set the self-reference.
        dictionary[subsystem]["sub"] = newsub.__getattribute__(subsystem).sub
        # Then, load in the dictionary.
        newsub.__getattribute__(subsystem).__dict__ = dictionary[subsystem]
        # Finally, modify the dictionary to contain the current value of the
        # subsystem, so that it isn't overwritten later.
        dictionary[subsystem] = newsub.__getattribute__(subsystem)

    newsub.__dict__ = dictionary
    return newsub