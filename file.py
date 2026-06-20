from collections import deque
from queue import Queue
from copy import copy
import pygame
import random
import math
import json
import sys

class Stack:
    def __init__(self):
        self.items = deque()

    def is_empty(self):
        return len(self.items) == 0

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if not self.is_empty():
            return self.items.pop()
        return

    def peek(self):
        if not self.is_empty():
            return self.items[-1]
        return
    
    def size(self):
        return len(self.items)

WIDTH = 800
HEIGHT = 1000
FPS = 60

WHITE_TILE = (232, 237, 205)
BLACK_TILE = (120, 154, 87)
BORDER = (48, 46, 43)
BACKGROUND = (38, 37, 34)

DARK_GRAY = (78, 78, 78)
LIGHT_GRAY = (211, 211, 211)

WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)




BORDER_SIZE = WIDTH / 10 * 9
BORDER_X = (WIDTH - BORDER_SIZE) / 2
BORDER_Y = (WIDTH - BORDER_SIZE) / 2

BORDER_STRENGTH = 25

BOARD_X = BORDER_X + BORDER_STRENGTH
BOARD_Y = BORDER_Y + BORDER_STRENGTH
BOARD_SIZE = BORDER_SIZE - BORDER_STRENGTH * 2

TILE_SIZE = BOARD_SIZE / 8
DOT_SIZE = TILE_SIZE / 4
ATTACK_SIZE = DOT_SIZE * 2

INFO_BORDER_X = BORDER_X + BORDER_SIZE + (WIDTH - BORDER_SIZE) / 2
INFO_BORDER_Y = BORDER_Y
INFO_BORDER_WIDTH = WIDTH - BORDER_SIZE - (WIDTH - BORDER_SIZE) / 2 * 3
INFO_BORDER_HEIGHT = TILE_SIZE * 3 + BORDER_STRENGTH

HEALTH_WIDTH = TILE_SIZE / 10 * 8
HEALTH_HEIGHT = TILE_SIZE / 10 * 2

STATS_X = BORDER_X
STATS_Y =  BORDER_Y + BORDER_SIZE + BORDER_Y / 2
STATS_WIDTH = BORDER_SIZE
STATS_HEIGHT = HEIGHT - BORDER_SIZE - BORDER_Y * 2


pygame.init()
screen = pygame.display.set_mode([WIDTH, HEIGHT], pygame.SRCALPHA)
pygame.display.set_caption('Rapolo Žaidimas')
timer = pygame.time.Clock()

class Player:
    def __init__(self, team, turn):
        self.team = team
        self.turn = turn
        self.win = False
        self.history = Stack()
        self.figures = []
        self.undo = True

    def take_turn(self, enemy):
        turn = True
        while turn:
            turn = self.auto_end_turn(enemy)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for figure in self.figures:
                            if figure.position == select_tile(event.pos):
                                figure.interact(self, enemy)
                                selected = figure
                        for figure in enemy.figures:
                            if figure.position == select_tile(event.pos):
                                selected = figure
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_z:
                        self.use_undo(enemy)
                    elif event.key == pygame.K_RETURN:
                        turn = self.end_turn(enemy)

            if check_outcome():
                return
            
            selected = None
            timer.tick(FPS)
            load(selected)
            pygame.display.update()

    def take_random_turn(self, enemy):
        queue = Queue()
        random.shuffle(self.figures)
        for unit in self.figures:
            queue.put(unit)
        
        while not queue.empty():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            if check_outcome():
                return
            
            selected = queue.get()
            selected.is_attacking = False
            selected.is_healing = False

            selected.is_moving = True
            selected.check()
            if selected.valid_moves:
                destination = random.choice(selected.valid_moves)
                load(selected)
                selected.move(destination, self, enemy)
            
            pygame.time.delay(500)

            selected.is_attacking = True
            selected.check()
            if selected.valid_attacks:
                targets = [destination for destination in selected.valid_attacks if any(figure.position == destination for figure in enemy.figures)]
                if targets:
                    load(selected)
                    selected.attack(random.choice(targets), self, enemy)
                else:
                    selected.is_healing = True
                    load(selected)
                    selected.heal(selected.position, self, enemy)
            pygame.time.delay(500)

            if selected.move_counter > 0 or selected.action_counter > 0:
                queue.put(selected)

            selected = None
        self.end_turn(enemy)
    
    def auto_end_turn(self, enemy):
        counters = [figure.move_counter for figure in self.figures] + [figure.action_counter for figure in self.figures]
        if all(counter == 0 for counter in counters):
            return self.end_turn(enemy)
        else:
            return True

    def end_turn(self, enemy):
        self.turn = False
        enemy.turn = True
        for figure in self.figures:
            figure.reset()
        return self.turn

    def lose():
        pass

    def update_history(self, enemy):
        move = {}
        move[self.team] = [copy(figure) for figure in self.figures]
        move[enemy.team] = [copy(figure) for figure in enemy.figures]
        self.history.push(move)

    def undo_move(self, enemy):
        if not self.history.is_empty():
            move = self.history.pop()
            self.figures = move[self.team]
            enemy.figures = move[enemy.team]

    def use_undo(self, enemy):
        undos = 5
        if self.undo:
            self.undo_move(enemy)
            undos -= 1
            while undos > 0:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        self.undo = False
                        return
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_z:
                            self.undo_move(enemy)
                            undos -= 1
                        else:
                            self.undo = False
                            return
                
                timer.tick(FPS)
                load_board()
                load_pieces()
                pygame.draw.rect(screen, BORDER, pygame.Rect(STATS_X, STATS_Y, STATS_WIDTH, STATS_HEIGHT))
                print_text(f'Z - grąžinti dar 1 ėjimą (likę grąžinimai: {undos}).', 28, WHITE, STATS_X + 5, STATS_Y + 24 * 0, center=False)
                print_text('ENTER - Patvirtinti grąžinimus.', 28, WHITE, STATS_X + 5, STATS_Y + 24 * 1, center=False)

                pygame.display.update()
            

