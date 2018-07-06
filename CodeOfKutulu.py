import sys
import math
from heapq import heappush
from typing import List, Dict, Set, Tuple, Optional
from time import time
from collections import defaultdict

SPAWNING = 0
WANDERING = 1
STALKING = 2
RUSHING = 3
STUNNED = 4


class Graph:
    def __init__(self):
        self.nodes = set()
        self.edges = defaultdict(set)

    def add_node(self, value):
        self.nodes.add(value)

    def add_edge(self, from_node, to_node):
        self.edges[from_node].add(to_node)
        self.edges[to_node].add(from_node)


def dijkstra(graph: Graph, initial):
    visited = {initial: 0}
    path = {}
    next_node = {initial: initial}

    nodes = set(graph.nodes)
    while nodes:
        min_node = None
        for node in nodes:
            if node in visited:
                if min_node is None:
                    min_node = node
                elif visited[node] < visited[min_node]:
                    min_node = node

        if min_node is None:
            break

        nodes.remove(min_node)
        current_weight = visited[min_node]

        for edge in graph.edges[min_node]:
            weight = current_weight + 1
            if edge not in visited or weight < visited[edge]:
                visited[edge] = weight
                path[edge] = min_node

    for node in graph.nodes:
        if node != initial and node in path:
            next_node[node] = path[node]
            for i in range(visited[node] - 2):
                if next_node[node] in path:
                    next_node[node] = path[next_node[node]]

    return visited, path, next_node


def update_moves(s0: 'State', depth: int):
    all_states = {}
    all_actions = {}
    states = [(s0.value(), 0, s0)]

    n = 0
    for i in range(depth):
        new_states = []
        for v, parent_id, s in states:
            for id in other_ids:
                all_actions[id] = enemy_action(s, id)
            if player_id in s.ex_ids:
                poss_actions = possible_actions(player_id, s)
            else:
                poss_actions = ["WAIT"]
            for action in poss_actions:
                n += 1
                all_actions[player_id] = action
                ns = s.new_state(all_actions)
                heappush(new_states, (s.value(), n, ns))
                all_states[n] = (action, parent_id, ns)

        states = new_states[:40]

    queued_actions = []
    state_id = states[0][1]

    for i in range(depth):
        queued_actions.append(all_states[state_id][0])
        state_id = all_states[state_id][1]

    return queued_actions

def enemy_action(s: 'State', id: int):

    if id in s.ex_ids:
        cells = board.walkable_cells(s.ex_pos[id])

        for m_id in s.m_ids:
            if s.m_pos[m_id] in cells:
                cells.remove(s.m_pos[m_id])
        if cells:
            cell = cells.pop()
            a = ("MOVE", cell[0], cell[1])
        else:
            a = ("WAIT", 0)
    else:
        a = ("WAIT", 0)

    return a

def debug(msg):
    print(msg, file=sys.stderr)


class Pos:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    @staticmethod
    def m_dist(pos0: Tuple[int, int], pos1: Tuple[int, int]) -> int:
        return abs(pos1[0] - pos0[0]) + abs(pos1[1] - pos0[1])


