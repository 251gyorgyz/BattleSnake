import random
import typing
import copy
import torch
import numpy as np
from collections import deque

def info() -> typing.Dict:
    print("INFO")

    return {
        "apiversion": "1",
        "author": "Zalan",
        "color": "#f5f00d",
        "head": "fang",
        "tail": "small-rattle",
    }
def start(game_state: typing.Dict):
    print("GAME START")
def end(game_state: typing.Dict):
    print("GAME OVER\n")



max_self_iterations = 3
path = [["right","right","right","right","right","right","right","right","right","right","down"],
        ["up","down","left","left","left","left","left","left","left","left","left"],
        ["up","right","right","right","right","right","right","right","right","right","down"],
        ["up","down","left","left","left","left","left","left","left","left","left"],
        ["up","right","right","right","right","right","right","right","right","right","down"],
        ["up","down","left","left","left","left","left","left","left","left","left"],
        ["up","right","right","right","right","right","right","right","right","right","down"],
        ["up","down","left","left","left","left","left","left","left","left","left"],
        ["up","right","right","right","right","right","right","right","right","right","down"],
        ["up","left","down","left","down","left","down","left","down","left","down"],
        ["up","up","left","up","left","up","left","up","left","up","left"]]
def move(game_state: typing.Dict) -> typing.Dict:
    moves = {"up":0, "down":0, "left":0, "right":0}
    board_width = game_state['board']['width']
    board_height = game_state['board']['height']
    
    # longest survival alone
    #if len(game_state['board']['snakes']) == 1:
        #return {"move":path[10-game_state["you"]["head"]["y"]][game_state["you"]["head"]["x"]]}

    # evaluate each move
    for move in moves:
        moves[move] = evaluate_move(game_state, game_state["you"], move, 0, max_self_iterations)

    # choose best move
    best = "down"
    for move in moves:
        if moves[move] > moves[best]:
            best = move
    
    #print(f"MOVE {game_state['turn']}:{best}, Score: " + str(moves[best]))
    #print(str(game_state['turn']), moves)
    return {"move": best}

def evaluate_move(game_state, snake, move, iteration, max_iterations):
    score = 1
    current_head = game_state["you"]["head"]
    next_state = next(game_state, move)
    next_head = next_state["you"]["head"]
    board_width = game_state["board"]["width"]
    board_height = game_state["board"]["height"]
    length = len(next_state["you"]["body"])

    # check collisions
    if next_head["x"] >= board_width or next_head["x"] < 0 or next_head["y"] >= board_height or next_head["y"] < 0:
        return -100
    for enemy in game_state["board"]["snakes"]:
        if next_head in enemy["body"]:
            return -100
        
    # head to head
    for enemy in game_state["board"]["snakes"]:
        head_dist = dist(next_head, enemy["head"])
        if head_dist < 3 and length <= enemy["length"] and head_dist < dist(current_head, enemy["head"]):
            score -= 10
        """
        if head_dist < dist(current_head, enemy["head"]) and length > enemy["length"]:
            score += 3
        elif head_dist < dist(current_head, enemy["head"]) and length <= enemy["length"]:
            score -= 5
        """
    
    
    # reward eating food
    if next_head in next_state["board"]["food"]:
        if next_state["you"]["length"] < 50:
            score += 5
        if next_state["you"]["health"] < 20:
            score += 10
        if next_state["you"]["health"] > 20:
            #score -= .5
            pass
    

    # go for food
    closest_food = find_food(next_state)
    if dist(closest_food, next_head) < dist(closest_food, current_head):
        score += 5 / (iteration + 1)
    else:
        score -= 1 / (iteration + 1)
    
    
    """
    # count amount of obstacles in head's direction
    vision_dist = 4
    if move == "up":    
        start_x, end_x, start_y, end_y = max(next_head["x"] - vision_dist, 0), min(next_head["x"] + vision_dist, board_width), next_head["y"], board_height
    elif move == "down":    
        start_x, end_x, start_y, end_y = max(next_head["x"] - vision_dist, 0), min(next_head["x"] + vision_dist, board_width), 0, next_head["y"] + 1
    elif move == "left":    
        start_x, end_x, start_y, end_y = 0, next_head["x"] + 1, max(next_head["y"] - vision_dist, 0), min(next_head["y"] + vision_dist, board_height)
    else:    
        start_x, end_x, start_y, end_y = next_head["x"], board_width, max(next_head["y"] - vision_dist, 0), min(next_head["y"] + vision_dist, board_height)
    enemy_ahead = 0
    for enemy in next_state["board"]["snakes"]:
        for i in range(start_x, end_x):
            for j in range(start_y, end_y):
                if {"x":i, "y":j} in enemy["body"] and {"x":i, "y":j} != next_head:
                    enemy_ahead += 10 / dist({"x":i, "y":j}, next_head)
    score -= enemy_ahead / next_state["you"]["length"]
    """

    # count open spaces
    score += dumb_fill(next_state, next_head) / 2

    # recursion
    if iteration < max_iterations:
        next_moves = dict()
        for next_move in ("up", "down", "left", "right"):
            next_moves[next_move] = evaluate_move(next_state, snake, next_move, iteration + 1, max_iterations)
        for next_move in list(next_moves.keys()):
            if next_moves[next_move] == -100:
                del next_moves[next_move]
        if len(next_moves) == 0:
            return -100
        else:
            for next_score in next_moves.values():
                score += next_score / len(next_moves)
    return score

