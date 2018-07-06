import sys
import math
import numpy as np

width, height = [int(i) for i in input().split()]
count = int(input())


def make_tower():
    tower = list()
    for i in range(height):
        tower.append(list())
        for b in input():
            tower[i].append(b)
    return np.array(tower)


def tumble(tower: np.ndarray):
    new_tower = tower.transpose()
    #Espacios libres en cada columna.
    empty_spaces = [list() for i in range (new_tower.shape[1])]
    #Se recorre la torre de abajo a arriba.
    for row in reversed(range(new_tower.shape[0])):
        for col in range(new_tower.shape[1]):
            #Si se encuentra un espacio libre, se añade al final de los espacios libres de la columna.
            if new_tower[row][col] == ".":
                empty_spaces[col].append([row, col])
            else:
                # Si está ocupado y hay espacios libres en la columna, se realizan 3 operaciones
                if len(empty_spaces[col]) > 0:
                    # 1 - Se pone el espacio actual a 0
                    new_tower[row][col] = "."
                    # 2 - Se obtiene el primer espacio libre de la columna, se quita de la lista y se pone a 1
                    empty_row, empty_col = empty_spaces[col].pop(0)
                    new_tower[empty_row, empty_col] = "#"
                    # 3 - Se añade el espacio actual a espacios libres de la columna
                    empty_spaces[col].append([row, col])
    return new_tower


def print_tower(tower: np.ndarray):
    for row in range(tower.shape[0]):
        output = ""
        for col in range(tower.shape[1]):
            output += tower[row][col]
        print(output)


tower = make_tower()

for i in range(count):
    tower = tumble(tower)

print_tower(tower)