class Board:
    graph: Graph
    walls: Set[Tuple[int, int]] = set()
    spawners: Set[Tuple[int, int]] = set()
    shelters: Set[Tuple[int, int]] = set()
    walkable: Set[Tuple[int, int]] = set()

    def __init__(self, lines: List[str]):
        self.graph = Graph()

        for j in range(len(lines)):
            for i in range(len(lines[0])):
                c = lines[j][i]
                pos = (i, j)
                if c == "#":
                    self.walls.add(pos)
                elif c == "w":
                    self.spawners.add(pos)
                    self.walkable.add(pos)
                    self.graph.add_node(pos)
                elif c == "U":
                    self.shelters.add(pos)
                    self.walkable.add(pos)
                    self.graph.add_node(pos)
                else:
                    self.walkable.add(pos)
                    self.graph.add_node(pos)

        for origen in self.walkable:
            for cell in self.adyacent_cells(origen):
                self.graph.add_edge(origen, cell)

        self.distance = dict()
        self.next_node = dict()
        self.close_cells5 = dict()
        self.close_cells2 = dict()

        for start in self.graph.nodes:
            distance, path, next_node = dijkstra(self.graph, start)
            self.distance[start] = distance
            self.next_node[start] = next_node
            self.close_cells5[start] = self.close_cells(start, 5)
            self.close_cells2[start] = self.close_cells(start, 2)

    def adyacent_cells(self, origen: Tuple[int, int]) -> Set[Tuple[int,int]]:
        cells = set()

        cell = (origen[0] + 1, origen[1])
        if cell in self.walkable:
            cells.add(cell)

        cell = (origen[0] - 1, origen[1])
        if cell in self.walkable:
            cells.add(cell)

        cell = (origen[0], origen[1] + 1)
        if cell in self.walkable:
            cells.add(cell)

        cell = (origen[0], origen[1] - 1)
        if cell in self.walkable:
            cells.add(cell)

        return cells

    def los_cells(self, origen: Tuple[int, int]) -> Set[Tuple[int, int]]:
        cells = set()

        top_walled = False
        right_walled = False
        bot_walled = False
        left_walled = False

        steps = 0
        while top_walled and right_walled and bot_walled and left_walled == False:
            steps += 1
            top = (origen[0] + steps, origen[1])
            right = (origen[0], origen[1] + steps)
            bot = (origen[0] - steps, origen[1])
            left = (origen[0], origen[1] - steps)
            if not top_walled and top in board.walkable:
                cells.add(top)
            else:
                top_walled = True

            if not right_walled and right in board.walkable:
                cells.add(right)
            else:
                right_walled = True

            if not bot_walled and bot in board.walkable:
                cells.add(bot)
            else:
                bot_walled = True

            if not left_walled and left in board.walkable:
                cells.add(left)
            else:
                left_walled = True

        return cells

    def close_cells(self, origen: Tuple[int, int], distance: int) -> Set[Tuple[int, int]]:
        cells = {origen}
        visited = set()

        for i in range(distance):
            for cell in cells - visited:
                cells = cells.union(self.adyacent_cells(cell))
                visited.add(cell)

        return cells

    def closest_adyacent_walkable_cell(self, origen: Tuple[int,int], destino: Tuple[int,int]) -> Tuple[int,int]:
        cell, current_distance = tuple(), 100000
        for x in range(origen[0] - 1, origen[0] + 2):
            for y in range(origen[1] - 1, origen[1] + 2):
                distance = Pos.m_dist((x,y),destino)
                if (x, y) in self.walkable and distance < current_distance:
                    cell = (x,y)
                    current_distance = distance
        return cell

    def move_actions_adyacent_walkable_cells(self, origen: Tuple[int,int]) -> Set[Tuple]:
        actions: Set[Tuple] = set()

        cell = (origen[0] + 1, origen[1])
        if cell in self.walkable:
            actions.add(("MOVE", cell[0], cell[1]))

        cell = (origen[0] - 1, origen[1])
        if cell in self.walkable:
            actions.add(("MOVE", cell[0], cell[1]))

        cell = (origen[0], origen[1] + 1)
        if cell in self.walkable:
            actions.add(("MOVE", cell[0], cell[1]))

        cell = (origen[0], origen[1] - 1)
        if cell in self.walkable:
            actions.add(("MOVE", cell[0], cell[1]))

        return actions

    def walkable_cells(self, origen: Tuple[int, int]):
        cells = {origen}

        cell = (origen[0] + 1, origen[1])
        if cell in self.walkable:
            cells.add(cell)

        cell = (origen[0] - 1, origen[1])
        if cell in self.walkable:
            cells.add(cell)

        cell = (origen[0], origen[1] + 1)
        if cell in self.walkable:
            cells.add(cell)

        cell = (origen[0], origen[1] - 1)
        if cell in self.walkable:
            cells.add(cell)

        return cells

