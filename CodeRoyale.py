import sys
import math
import copy
import time
import numpy as np
from heapq import heappush, heappop
from typing import List, Dict, Tuple, Optional
from operator import add

KNIGHT_SPEED = 100
KNIGHT_RADIUS = 20
QUEEN_RADIUS = 30

start = None


def is_point_inside_circle(point: List[int], circle_center: List[int], circle_radius: int) -> bool:
    # (x - center_x)^2 + (y - center_y)^2 < radius^2
    return (point[0] - circle_center[0]) ** 2 + (point[1] - circle_center[1]) ** 2 < circle_radius ** 2


def is_circle_intersecting_circle(p1: List[int], r1: int, p2: List[int], r2: int) -> bool:
    # (R0 - R1)^2 <= (x0 - x1)^2 + (y0 - y1)^2 <= (R0 + R1)^2
    return (r1 - r2) ** 2 <= (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2 <= (r1 + r2) ** 2


def is_circle_intersecting_circle2(p1: List[int], r1: int, p2: List[int], r2: int) -> bool:
    d = distance(p1, p2)
    return d - r1 - r2 <= 0

def is_point_outside(point: List[int]):
    if point[0] < 30 or point[0] > 1890:
        return True

    if point[1] < 30 or point[1] > 980:
        return True

    return False


def distance(p1: List[int], p2: List[int]):
    return math.sqrt(abs(p1[0] - p2[0]) ** 2 + abs(p1[1] - p2[1]) ** 2)


def debug(msg):
    print(msg, file=sys.stderr)


structure_names = {(0, 0, 0, 0): "NO_STRUCTURE", (1, 0, 0, 0): "MINE", (0, 1, 0, 0): "TOWER",
                   (0, 0, 1, 0): "BARRACKS-KNIGHT", (0, 0, 0, 1): "BARRACKS-ARCHER"}
structure_codes = {"NO_STRUCTURE": (0, 0, 0, 0), "MINE": (1, 0, 0, 0), "TOWER": (0, 1, 0, 0),
                   "BARRACKS-KNIGHT": (0, 0, 1, 0), "BARRACKS-ARCHER": (0, 0, 0, 1)}
unit_code = {"KNIGHT": 0, "ARCHER": 1, "GIANT": 2}

structure_to_code = {"MINE": (0, 1, -1), "TOWER": (1, 200, -1), "BARRACKS-KNIGHT": (2,0,0), "BARRACKS-ARCHER": (2,0,1), "BARRACKS-GIANT": (2,0,2)}
unit_stats = {
    0: {"cost": 80, "number": 4, "speed": 100, "damage": 1, "range": 0, "health": 30, "training_time": 5, "radius": 20},
    1: {"cost": 100, "number": 2, "speed": 75, "damage": 2, "range": 200, "health": 45, "training_time": 8,
        "radius": 25},
    2: {"cost": 140, "number": 1, "speed": 50, "damage": 80, "range": 0, "health": 200, "training_time": 10,
        "radius": 40},
    -1: {"cost": None, "number": None, "speed": 60, "damage": None, "range": None, "health": 200, "training_time": None,
         "radius": 30}}
unit_cost = {0: 80, 1: 100, 2: 140}


class BuildCommand:
    def __init__(self, structure_name: str, sitemap_pos: List[int]):
        site = Sites.sitemap[sitemap_pos[0]][sitemap_pos[1]]
        self.structure_name = structure_name
        self.structure_code = structure_codes[structure_name]
        self.pos = site.pos
        self.site_id = site.site_id
        self.sitemap_pos = site.sitemap_pos


class BuildManager:
    def __init__(self, build_order: List[BuildCommand]):
        self.build_order: List[BuildCommand] = None
        self.build_conditions: List[List[int]] = [[0, 0, 0, 0]]
        self.read_build_order(build_order)
        self.build_conditions_index = 0

    def read_build_order(self, build_order: List[BuildCommand]):
        self.build_order: List[BuildCommand] = build_order
        for i, build_command in enumerate(build_order):
            building_condition = list(map(add, self.build_conditions[i], build_command.structure_code))
            self.build_conditions.append(building_condition)

    def next_build(self, current_buildings: List[int]) -> BuildCommand:

        for i in range(len(self.build_conditions) - 1):
            if self.build_conditions[i] == current_buildings:
                self.build_conditions_index += 1
                return self.build_order[i]

        return BuildCommand("NO_STRUCTURE", [-1, -1])


'''
-1: No structure
0: Goldmine
1: Tower
2: Barracks
'''

''' SITEMAP       
      0 1 2 3 4 5 ->
    0 s s s s s s
    1 s s s s s s
    2 s s s s s s
    3 s s s s s s
    Se supone que se empieza arriba a la izquierda, si empezara abajo a la derecha se invierte solo
'''


class Sites:
    unownedSites: 'List[Site]' = []

    alliedSites: 'List[Site]' = []
    alliedMines: 'List[Site]' = []
    alliedUpgradeableMines: 'List[Site]' = []
    alliedAlmostDepletedMines: 'List[Site]' = []
    alliedBarracks: 'List[Site]' = []
    alliedBarracksKnights: 'List[Site]' = []
    alliedBarracksArcher: 'List[Site]' = []
    alliedBarracksGiant: 'List[Site]' = []
    alliedBarracksWaiting: 'List[Site]' = []
    alliedBarracksWaitingKnights: 'List[Site]' = []
    alliedBarracksWaitingArcher: 'List[Site]' = []
    alliedBarracksWaitingGiant: 'List[Site]' = []
    alliedBarracksTraining: 'List[Site]' = []
    alliedBarracksTrainingKnights: 'List[Site]' = []
    alliedBarracksTrainingArcher: 'List[Site]' = []
    alliedBarracksTrainingGiant: 'List[Site]' = []
    alliedTowers: 'List[Site]' = []
    alliedUpgradeableTowers: 'List[Site]' = []

    enemySites: 'List[Site]' = []
    enemyMines: 'List[Site]' = []
    enemyAlmostDepletedMines: 'List[Site]' = []
    enemyBarracks: 'List[Site]' = []
    enemyBarracksKnights: 'List[Site]' = []
    enemyBarracksArcher: 'List[Site]' = []
    enemyBarracksGiant: 'List[Site]' = []
    enemyBarracksWaiting: 'List[Site]' = []
    enemyBarracksWaitingKnights: 'List[Site]' = []
    enemyBarracksWaitingArcher: 'List[Site]' = []
    enemyBarracksWaitingGiant: 'List[Site]' = []
    enemyBarracksTraining: 'List[Site]' = []
    enemyBarracksTrainingKnights: 'List[Site]' = []
    enemyBarracksTrainingArcher: 'List[Site]' = []
    enemyBarracksTrainingGiant: 'List[Site]' = []
    enemyTowers: 'List[Site]' = []

    minableSites: 'List[Site]' = []
    barrackableSites: 'List[Site]' = []

    sites: 'Dict[int, Site]' = {}
    sitemap: 'List[List[Site]]' = []

    sites_pos: np.ndarray = None
    sites_r: np.ndarray = None
    my_towers_pos: np.ndarray = None

    map_points: List[List[int]] = [[]*19]*9

    @classmethod
    def set_sites(cls, sites: 'Dict[int, Site]'):
        cls.sites = sites

    @classmethod
    def clear(cls):
        cls.unownedSites: 'List[Site]' = []

        cls.alliedSites: 'List[Site]' = []
        cls.alliedMines: 'List[Site]' = []
        cls.alliedUpgradeableMines: 'List[Site]' = []
        cls.alliedAlmostDepletedMines: 'List[Site]' = []
        cls.alliedBarracks: 'List[Site]' = []
        cls.alliedBarracksKnights: 'List[Site]' = []
        cls.alliedBarracksArcher: 'List[Site]' = []
        cls.alliedBarracksGiant: 'List[Site]' = []
        cls.alliedBarracksWaiting: 'List[Site]' = []
        cls.alliedBarracksWaitingKnights: 'List[Site]' = []
        cls.alliedBarracksWaitingArcher: 'List[Site]' = []
        cls.alliedBarracksWaitingGiant: 'List[Site]' = []
        cls.alliedBarracksTraining: 'List[Site]' = []
        cls.alliedBarracksTrainingKnights: 'List[Site]' = []
        cls.alliedBarracksTrainingArcher: 'List[Site]' = []
        cls.alliedBarracksTrainingGiant: 'List[Site]' = []
        cls.alliedTowers: 'List[Site]' = []
        cls.alliedUpgradeableTowers: 'List[Site]' = []

        cls.enemySites: 'List[Site]' = []
        cls.enemyMines: 'List[Site]' = []
        cls.enemyAlmostDepletedMines: 'List[Site]' = []
        cls.enemyBarracks: 'List[Site]' = []
        cls.enemyBarracksKnights: 'List[Site]' = []
        cls.enemyBarracksArcher: 'List[Site]' = []
        cls.enemyBarracksGiant: 'List[Site]' = []
        cls.enemyBarracksWaiting: 'List[Site]' = []
        cls.enemyBarracksWaitingKnights: 'List[Site]' = []
        cls.enemyBarracksWaitingArcher: 'List[Site]' = []
        cls.enemyBarracksWaitingGiant: 'List[Site]' = []
        cls.enemyBarracksTraining: 'List[Site]' = []
        cls.enemyBarracksTrainingKnights: 'List[Site]' = []
        cls.enemyBarracksTrainingArcher: 'List[Site]' = []
        cls.enemyBarracksTrainingGiant: 'List[Site]' = []
        cls.enemyTowers: 'List[Site]' = []

        cls.minableSites: 'List[Site]' = []
        cls.barrackableSites: 'List[Site]' = []

        cls.sites_pos: np.ndarray = np.array([])
        cls.sites_r: np.ndarray = np.array([])

        cls.my_towers_pos: np.ndarray = np.array([])

    @classmethod
    def add_site(cls, site: 'Site'):

        if cls.sites_pos.size <= 0:
            cls.sites_pos = np.hstack((cls.sites_pos, np.array(site.pos)))
            cls.sites_r = np.hstack((cls.sites_r, np.array(site.radius)))
        else:
            cls.sites_pos = np.vstack((cls.sites_pos, np.array(site.pos)))
            cls.sites_r = np.vstack((cls.sites_r, np.array(site.radius)))


        if site.owner == 0:
            cls.alliedSites.append(site)
        elif site.owner == 1:
            cls.enemySites.append(site)

        if site.structure_type == -1:  # No structure
            cls.unownedSites.append(site)
        elif site.structure_type == 0:  # Mine
            if site.owner == 0:
                cls.alliedMines.append(site)
                Strategy.income += site.income()
                if site.max_mine_size - site.param1 > 0:
                    cls.alliedUpgradeableMines.append(site)
            else:
                cls.enemyMines.append(site)
        elif site.structure_type == 1:  # Tower
            if site.owner == 0:
                if cls.sites_pos.size <= 0:
                    cls.sites_pos = np.hstack((cls.sites_pos, np.array(site.pos)))
                else:
                    cls.sites_pos = np.vstack((cls.sites_pos, np.array(site.pos)))
                cls.alliedTowers.append(site)
                if site.hp() < 700:
                    cls.alliedUpgradeableTowers.append(site)
            else:
                cls.enemyTowers.append(site)
        else:  # site.structure_type == 2: #Barracks
            if site.owner == 0:  # Allied
                cls.alliedBarracks.append(site)
                if site.param1 > 0:  # Training
                    cls.alliedBarracksTraining.append(site)
                    if site.param2 == 0:  # Knight
                        cls.alliedBarracksTrainingKnights.append(site)
                        cls.alliedBarracksKnights.append(site)
                    elif site.param2 == 1:  # Archer
                        cls.alliedBarracksTrainingArcher.append(site)
                        cls.alliedBarracksArcher.append(site)
                    else:  # Giant
                        cls.alliedBarracksTrainingGiant.append(site)
                        cls.alliedBarracksGiant.append(site)
                else:  # Waiting
                    cls.alliedBarracksWaiting.append(site)
                    if site.param2 == 0:  # Knight
                        cls.alliedBarracksWaitingKnights.append(site)
                        cls.alliedBarracksKnights.append(site)
                    elif site.param2 == 1:  # Archer
                        cls.alliedBarracksWaitingArcher.append(site)
                        cls.alliedBarracksArcher.append(site)
                    else:  # Giant
                        cls.alliedBarracksWaitingGiant.append(site)
                        cls.alliedBarracksGiant.append(site)
            else:  # Enemy
                cls.enemyBarracks.append(site)
                if site.param1 > 0:  # Training
                    cls.enemyBarracksTraining.append(site)
                    if site.param2 == 0:  # Knights
                        cls.enemyBarracksTrainingKnights.append(site)
                        cls.enemyBarracksKnights.append(site)
                    elif site.param2 == 1:  # Archer
                        cls.enemyBarracksTrainingArcher.append(site)
                        cls.enemyBarracksArcher.append(site)
                    else:  # Giant
                        cls.enemyBarracksTrainingGiant.append(site)
                        cls.enemyBarracksGiant.append(site)
                else:  # Waiting
                    cls.enemyBarracksWaiting.append(site)
                    if site.param2 == 0:  # Knight
                        cls.enemyBarracksWaitingKnights.append(site)
                        cls.enemyBarracksKnights.append(site)
                    elif site.param2 == 1:  # Archer
                        cls.enemyBarracksWaitingArcher.append(site)
                        cls.enemyBarracksArcher.append(site)
                    else:  # Giant
                        cls.enemyBarracksWaitingGiant.append(site)
                        cls.enemyBarracksGiant.append(site)

        # Sites donde se puede construir una mina
        if (site.gold >= 200 and site.is_unowned or (
                (site.is_unowned())
                or (site.is_tower() and site.is_allied())
                or (site.is_barrack() and site.is_allied())
                or (site.is_barrack() and not site.is_allied())
                or (site.is_mine() and not site.is_allied()))
                ):
            cls.minableSites.append(site)

        # Sites donde se puede construir un barracks
        if ((site.is_allied() and site.is_mine() and site.gold < 10)  # Mina aliada vacia
                or (site.is_allied() and site.is_tower() and Strategy.time > 100)  # Torre en mid game
                or (site.is_enemy() and site.is_barrack())
                or (site.is_enemy() and site.is_mine())
                or site.is_unowned()):
            cls.barrackableSites.append(site)


    @staticmethod
    def front_buildings_with_sitemap_pos()-> List:

        front_sites: 'List[Site]' = []

        if Strategy.starting_cuadrant == [0,0]:
            starting = 'left'
            farthest_x = 0
        else:
            starting = 'right'
            farthest_x = 1920

        for row in range(len(Sites.sitemap)):
            front_site = None
            sitemap_pos = []
            for col in range(len(Sites.sitemap[row])):
                site = Sites.sitemap[row][col]

                if site.is_allied() and site.pos[0] > farthest_x and starting == 'left':
                    front_site = site
                    sitemap_pos = [row, col]
                elif site.is_allied() and site.pos[0] < farthest_x and starting == 'right':
                    front_site = site
                    sitemap_pos = [row, col]
            front_sites.append((front_site, sitemap_pos))

        return front_sites

    @staticmethod
    def closest(sites: 'List[Site]', pos: 'List[int]') -> 'Optional[Site]':
        if len(sites) > 0:
            return min(sites, key=lambda s: distance(pos, s.pos))
        else:
            return None

    @staticmethod
    def farthest(sites: 'List[Site]', pos: 'List[int]') -> 'Optional[Site]':
        if len(sites) > 0:
            return max(sites, key=lambda s: distance(pos, s.pos))
        else:
            return None

    @staticmethod
    def lowest_hp_tower(towers: 'List[Site]') -> 'Optional[Site]':
        if len(towers) > 0:
            return min(towers, key=lambda t: t.param1)
        else:
            return None

    @staticmethod
    def towers_in_range(towers: 'List[Site]', point: 'List[int]', radius: int = 0) -> 'List[Site]':
        return [tower for tower in towers if is_circle_intersecting_circle2(point, radius, tower.pos, tower.attack_radius) and len(tower.opponent_knights_in_range()) <= 1]


    @staticmethod
    def is_building_at_point(point: 'List[int]') -> bool:
        for site in Sites.sites.values():
            if is_point_inside_circle(point,site.pos, site.radius):
                return True
        return False

    @staticmethod
    def is_point_in_obstacle(point: 'List[int]', radius: int = 0) -> bool:
        is_tower_in_range = True if len(Sites.towers_in_range(Sites.enemyTowers, point, radius)) > 0 else False
        is_building_in_point = Sites.is_building_at_point(point)

        return any([is_tower_in_range, is_building_in_point])

    @staticmethod
    def ordered_by_closest(sites: 'List[Site]', pos: 'List[int]') -> 'List[Site]':
        return sorted(sites, key=lambda s: distance(pos, s.pos))

    @staticmethod
    def site_touched() -> 'Optional[Site, int]':
        if Units.touchedSite != -1:
            return Sites.sites[Units.touchedSite]
        return None

    @staticmethod
    def damage_to_point(tower: 'Site', point: List[int], is_queen: bool) -> int:
        if tower.is_tower() and is_point_inside_circle(point, tower.pos, tower.attack_radius):
            base_damage = 1 if is_queen else 3
            extra_damage = int((tower.attack_radius - distance(point, tower.pos)) / 200)
            return base_damage + extra_damage
        else:
            return 0

    @staticmethod
    def towerable_sites() -> 'List[Site]':
        return [site for site in Sites.sites.values() if (
            len(Sites.towers_in_range(Sites.enemyTowers, site.pos, site.radius)) < 1 and (
                site.is_unowned()
            or (site.is_allied() and site.is_mine() and site.gold < 10) #Mina aliada vacia
            or (site.is_allied() and site.is_barrack() and not site.is_training() and len(Sites.alliedBarracks) > 2) #Barracks aliado donde no se entrena
            or (site.is_enemy() and site.is_barrack())
            or (site.is_enemy() and site.is_mine()))
            )]

    @staticmethod
    def minable_sites() -> 'List[Site]':
        return [site for site in Sites.sites.values() if (
                (len(Sites.towers_in_range(Sites.enemyTowers, site.pos, site.radius)) < 1 and not (site.is_allied() and site.is_mine())) and(
                (site.gold >= 150 and site.is_unowned) or (
                   (site.is_tower() and site.is_allied() and len(Sites.alliedTowers) > 3 and Strategy.time > 100 and len(Sites.unownedSites) < 3)
                or (site.is_barrack() and site.is_allied() and not site.is_training() and len(Sites.alliedBarracks) > 2 and Strategy.time > 100 and len(Sites.unownedSites) < 3)
                or (site.is_barrack() and site.is_enemy())
                or (site.is_mine() and site.is_enemy())
        )))]

    @staticmethod
    def barrackable_sites() -> 'List[Site]':
        return [site for site in Sites.sites.values() if (
                len(Sites.towers_in_range(Sites.enemyTowers, site.pos, site.radius)) < 1 and (
                    (site.is_allied() and site.is_mine() and site.gold < 10)  # Mina aliada vacia
                or (site.is_allied() and site.is_tower() and Strategy.time > 100)  # Torre en mid game
                or (site.is_enemy() and site.is_barrack())
                or (site.is_enemy() and site.is_mine())
                or site.is_unowned()))]


    @staticmethod
    def sitemap_col(col: int) -> 'List[Site]':
        return [row[col] for row in Sites.sitemap]

    @staticmethod
    def safe(sites: 'List[Site]') -> 'Optional[List[Site]]':
        return [site for site in sites if len(Sites.towers_in_range(Sites.enemyTowers, site.pos)) == 0]


class Site:
    def __init__(self, site_id: int, x: int, y: int, radius: int):
        self.site_id: int = site_id
        self.pos = [x, y]
        self.radius: int = radius
        self.gold: int = None
        self.max_mine_size: int = None
        self.structure_type: int = None
        self.owner: int = None
        self.param1: int = None
        self.param2: int = None
        self.attack_radius: int = None
        self.sitemap_pos: List[int] = None

    def update(self, gold, max_mine_size, structure_type, owner, param1, param2):
        self.gold = gold
        self.max_mine_size = max_mine_size
        self.structure_type = structure_type
        self.owner = owner
        self.param1 = param1
        self.param2 = param2

        if self.is_tower():
            self.set_hp(param1)

    def can_be_built_into(self, new_structure_name: str, new_owner: int) -> bool:
        if self.owner != new_owner and self.is_tower():
            return False

        if self.owner == new_owner and self.is_training():
            return False

        if new_structure_name == "MINE":
            if self.gold < 10 or (self.is_mine() and self.owner == new_owner and self.income() >= self.max_mine_size):
                return False

        if new_structure_name == "TOWER":
            if self.hp() > 750:
                return False

        if new_structure_name == "BARRACKS-KNIGHT" and self.is_barrack_knight():
            return False
        if new_structure_name == "BARRACKS-ARCHER" and self.is_barrack_archer():
            return False
        if new_structure_name == "BARRACKS-GIANT" and self.is_barrack_giant():
            return False

        return True

    def built_into(self,new_structure_name: str, new_owner: int):
        structure_type, param1, param2 = structure_to_code[new_structure_name]

        if self.is_mine() and self.income() < self.max_mine_size:
            self.param1 += 1
            return

        self.structure_type = structure_type
        self.owner = new_owner

        if self.is_mine():
            self.param1 = param1
            self.param2 = param2
        elif self.is_tower():
            self.param1 = param1
            self.param2 = math.sqrt((self.param1 * 1000 + self.radius) / math.pi)
        else:
            self.param1 = param1
            self.param2 = param2


    def set_hp(self, hp: int):
        if self.is_tower():
            self.param1 = hp
            # sqrt((hp * 1000 + siteArea) / PI)
            self.attack_radius = math.sqrt((self.param1 * 1000 + self.radius) / math.pi)

    def is_mine(self):
        if self.structure_type == 0: return True
        else: return False

    def is_tower(self):
        if self.structure_type == 1: return True
        else: return False

    def is_barrack(self):
        if self.structure_type == 2: return True
        else: return False

    def is_barrack_knight(self):
        if self.is_barrack() and self.param2 == 0: return True
        else: return False

    def is_barrack_archer(self):
        if self.is_barrack() and self.param2 == 1: return True
        else: return False

    def is_barrack_giant(self):
        if self.is_barrack() and self.param2 == 2: return True
        else: return False

    def is_training(self):
        if self.is_barrack() and self.param1 > 0: return True
        else: return False

    def is_unowned(self):
        if self.owner == -1: return True
        else: return False

    def is_allied(self):
        if self.owner == 0: return True
        else: return False

    def is_enemy(self):
        if self.owner == 1: return True
        else: return False

    def structure_name(self):
        if self.is_unowned(): return "NO-STRUCTURE"
        elif self.is_mine(): return "MINE"
        elif self.is_tower(): return "TOWER"
        elif self.is_barrack_knight(): return "BARRACKS-KNIGHT"
        elif self.is_barrack_archer(): return "BARRACKS-ARCHER"
        else: return "BARRACKS-GIANT"

    def training_cost(self):
        if self.is_barrack_knight(): return 80
        elif self.is_barrack_archer(): return 100
        elif self.is_barrack_giant(): return 140
        else: return 10000

    def start_training(self):
        if not self.is_barrack():
            return 0

        if self.is_barrack_knight():
            self.param1 = unit_stats[0]["training_time"]
            self.param2 = 0
            return 80
        elif self.is_barrack_archer():
            self.param1 = unit_stats[1]["training_time"]
            self.param2 = 1
            return 100
        elif self.is_barrack_giant():
            self.param1 = unit_stats[2]["training_time"]
            self.param2 = 2
            return 140


    def hp(self):
        if self.is_tower(): return self.param1
        else: return -1

    def income(self):
        if self.is_mine(): return self.param1
        else: return -1

    def turns_waiting(self):
        if self.is_barrack(): return self.param1
        else: return -1

    def is_upgradeable(self, upgrade_to_hp: int = 720):
        if self.is_allied() and ((self.is_tower() and self.hp() <= upgrade_to_hp) or (self.is_mine() and self.max_mine_size > self.income())): return True
        else: return False

    def decaying_rate(self):
        if self.is_tower(): return 4
        else: return 0

    def destroy(self):
        self.structure_type = -1
        self.owner = -1
        self.param1 = -1
        self.param2 = -1

    def spawn_units(self) -> 'List[Unit]':
        new_units: 'List[Unit]' = []
        if self.is_barrack_knight():
            new_units.append(Unit.spawn_at(self.pos, self.owner, 0, 30))
            new_units.append(Unit.spawn_at(self.pos, self.owner, 0, 30))
            new_units.append(Unit.spawn_at(self.pos, self.owner, 0, 30))
            new_units.append(Unit.spawn_at(self.pos, self.owner, 0, 30))
        elif self.is_barrack_archer():
            new_units.append(Unit.spawn_at(self.pos, self.owner, 1, 45))
            new_units.append(Unit.spawn_at(self.pos, self.owner, 1, 45))
        elif self.is_barrack_giant():
            new_units.append(Unit.spawn_at(self.pos, self.owner, 2, 200))
        return new_units

    def opponent_knights_in_range(self):
        return [unit for unit in Units.alliedKnights if is_circle_intersecting_circle2(self.pos, self.attack_radius, unit.pos, unit.radius)]


class Units:
    units: 'List[Unit]' = []

    touchedSite: int = -1

    alliedQueen: 'Unit' = None
    alliedUnits: 'List[Unit]' = []
    alliedKnights: 'List[Unit]' = []
    alliedArchers: 'List[Unit]' = []
    alliedGiants: 'List[Unit]' = []

    enemyQueen: 'Unit' = None
    enemyUnits: 'List[Unit]' = []
    enemyKnights: 'List[Unit]' = []
    enemyArchers: 'List[Unit]' = []
    enemyGiants: 'List[Unit]' = []

    enemyKnihtsPos: 'np.ndarray' = np.array([], int)
    myQueenPos: 'np.ndarray' = np.array([], int)

    _stored_biggest_threat: 'Unit' = None

    @classmethod
    def clear(cls):
        cls.units = []

        cls.alliedQueen = None
        cls.alliedKnights = []
        cls.alliedArchers = []
        cls.alliedGiants = []
        cls.alliedUnits = []

        cls.enemyQueen = None
        cls.enemyUnits = []
        cls.enemyKnights = []
        cls.enemyArchers = []
        cls.enemyGiants = []

        cls.enemyKnihtsPos: 'np.ndarray' = np.array([], int)
        cls.myQueenPos: 'np.ndarray' = np.array([], int)

        cls._stored_biggest_threat: 'Unit' = None


    @classmethod
    def add_queen(cls, queen: 'Unit'):
        if queen.owner == 0:
            cls.alliedQueen = queen
        else:
            cls.enemyQueen = queen

    @classmethod
    def add_units(cls, units: 'List[Unit]'):
        for unit in units:
            cls.units.append(unit)
            if unit.unit_type == -1:
                continue
            if unit.owner == 0:  # Allied

                unit.distance_to_opposite_queen = distance(cls.enemyQueen.pos, unit.pos)
                cls.alliedUnits.append(unit)

                if unit.unit_type == 0:  # Knights
                    cls.alliedKnights.append(unit)
                elif unit.unit_type == 1:  # Archer
                    cls.alliedArchers.append(unit)
                else:  # Giant
                    cls.alliedGiants.append(unit)
            else:  # Enemy

                unit.distance_to_opposite_queen = distance(cls.alliedQueen.pos, unit.pos)
                cls.enemyUnits.append(unit)

                if unit.unit_type == 0:  # Knights
                    cls.enemyKnights.append(unit)
                    if cls.enemyKnihtsPos.size <= 0:
                        cls.enemyKnihtsPos = np.hstack((cls.enemyKnihtsPos, np.array(unit.pos)))
                        cls.myQueenPos = np.hstack((cls.myQueenPos, np.array(Units.alliedQueen.pos)))
                    else:
                        cls.enemyKnihtsPos = np.vstack((cls.enemyKnihtsPos, np.array(unit.pos)))
                        cls.myQueenPos = np.vstack((cls.myQueenPos, np.array(Units.alliedQueen.pos)))

                elif unit.unit_type == 1:  # Archer
                    cls.enemyArchers.append(unit)
                else:  # Giant
                    cls.enemyGiants.append(unit)

    @staticmethod
    def closer(units: 'List[Unit]', from_point: List[int], max_distance: int) -> 'List[Unit]':
        return [unit for unit in units if distance(unit.pos, from_point) <= max_distance]

    @staticmethod
    def enemy_units_closer_than(max_distance: int) -> 'List[Unit]':
        return [unit for unit in Units.enemyUnits if unit.distance_to_opposite_queen <= max_distance]

    @staticmethod
    def biggest_threat_to_queen() -> 'Optional[Unit]':
        close_knights = Units.closer(Units.enemyKnights, Units.alliedQueen.pos, 350)
        if close_knights:
            return close_knights[0]
        else:
            return None
        threats = [knight for knight in close_knights if knight.turns_until_death() > knight.turns_to_reach_opposite_queen()]
        if len(threats) > 0:
            Units._stored_biggest_threat = min(threats, key=lambda k: k.threat_level())
        else:
            Units._stored_biggest_threat = None
        return Units._stored_biggest_threat

    '''They deal 3 base damage at the edge of their firing range. The closer the creep is to the tower, the more damage 
            will be dealt (+1 for every 200 units closer) If there are no creeps in range, but the enemy Queen is in range, a 
            tower will fire upon her instead, dealing 1 base damage +1 for every 200 units of distance closer.'''


class Unit:
    def __init__(self, x, y, owner, unit_type, health):
        self.pos = [x, y]
        self.owner = owner
        self.unit_type = unit_type
        self.health = health
        self.distance_to_opposite_queen = None
        self.speed = unit_stats[unit_type]["speed"]
        self.damage = unit_stats[unit_type]["damage"]
        self.range = unit_stats[unit_type]["range"]
        self.radius = unit_stats[unit_type]["radius"]
        # damage que va a hacer a la reinasi se queda quieta, suma la de las unidades cercanas
        self.stored_path: List[List[int]] = None
        self.stored_turns_until_death: int = None

    @staticmethod
    def spawn_at(pos: List[int], owner, unit_type, health):
        return Unit(pos[0], pos[1], owner, unit_type, health)

    def is_queen(self):
        if self.unit_type == -1: return True
        else: return False

    def is_knight(self):
        if self.unit_type == 0: return True
        else: return False

    def is_archer(self):
        if self.unit_type == 1: return True
        else: return False

    def is_giant(self):
        if self.unit_type == 2: return True
        else: return False

    def is_allied(self):
        if self.owner == 0: return True
        else: return False

    def check_collision(self, pos):
        new_pos = pos
        for site in Sites.sites.values():
            overlap = self.radius + site.radius - distance(pos, site.pos)
            if overlap < 0.000001:
                continue
            else:
                p1 = pos
                p2 = site.pos

                theta = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
                new_pos = [p1[0] - (1 + overlap) * math.cos(theta), p1[1] - (1 + overlap) * math.sin(theta)]
                break

        return new_pos



    def path(self) -> List[List[int]]:

        if self.stored_path is not None:
            return self.stored_path

        path = []
        p1 = self.pos

        if self.is_knight():
            if self.is_allied():
                p2 = Units.enemyQueen.pos
            else:
                p2 = Units.alliedQueen.pos
        else: # unit.is_giant():
            if self.is_allied():
                p2 = Sites.closest(Sites.enemyTowers, p1).pos
            else:
                p2 = Sites.closest(Sites.alliedTowers, p1).pos

        theta = math.atan2(p2[1]-p1[1], p2[0]-p1[0])
        cos_theta = math.cos(theta)
        sin_theta = math.sin(theta)
        phi = self.speed
        # x = x0 + phi*t * cos(theta) -> t = (x-x0)/(phi*cos(theta))
        # y = y0 + phi*t * sen(theta)
        time_until_destination = int(math.ceil(abs( (p2[0] - p1[0])/(phi * cos_theta) )))

        new_x = p1[0]
        new_y = p1[1]
        for t in range(1, time_until_destination):
            new_x += phi * cos_theta
            new_y += phi * sin_theta
            new_x, new_y = self.check_collision([new_x,new_y])
            path.append([new_x, new_y])

        if len(path) > 0:
            path.extend([path[-1]] * 10)
        else:
            path.extend([p2] * 10)
        self.stored_path = path
        return path

    def turns_to_reach_opposite_queen(self) -> 'Optional[int]':
        if self.unit_type == 0:
            if self.owner == 1:
                opposite_queen_pos = Units.alliedQueen.pos
            else:
                opposite_queen_pos = Units.enemyQueen.pos
            turns = distance(opposite_queen_pos, self.pos) / self.speed
            return int(turns)
        else:
            return None

    def turns_until_death(self):
        if self.stored_turns_until_death is not None:
            return self.stored_turns_until_death
        path = self.path()
        opposite_towers = Sites.enemyTowers if self.is_allied() else Sites.alliedTowers
        units_pack = self.units_pack()

        remaining_health = sum([unit.health for unit in units_pack])
        turns = 0

        for i in range(len(path)):
            if remaining_health <= 0: break
            for tower in opposite_towers:
                remaining_health -= Sites.damage_to_point(tower, path[i], self.is_queen())
            remaining_health -= 1 * len(units_pack)
            turns += 1

        self.stored_turns_until_death = turns
        return turns

    def units_pack(self) -> 'List[Unit]':
        return [unit for unit in Units.closer(Units.alliedKnights if self.is_allied() else Units.enemyUnits,
                                              self.pos, 150
                                              )]

    def threat_level(self) -> int:
        return (self.turns_until_death() - self.turns_to_reach_opposite_queen()) * len(self.units_pack())

    def farthest_point_reached(self, destination_point: List[int], turns: int) -> 'List[int]':
        p1 = self.pos
        p2 = destination_point

        theta = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
        phi = self.speed

        return [int(p1[0] + phi * turns * math.cos(theta)), int(p1[1] + phi * turns * math.sin(theta))]

    def is_touching(self, other: 'Union(Unit, Site)'):
        #isTouching = distance - radius1 - radius2 < 5
        d = distance(self.pos, other.pos)
        return d - self.radius - other.radius < 5

class Simulator:
    state: 'State' = None

    def __init__(self):
        self.state = State.initial_state()

    def simulations(self, commands: List[str]):
        for command in commands:
            self.state = Simulator.next_turn(self.state, command)

    @staticmethod
    def next_turn(current_state: 'State', command: str) -> 'State':
        new_state = current_state
        new_state.command_given = command
        new_state = Simulator.process_command(new_state)
        new_state = Simulator.creeps_move(new_state)
        new_state = Simulator.creeps_attack(new_state)
        # new_state = Simulator.queens_destroy_enemy_mines_and_barracks(new_state)
        # new_state = Simulator.remaining_structures_act(new_state)
        #new_state = Simulator.creeps_age(new_state)
        new_state = Simulator.check_end_game(new_state)
        return new_state

    @staticmethod
    def receive_state(state: 'State') -> 'State':
        # modifica state.command_given
        return state

    @staticmethod
    def process_command(state: 'State') -> 'State':
        def new_trainees_started(sites: List['Site']):
            gold_spent = 0
            for site in sites:
                gold_spent += state.sites[site.site_id].start_training()
            state.my_gold -= gold_spent

        def queens_move(destination_point: List[int]):
            state.my_queen.pos = state.my_queen.farthest_point_reached(destination_point, 1)

        def new_structures_build(site: 'Site', building_name: 'str'):

            is_site_touched = state.my_queen.is_touching(site)
            if is_site_touched and state.sites[site.site_id].can_be_built_into(building_name, state.my_queen.owner):
                state.sites[site.site_id].built_into(building_name, state.my_queen.owner)
            else:
                queens_move(site.pos)

        def wait():
            pass

        command = state.command_given.split(" ")
        if command[0] == "MOVE":
            destination_point = [int(command[1]), int(command[2])]
            queens_move(destination_point)
        elif command[0] == "BUILD":
            site = state.sites[int(command[1])]
            building_type = command[2]
            new_structures_build(site, building_type)
        elif command[0] == "TRAIN":
            training_sites = [state.sites[int(site_id)] for site_id in command[1:]]
            if sum([site.training_cost() for site in training_sites]) <= state.my_gold:
                new_trainees_started(training_sites)
            else:
                wait()
        else:
            wait()

        return state

    @staticmethod
    def creeps_move(state: 'State') -> 'State':

        if state.en_knights_pos.size > 0:
            my_queen_pos = np.array([state.my_queen.pos], int)
            my_queen_pos = np.repeat(my_queen_pos, state.en_knights_pos.shape[0], axis=0)
            P1P2 = my_queen_pos - state.en_knights_pos
            Theta = np.arctan2(P1P2[:, 1], P1P2[:, 0])
            T = np.column_stack([np.cos(Theta), np.sin(Theta)])
            state.en_knights_pos = state.en_knights_pos + KNIGHT_SPEED * T

        # collisions
        sites_pos = Sites.sites_pos
        sites_radius = Sites.sites_r
        for i in range(0, min(state.en_knights_pos.shape[0], 2)):
            # espero no tener que modificar este codigo
            knight_pos = np.array([state.en_knights_pos[i]] * Sites.sites_pos.shape[0], int)
            knight_radius = np.array([KNIGHT_RADIUS] * Sites.sites_pos.shape[0], int)
            d = np.array(np.sqrt((knight_pos[:, 0] - sites_pos[:, 0]) ** 2 + (knight_pos[:, 1] - sites_pos[:, 1]) ** 2),
                         int)
            all_overlap = knight_radius + sites_radius - d
            all_overlap = np.array(all_overlap * (all_overlap > 0.0001), int)
            single_overlap = np.sum(all_overlap)
            if single_overlap > 0:
                site_id = np.where(all_overlap > 0)[0][0]
                P1P2 = sites_pos[site_id] - knight_pos[0]
                theta = np.arctan2(P1P2[1], P1P2[0])
                state.en_knights_pos[i] = np.array([knight_pos[0][0] - (1 + single_overlap) * np.cos(theta),
                                                    knight_pos[0][1] - (1 + single_overlap) * np.sin(theta)])

        return state

    @staticmethod
    def creeps_attack(state: 'State') -> 'State':

        knights_pos = state.en_knights_pos
        if knights_pos.size > 0:
            my_queen_pos = np.array([state.my_queen.pos] * knights_pos.shape[0], int)
            d = np.sqrt((knights_pos[:, 0] - my_queen_pos[:, 0]) ** 2 + (knights_pos[:, 1] - my_queen_pos[:, 1]) ** 2)
            units_close = (d - KNIGHT_RADIUS - QUEEN_RADIUS) < 5
            state.my_queen.health -= sum(units_close)


        return state

    @staticmethod
    def queens_destroy_enemy_mines_and_barracks(state: 'State') -> 'State':
        for i in range(len(state.sites.values())):
            site = state.sites[i]
            if (site.is_mine() or site.is_barrack()):
                if site.owner == 0 and state.en_queen.is_touching(site):
                    state.sites[i].destroy()
                elif site.owner == 1 and state.my_queen.is_touching(site):
                    state.sites[i].destroy()
        return state

    @staticmethod
    def remaining_structures_act(state: 'State') -> 'State':
        def towers_shoot(tower: 'Site'):
            units_in_range = []
            for i in range(len(state.units)):
                unit = state.units[i]
                if unit.owner == tower.owner: continue
                d = distance(unit.pos, tower.pos)
                if d - unit.radius - tower.radius < 0:
                    units_in_range.append((d, i))
            if units_in_range:
                index = min(units_in_range)[1]
                state.units[index].health -= Sites.damage_to_point(tower, state.units[index].pos,
                                                                   state.units[index].is_queen())

        def barracks_advance_progress_and_spawn_new_creeps(barrack: 'Site'):
            if barrack.is_training():
                barrack.param1 -= 1
                if barrack.param1 == 0:
                    new_units = barrack.spawn_units()
                    state.units.extend(new_units)

        def mines_collect_gold(mine: 'Site'):
            if mine.is_allied():
                state.my_gold += mine.income()
                state.sites[mine.site_id].gold -= mine.income()
                if state.sites[mine.site_id].gold <= 0:
                    state.sites[mine.site_id].destroy()

        for site in state.sites.values():
            if site.is_tower:
                towers_shoot(site)
            elif site.is_barrack:
                barracks_advance_progress_and_spawn_new_creeps(site)
            elif site.is_mine:
                mines_collect_gold(site)

        return state

    @staticmethod
    def creeps_age(state: 'State') -> 'State':
        removed_creeps: List[int] = []
        for i in range(len(state.units)):
            state.units[i].health -= 1
            if state.units[i].health <= 0:
                removed_creeps.insert(0, i)

        for i in removed_creeps:
            del (state.units[i])
        return state

    @staticmethod
    def check_end_game(state: 'State') -> 'State':
        return state


class State:
    en_knights_pos: np.ndarray = None
    my_towers_pos: np.ndarray = None
    sites_pos: np.ndarray = None
    units: List['Unit'] = []
    sites: Dict[int,'Site'] = {}
    my_queen: 'Unit' = None
    my_gold: int = None
    en_queen: 'Unit' = None
    command_given: str = None

    @staticmethod
    def initial_state():
        s = State()
        s.units = Units.units
        s.sites = Sites.sites
        s.my_queen = Unit(Units.alliedQueen.pos[0], Units.alliedQueen.pos[1], Units.alliedQueen.owner, Units.alliedQueen.unit_type, Units.alliedQueen.health)
        s.en_knights_pos = np.copy(Units.enemyKnihtsPos)
        s.my_gold = Strategy.myGold
        s.en_queen = Units.enemyQueen
        return s

    @staticmethod
    def load_state(state: 'State'):
        s = State()
        s.units = state.units
        s.sites = state.sites
        s.my_queen = state.my_queen
        s.my_gold = state.my_gold
        s.en_queen = state.en_queen
        return s

'''
class Prediction:

    units: List[List['Unit']] = []
    sites: List[Dict[int, 'Site']] = {]
    my_queen: 'Unit' = None

    @classmethod
    def next_turn(cls, player_input):
        #Wait
        pass


    @classmethod
    def start_new_trainees(cls, player_input):
        pass'''



'''
action_string:  "BUILD" - str building_type - "CLOSEST", "SECURE", 
                                              "SITEMAP_POS", "CLOSE_TO" - [int,int] coords
                                              "SITE_ID"                 - str|int siteid
                "AVOID" - Unit
                "MOVE" - [int, int] coords

                "TRAIN" - int quantity - "KNIHGT", "ARCHER", "GIANT"
                "WAIT"
'''


class Action:
    def __init__(self, action: List):
        self.command: str = ""

        if action[0] == "BUILD":
            self.command = self.parse_build_action(action)
            self.command += " \nTRAIN"

        elif action[0] == "AVOID":
            self.command = self.parse_avoid_action(action)
            self.command += " \nTRAIN"

        elif action[0] == "WAIT":
            self.command = "WAIT"
            self.command += " \nTRAIN"

        elif action[0] == "MOVE":
            self.command = Action.move(action[1])
            self.command += " \nTRAIN"

        elif action[0] == "TRAIN":
            self.command = self.parse_train_action(action)



    def parse_train_action(self, action):

        quantity = action[1]

        if action[2] == "KNIGHT":
            training_sites = Sites.alliedBarracksWaitingKnights
        elif action[2] == "ARCHER":
            training_sites = Sites.alliedBarracksWaitingArcher
        else:
            training_sites = Sites.alliedBarracksWaitingGiant

        training_sites = Sites.ordered_by_closest(training_sites, Units.enemyQueen.pos)

        if len(training_sites) >= quantity:
            return Action.train(training_sites[:quantity])
        else:
            return ""



    def parse_avoid_action(self, action):
        unit_to_avoid: 'Unit' = action[1]
        p1 = Units.alliedQueen.pos
        p2 = unit_to_avoid.pos

        dy = 1 if p2[1] - p1[1] == 0 else p2[1] - p1[1]
        dx = 1 if p2[0] - p1[0] == 0 else p2[0] - p1[0]

        m = dy / dx
        if p1[0] < p2[0]:
            xr = p1[0] - 60
        else:
            xr = p1[0] + 60
        y = m * (xr - p1[0]) + p1[1]
        return "MOVE " + str(int(xr)) + " " + str(int(y))

    def parse_build_action(self, action):
        structure_name = action[1]
        location_type = action[2]
        site_id = ""

        if location_type == "CLOSEST":

            if structure_name == "MINE":
                site_id = Sites.closest(Sites.minable_sites(), Units.alliedQueen.pos).site_id
            elif structure_name == "BARRACKS-KNIGHT":
                site_id = Sites.closest(Sites.barrackable_sites(), Units.alliedQueen.pos).site_id
            else:
                site_id = Sites.closest(Sites.unownedSites, Units.alliedQueen.pos).site_id


        elif location_type == "SECURE":
            pass
        elif location_type == "SITEMAP_POS":
            row = action[3][0]
            col = action[3][1]
            initial_site = Sites.sitemap[row][col]
            site = Sites.closest(Sites.unownedSites, initial_site.pos)
            site_id = site.site_id
            Strategy.current_build_order[0].site_id = site_id
            Strategy.current_build_order[0].pos = site.pos

        elif location_type == "SITE_ID":
            site_id = action[3]

        elif location_type == "CLOSE_TO":
            if structure_name == "MINE":
                site_id = Sites.closest(Sites.minable_sites(), action[3]).site_id
            else:
                site_id = Sites.closest(Sites.unownedSites, action[3]).site_id

        elif location_type == "SITE_LIST":
            sites = action[3]
            site_id = Sites.closest(sites, Units.alliedQueen.pos).site_id

        return self.build(site_id, structure_name)

    '''
    building = Sites.sitemap[next_building.sitemap_pos[0]][next_building.sitemap_pos[1]]
        self.build(Sites.closest(Sites.unownedSites, building.pos).site_id, next_building.structure_name)
    '''

    @staticmethod
    def move(pos: List[int]):
        return "MOVE {} {}".format(pos[0], pos[1])

    @staticmethod
    def build(site_id: int, structure: str):
        return "BUILD " + str(site_id) + " " + structure

    @staticmethod
    def train(list_of_sites: List[Site]):
        train_command = ""
        for site in list_of_sites:
            train_command += " " + str(site.site_id)
        return train_command


class Movement:

    @staticmethod
    def from_command_to_point(command: str) -> List[int]:
        command = command.split(" ")
        if command[0] == "MOVE":
            return [int(command[1]),int(command[2])]
        elif command[0] == "BUILD":
            site_id = int(command[1])
            return Sites.sites[site_id].pos
        else:
            return Units.alliedQueen.pos

    @staticmethod
    def from_point_to_command(pos: List[int]) -> str:
        return "MOVE {} {} \nTRAIN".format(int(pos[0]), int(pos[1]))

    @staticmethod
    def dance(site: 'Site', unit: 'Unit'):

        q = Units.alliedQueen

        theta1 = np.arctan2(unit.pos[1] - q.pos[1], unit.pos[0]-q.pos[0])
        theta2 = np.arctan2(site.pos[1] - q.pos[1], site.pos[0]-q.pos[0])

        if theta2 - theta1 < -0.1:
            new_pos = [int(q.pos[0] + 60 * np.cos(theta2 - 0.4)), int(q.pos[1] + 60 * np.sin(theta2 - 0.4))]
        elif theta2 - theta1 > 0.1:
            new_pos = [int(q.pos[0] + 60 * np.cos(theta2 + 0.4)), int(q.pos[1] + 60 * np.sin(theta2 + 0.4))]
        else:
            new_pos = q.pos

        return new_pos



    @staticmethod
    def smoother(command: str) -> str:

        if len(Sites.towers_in_range(Sites.enemyTowers, Units.alliedQueen.pos, Units.alliedQueen.radius)) > 0:
            return Movement.from_point_to_command(Sites.farthest(Sites.alliedTowers, Units.alliedQueen.pos).pos)

        command_unzipped = command.split(" ")
        destination_radius = 0
        if command_unzipped[0] == "BUILD":
            site =  Sites.sites[int(command_unzipped[1])]
            destination_radius = site.radius + 5

        p1 = Units.alliedQueen.pos
        p2 = Movement.from_command_to_point(command)
        speed = Units.alliedQueen.speed

        theta = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
        phi = speed

        new_point = [p1[0] + phi * math.cos(theta), p1[1] + phi * math.sin(theta)]

        changed = False
        theta_change = 0
        VARIATION = 0.1
        biggest_threat = Units.biggest_threat_to_queen()

        while theta_change < math.pi:
            #d_queen_to_threat = distance(biggest_threat.pos, p1) if biggest_threat else 0

            theta_change += VARIATION
            new_point = [p1[0] + phi * math.cos(theta + theta_change), p1[1] + phi * math.sin(theta + theta_change)]
            #d_newpos_to_threat = distance(biggest_threat.pos, new_point) if biggest_threat else 1 and d_newpos_to_threat > d_queen_to_threat

            if not Sites.is_point_in_obstacle(new_point, Units.alliedQueen.radius) and not is_point_outside(new_point):
                changed = True
                break

            new_point = [p1[0] + phi * math.cos(theta - theta_change), p1[1] + phi * math.sin(theta - theta_change)]
            #d_newpos_to_threat = distance(biggest_threat.pos, new_point) if biggest_threat else 1

            if not Sites.is_point_in_obstacle(new_point, Units.alliedQueen.radius) and not is_point_outside(new_point):
                changed = True
                break

        if distance(p2, new_point) <= destination_radius + speed:
            return command
        elif changed:
            return Movement.from_point_to_command(new_point)
        else:
            return command


class Strategy:
    coreBuild: List[BuildCommand] = None

    income = 0
    corebuildings = 0

    current_build_order: List[BuildCommand] = None
    buildManager: BuildManager = None
    myGold: int
    time: int = 0
    starting_cuadrant: List[int] = []

    safety: Dict[List[int], int] = {}

    @staticmethod
    def check_current_building_built() -> bool:

        if not Strategy.current_build_order:
            return False

        s = Sites.sites[Strategy.current_build_order[0].site_id]
        cb = Strategy.current_build_order[0]

        if s.structure_name() == cb.structure_name and s.owner == 0:
            Strategy.current_build_order.pop(0)
            return True

        return False

    @staticmethod
    def set_core_build():
        Strategy.coreBuild = [BuildCommand("MINE", [0, 0]),
                              BuildCommand("MINE", [0, 0]),
                              BuildCommand("MINE", [0, 0]),
                              BuildCommand("BARRACKS-KNIGHT", [1, 1]),
                              BuildCommand("TOWER", [1, 1]),
                              BuildCommand("TOWER", [1, 1]),
                              ]

        Strategy.current_build_order = Strategy.coreBuild
        Strategy.buildManager = BuildManager(Strategy.coreBuild)

        for x in range(120, 1821, 100):
            for y in range(100, 901, 100):
                Strategy.safety[(x, y)] = 0

    @staticmethod
    def update():
        if Strategy.check_current_building_built():
            Strategy.corebuildings += 1

    @staticmethod
    def is_core_built():
        return Strategy.corebuildings >= 5

    @staticmethod
    def discard_current_building():
        Strategy.current_build_order.pop(0)

    @staticmethod
    def safest_point():
        for x in range(120, 1821, 100):
            for y in range(100, 901, 100):
                Strategy.safety[(x, y)] = len(Sites.towers_in_range(Sites.alliedTowers, [x,y]))
        item = max([item for item in Strategy.safety.items()], key= lambda p: p[1])
        return item[0]



    def safest_tower_pos(self):
        return max([tower for tower in Sites.alliedTowers], key=lambda t: Sites.towers_in_range(Sites.alliedTowers, t.pos)).pos




class Game:
    def __init__(self):
        self.starting_pos = None
        self.training_order = [0, 0, 0, 0, 0, 0, 0, 0]
        self.training_order_index = 0
        self.touched_site: int = -1
        self.command: str = None
        self.active_units: List[Unit] = []
        self.starting_cuadrant: List[int] = []

    def wait(self):
        self.command = "WAIT \nTRAIN"

    def move(self, x, y):
        self.command = "MOVE " + str(x) + " " + str(y) + " \nTRAIN"

    def build(self, site_id: int, structure: str):
        self.command = "BUILD " + str(site_id) + " " + structure + " \nTRAIN"

    def compose_command(self):

        actions: List[Tuple[Action]] = []
        training: List[Tuple[Action]] = []

        num_barracks_knights = len(Sites.alliedBarracksKnights)
        num_barracks_archer = len(Sites.alliedBarracksArcher)
        num_barracks_giant = len(Sites.alliedBarracksGiant)
        num_enemy_towers = len(Sites.enemyTowers)
        num_towers = len(Sites.alliedTowers)
        num_mines = len(Sites.alliedMines)

        current_buildings = [num_mines, num_towers, num_barracks_knights, num_barracks_archer]
        closest_upgradeable_mine = Sites.closest(Sites.alliedUpgradeableMines, Units.alliedQueen.pos)
        touched_site = Sites.site_touched()
        biggest_threat = Units.biggest_threat_to_queen()

        closest_unowned_site = Sites.closest(Sites.unownedSites, Units.alliedQueen.pos)
        unowned_site_close = is_point_inside_circle(closest_unowned_site.pos,Units.alliedQueen.pos,
                                                    closest_unowned_site.radius + 100) if closest_unowned_site else False



        aq = Units.alliedQueen
        eq = Units.enemyQueen
        nb = None
        if Strategy.current_build_order:
            nb = Strategy.current_build_order[0]
        ct = Sites.closest(Sites.alliedTowers, aq.pos)
        ft = Sites.closest(Sites.alliedTowers, eq.pos)
        fts = Sites.closest(Sites.towerable_sites(), eq.pos)
        cu = Sites.closest(Sites.unownedSites, aq.pos)


        a = Sites.towers_in_range(Sites.enemyTowers, Units.alliedQueen.pos, aq.radius)
        if len(a) > 0:
            heappush(actions, (4, Action(["BUILD", "MOVE", "SITE_ID", Sites.farthest(Sites.alliedTowers, aq.pos).site_id])))

        if closest_upgradeable_mine:
            heappush(actions, (6, Action(["BUILD", "MINE", "SITE_ID", closest_upgradeable_mine.site_id])))

        # Mejora la torre  hasta 400 de hp si la esta tocando
        if touched_site and touched_site.is_tower() and touched_site.is_upgradeable(550):
            heappush(actions, (7, Action(["BUILD", "TOWER", "SITE_ID", touched_site.site_id])))

        # Mejora la torre al maximo si la esta tocando
        if touched_site and touched_site.is_tower() and touched_site.is_upgradeable(730):
            heappush(actions, (9, Action(["BUILD", "TOWER", "SITE_ID", touched_site.site_id])))

        def no_threats():
            if Strategy.is_core_built(): #He terminado con la core build?
                if cu and aq.health < eq.health and (len(Sites.alliedMines) == 0 or Strategy.income < 5): #Me he quedado sin minas y voy perdiendo?
                    heappush(actions, (10, Action(["BUILD", "MINE", "SITE_ID", cu.site_id])))
                elif aq.health < eq.health and len(Sites.alliedBarracks) == 0: # Me he quedado sin barracks y voy perdiendo?
                    heappush(actions, (10, Action(["BUILD", "BARRACKS-KNIGHT", "CLOSEST"])))
                elif fts:
                    heappush(actions, (10, Action(["BUILD", "TOWER", "SITE_ID", fts.site_id])))
                elif ft:
                    heappush(actions, (16, Action(["BUILD", "TOWER", "SITE_ID", ft.site_id])))
            else:
                heappush(actions, (8, Action(["BUILD", nb.structure_name, "SITEMAP_POS", nb.sitemap_pos])))

        if biggest_threat:  #Hay amenazas?
            threat = biggest_threat.turns_until_death() - biggest_threat.turns_to_reach_opposite_queen()

            if biggest_threat.turns_until_death() - biggest_threat.turns_to_reach_opposite_queen() < 3: #Me va a hacer menos de 5 dmg?
                closest_mine = Sites.closest(Sites.alliedMines, aq.pos)
                if ct and is_circle_intersecting_circle(aq.pos, aq.radius + 75, closest_mine.pos, closest_mine.radius): #estoy cerca de una mina?
                    heappush(actions, (10, Action(["MOVE", ct.pos])))
                else:
                    if nb and nb.structure_name == "MINE": # Voy a construir una mina?
                        heappush(actions, (10, Action(["BUILD", "TOWER", Sites.closest(Sites.towerable_sites(), aq.pos).site_id])))
                    else:
                        no_threats()
            else:
                if cu and is_circle_intersecting_circle2(cu.pos, cu.radius, aq.pos, aq.radius + 90):  # Estoy cerca de un site vacio?
                    heappush(actions, (10, Action(["BUILD", "TOWER", "SITE_ID", cu.site_id])))
                    debug("aprovecha")
                elif ct and is_circle_intersecting_circle2(ct.pos, ct.radius + 200, aq.pos, aq.radius): # Estoy cerca de torre aliada?
                    heappush(actions, (5, Action(["MOVE",  Movement.dance(ct, biggest_threat)])))
                    debug("dance")
                elif ct:
                    debug("torre cerca")
                    heappush(actions, (10, Action(["MOVE", ct.pos])))
                elif cu:
                    debug("unowned cerca")
                    heappush(actions, (10, Action(["BUILD", "TOWER", "SITE_ID", cu.site_id])))
        else:
            no_threats()

        #-- Training

        if Strategy.myGold >= 80:
            heappush(training, (10, Action(["TRAIN", 1, "KNIGHT"])))

        '''
        for action in list(actions):
            destination = Movement.from_command_to_point(action[1].command)
            if len(Sites.towers_in_range(Sites.enemyTowers, destination)) > 0:
                heappop(actions)
            else:
                break
        '''

        self.command = Movement.smoother(actions[0][1].command)

        if len(training) > 0:
            self.command += training[0][1].command
    def end_turn(self):
        print(self.command)

    def set_starting_pos(self, pos):
        def invert_build_order_cords():
            for i, build_command in enumerate(Strategy.coreBuild):
                Strategy.coreBuild[i].sitemap_pos = [3 - build_command.sitemap_pos[0], 5 - build_command.sitemap_pos[1]]

        def set_mapsites(reverse: bool):
            if reverse:
                map_ordered_by_y = sorted(sites.values(), key=lambda s: -s.pos[1])
            else:
                map_ordered_by_y = sorted(sites.values(), key=lambda s: s.pos[1])
            for i in range(0, 4):
                if reverse:
                    row_ordered_by_x = sorted(map_ordered_by_y[i * 6:i * 6 + 6], key=lambda s: -s.pos[0])
                else:
                    row_ordered_by_x = sorted(map_ordered_by_y[i * 6:i * 6 + 6], key=lambda s: s.pos[0])
                for j in range(0, 6):
                    Sites.sites[row_ordered_by_x[j].site_id].sitemap_pos = [i, j]
                Sites.sitemap.append(row_ordered_by_x)

        d00 = distance([0, 0], pos)
        d11 = distance([1920, 1000], pos)

        if min(d00, d11) == d00:
            Strategy.starting_cuadrant = [0, 0]
            set_mapsites(False)
        else:
            Strategy.starting_cuadrant = [1, 1]
            #invert_build_order_cords()
            set_mapsites(True)

        self.starting_pos = pos

    def update_units(self):
        Units.add_units(self.active_units)

class GA:
    DNA_SIZE = 5
    POP_SIZE = 10
    CROSS_RATE  = 0.8
    MUTATION_RATE = 0.003
    N_GENERATIONS = 2
    COMMANDS: List[str] = ["MOVE 0 0", "MOVE 1920 0", "MOVE 0 1000", "MOVE 1920 1000"]
    num_sim = 0

    def translateDNA(self, pop: List[List[int]]) -> List[List[str]]: #Se le pasa una lista de enteros(indices) y devuelve los commands
        return [[self.COMMANDS[i] for i in dna] for dna in pop]

    def get_all_fitness(self, pop_commands: List[List[str]]) -> 'np.ndarray':  # Se le pasa una lista de commands y devuelve un valor de fitness, aqui van las simulaciones
        fitn = []
        for dna_commands in pop_commands:
            fitn.append(self.get_fitness(dna_commands))
        return np.array(fitn)

    def get_fitness(self, commands: List[str]) -> int:
        sm = Simulator()
        sm.simulations(commands)

        return max(sm.state.my_queen.health, 0)

    def select(self, pop, fitness):
        idx = np.random.choice(np.arange(self.POP_SIZE), size=self.POP_SIZE, replace=True,
                               p=fitness / fitness.sum())
        return pop[idx]

    def crossover(self, parent, pop):
        if np.random.rand() < self.CROSS_RATE:
            i_ = np.random.randint(0, self.POP_SIZE, size=1)  # select another individual from pop
            cross_points = np.random.randint(0, 2, size=self.DNA_SIZE).astype(np.bool)  # choose crossover points
            parent[cross_points] = pop[i_, cross_points]  # mating and produce one child
        return parent

    def mutate(self, child):
        for point in range(self.DNA_SIZE):
            if np.random.rand() < self.MUTATION_RATE:
                child[point] = 1 if child[point] == 0 else 0 #CAMBIAR
        return child

    def get_best(self) -> str:
        pop = np.random.randint(len(self.COMMANDS), size=(self.POP_SIZE, self.DNA_SIZE))
        fitness = None
        for _ in range(self.N_GENERATIONS):
            # GA part (evolution)
            translated = self.translateDNA(pop)
            fitness = self.get_all_fitness(translated)
            pop = self.select(pop, fitness)
            pop_copy = pop.copy()
            for parent in pop:
                child = self.crossover(parent, pop_copy)
                child = self.mutate(child)
                parent[:] = child  # parent is replaced by its child

        return self.COMMANDS[pop[np.argmax(fitness)][0]]

game = Game()

sites = {}

num_sites = int(input())
for i in range(num_sites):
    site_id, x, y, radius = [int(j) for j in input().split()]
    sites[site_id] = Site(site_id, x, y, radius)

Sites.set_sites(sites)

# game loop
while True:
    start = time.time()
    Strategy.time += 1

    gold, touched_site = [int(i) for i in input().split()]

    Strategy.myGold = gold
    Strategy.income = 0
    game.touched_site = touched_site
    Units.touchedSite = touched_site

    Sites.clear()
    game.active_units = []
    Units.clear()

    for i in range(num_sites):
        # structure_type: -1 = No structure, 2 = Barracks
        # owner: -1 = No structure, 0 = Friendly, 1 = Enemy
        site_id, gold, max_mine_site, structure_type, owner, param_1, param_2 = [int(j) for j in input().split()]
        Sites.sites[site_id].update(gold, max_mine_site, structure_type, owner, param_1, param_2)
        Sites.add_site(Sites.sites[site_id])
    num_units = int(input())
    for i in range(num_units):
        # unit_type: -1 = QUEEN, 0 = KNIGHT, 1 = ARCHER
        x, y, owner, unit_type, health = [int(j) for j in input().split()]
        if unit_type == -1 and owner == 0:
            Units.alliedQueen = Unit(x, y, owner, unit_type, health)
            if game.starting_pos is None:
                game.set_starting_pos([x, y])
                Strategy.set_core_build()
        elif unit_type == -1 and owner == 1:
            Units.enemyQueen = Unit(x, y, owner, unit_type, health)
        else:
            game.active_units.append(Unit(x, y, owner, unit_type, health))

    Strategy.update()
    game.update_units()
    game.compose_command()
    game.end_turn()
    debug("Fin: " + str((time.time() - start)*1000))
