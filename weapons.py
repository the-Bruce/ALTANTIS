"""
Allows subs to charge and fire (stunning) weapons.
"""

from state import get_subs, get_sub
from npc import get_npcs, get_npc
from utils import diagonal_distance, list_to_and_separated
from world import in_world

import math
from random import shuffle

class Weaponry():
    def __init__(self, sub):
        self.sub = sub
        self.weapons_charge = 1
        self.range = 4
        # A list of shots of (damaging, x, y).
        self.planned_shots = []
    
    def prepare_shot(self, damaging, x, y):
        if not in_world(x, y):
            return "Coordinate outside of world."
        if diagonal_distance(self.sub.movement.get_position(), (x,y)) > self.range:
            return "Coordinate outside of range."
        if damaging and self.weapons_charge >= 2:
            self.planned_shots.append((True, x, y))
            self.weapons_charge -= 2
            return f"Damaging shot fired at ({x}, {y})!"
        if (not damaging) and self.weapons_charge >= 1:
            self.planned_shots.append((False, x, y))
            self.weapons_charge -= 1
            return f"Non-damaging shot fired at ({x}, {y})!"
        return "Not enough charge to use that."
    
    def weaponry_tick(self):
        # Do the hits for the current turn:
        results = ""
        for shot in self.planned_shots:
            (damaging, x, y) = shot
            hits = {}
            if damaging:
                hits = self.damaging(x, y)
            else:
                hits = self.nondamaging(x, y)
            direct_hits = list_to_and_separated(list(map(lambda entity: entity.name(), hits["direct"])))
            if direct_hits == "":
                direct_hits = "nobody"
            indirect_hits = list_to_and_separated(list(map(lambda entity: entity.name(), hits["indirect"])))
            if indirect_hits == "":
                indirect_hits = "nobody"
            damaging_str = "damaging" if damaging else "non-damaging"
            results += f"Shot {damaging_str} shot at ({x}, {y}) - directly hit {direct_hits}; indirectly hit {indirect_hits}.\n"
        self.planned_shots = []

        # Then recharge.
        weapons_power = self.sub.power.get_power("weapons")
        recharge = math.ceil(weapons_power / 2)
        old_charge = self.weapons_charge
        self.weapons_charge = min(weapons_power, old_charge + recharge)
        if old_charge != self.weapons_charge:
            return f"{results}Recharged weapons up to {self.weapons_charge} charge!"
        return results
    
    def hits(self, x, y):
        # Returns a list of indirect and direct hits.
        indirect = []
        direct = []
        for subname in get_subs():
            sub = get_sub(subname)
            pos = sub.movement.get_position()
            distance = diagonal_distance(pos, (x, y))
            if distance == 0:
                direct.append(sub)
            elif distance == 1:
                indirect.append(sub)
        
        for npcid in get_npcs():
            npc = get_npc(npcid)
            pos = npc.get_position()
            distance = diagonal_distance(pos, (x, y))
            if distance == 0:
                direct.append(npc)
            elif distance == 1:
                indirect.append(npc)

        shuffle(indirect)
        shuffle(direct)
        return {"indirect": indirect, "direct": direct}
    
    def nondamaging(self, x, y):
        results = self.hits(x, y)
        for target in results["direct"]:
            if target.is_weak():
                target.damage(1)
        for target in results["indirect"]:
            if target.is_weak():
                target.damage(1)
        return results

    def damaging(self, x, y):
        results = self.hits(x, y)
        for target in results["indirect"]:
            target.damage(2)
        for target in results["direct"]:
            target.damage(1)
        return results
    
    def status(self):
        weapons_power = self.sub.power.get_power("weapons")
        if weapons_power == 0:
            return ""
        return f"\nWeapons are powered with {self.weapons_charge} weapons charge(s) available (maximum {weapons_power}).\n"