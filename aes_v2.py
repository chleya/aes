"""
AES v2.0 - 黄金参数版
"""

import random


class Agent:
    def __init__(s, x, y):
        s.x, s.y = x, y
        s.e = 30
        s.w = [[random.random()*0.3-0.15 for _ in range(9)] for _ in range(4)]
    
    def act(s, view):
        scores = [sum(v*w for v,w in zip(view,row)) for row in s.w]
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
            s.e += 20
            food.remove((nx, ny))
        
        s.x, s.y = nx, ny
        s.e -= 0.5


def run(steps=1000):
    print("AES v2.0 - Golden Params")
    print("="*40)
    
    food = [(random.randint(0,9),random.randint(0,9)) for _ in range(8)]
    agents = [Agent(random.randint(0,9),random.randint(0,9)) for _ in range(10)]
    
    history = []
    
    for st in range(steps):
        while len(food) < 8:
            food.append((random.randint(0,9),random.randint(0,9)))
        
        for a in agents:
            a.step(food)
            if a.e >= 50:
                child = Agent(a.x, a.y)
                child.e = a.e // 2
                a.e = a.e // 2
                agents.append(child)
        
        agents = [a for a in agents if a.e > 0]
        while len(agents) < 5:
            agents.append(Agent(random.randint(0,9),random.randint(0,9)))
        
        if st % 100 == 0:
            n = len(agents)
            avg_e = sum(a.e for a in agents) / max(1, n)
            history.append((st, n, avg_e))
            print(f"Step {st}: Agents={n}, AvgE={avg_e:.1f}")

    print(f"\nFinal: {len(agents)} agents")
    return history


if __name__ == "__main__":
    run()
