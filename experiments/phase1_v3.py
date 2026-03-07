"""
AES 阶段1验证 - 能量优化版
"""

import random


class Entity:
    def __init__(s, etype='food', grid=10):
        s.x = random.randint(0, grid-1)
        s.y = random.randint(0, grid-1)
        s.type = etype


class Agent:
    def __init__(s, x, y):
        s.x = x; s.y = y
        s.e = 50  # 更高初始能量
        s.alive = 1
        s.w = [[random.random()*0.3-0.15 for _ in range(9)] for _ in range(4)]
    
    def act(s, view):
        scores = [sum(v*w for v,w in zip(view, row)) for row in s.w]
        act = scores.index(max(scores))
        moves = [(0,-1), (0,1), (-1,0), (1,0)]
        return moves[act]
    
    def step(s, dx, dy, food, grid):
        nx = (s.x + dx) % grid
        ny = (s.y + dy) % grid
        
        # 吃食物
        for f in list(food):
            if f.x == nx and f.y == ny:
                s.e += 25
                food.remove(f)
                break
        
        s.x, s.y = nx, ny
        s.e -= 0.5  # 更低消耗


def run_trial(grid=10, n_food=8, steps=500):
    food = [Entity('food', grid) for _ in range(n_food)]
    agents = [Agent(random.randint(0,grid-1), random.randint(0,grid-1)) for _ in range(10)]
    
    for st in range(steps):
        while len(food) < n_food:
            food.append(Entity('food', grid))
        
        for a in agents:
            if not a.alive: continue
            
            view = []
            for dy in [-1,0,1]:
                for dx in [-1,0,1]:
                    nx = (a.x + dx) % grid
                    ny = (a.y + dy) % grid
                    view.append(1 if any(f.x==nx and f.y==ny for f in food) else 0)
            
            dx, dy = a.act(view)
            a.step(dx, dy, food, grid)
        
        # 死亡复制
        agents = [a for a in agents if a.alive and a.e > 0]
        for a in agents:
            if a.e >= 80:
                child = Agent(a.x, a.y)
                child.e = a.e // 2
                a.e = a.e // 2
                agents.append(child)
        
        while len(agents) < 5:
            agents.append(Agent(random.randint(0,grid-1), random.randint(0,grid-1)))
    
    return len(agents)


def verify():
    print("="*50)
    print("阶段1验证: 能量优化版")
    print("="*50)
    
    results = []
    for i in range(10):
        n = run_trial()
        results.append(n)
        print(f"Trial {i+1}: Agents = {n}")
    
    avg = sum(results) / len(results)
    print(f"\n平均: {avg:.1f}")
    print(f"增长: 10 -> {avg:.0f}")
    
    # 对比
    print("\n对比:")
    print(f"本版本: {avg:.1f}")
    print(f"之前版本(无预测): 3.0")
    print(f"v0.4历史数据: 253")
    
    return results


if __name__ == "__main__":
    verify()
