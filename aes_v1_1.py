"""
AES v1.1 - 能量优化版
目标: 长时间稳定运行
"""

import random


class Agent:
    def __init__(s, x, y):
        s.x, s.y = x, y
        s.e = 50  # 更高初始能量
        s.predictor_w = [[random.random()*0.2-0.1 for _ in range(9)] for _ in range(4)]
        s.actor_w = [[random.random()*0.2-0.1 for _ in range(9)] for _ in range(4)]
    
    def predict(s, view):
        return [sum(v*w for v,w in zip(view,row)) for row in s.predictor_w]
    
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
            s.e += 25  # 更高食物奖励
            food.remove((nx, ny))
        
        s.x, s.y = nx, ny
        s.e -= 0.5  # 更低消耗


def run(steps=1000):
    print("AES v1.1 - Energy Optimized")
    print("="*40)
    
    food = [(random.randint(0,9),random.randint(0,9)) for _ in range(8)]  # 更多食物
    agents = [Agent(random.randint(0,9),random.randint(0,9)) for _ in range(10)]
    
    for st in range(steps):
        while len(food) < 8:
            food.append((random.randint(0,9),random.randint(0,9)))
        
        for a in agents:
            child = a.step(food)
            if child and a.e >= 80:  # 更高复制阈值
                child.e = a.e // 2
                a.e = a.e // 2
                agents.append(child)
        
        agents = [a for a in agents if a.e > 0]
        while len(agents) < 5:  # 更高维持
            agents.append(Agent(random.randint(0,9),random.randint(0,9)))
        
        if st % 200 == 0:
            n = len(agents)
            avg_e = sum(a.e for a in agents) / max(1, n)
            print(f"Step {st}: Agents={n}, AvgE={avg_e:.1f}")

    print(f"\nFinal: {len(agents)} agents")


if __name__ == "__main__":
    run()