class State:
    turn: int

    ex_ids: Set[int]
    ex_pos: Dict[int, Tuple[int, int]]
    ex_sanity: Dict[int, int]
    ex_plans: Dict[int, int]
    ex_lights: Dict[int, int]
    ex_stuck: Set[int]
    ex_has_effect: Dict[int, bool]

    m_type: Dict[int, str]
    m_ids: Set[int]
    m_pos: Dict[int, Tuple[int, int]]
    m_time_left: Dict[int, int]
    m_state: Dict[int, int]
    m_target: Dict[int, Optional[int]]
    m_target_last_seen: Dict[int, Optional[Tuple[int, int]]]

    ef_pos: List[Tuple[int, int]]
    ef_type: List[str]
    ef_time_energy_left: List[int]
    ef_started_by: List[int]
    ef_target: List[int]

    b_lighted_cells: Set[Tuple[int, int]]
    yelled: Dict[int, Set[int]]

    def __init__(self, turn, ex_ids, ex_pos, ex_sanity, ex_plans, ex_lights, ex_stuck, m_type, m_target_last_seen,
                 m_ids, m_pos, m_time_left, m_state, m_target, ef_pos, ef_type,
                 ef_time_energy_left, ef_stated_by, ef_target, yelled, ex_has_effect):
        self.turn = turn
        self.ex_ids = ex_ids
        self.ex_pos, self.ex_sanity, self.ex_plans, self.ex_lights, self.ex_stuck = ex_pos, ex_sanity, ex_plans, ex_lights, ex_stuck
        self.m_type, self.m_target_last_seen = m_type, m_target_last_seen
        self.m_ids, self.m_pos, self.m_time_left, self.m_state, self.m_target = m_ids, m_pos, m_time_left, m_state, m_target
        self.ef_pos, self.ef_time_energy_left, self.ef_type, self.ef_started_by, self.ef_target = ef_pos, ef_time_energy_left, ef_type, ef_stated_by, ef_target
        self.b_lighted_cells = set()
        self.yelled = yelled
        self.ex_has_effect = ex_has_effect

    def copy(self) -> 'State':
        return State(self.turn, set(self.ex_ids), dict(self.ex_pos), dict(self.ex_sanity),
                     dict(self.ex_plans), dict(self.ex_lights),
                     set(self.ex_stuck), dict(self.m_type), dict(self.m_target_last_seen),
                     set(self.m_ids),dict(self.m_pos), dict(self.m_time_left), dict(self.m_state),
                     dict(self.m_target), list(self.ef_pos), list(self.ef_type), list(self.ef_time_energy_left),
                     list(self.ef_started_by), list(self.ef_target), dict(yelled), dict(self.ex_has_effect))

    def __gt__(self, other):
        return self.value() < other.value()

    def value(self):
        if player_id in self.ex_sanity:
            closest_m_d = 1000
            closest_ex_d = 1000
            slashers_in_los = 0
            ate_minion = 0
            sanity = self.ex_sanity[player_id]
            if sanity < 40:
                sanity *= 10
            elif sanity < 10:
                sanity *= 100

            for id in self.ex_ids:
                if id == player_id:
                    continue
                my_ex_pos = self.ex_pos[player_id]
                ot_ex_pos = self.ex_pos[id]
                d = Pos.m_dist(my_ex_pos, ot_ex_pos)
                if d < closest_ex_d:
                    closest_ex_d = d

            for id in self.m_ids:
                m_pos = self.m_pos[id]
                ex_pos = self.ex_pos[player_id]
                d = board.distance[ex_pos][m_pos]
                if d < closest_m_d:
                    closest_m_d = d
                if self.m_type[id] == "SLASHER" and board.distance[m_pos][ex_pos] in {abs(m_pos[0] - ex_pos[0]), abs(m_pos[1] - ex_pos[1])}:
                    slashers_in_los += 1

            for m_id in self.m_ids:
                if self.m_pos[m_id] in self.ex_pos[player_id]:
                    ate_minion += 1

            return -2*sanity + 15 * slashers_in_los
        else:
            return 100

    def new_state(self, explorers_action: Dict[int, List]):
        ns = self.copy()
        ns.turn += 1
        if len(ns.ex_ids) <= 1:
            return ns

        # 2 - Commands
        # 2.1 - YELLS (YELL)
        for id, action in explorers_action.items():
            if id not in ns.ex_ids:
                continue
            if action[0] == "YELL":
                adyacent_cells = board.adyacent_cells(ns.ex_pos[id])
                for t_id in ns.ex_ids:
                    if id != t_id and ns.ex_pos[t_id] in adyacent_cells and explorers_action[t_id][0] != "YELL"\
                            and t_id not in ns.yelled[id]:
                        explorers_action[t_id] = ("WAIT", 0)
                        ns.ex_stuck.add(t_id)
                        ns.yelled[id].add(t_id)
                        #Add yell effect
                        ns.ef_type.append("EFFECT_YELL")
                        ns.ef_pos.append(ns.ex_pos[t_id])
                        ns.ef_time_energy_left.append(2)
                        ns.ef_started_by.append(id)
                        ns.ef_target.append(t_id)

        # 2.2 - Others commands (MOVE, PLAN, LIGHT)
        for id, action in explorers_action.items():
            if id not in ns.ex_ids:
                continue
            if id in ns.ex_stuck:
                continue
            elif action[0] == "MOVE":
                cell = (action[1], action[2])
                if id == player_id:
                    ns.ex_pos[id] = cell
                else:
                    ns.ex_pos[id] = board.next_node[ns.ex_pos[id]][cell]
            elif action[0] == "PLAN":
                if ns.ex_plans[id] > 0:
                    ns.ex_plans[id] -= 1
                    ns.ex_has_effect[id] = True
                    #Add plan effect
                    ns.ef_type.append("EFFECT_PLAN")
                    ns.ef_pos.append(ns.ex_pos[id])
                    ns.ef_time_energy_left.append(5)
                    ns.ef_started_by.append(id)
                    ns.ef_target.append(-1)
            elif action[0] == "LIGHT": # aposta
                if ns.ex_lights[id] > 0:
                    ns.ex_lights[id] -= 1
                    ns.ex_has_effect[id] = True
                    # Add light effect
                    ns.ef_type.append("EFFECT_LIGHT")
                    ns.ef_pos.append(ns.ex_pos[id])
                    ns.ef_time_energy_left.append(3)
                    ns.ef_started_by.append(id)
                    ns.ef_target.append(-1)

        # 3 - Effects apply, remove if finished after apply
        effects_to_remove = list()
        for i in range(len(ns.ef_pos)):
            if ns.ef_started_by[i] not in ns.ex_ids:
                effects_to_remove.append(i)
            elif ns.ef_type[i] == "EFFECT_PLAN":
                ex_started_id = ns.ef_started_by[i]
                ns.ef_pos[i] = ns.ex_pos[ex_started_id]
                planned_cells = board.close_cells2[ns.ef_pos[i]]

                explorers_healed = 0
                for id in ns.ex_ids:
                    if ns.ex_pos[id] in planned_cells and id != ex_started_id:
                        ns.ex_sanity[id] += 3
                        explorers_healed += 1

                ns.ex_sanity[ex_started_id] += 2 + explorers_healed * 3

                ns.ef_time_energy_left[i] -= 1
                if ns.ef_time_energy_left[i] <= 0:
                    effects_to_remove.append(i)
                    ns.ex_has_effect[ex_started_id] = False


            elif ns.ef_type[i] == "EFFECT_LIGHT":
                ex_started_id = ns.ef_started_by[i]
                ns.ef_pos[i] = ns.ex_pos[ex_started_id]
                #ns.b_lighted_cells = ns.b_lighted_cells.union(board.close_cells2[ns.ef_pos[i]])

                ns.ef_time_energy_left[i] -= 1
                if ns.ef_time_energy_left[i] <= 0:
                    effects_to_remove.append(i)
                    ns.ex_has_effect[ex_started_id] = False

            elif ns.ef_type[i] == "EFFECT_SHELTER":
                pos = ns.ef_pos[i]
                for id in ns.ex_ids:
                    if pos == ns.ex_pos[id]:
                        ns.ex_sanity[id] += 5
                        ns.ef_time_energy_left[i] -= 1

                ns.ef_time_energy_left[i] -= 1
                if ns.ef_time_energy_left[i] <= 0:
                    effects_to_remove.append(i)

            elif ns.ef_type[i] == "EFFECT_YELL":
                ns.ef_time_energy_left[i] -= 1
                if ns.ef_time_energy_left[i] <= 0:
                    ns.ex_stuck.remove(ns.ef_target[i])
                    #ns.yelled[ns.ef_started_by[i]].remove(ns.ef_target[i])
                    effects_to_remove.append(i)

        for i in reversed(effects_to_remove):
            del(ns.ef_time_energy_left[i])
            del(ns.ef_pos[i])
            del(ns.ef_type[i])
            del(ns.ef_started_by[i])
            del(ns.ef_target[i])

        # 4 - Minions update - se hace to menos la perdida pasiva

        for m_id in set(ns.m_ids):
            if ns.m_type[m_id] == "WANDERER":
                State.w_next_state(m_id, ns)
            else:
                State.sl_next_state(m_id, ns)

        # 5 - Explorers lose passive sanity

        for ex_id in ns.ex_ids:

            has_close_ex = False

            for ex2_id in ns.ex_ids:
                if ex_id == ex2_id:
                    continue
                p1 = ns.ex_pos[ex_id]
                p2 = ns.ex_pos[ex2_id]
                if Pos.m_dist(p1, p2) <= 2:
                    has_close_ex = True
                    break

            if has_close_ex:
                ns.ex_sanity[ex_id] -= SANITY_LOSS_GROUP
            else:
                ns.ex_sanity[ex_id] -= SANITY_LOSS_LONELY

        # 6 - Remove dead explorers

        for ex_id in set(ns.ex_ids):
            if ns.ex_sanity[ex_id] <= 0:
                State.ex_remove(ex_id, ns)

        return ns


    @staticmethod
    def m_closest_player(m_id: int, ns: 'State') -> int:
        closest_player = 0
        closest_distance = 10000
        start = ns.m_pos[m_id]
        for id in ns.ex_ids:
            d = board.distance[start][ns.ex_pos[id]]
            if d < closest_distance:
                closest_player = id
                closest_distance = d
        return closest_player

    @staticmethod
    def update_slasher_target(sl_id: int, ns: 'State') -> bool:
        if sl_id in ns.m_target:
            previous_target = ns.m_target[sl_id]
        else:
            previous_target = None

        ex_in_los = set()
        start = ns.m_pos[sl_id]
        for ex_id in ns.ex_ids:
            pos = ns.ex_pos[ex_id]
            on_los = board.distance[start][pos] in {abs(pos[0] - start[0]), abs(pos[1] - start[1])}
            if on_los:
                ex_in_los.add(ex_id)

        if previous_target and previous_target in ex_in_los:
            ns.m_target[sl_id] = previous_target
            ns.m_target_last_seen[sl_id] = ns.ex_pos[previous_target]
            return True

        if not ex_in_los:
            ns.m_target[sl_id] = None
            return False
        elif len(ex_in_los) == 1:
            ns.m_target[sl_id] = ex_in_los.pop()
            ns.m_target_last_seen[sl_id] = ns.ex_pos[ns.m_target[sl_id]]
            return True
        else:
            ns.m_target[sl_id] = None
            ns.m_target_last_seen[sl_id] = None
            return False

    @staticmethod
    def update_slasher_last_seen(sl_id: int, m_target_last_seen, ns: 'State') -> bool:
        if sl_id in ns.m_target:
            previous_target = ns.m_target[sl_id]
        else:
            previous_target = None

        ex_in_los = set()
        start = ns.m_pos[sl_id]
        for ex_id in ns.ex_ids:
            pos = ns.ex_pos[ex_id]
            x_dif = abs(pos[0] - start[0])
            y_dif = abs(pos[1] - start[1])
            on_los = board.distance[start][pos] in {x_dif, y_dif}
            if on_los:
                ex_in_los.add(ex_id)

        if previous_target and previous_target in ex_in_los:
            m_target_last_seen[sl_id] = ns.ex_pos[previous_target]
            return True

        if not ex_in_los:
            return False

        elif len(ex_in_los) == 1:
            target = ex_in_los.pop()
            m_target_last_seen[sl_id] = ns.ex_pos[target]
            return True

        else:
            m_target_last_seen[sl_id] = None
            return False

    @staticmethod
    def scare_explorers(pos: Tuple[int, int], ns: 'State'):
        for ex_id in ns.ex_ids:
            if pos == ns.ex_pos[ex_id]:
                ns.ex_sanity[ex_id] -= 20


    @staticmethod
    def ex_remove(id: int, ns: 'State'):
        del (ns.ex_sanity[id])
        del (ns.ex_pos[id])
        del (ns.ex_lights[id])
        del (ns.ex_plans[id])
        ns.ex_ids.remove(id)
        if id in ns.ex_stuck:
            ns.ex_stuck.remove(id)

    @staticmethod
    def m_remove(id: int, ns: 'State'):
        del (ns.m_pos[id])
        del (ns.m_time_left[id])
        del (ns.m_state[id])
        del (ns.m_type[id])
        del (ns.m_target[id])
        ns.m_ids.remove(id)
        if id in ns.m_target_last_seen:
            del (ns.m_target_last_seen[id])

    @staticmethod
    def w_next_state(id: int, ns: 'State'):
        if ns.m_state[id] == SPAWNING:
            ns.m_time_left[id] -= 1
            if ns.m_time_left[id] == 0:
                ns.m_state[id] = WANDERING
                ns.m_time_left[id] = WANDERER_LIFE_TIME
        else:
            closest_ex = State.m_closest_player(id, ns)
            ns.m_pos[id] = board.next_node[ns.m_pos[id]][ns.ex_pos[closest_ex]]
            success = False
            for ex_id in ns.ex_ids:
                if ns.ex_pos[ex_id] == ns.m_pos[id]:
                    State.scare_explorers(ns.ex_pos[ex_id], ns)
                    success = True
            if success:
                State.m_remove(id, ns)
            else:
                ns.m_time_left[id] -= 1
                if ns.m_time_left[id] == 0:
                    State.m_remove(id, ns)

    @staticmethod
    def sl_next_state(id: int, ns: 'State'):
        if ns.m_state[id] == SPAWNING:
            ns.m_time_left[id] -= 1
            if ns.m_time_left[id] == 0:
                ns.m_state[id] = RUSHING
        elif ns.m_state[id] == STALKING:
            ns.m_time_left[id] -= 1
            State.update_slasher_target(id, ns)
            if ns.m_time_left[id] == 0:
                ns.m_state[id] = RUSHING
        elif ns.m_state[id] == RUSHING:
            if State.update_slasher_target(id, ns):
                ns.m_pos[id] = ns.ex_pos[ns.m_target[id]]
            elif id in ns.m_target_last_seen and ns.m_target_last_seen[id]:
                ns.m_pos[id] = ns.m_target_last_seen[id]
            State.scare_explorers(ns.m_pos[id], ns)
            ns.m_state[id] = STUNNED
            ns.m_time_left[id] = 6
        elif ns.m_state[id] == STUNNED:
            ns.m_time_left[id] -= 1
            if ns.m_time_left[id] == 0:
                ns.m_state[id] = WANDERING
        else:
            if State.update_slasher_target(id, ns):
                ns.m_time_left[id] = 2
                ns.m_state[id] = STALKING
            else:
                closest_ex = State.m_closest_player(id, ns)
                ns.m_pos[id] = board.next_node[ns.m_pos[id]][ns.ex_pos[closest_ex]]

    @staticmethod
    def new_turn(s: 'State'):
        s.turn += 1
        s.ex_ids = set()
        s.ex_pos: Dict[int, Tuple[int, int]] = dict()
        s.ex_sanity: Dict[int, int] = dict()
        s.ex_plans: Dict[int, int] = dict()
        s.ex_lights: Dict[int, int] = dict()

        s.m_ids = set()
        s.m_type: Dict[int, str] = dict()
        s.m_pos: Dict[int, Tuple[int, int]] = dict()
        s.m_time_left: Dict[int, int] = dict()
        s.m_state: Dict[int, int] = dict()
        s.m_target: Dict[int, int] = dict()

        s.ef_pos: List[Tuple[int, int]] = list()
        s.ef_type: List[int] = list()
        s.ef_time_energy_left: List[int] = list()  # time_left, energy_left
        s.ef_started_by: List[int] = list()  # started_by
        s.ef_target: List[int] = list()  # -1, yelled_player