class Figure:
    def __init__(self, name, max_health, power, range, movespeed, moves, attacks, value, team, position):
        self.name = name
        self.max_health = max_health
        self.health = max_health
        self.power = power
        self.range = range
        self.movespeed = movespeed
        self.moves = moves
        self.attacks = attacks
        self.value = value

        self.valid_attacks = []
        self.valid_moves = []

        self.team = team
        self.position = position
        self.art = pygame.transform.smoothscale(pygame.image.load(f'Graphics/{self.team} {self.name}.png'), (TILE_SIZE, TILE_SIZE))

        self.action_counter = 1
        self.move_counter = 1

        self.is_attacking = False
        self.is_healing = False
        self.is_moving = False

        self.kills = 0

    def attack(self, destination, player, enemy):
        kills = self.kills
        for attack in self.valid_attacks:
            if attack == tuple(destination):
                player.update_history(enemy)
                self.action_counter -= 1
                attackee = None
                for other_piece in player.figures + enemy.figures:
                    if other_piece.position == destination:
                        attackee = other_piece
                if attackee is not None:
                    attackee.take_damage(self, self.power)
                    if kills == self.kills:
                        attackee.retaliate(self)
                self.is_attacking = False
                self.is_moving = True
                return True
        return False

    def retaliate(self, attacker):
        self.valid_attacks = []
        for attack in self.attacks:
            self.valid_attacks.append(tuple([a + b for a, b in zip(attack, self.position)]))
        for attack in self.valid_attacks:
            if attack == tuple(attacker.position):
                attacker.take_damage(self, self.power)
            
    def take_damage(self, attacker, amount):
        self.health -= amount
        if self.health <= 0:
            self.die(attacker)

    def heal(self, destination, player, enemy):
        if self.action_counter > 0 and destination == self.position:
            player.update_history(enemy)
            self.action_counter -= 1
            if self.max_health > self.health:
                self.health += math.ceil((self.max_health - self.health) * 0.4)
                self.is_healing = False
                self.is_moving = True
                return True
        return False
    
    def move(self, destination, player, enemy):
        for move in self.valid_moves:
            if move == tuple(destination):
                player.update_history(enemy)
                self.move_counter -= 1
                self.position = destination
                self.is_moving = False
                return True
        return False
    
    def die(self, killer):
        position = self.position
        if self in player.figures:
            player.figures.remove(self)
        elif self in enemy.figures:
            enemy.figures.remove(self)
        del self
        if killer is not None:
            killer.kill(position)

    def kill(self, destination):
        self.kills += 1
        self.position = destination
    
    def reset(self):
        self.action_counter = 1
        self.move_counter = 1

    def check(self):
        positions = [tuple(figure.position) for figure in player.figures + enemy.figures]

        self.valid_moves = []
        if self.move_counter > 0 and self.is_moving:
            for direction in self.moves:
                for step in range(1, self.movespeed + 1):
                    move = (self.position[0] + direction[0] * step, self.position[1] + direction[1] * step)
                    if move in positions or move[0] < 0 or move[0] > 7 or move[1] < 0 or move[1] > 7:
                        break
                    self.valid_moves.append(move)

        taunted = False
        self.valid_attacks = []
        if self.action_counter > 0 and self.is_attacking:
            nearby = [(self.position[0] + direction[0], self.position[1] + direction[1]) for direction in [(1, 1), (-1, 1), (1, -1), (-1, -1), (0, 1), (0, -1), (1, 0), (-1, 0)]]
            for figure in player.figures + enemy.figures:
                if figure.__class__.__name__ == "Rook" and tuple(figure.position) in nearby and figure.team != self.team:
                    for direction in self.attacks:
                        attack = (self.position[0] + direction[0], self.position[1] + direction[1])
                        if attack in nearby:
                            taunted = True
                            if tuple(figure.position) == attack and tuple(figure.position) not in self.valid_attacks:
                                self.valid_attacks.append(tuple(figure.position))
                                
            if not taunted:
                for direction in self.attacks:
                    for step in range(1, self.range + 1):
                        attack = (self.position[0] + direction[0] * step, self.position[1] + direction[1] * step)
                        if attack in positions:
                            self.valid_attacks.append(attack)
                            break
                        if attack[0] < 0 or attack[0] > 7 or attack[1] < 0 or attack[1] > 7:
                            break
                        self.valid_attacks.append(attack)

    def interact(self, player, enemy):
        self.is_moving = True

        run = True
        while run:
            timer.tick(FPS)
            load(self)

            if self.action_counter == 0 and self.move_counter == 0:
                return
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if self.is_attacking:
                            if not self.attack(select_tile(event.pos), player, enemy):
                                self.is_attacking = False
                                return

                        elif self.is_healing:
                            if not self.heal(select_tile(event.pos), player, enemy):
                                self.is_healing = False
                                return

                        elif self.is_moving:
                            if not self.move(select_tile(event.pos), player, enemy):
                                self.is_moving = False
                                return

                    elif event.button == 3:
                        if not self.is_moving:
                            self.is_attacking = False
                            self.is_healing = False
                            self.is_moving = True
                        else:
                            return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.is_attacking = True
                        self.is_healing = False
                        self.is_moving = False
                    elif event.key == pygame.K_2:
                        self.is_attacking = False
                        self.is_healing = True
                        self.is_moving = False
                    elif event.key == pygame.K_z:
                        pass
            if check_outcome():
                return
            pygame.display.update()

