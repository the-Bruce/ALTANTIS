CONTROL_ROLE = "CONTROL"
ENGINEER = "engineer"
SCIENTIST = "scientist"
CAPTAIN = "captain"

CURRENCY_NAME = "squid"
RESOURCES = ["circuitry", "specimen", "plating", "tool"]

# The speed of the game, in _seconds_. Remember that most submarines will start
# moving every four "turns", so really you should think about 4*GAME_SPEED.
GAME_SPEED = 5

# Comms system.
GARBLE = 10
COMMS_COOLDOWN = 30

# Map size.
X_LIMIT = 40
Y_LIMIT = 40

direction_emoji = {"n": "⬆", "e": "➡", "s": "⬇",
                   "w": "⬅", "ne": "↗",
                   "nw": "↖", "se": "↘",
                   "sw": "↙"}

TICK = "<:greentick:745348214210822255>"
CROSS = "<:redcross:745348213149532170>"
PLUS = "<:greenplus:745389551597519061>"

ADMIN_NAME = "<@!366644564137738240>"

# env stuff

from dotenv import load_dotenv
import os
load_dotenv()

MAP_TOKEN = os.getenv('MAP_TOKEN')
MAP_DOMAIN = os.getenv('MAP_DOMAIN')
TOKEN = os.getenv('DISCORD_TOKEN')