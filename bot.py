"""
The main entry point for our bot, which tells Discord what commands the bot can
perform and how to do so.
"""

import os

from discord.ext import commands, tasks
from dotenv import load_dotenv

from actions import *
from game import perform_timestep, load_game
from utils import OKAY_REACT
from consts import *

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# GENERAL COMMANDS

# TODO: CREATE COGS FOR THE DIFFERENT SETS OF COMMANDS (e.g. one for movement, one for power etc)

bot = commands.Bot(command_prefix="!")

@bot.command(name="setdir")
@commands.has_any_role(CAPTAIN, NAVIGATOR)
async def player_move(ctx, direction):
    """
    Sets the direction of your submarine to <direction>.
    """
    await perform(move, ctx, direction, get_team(ctx.author))

@bot.command(name="force_setdir")
@commands.has_role(CONTROL_ROLE)
async def control_move(ctx, team, direction):
    """
    (CONTROL) Forces <team>'s submarine to a given direction. Does not inform them.
    """
    await perform(move, ctx, direction, team)

@bot.command(name="teleport")
@commands.has_role(CONTROL_ROLE)
async def teleport_sub(ctx, team, x : int, y : int):
    """
    (CONTROL) Teleports <teams>'s submarine to a given (<x>, <y>). Does not inform them.
    Also does _not_ check if the position is blocked, but does check if it's a valid point in the world.
    """
    await perform(teleport, ctx, team, x, y)

@bot.command(name="register")
@commands.has_role(CONTROL_ROLE)
async def register_team(ctx, x : int = 0, y : int = 0):
    """
    (CONTROL) Registers a new team (with sub at (x,y) defaulting to (0,0)) to the parent channel category.
    Assumes that its name is the name of channel category, and that a channel exists per role in that category: #engineer, #navigator, #captain and #scientist.
    """
    await perform_async(register, ctx, ctx.message.channel.category, x, y)

@bot.command(name="activate")
@commands.has_any_role(CAPTAIN, NAVIGATOR)
async def on(ctx):
    """
    Activates your submarine, allowing it to move and do actions in real-time.
    """
    await perform(set_activation, ctx, get_team(ctx.author), True)

@bot.command(name="deactivate")
@commands.has_any_role(CAPTAIN, NAVIGATOR)
async def off(ctx):
    """
    Deactivates your submarine, stopping it from moving and performing actions.
    Needed for docking.
    """
    await perform(set_activation, ctx, get_team(ctx.author), False)

@bot.command(name="map")
async def player_map(ctx):
    """
    Shows a map of the world, including your submarine!
    """
    await perform(print_map, ctx, get_team(ctx.author))

@bot.command(name="mapall")
@commands.has_role(CONTROL_ROLE)
async def control_map(ctx):
    """
    (CONTROL) Shows a map of the world, including all submarines.
    """
    await perform(print_map, ctx, None)

@bot.command(name="power")
@commands.has_any_role(CAPTAIN, ENGINEER)
async def power(ctx, *systems):
    """
    Gives one power to all of <systems> (any number of systems, can repeat).
    Fails if this would overload the power.
    """
    await perform(power_systems, ctx, get_team(ctx.author), list(systems))

@bot.command(name="force_power")
@commands.has_role(CONTROL_ROLE)
async def control_power(ctx, team, *systems):
    """
    (CONTROL) Forces <team> to give one power to all of <systems>.
    """
    await perform(power_systems, ctx, team, list(systems))

@bot.command(name="unpower")
@commands.has_any_role(CAPTAIN, ENGINEER)
async def unpower(ctx, *systems):
    """
    Removes one power from all of <systems> (any number of systems, can repeat).
    Fails if this would reduce a system's power below zero.
    """
    await perform(unpower_systems, ctx, get_team(ctx.author), list(systems))

@bot.command(name="force_unpower")
@commands.has_role(CONTROL_ROLE)
async def control_unpower(ctx, team, *systems):
    """
    (CONTROL) Forces <team> to remove one power from all of <systems>.
    """
    await perform(unpower_systems, ctx, team, list(systems))

@bot.command(name="status")
async def status(ctx):
    """
    Reports the status of the submarine, including power and direction.
    """
    await perform(get_status, ctx, get_team(ctx.author), main_loop)

@bot.command(name="broadcast")
@commands.has_any_role(CAPTAIN, NAVIGATOR)
async def do_broadcast(ctx, message):
    """
    Broadcasts a <message> to all in range. Requires the sub to be activated.
    """
    await perform_async(broadcast, ctx, get_team(ctx.author), message)

@bot.command(name="puzzle")
@commands.has_role(ENGINEER)
async def repair_puzzle(ctx):
    """
    Gives you a puzzle, which must be solved before you next move. If you
    already have a puzzle in progress, it will be treated as if you ran out of
    time!
    """
    await perform_async(give_team_puzzle, ctx, get_team(ctx.author), "repair")

@bot.command(name="answer")
@commands.has_any_role(CAPTAIN, ENGINEER)
async def answer_puzzle(ctx, answer: str):
    """
    Lets you answer a set puzzle that hasn't resolved yet.
    """
    await perform_async(answer_team_puzzle, ctx, get_team(ctx.author), answer)