class Pawn(Figure):
    def __init__(self, name, max_health, power, range, movespeed, moves, attacks, value, team, position):
        super().__init__(name, max_health, power, range, movespeed, moves, attacks, value, team, position)

    def kill(self, destination):
        self.kills += 1
        self.position = destination
        self.max_health += 1
        self.health = self.max_health

class Rook(Figure):
    def __init__(self, name, max_health, power, range, movespeed, moves, attacks, value, team, position):
        super().__init__(name, max_health, power, range, movespeed, moves, attacks, value, team, position)

class Knight(Figure):
    def __init__(self, name, max_health, power, range, movespeed, moves, attacks, value, team, position):
        super().__init__(name, max_health, power, range, movespeed, moves, attacks, value, team, position)

    def kill(self, destination):
        self.kills += 1
        self.position = destination
        self.action_counter += 1
        self.move_counter += 1 

class Bishop(Figure):
    def __init__(self, name, max_health, power, range, movespeed, moves, attacks, value, team, position):
        super().__init__(name, max_health, power, range, movespeed, moves, attacks, value, team, position)

    def attack(self, destination, player, enemy):
        kills = self.kills
        for attack in self.valid_attacks:
            if attack == destination:
                player.update_history(enemy)
                self.action_counter -= 1
                left_attackee = None
                right_attackee = None
                attackee = None
                for figure in player.figures + enemy.figures:
                    if (destination[0] > self.position[0] and destination[1] > self.position[1] or 
                        destination[0] < self.position[0] and destination[1] < self.position[1]):
                        if figure.position == (destination[0] - 1, destination[1] + 1):
                            left_attackee = figure
                        elif figure.position == (destination[0] + 1, destination[1] - 1):
                            right_attackee = figure
                    elif (destination[0] > self.position[0] and destination[1] < self.position[1] or 
                        destination[0] < self.position[0] and destination[1] > self.position[1]):
                        if figure.position == (destination[0] - 1, destination[1] - 1):
                            left_attackee = figure
                        elif figure.position == (destination[0] + 1, destination[1] + 1):
                            right_attackee = figure
                    if figure.position == destination:
                        attackee = figure
                    
                
                back = (math.copysign(1, self.position[0] - destination[0]), math.copysign(1, self.position[1] - destination[1]))
                self.push(self, back)

                away = (math.copysign(1, destination[0] - self.position[0]), math.copysign(1, destination[1] - self.position[1]))

                if attackee is not None:
                    attackee.take_damage(self, self.power)
                    self.push(attackee, away)
                    if kills == self.kills:
                        attackee.retaliate(self)

                if left_attackee is not None:
                    left_attackee.take_damage(self, self.power)
                    self.push(left_attackee, away)
                    if kills == self.kills:
                        left_attackee.retaliate(self)

                if right_attackee is not None:
                    right_attackee.take_damage(self, self.power)
                    self.push(right_attackee, away)
                    if kills == self.kills:
                        right_attackee.retaliate(self)
                self.is_attacking = False
                self.is_moving = True
                return True
        return False

    def retaliate(self, attacker):
        self.valid_attacks = []
        retaliate = False
        for attack in self.attacks:
            self.valid_attacks.append(tuple([a + b for a, b in zip(attack, self.position)]))
        for attack in self.valid_attacks:
            if attack == tuple(attacker.position):
                retaliate = True
        
        if retaliate:
            for figure in player.figures + enemy.figures:
                left_attacker = None
                right_attacker = None
                if (attacker.position[0] > self.position[0] and attacker.position[1] > self.position[1] or 
                    attacker.position[0] < self.position[0] and attacker.position[1] < self.position[1]):
                    if figure.position == (attacker.position[0] - 1, attacker.position[1] + 1):
                        left_attacker = figure
                    elif figure.position == (attacker.position[0] + 1, attacker.position[1] - 1):
                        right_attacker = figure
                elif (attacker.position[0] > self.position[0] and attacker.position[1] < self.position[1] or 
                    attacker.position[0] < self.position[0] and attacker.position[1] > self.position[1]):
                    if figure.position == (attacker.position[0] - 1, attacker.position[1] - 1):
                        left_attacker = figure
                    elif figure.position == [attacker.position[0] + 1, attacker.position[1] + 1]:
                        right_attacker = figure
                if figure.position == attacker.position:
                    attacker = figure
                        
            back = (math.copysign(1, self.position[0] - attacker.position[0]), math.copysign(1, self.position[1] - attacker.position[1]))
            self.push(self, back)

            away = (math.copysign(1, attacker.position[0] - self.position[0]), math.copysign(1, attacker.position[1] - self.position[1]))

            if attacker is not None:
                attacker.take_damage(self, self.power)
                self.push(attacker, away)

            if left_attacker is not None:
                left_attacker.take_damage(self, self.power)
                self.push(left_attacker, away)

            if right_attacker is not None:
                right_attacker.take_damage(self, self.power)
                self.push(right_attacker, away)

    def push(self, pushee, direction):
        destination = tuple([a + b for a, b in zip(direction, pushee.position)])
        if destination[0] > 7 or destination[1] > 7 or destination[0] < 0 or destination[1] < 0:
            return
        for figure in player.figures + enemy.figures:
            if destination == tuple(figure.position):
                figure.take_damage(None, 1)
                pushee.take_damage(None, 1)
                return
        pushee.position = tuple(destination)

    def check(self):
        positions = [tuple(figure.position) for figure in player.figures + enemy.figures]

        self.valid_moves = []
        if self.move_counter > 0 and self.is_moving:
            for direction in self.moves:
                for step in range(1, self.movespeed + 1):
                    move = (self.position[0] + direction[0] * step, self.position[1] + direction[1] * step)
                    if move in positions or move[0] < 0 or move[0] > 7 or move[1] < 0 or move[1] > 7:
                        break
                    self.valid_moves.append(move)

        taunted = False
        self.valid_attacks = []
        if self.action_counter > 0 and self.is_attacking:
            nearby = [(self.position[0] + direction[0], self.position[1] + direction[1]) for direction in [(1, 1), (-1, 1), (1, -1), (-1, -1), (0, 1), (0, -1), (1, 0), (-1, 0)]]
            for figure in player.figures + enemy.figures:
                if figure.__class__.__name__ == "Rook" and tuple(figure.position) in nearby and figure.team != self.team:
                    for direction in self.attacks:
                        attack = (self.position[0] + direction[0], self.position[1] + direction[1])
                        if attack in nearby:
                            taunted = True
                            if tuple(figure.position) == attack and tuple(figure.position) not in self.valid_attacks:
                                self.valid_attacks.append(tuple(figure.position))
                            

            if not taunted:
                if self.action_counter > 0 and self.is_attacking:
                    for direction in self.attacks:
                        for step in range(1, self.range + 1):
                            attack = (self.position[0] + direction[0] * step, self.position[1] + direction[1] * step)
                            if attack[0] < 0 or attack[0] > 7 or attack[1] < 0 or attack[1] > 7:
                                break
                            self.valid_attacks.append(attack)

    def kill(self, destination):
        self.kills += 1 