def possible_actions(ex_id: int, s: 'State') -> Set:

    pos = s.ex_pos[ex_id]

    has_effect = s.ex_has_effect[ex_id]

    actions = board.move_actions_adyacent_walkable_cells(pos)

    if not has_effect:
        if s.ex_plans[ex_id] > 0:
            a = ("PLAN", " ")
            actions.add(a)
        elif s.ex_lights[ex_id] > 0:
            a = ("LIGHT", " ")
            actions.add(a)
    #if len(s.yelled[player_id]) < 3:
     #   a = ("YELL", " ")
      #  actions.add(a)

    return actions


player_id: int = 0
other_ids: Set[int] = set()
ex_ids0: List[int] = list()
minions_id: Set[int] = set()
slashers_id: List[int] = list()
yelled: Dict[int, Set[int]] = {0: set(), 1: set(), 2: set(), 3: set()}

WIDTH = int(input())
HEIGHT = int(input())

lines = []
for i in range(HEIGHT):
    lines.append(input())

# sanity_loss_lonely: how much sanity you lose every turn when alone, always 3 until wood 1
# sanity_loss_group: how much sanity you lose every turn when near another player, always 1 until wood 1
# wanderer_spawn_time: how many turns the wanderer take to spawn, always 3 until wood 1
# wanderer_life_time: how many turns the wanderer is on map after spawning, always 40 until wood 1
SANITY_LOSS_LONELY, SANITY_LOSS_GROUP, WANDERER_SPAWN_TIME, WANDERER_LIFE_TIME = [int(i) for i in input().split()]

