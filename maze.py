import pygame
from random import choice
import queue

RES = WIDTH, HEIGHT = 1202, 902
TILE = 50
cols, rows = WIDTH // TILE, HEIGHT // TILE

pygame.init()
sc = pygame.display.set_mode(RES)
clock = pygame.time.Clock()
gr = [[] for _ in range(cols * rows)]


path = []


class Cell:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.walls = {'top': True, 'right': True, 'bottom': True, 'left': True}
        self.visited = False

    def draw(self):
        x, y = self.x * TILE, self.y * TILE
        if self.visited:
            pygame.draw.rect(sc, pygame.Color('black'), (x, y, TILE, TILE))

        if self.walls['top']:
            pygame.draw.line(sc, pygame.Color('darkorange'), (x, y), (x + TILE, y), 2)
        if self.walls['right']:
            pygame.draw.line(sc, pygame.Color('darkorange'), (x + TILE, y), (x + TILE, y + TILE), 2)
        if self.walls['left']:
            pygame.draw.line(sc, pygame.Color('darkorange'), (x, y), (x, y + TILE), 2)
        if self.walls['bottom']:
            pygame.draw.line(sc, pygame.Color('darkorange'), (x, y + TILE), (x + TILE, y + TILE), 2)

    @staticmethod
    def check_cell(x, y):
        find_index: (x, y) = lambda x, y: x + y * cols
        if x < 0 or x > cols - 1 or y < 0 or y > rows - 1:
            return False
        return grid_cells[find_index(x, y)]

    def check_neighbours(self):
        neighbours = []
        top = self.check_cell(self.x, self.y - 1)
        right = self.check_cell(self.x + 1, self.y)
        bottom = self.check_cell(self.x, self.y + 1)
        left = self.check_cell(self.x - 1, self.y)
        if top and not top.visited:
            neighbours.append(top)
        if right and not right.visited:
            neighbours.append(right)
        if bottom and not bottom.visited:
            neighbours.append(bottom)
        if left and not left.visited:
            neighbours.append(left)
        return choice(neighbours) if neighbours else False

    def draw_current_cell(self):
        x, y = self.x * TILE, self.y * TILE
        if self.visited:
            pygame.draw.rect(sc, pygame.Color('saddlebrown'), (x + 2, y + 2, TILE - 2, TILE - 2))

    def draw_start_cell(self):
        x, y = self.x * TILE, self.y * TILE
        pygame.draw.rect(sc, pygame.Color('green'), (x + 2, y + 2, TILE - 2, TILE - 2))

    def draw_end_cell(self):
        x, y = self.x * TILE, self.y * TILE
        pygame.draw.rect(sc, pygame.Color('orange'), (x + 2, y + 2, TILE - 2, TILE - 2))


def remove_walls(current, next):
    dx = current.x - next.x
    if dx == 1:
        current.walls['left'] = False
        next.walls['right'] = False
    elif dx == -1:
        current.walls['right'] = False
        next.walls['left'] = False
    dy = current.y - next.y
    if dy == 1:
        current.walls['top'] = False
        next.walls['bottom'] = False
    elif dy == -1:
        current.walls['bottom'] = False
        next.walls['top'] = False


def bfs(start, end, graph):
    frontier = queue.Queue()
    frontier.put(start)
    came_from = {start: None}

    while not frontier.empty():
        current = frontier.get()
        if came_from == end:
            break
        for next in graph[current]:
            if next not in came_from:
                frontier.put(next)
                came_from[next] = current
    current = end
    p = [current]
    while current != start:
        current = came_from[current]
        p.append(current)
    p.reverse()
    print(f'start={start},end={end},graph={graph}')
    print(f'path={path}')
    return p


grid_cells = [Cell(col, row) for row in range(rows) for col in range(cols)]

current_cell = grid_cells[0]
stack = []
coord_cell = 0
coord_cell_x = 0
coord_cell_y = 0
toggle_gr = True
pos_x, pos_y = 0, 0
start_way = None
toggle_start_way = True
end_way = None
toggle_end_way = False
toggle_path = True
toggle_mousebutton = False

while True:
    sc.fill(pygame.Color('darkslategray'))
    [cell.draw() for cell in grid_cells]
    current_cell.visited = True
    next_cell = current_cell.check_neighbours()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if toggle_mousebutton:
                if toggle_start_way:
                    start_way = event.pos[0] // TILE + event.pos[1] // TILE * cols
                    toggle_start_way = False
                    toggle_end_way = True
                elif toggle_end_way:
                    end_way = event.pos[0] // TILE + event.pos[1] // TILE * cols
                    toggle_end_way = False

    if next_cell:
        next_cell.visited = True
        stack.append(current_cell)
        remove_walls(current_cell, next_cell)
        current_cell = next_cell
        current_cell.draw_current_cell()
    elif stack:
        current_cell = stack.pop()
        current_cell.draw_current_cell()

    if not stack:
        if toggle_gr:
            # постороение графа из лабиринта
            for i in range(0, len(grid_cells)):
                if not grid_cells[i].walls['top']:
                    gr[i].append(i - cols)
                if not grid_cells[i].walls['right']:
                    gr[i].append(i + 1)
                if not grid_cells[i].walls['bottom']:
                    gr[i].append(i + cols)
                if not grid_cells[i].walls['left']:
                    gr[i].append(i - 1)
            toggle_gr = False
            toggle_mousebutton = True
        if toggle_path and start_way and end_way is not None:
            path = bfs(start_way, end_way, gr)
            toggle_path = False

        if start_way is not None:
            grid_cells[start_way].draw_start_cell()
        if end_way is not None:
            grid_cells[end_way].draw_end_cell()
        for v in range(len(path) - 1):
            coord_x1 = TILE // 2 + (path[v] % cols) * TILE
            coord_y1 = TILE // 2 + (rows - (rows - path[v] // cols)) * TILE
            coord_x2 = TILE // 2 + (path[v + 1] % cols) * TILE
            coord_y2 = TILE // 2 + (rows - (rows - path[v + 1] // cols)) * TILE
            pygame.draw.line(sc, pygame.Color('cadetblue3'), (coord_x1, coord_y1), (coord_x2, coord_y2), 12)

    pygame.display.flip()
    clock.tick(300)