class Queen(Figure):
    def __init__(self, name, max_health, power, range, movespeed, moves, attacks, value, team, position):
        super().__init__(name, max_health, power, range, movespeed, moves, attacks, value, team, position)

    def attack(self, destination, player, enemy):
        kills = self.kills
        for attack in self.valid_attacks:
            if attack == tuple(destination):
                player.update_history(enemy)
                self.action_counter -= 1
                attackee = None
                for other_piece in player.figures + enemy.figures:
                    if other_piece.position == destination:
                        attackee = other_piece
                if attackee is not None:
                    attackee.take_damage(self, self.power)
                    if kills == self.kills:
                        direction = [0, 0]
                        if self.position[0] == destination[0]:
                            direction[0] = 0
                        else:
                            direction[0] = math.copysign(1, self.position[0] -  destination[0])
                        if self.position[1] == destination[1]:
                            direction[1] = 0
                        else:
                            direction[1] = math.copysign(1, self.position[1] -  destination[1])
                        self.position = tuple([int(a + b) for a, b in zip(attackee.position, tuple(direction))])
                        attackee.retaliate(self)
                else:
                    self.position = destination
                self.is_attacking = False
                self.is_moving = True
                return True
        return False

class King(Figure):
    def __init__(self, name, max_health, power, range, movespeed, moves, attacks, value, team, position):
        super().__init__(name, max_health, power, range, movespeed, moves, attacks, value, team, position)

    def die(self, killer):
        position = self.position
        if self in player.figures:
            player.figures.remove(self)
        elif self in enemy.figures:
            enemy.figures.remove(self)
        if self.team == 'Black':
            player.win = True
        del self
        if killer is not None:
            killer.kill(position)

