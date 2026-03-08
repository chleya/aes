"""
AES v1.2 - 平衡版
"""

import random


class Agent:
    def __init__(s, x, y):
        s.x, s.y = x, y
        s.e = 40
        s.predictor_w = [[random.random()*0.2-0.1 for _ in range(9)] for _ in range(4)]
        s.actor_w = [[random.random()*0.2-0.1 for _ in range(9)] for _ in range(4)]
    
    def act(s, view):
        scores = [sum(v*w for v,w in zip(view,row)) for row in s.actor_w]
        moves = [(0,-1),(0,1),(-1,0),(1,0)]
        return moves[scores.index(max(scores))]
    
    def step(s, food):
        view = []
        for dy in [-1,0,1]:
            for dx in [-1,0,1]:
                view.append(1 if ((s.x+dx)%10,(s.y+dy)%10) in food else 0)
        
        dx, dy = s.act(view)
        nx, ny = (s.x+dx)%10, (s.y+dy)%10
        
        if (nx, ny) in food:
            s.e += 15
            food.remove((nx, ny))
        
        s.x, s.y = nx, ny
        s.e -= 1


def run(steps=1000):
    print("AES v1.2 - Balanced")
    print("="*40)
    
    food = [(random.randint(0,9),random.randint(0,9)) for _ in range(6)]
    agents = [Agent(random.randint(0,9),random.randint(0,9)) for _ in range(10)]
    
    for st in range(steps):
        while len(food) < 6:
            food.append((random.randint(0,9),random.randint(0,9)))
        
        for a in agents:
            a.step(food)
            if a.e >= 60:
                child = Agent(a.x, a.y)
                child.e = a.e // 2
                a.e = a.e // 2
                agents.append(child)
        
        agents = [a for a in agents if a.e > 0]
        while len(agents) < 3:
            agents.append(Agent(random.randint(0,9),random.randint(0,9)))
        
        if st % 200 == 0:
            print(f"Step {st}: Agents={len(agents)}")

    print(f"\nFinal: {len(agents)} agents")


if __name__ == "__main__":
    run()