board = Board(lines)


m_target_last_seen = dict()

s0 = State(0, set(), {}, {}, {}, {}, set(), {}, {}, set(), {}, {}, {}, {}, [], [], [], [], [], {0:set(), 1:set(), 2:set(), 3:set()}, {0: False, 1: False, 2:False, 3:False})
moves = []
while True:

    State.new_turn(s0)

    entity_count = int(input())  # the first given entity corresponds to your explorer
    for i in range(entity_count):
        entity_type, id, x, y, param_0, param_1, param_2 = input().split()
        id = int(id)
        x = int(x)
        y = int(y)
        param_0 = int(param_0) #sanity, time_left
        param_1 = int(param_1) #plans, spawning 0 or wandering 1, id explorer who started effect
        param_2 = int(param_2) #lights, target explorer of minion -1 if no target
        if entity_type == "EXPLORER":
            if i == 0:
                player_id = id
                other_ids = {0,1,2,3}
                other_ids.remove(id)
            s0.ex_ids.add(id)
            s0.ex_pos[id] = (x, y)
            s0.ex_sanity[id] = param_0
            s0.ex_plans[id] = param_1
            s0.ex_lights[id] = param_2
            s0.ex_has_effect[id] = False

        elif entity_type in {"WANDERER", "SLASHER"}:
            s0.m_ids.add(id)
            s0.m_type[id] = entity_type
            s0.m_pos[id] = (x, y)
            s0.m_time_left[id] = param_0
            s0.m_state[id] = param_1
            s0.m_target[id] = param_2
            if entity_type == "SLASHER" and s0.turn > 1:
                State.update_slasher_last_seen(id, m_target_last_seen, s0)

        elif entity_type in {"EFFECT_PLAN", "EFFECT_SHELTER", "EFFECT_YELL", "EFFECT_LIGHT"}:
            s0.ef_pos.append((x, y))
            s0.ef_type.append(entity_type)
            s0.ef_time_energy_left.append(param_0)
            s0.ef_started_by.append(param_1)
            if entity_type in ("EFFECT_PLAN", "EFFECT_LIGHT"):
                s0.ex_has_effect[param_1] = True
            s0.ef_target.append(param_2)

    actions = {0: ["WAIT"], 1: ["WAIT"], 2: ["WAIT"], 3: ["WAIT"]}
    t0 = time()

    if len(moves) == 0:
        moves = update_moves(s0, 4)

    debug(moves)

    m = moves.pop()
    if len(m) == 3:
        m = "{} {} {}".format(m[0], m[1], m[2])
    if len(m) == 2:
        m = m[0]
    else:
        m = m

    debug(time() - t0)
    print(m)