def select_tile(mouse_pos):
    selected_tile = (-1, -1)
    for row in range(8):
        for column in range(8):
            tile_rect = pygame.Rect(BOARD_X + TILE_SIZE * row, BOARD_Y + TILE_SIZE * column, TILE_SIZE, TILE_SIZE)
            if tile_rect.collidepoint(mouse_pos):
                selected_tile = (row, column)
    
    return selected_tile

def check_outcome():
    if 'King' not in [figure.__class__.__name__ for figure in player.figures] or 'King' not in [figure.__class__.__name__ for figure in enemy.figures]:
        return True



# VIZUALIZACIJOS FUNKCIJOS

def print_text(text, size, color, x, y, alpha=255, center=True):
    font = pygame.font.Font(None, size)
    line = font.render(text, True, color)
    line.set_alpha(alpha)
    if center:
        rect = line.get_rect()
        rect.center = (x, y)
    else:
        rect = (x, y)
    screen.blit(line, rect)

def load_board():
    screen.fill(BACKGROUND)
    pygame.draw.rect(screen, BORDER, (BORDER_X, BORDER_Y, BORDER_SIZE, BORDER_SIZE))
    pygame.draw.rect(screen, BLACK_TILE, (BOARD_X, BOARD_Y, BOARD_SIZE, BOARD_SIZE))
    for row in range(8):
        for column in range(8):
            if (row % 2 == 1 and column % 2 == 1) or (row % 2 == 0 and column % 2 == 0):
                pygame.draw.rect(screen, WHITE_TILE, (BOARD_X + TILE_SIZE * row, BOARD_Y + TILE_SIZE * column, TILE_SIZE, TILE_SIZE))
    
    for row in range(8):
        print_text(f'{chr(97 + row)}', 28, LIGHT_GRAY, BORDER_X + BORDER_STRENGTH + TILE_SIZE / 2 + TILE_SIZE * row, BORDER_Y + BORDER_SIZE - BORDER_STRENGTH / 2)

    for column in range(8):
        print_text(f'{column + 1}', 28, LIGHT_GRAY, BORDER_X + BORDER_STRENGTH / 2, BORDER_Y + BORDER_STRENGTH + TILE_SIZE / 2 + TILE_SIZE * column)