# LOOP HANDLING

@tasks.loop(seconds=GAME_SPEED)
async def main_loop():
    await perform_timestep(main_loop.current_loop)

@bot.command(name="startloop")
@commands.has_role(CONTROL_ROLE)
async def startloop(ctx):
    """
    (CONTROL) Starts the main game loop, so that all submarines can act if activated.
    You should use this at the start of the game, and then only again if you have to pause the game for some reason.
    """
    main_loop.start()
    await OKAY_REACT.do_status(ctx)

# TODO: replace stop with cancel, but only after introducing a lock that prevents cancellation during the running of the loop.
# in fact, have a lock just so that the loop bit runs without issue.
# you can do this with asyncio.Lock - although it's slightly more complex than that.
# do we want a reader-writer lock?

@bot.command(name="stoploop")
@commands.has_role(CONTROL_ROLE)
async def stoploop(ctx):
    """
    (CONTROL) Stops the main game loop, effectively pausing the game.
    You should only use this at the end of the game, or if you need to pause the game for some reason.
    """
    main_loop.stop()
    await OKAY_REACT.do_status(ctx)

# USEFUL CONTROL FUNCTIONALITY

@bot.command(name="control_message")
@commands.has_role(CONTROL_ROLE)
async def message_team(ctx, team, message):
    """
    (CONTROL) Sends to <team> the message <message>, regardless of distance.
    """
    await perform_async(shout_at_team, ctx, team, message)

@bot.command(name="damage")
@commands.has_role(CONTROL_ROLE)
async def damage(ctx, team, amount : int, reason=""):
    """
    (CONTROL) Forces <team> to take <amount> damage. You can optionally specify a <reason> which will be messaged to them before.
    """
    await perform_async(deal_damage, ctx, team, amount, reason)

@bot.command(name="upgrade")
@commands.has_role(CONTROL_ROLE)
async def upgrade(ctx, team, amount : int):
    """
    (CONTROL) Upgrades <team>'s reactor by <amount>.
    You can specify a negative number, but this will not check that the resulting state makes sense (that is, the team is not using more power than they have) - in general you should use !damage instead.
    """
    await perform_async(upgrade_sub, ctx, team, amount)

@bot.command(name="upgrade_system")
@commands.has_role(CONTROL_ROLE)
async def upgrade_system(ctx, team, system, amount : int):
    """
    (CONTROL) Upgrades <team>'s system by <amount>.
    You can specify a negative number to downgrade, and it will check that this makes sense.
    """
    await perform_async(upgrade_sub_system, ctx, team, system, amount)

@bot.command(name="upgrade_innate")
@commands.has_role(CONTROL_ROLE)
async def upgrade_innate(ctx, team, system, amount : int):
    """
    (CONTROL) Upgrades <team>'s innate system by <amount>.
    You can specify a negative number to downgrade, and it will check that this makes sense.
    """
    await perform_async(upgrade_sub_innate, ctx, team, system, amount)

@bot.command(name="install_system")
@commands.has_role(CONTROL_ROLE)
async def new_system(ctx, team, system):
    """
    (CONTROL) Gives <team> access to new system <system>.
    """
    await perform_async(add_system, ctx, team, system)

@bot.command(name="bury")
@commands.has_role(CONTROL_ROLE)
async def bury(ctx, treasure, x : int, y : int):
    """
    (CONTROL) Buries a treasure <treasure> at location (<x>, <y>).
    """
    await perform(bury_treasure, ctx, treasure, x, y)

@bot.command(name="force_puzzle")
@commands.has_role(CONTROL_ROLE)
async def force_puzzle(ctx, team):
    """
    (CONTROL) Gives team <team> a puzzle, resolving any puzzles they currently have.
    """
    await perform_async(give_team_puzzle, ctx, team, "fixing")

@bot.command(name="load")
@commands.has_role(CONTROL_ROLE)
async def load(ctx, arg):
    """
    (CONTROL) Loads either the map, state or both from file.
    """
    await perform(load_game, ctx, arg, bot)

# HELPER FUNCTIONS

def get_team(author):
    """
    Gets the first role that has a submarine associated with it, or None.
    """
    roles = list(map(lambda x: x.name, author.roles))
    for team in get_teams():
        if team in roles:
            return team
    return None

async def perform(fn, ctx, *args):
    """
    Performs an action fn with *args and then performs the Discord action
    returned by fn using the context ctx.
    """
    status = fn(*args)
    if status: await status.do_status(ctx)

async def perform_async(fn, ctx, *args):
    """
    Performs an async fn with *args and then the Discord action returned
    by fn using the context ctx.
    """
    status = await fn(*args)
    if status: await status.do_status(ctx)

# ERROR HANDLING AND BOT STARTUP

@bot.event
async def on_command_error(ctx, error):
    print(error)
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send("You do not have the correct role for this command.")
    else:
        await ctx.send(f"ERROR: {error}")

print("ALTANTIS READY")
bot.run(TOKEN)