def next(game_state, move):
    # update head position
    next_head = copy.deepcopy(game_state["you"]["head"])
    if move == "left":
        next_head["x"] -= 1
    elif move == "right":
        next_head["x"] += 1
    elif move == "down":
        next_head["y"] -= 1
    else:
        next_head["y"] += 1
    new_state = copy.deepcopy(game_state)
    new_state["you"]["head"] = next_head
    new_state["you"]["body"].insert(0, next_head)
    foods = game_state["board"]["food"]
    if {"x":next_head["x"], "y":next_head["y"]} not in foods:
        del new_state["you"]["body"][-1]
    return new_state

def find_food(game_state):
    food = game_state["board"]["food"]
    enemy_closests = {}

    # find closest food for enemy
    for enemy in game_state["board"]["snakes"]:
        head = enemy["head"]
        closest = {"x" : 100, "y" : 100}
        for apple in food:
            if dist(head, apple) < dist(head, closest):
                closest = apple
        if enemy != game_state["you"]:
            enemy_closests.update({dist(head, closest):closest})

    # find closest food that isn't closer to enemy
    head = game_state["you"]["head"]
    closest = {"x" : 100, "y" : 100}
    for apple in food:
        good = True
        if dist(head, apple) < dist(head, closest):
            for d in enemy_closests:
                if enemy_closests[d] == closest and d <= dist(head, apple):
                    good = False
            if good:
                closest = apple
    return closest

def dist(pos_1, pos_2):
    return ((pos_1["x"] - pos_2["x"]) ** 2 + (pos_1["y"] - pos_2["y"]) ** 2) ** .5

def dumb_fill(game_state, head):
    moves = 0
    blocked = []
    for enemy in game_state["board"]["snakes"]:
        for i in range(len(enemy["body"])):
            blocked.append(enemy["body"][i])
    if head in blocked:
        blocked.remove(head)
    for i in range(head["x"], 0, -1):
        if {"x":i, "y":head["y"]} in blocked:
            break
        else:
            moves += 1
    for i in range(head["x"], game_state["board"]["width"]):
        if {"x":i, "y":head["y"]} in blocked:
            break
        else:
            moves += 1
    for i in range(head["y"], 0, -1):
        if {"x":head["x"], "y":i} in blocked:
            break
        else:
            moves += 1
    for i in range(head["y"], game_state["board"]["height"]):
        if {"x":head["x"], "y":i} in blocked:
            break
        else:
            moves += 1
    #print(moves)
    return moves

# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server
    #train()
    run_server({"info": info, "start": start, "move": move, "end": end})