def load_moves(figure):
    if figure is not None:
        figure.check()
        for move in figure.valid_moves:
            for row in range(8):
                for column in range(8):
                    if move == (row, column) and figure.is_moving:
                        dot = pygame.Surface((DOT_SIZE*2, DOT_SIZE*2), pygame.SRCALPHA)
                        pygame.draw.circle(dot, DARK_GRAY + (128,), (DOT_SIZE, DOT_SIZE), DOT_SIZE)
                        screen.blit(dot, (BOARD_X + TILE_SIZE * row + TILE_SIZE // 2 - DOT_SIZE, BOARD_Y + TILE_SIZE * column + TILE_SIZE // 2 - DOT_SIZE))

def load_attacks(figure):
    if figure is not None:
        for attack in figure.valid_attacks:
            for row in range(8):
                for column in range(8):
                    if attack == (row, column) and figure.is_attacking:
                        print_text(f'{figure.power}', 72, RED, BOARD_X + TILE_SIZE * row + TILE_SIZE / 2, BOARD_Y + TILE_SIZE * column + TILE_SIZE / 2, 200)

def load_heal(figure):
    if figure is not None:
        for row in range(8):
            for column in range(8):
                if figure.position == (row, column) and figure.is_healing:
                    if figure.health < figure.max_health:
                        print_text(f'{math.ceil((figure.max_health - figure.health) * 0.4)}', 72, GREEN, BOARD_X + TILE_SIZE * row + TILE_SIZE / 2, BOARD_Y + TILE_SIZE * column + TILE_SIZE / 2, 200)
                    else:
                        print_text('0', 72, GREEN, BOARD_X + TILE_SIZE * row + TILE_SIZE / 2, BOARD_Y + TILE_SIZE * column + TILE_SIZE / 2, 200)

def load_pieces():
    for figure in player.figures + enemy.figures:
        screen.blit(figure.art, (BOARD_X + TILE_SIZE * figure.position[0], BOARD_Y + TILE_SIZE * figure.position[1]))

def load_health(figure):
    if figure is not None:
        x = BOARD_X + TILE_SIZE * figure.position[0] + 10
        y = BOARD_Y + TILE_SIZE * figure.position[1] - 15

        pygame.draw.rect(screen, BLACK, pygame.Rect(x, y, HEALTH_WIDTH, HEALTH_HEIGHT))

        if figure.health / figure.max_health > 0.5:
            pygame.draw.rect(screen, GREEN, pygame.Rect(x + 2, y + 2, figure.health / figure.max_health * (HEALTH_WIDTH - 4), HEALTH_HEIGHT - 4))
        else:
            pygame.draw.rect(screen, RED, pygame.Rect(x + 2, y + 2, figure.health / figure.max_health * (HEALTH_WIDTH - 4), HEALTH_HEIGHT - 4))

        for health_point in range(figure.max_health):
            bar_x = x + health_point * (HEALTH_WIDTH - 4) / (figure.max_health)
            pygame.draw.line(screen, BLACK, (bar_x, y + 2), (bar_x, y + HEALTH_HEIGHT - 2), 2)
 
def load_stats(figure):
    load_health(figure)

    pygame.draw.rect(screen, BORDER, pygame.Rect(STATS_X, STATS_Y, STATS_WIDTH, STATS_HEIGHT))
    if figure is not None:
        if figure.__class__.__name__ == 'Pawn':
            print_text('Pėstininkas nužudęs figūrėlę gauną papildomą gyvybę ir pilnai pasigydo.', 28, WHITE, STATS_X + 5, STATS_Y + 5, center=False)
        elif figure.__class__.__name__ == 'Rook':
            print_text('Artimos priešo figūrėlės privalo pulti bokštą.', 28, WHITE, STATS_X + 5, STATS_Y + 5, center=False)
        elif figure.__class__.__name__ == 'Knight':
            print_text('Žirgas nužudęs figūrėlę gali dar kartą judėti ir dar kart1 atlikti veiksmą.', 28, WHITE, STATS_X + 5, STATS_Y + 5, center=False)
        elif figure.__class__.__name__ == 'Bishop':
            print_text('Rikis vienu metu puola 3 langelius.', 28, WHITE, STATS_X + 5, STATS_Y + 5, center=False)
            print_text('Puolimo metu priešus nustumia nuo savęs, o save nuo priešo.', 28, WHITE, STATS_X + 5, STATS_Y + 24, center=False)
        elif figure.__class__.__name__ == 'Queen':
            print_text('Po puolimo karalienė atsistoja šalia pultos figūros.', 28, WHITE, STATS_X + 5, STATS_Y + 5, center=False)
            print_text('Gali naudoti savo puolimą kaip judėjimą.', 28, WHITE, STATS_X + 5, STATS_Y + 24, center=False)
        elif figure.__class__.__name__ == 'King':
            print_text('Kai karalius miršta žaidėjas pralaimi žaidimą.', 28, WHITE, STATS_X + 5, STATS_Y + 5, center=False)
    else:
        print_text('MB1 - Judinti pasirinktą figūrą (1 - Pulti, 2 - Gydyti)', 28, WHITE, STATS_X + 5, STATS_Y + 5 + 24 * 0, center=False)
        print_text('Z - Grąžinti lentą iki 5 judesių atgal (galima naudoti tik kartą)', 28, WHITE, STATS_X + 5, STATS_Y + 5 + 24 * 1, center=False)
        print_text('ENTER - Baigti ėjimą', 28, WHITE, STATS_X + 5, STATS_Y + 5 + 24 * 2, center=False)

def load(selected):
    load_board()
    load_moves(selected)
    load_pieces()
    for figure in player.figures + enemy.figures:
        if figure.health < figure.max_health:
            load_health(figure)
    load_stats(selected)

    load_attacks(selected)
    load_heal(selected)
    pygame.display.update()
    timer.tick(FPS)


def generate_unit_position(units, x0=0, x1=8, y0=0, y1=8):
    positions = [(x, y) for x in range(x0, x1) for y in range(y0, y1)]
    occupied = {figure.position for figure in units}
    vacant = [position for position in positions if position not in occupied]
    position = random.choice(vacant)
    return position

def generate_enemy():
    enemy.figures = [King(king.name, king.max_health, king.power, king.range, king.movespeed, king.moves, king.attacks, king.value, 'Black', generate_unit_position(enemy.figures, y1=3))]
    while sum(figure.value for figure in enemy.figures) < 38 and len(enemy.figures) < 24:
        options = [Queen(queen.name, queen.max_health, queen.power, queen.range, queen.movespeed, queen.moves, queen.attacks, queen.value, 'Black', generate_unit_position(enemy.figures, y1=3)), 
                   Rook(rook.name, rook.max_health, rook.power, rook.range, rook.movespeed, rook.moves, rook.attacks, rook.value, 'Black', generate_unit_position(enemy.figures, y1=3)), 
                   Bishop(bishop.name, bishop.max_health, bishop.power, bishop.range, bishop.movespeed, bishop.moves, bishop.attacks, bishop.value, 'Black', generate_unit_position(enemy.figures, y1=3)), 
                   Knight(knight.name, knight.max_health, knight.power, knight.range, knight.movespeed, knight.moves, knight.attacks, knight.value, 'Black', generate_unit_position(enemy.figures, y1=3)), 
                   Pawn(pawn.name, pawn.max_health, pawn.power, pawn.range, pawn.movespeed, pawn.moves, pawn.attacks, pawn.value, 'Black', generate_unit_position(enemy.figures, y1=3))]
        figure = random.choice(options)
        if sum(figure.value for figure in enemy.figures) + figure.value <= 38:
            enemy.figures.append(figure)




# ŽAIDIMON FAZĖS
def home_loop():
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:  
                return
        
        pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, HEIGHT))
        print_text('RAPOLO ŽAIDIMAS #3', 98, WHITE, WIDTH / 2, HEIGHT / 2)
        print_text('Spustelkite bet kurį klavišą, kad pradėti', 36, GRAY, WIDTH / 2, HEIGHT / 3 * 2)
        pygame.display.update()
        timer.tick(FPS)

