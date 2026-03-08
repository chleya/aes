"""
AES v1.0 - Agent Team 简化版
"""

import random


class Agent:
    def __init__(s, x, y):
        s.x, s.y = x, y
        s.e = 30
        s.predictor_w = [[random.random()*0.2-0.1 for _ in range(9)] for _ in range(4)]
        s.actor_w = [[random.random()*0.2-0.1 for _ in range(9)] for _ in range(4)]
    
    def predict(s, view):
        return [sum(v*w for v,w in zip(view,row)) for row in s.predictor_w]
    
    def act(s, view):
        scores = [sum(v*w for v,w in zip(view,row)) for row in s.actor_w]
        moves = [(0,-1),(0,1),(-1,0),(1,0)]
        return moves[scores.index(max(scores))]
    
    def step(s, food):
        # 预测
        view = []
        for dy in [-1,0,1]:
            for dx in [-1,0,1]:
                view.append(1 if ((s.x+dx)%10,(s.y+dy)%10) in food else 0)
        
        # 行动
        dx, dy = s.act(view)
        nx, ny = (s.x+dx)%10, (s.y+dy)%10
        
        # 吃
        if (nx, ny) in food:
            s.e += 20
            food.remove((nx, ny))
        
        s.x, s.y = nx, ny
        s.e -= 1
        
        return None


def run(steps=500):
    print("AES v1.0 - Agent Team")
    food = [(random.randint(0,9),random.randint(0,9)) for _ in range(5)]
    agents = [Agent(random.randint(0,9),random.randint(0,9)) for _ in range(10)]
    
    for st in range(steps):
        while len(food) < 5:
            food.append((random.randint(0,9),random.randint(0,9)))
        
        for a in agents:
            child = a.step(food)
            if child and a.e >= 50:
                child.e = a.e // 2
                a.e = a.e // 2
                agents.append(child)
        
        agents = [a for a in agents if a.e > 0]
        while len(agents) < 3:
            agents.append(Agent(0,0))
        
        if st % 100 == 0:
            print(f"Step {st}: Agents={len(agents)}, AvgE={sum(a.e for a in agents)/len(agents):.1f}")

    print(f"Final: {len(agents)} agents")


if __name__ == "__main__":
    run()
