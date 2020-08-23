# ALTANTIS
A possible bot for an upcoming Megagame run by Warwick Tabletop.

**If you are planning to play in the Megagame, I recommend that you do not read the source code. Most spoilers aren't tracked by Git so won't appear here, but some parts of the code are inherently spoilery.**

## README
You'll need to do a few things to run this bot. In no particular order:

* Create a directory called `/puzzles` and fill it with puzzles (each a single file). Discord will upload these, so they must fit into Discord's upload limits. These will be presented to the players in alphabetical order, so you can present beginner puzzles in slot `00.png`, and so on. You should also have an `answers.json` file in there with a filename-answer mapping like so:

```json
{
    "puzzles/00.png": "a",
    "puzzles/01.pdf": "001"
}
```

You can also specify multiple answers for a puzzle - just replace the string with a list of strings.

## Feature list

Important features:
- [x] Can have submarines, which move.
- [x] Has a map with obstacles.
- [x] Can turn the sub off and on. (Allowing players to dock.)
- [x] Submarines can travel at multiple speeds.
- [x] Full power management. Can power systems, but has a power cap (which can be increased by control).
- [x] Pretty power management (!status will tell you about upcoming power changes.)
- [x] Can broadcast messages to all in range (via Comms system, which garbles longer-distance messages). Messages have a cooldown.
- [x] A channel per person, so that role-specific info can be broadcast (engineers only get puzzles, end-of-turn, scientists only gets scanners).
- [x] Can activate scanners, and inform players when they hover over things (level 1), are near things and other named subs (level 2), and further afield (level 3). Identify things via direction.
- [x] Control can drop items on the seafloor. (!bury for control)
- [x] Can shout at an engineer - control gives a question and answer, and then the engineer has to give a response. Ship takes more damage if the engineer gets it wrong.
- [x] Basic inventory management. (!give for control, !remove for control, no !drop as that's littering)
- [x] Trading between players (see Discord discussion for model).
- [x] The Crane.
- [x] Better map squares, including the ability for other types of square to have things in them, and "treasure chests". (Basically items that look like one thing but appear in the inventory as another.) Also update The Crane to work with these.
- [x] Weapons, oh my.
- [x] !death, so you can die.

Important non-gameplay features:
- [x] Save bot state to disk with each game loop, as to avoid any issues.
- [x] Deal with locking/unlocking of the main thread, if possible. (Could have issues if someone does something during game turn execution.) I don't believe this is actually necessary, as async is still single-threaded.
- [x] Possible minor refactor of submarine, encapsulating the power system into its own thing (with damage/healing) and navigation, communications, inventory and puzzles into their own things.
- [x] Sort commands by functionality.
- [ ] Complete README.
- [ ] Type annotations if possible, to make debugging significantly easier. Not sure how to structure.

New features:
- [x] Control alerts, which inform control about events such as: puzzle fails, treasure pickup, sub damage.
- [x] Turn tracker should always be visible even when deactivated. (Maybe add an extra message.)
- [x] Add !scan to recall previous scan command.
- [x] !drop item. Cannot drop Key Items (ending in *), which is a check that needs to be included.
- [x] NPCs/Structures in their own state dictionary (likely just a list - it's fine if this is a little slow, as it's called every few minutes). These NPCs have health, a treasure drop, and an optional `on_tick` ability which fires every turn.
- [x] NPCs/Structures can receive messages. (Effectively bringing them to submarine power levels, but without `power`, `puzzles`, message sending, only limited movement, `weapons`, `inventory` or `scanning`.)
- [ ] Squares should be able to hold multiple treasures, with cranes "lucky dipping" to pick n treasures (n power).
- [ ] Weapons messages should tell you if you did a murder.
- [ ] !explode, which explodes (x,y) with a range and amount of damage.
- [ ] See the list of keywords pinned in #spoilers and implement them. See if this can be done with class heirarchy stuff, but I am very slightly lost in that regard. (It will likely have to be on a keyword by keyword basis, tres sad.)
- [ ] Docking stations assign a role `at-base-{name}` which does as it says. (see notes in #bot-impl.)
- [ ] NPCs can trade.

Quality of life things:
- [x] If the loop hasn't started, only control commands work. Do this by modifying our `perform` and `perform_async` functions to check loop state. I might be able to unify `perform` and `perform_async` into just `perform` if we can await a non-async function - but I genuinely don't know if this works.
- [x] Default to lowercase for all inputs.
- [ ] Emoji map.
- [ ] !save (determine if this is a safe command to add)
- [ ] !disable/!enable, which disables commands for teams. (as a control-available safety valve).

Fixes:
- [x] Trading should cease at movement rather than tick.
- [x] Remove "focus sash" idea.
- [x] Fix issues when bot is deleted (causes A Lot).
- [x] !mapall should also show treasure
- [x] Sub "is online" should have tick emoji in !status
- [x] Communicate power ERRORS better (e.g. "x has too much power")
- [x] Tell _everyone_ when it's activated/deactivated.
- [x] !zoom, which shouts about the attributes/treasure of a given square (CONTROL)
- [x] Standardise commands to _team_ _strings_ _coordinates_.
- [x] Crane with more power can go up/down faster.