def select_loop():
    player.figures.append(King(king.name, king.max_health, king.power, king.range, king.movespeed, king.moves, king.attacks, king.value, 'White', generate_unit_position(player.figures, y0=5, y1=8)))
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return
                elif event.key == pygame.K_k and available_points - 9 >= 0:
                    tile = select_tile(pygame.mouse.get_pos())
                    if tile not in [figure.position for figure in player.figures] and tile[1] > 4:
                        player.figures.append(Queen(queen.name, queen.max_health, queen.power, queen.range, queen.movespeed, queen.moves, queen.attacks, queen.value, 'White', tile))
                elif event.key == pygame.K_b and available_points - 4 >= 0:
                    tile = select_tile(pygame.mouse.get_pos())
                    if tile not in [figure.position for figure in player.figures] and tile[1] > 4:
                        player.figures.append(Rook(rook.name, rook.max_health, rook.power, rook.range, rook.movespeed, rook.moves, rook.attacks, rook.value, 'White', tile))
                elif event.key == pygame.K_r and available_points - 3 >= 0:
                    tile = select_tile(pygame.mouse.get_pos())
                    if tile not in [figure.position for figure in player.figures] and tile[1] > 4:
                        player.figures.append(Bishop(bishop.name, bishop.max_health, bishop.power, bishop.range, bishop.movespeed, bishop.moves, bishop.attacks, bishop.value, 'White', tile))
                elif event.key == pygame.K_z and available_points - 3 >= 0:
                    tile = select_tile(pygame.mouse.get_pos())
                    if tile not in [figure.position for figure in player.figures] and tile[1] > 4:
                        player.figures.append(Knight(knight.name, knight.max_health, knight.power, knight.range, knight.movespeed, knight.moves, knight.attacks, knight.value, 'White', tile))
                elif event.key == pygame.K_p and available_points - 1 >= 0:
                    tile = select_tile(pygame.mouse.get_pos())
                    if tile not in [figure.position for figure in player.figures] and tile[1] > 4:
                        player.figures.append(Pawn(pawn.name, pawn.max_health, pawn.power, pawn.range, pawn.movespeed, pawn.moves, pawn.attacks, pawn.value, 'White', tile))
            elif event.type == pygame.MOUSEBUTTONDOWN:  
                if event.button == 1:
                    for figure in player.figures:
                        if select_tile(event.pos) == figure.position:
                            figure.die(None)

            
        load_board()
        zones = pygame.Surface((BOARD_SIZE, BOARD_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(zones, RED+(84,), (0, 0, BOARD_SIZE, BOARD_SIZE / 8 * 5))
        pygame.draw.rect(zones, GREEN+(84,), (0, BOARD_SIZE / 8 * 5, BOARD_SIZE, BOARD_SIZE  / 8 * 3))
        screen.blit(zones, (BOARD_X, BOARD_Y))
        
        load_pieces()
        pygame.draw.rect(screen, BORDER, pygame.Rect(STATS_X, STATS_Y, STATS_WIDTH, STATS_HEIGHT))
        print_text('K - Karalienė (9 taškai)', 28, WHITE, STATS_X + 5, STATS_Y + 5 + 24 * 0, center=False)
        print_text('B - Bokštas (4 taškai)', 28, WHITE, STATS_X + 5, STATS_Y + 5 + 24 * 1, center=False)
        print_text('R - Rikis (3 taškai)', 28, WHITE, STATS_X + 5, STATS_Y + 5 + 24 * 2, center=False)
        print_text('Z - Žirgas (3 taškai)', 28, WHITE, STATS_X + 5, STATS_Y + 5 + 24 * 3, center=False)
        print_text('P - Pėstininkas (1 taškas)', 28, WHITE, STATS_X + 5, STATS_Y + 5 + 24 * 4, center=False)
        print_text('MB1 - Pašalinti figūrėlę (+ taškai)', 28, WHITE, STATS_X + 5, STATS_Y + 5 + 24 * 5, center=False)
        print_text('ENTER - Patvirtinti kariauną', 28, WHITE, STATS_X + 5, STATS_Y + 5 + 24 * 6, center=False)

        available_points = 38 - sum(figure.value for figure in player.figures)
        print_text(f'{available_points}', 96, WHITE, STATS_X + BORDER_STRENGTH + TILE_SIZE * 6 + TILE_SIZE / 2, STATS_Y + BORDER_STRENGTH + TILE_SIZE / 2)


        pygame.display.update()
        timer.tick(FPS)

def gameplay_loop():
    while True:
        if player.turn:
            player.take_turn(enemy)
            
        elif enemy.turn:
            enemy.take_random_turn(player)

        if check_outcome():
            return

def end_loop():
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:  
                return
        load_board()
        load_pieces()
        shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(shade, BLACK + (200,), (0, 0, WIDTH, HEIGHT))
        screen.blit(shade, (0, 0))
        if player.win:
            print_text('PERGALĖ!', 98, WHITE, WIDTH / 2, HEIGHT / 2)
        else:
            print_text('MILKA, KINDER...', 98, WHITE, WIDTH / 2, HEIGHT / 2)
        print_text('Spustelkite bet kurį klavišą, kad grįžti į pradžią', 36, LIGHT_GRAY, WIDTH / 2, HEIGHT / 3 * 2)
        
        pygame.display.update()
        timer.tick(FPS)

with open('figure_info.json') as info:
    data = json.load(info)

for figure in data['figures']:
    if figure['name'] == 'Pawn':
        pawn = Pawn(figure['name'], figure['max_health'], figure['power'], figure['range'], figure['movespeed'], figure['moves'], figure['attacks'], figure['value'], 'White', (-1, -1))
    elif figure['name'] == 'Rook':
        rook = Rook(figure['name'], figure['max_health'], figure['power'], figure['range'], figure['movespeed'], figure['moves'], figure['attacks'], figure['value'], 'White', (-1, -1))
    elif figure['name'] == 'Knight':
        knight = Knight(figure['name'], figure['max_health'], figure['power'], figure['range'], figure['movespeed'], figure['moves'], figure['attacks'], figure['value'], 'White', (-1, -1))
    elif figure['name'] == 'Bishop':
        bishop = Bishop(figure['name'], figure['max_health'], figure['power'], figure['range'], figure['movespeed'], figure['moves'], figure['attacks'], figure['value'], 'White', (-1, -1))
    elif figure['name'] == 'Queen':
        queen = Queen(figure['name'], figure['max_health'], figure['power'], figure['range'], figure['movespeed'], figure['moves'], figure['attacks'], figure['value'], 'White', (-1, -1))
    elif figure['name'] == 'King':
        king = King(figure['name'], figure['max_health'], figure['power'], figure['range'], figure['movespeed'], figure['moves'], figure['attacks'], figure['value'], 'White', (-1, -1))

while True:
    player = Player('White', True)
    enemy = Player('Black', False)

    home_loop()
    select_loop()
    generate_enemy()
    gameplay_loop()
    end_loop()