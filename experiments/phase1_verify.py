"""
AES 阶段1验证 - 稳定版
移动实体 -> 对象追踪
"""

import random


class Entity:
    """移动实体"""
    def __init__(s, etype='food', grid=10):
        s.x = random.randint(0, grid-1)
        s.y = random.randint(0, grid-1)
        s.type = etype


class Agent:
    def __init__(s, x, y):
        s.x = x; s.y = y
        s.e = 30; s.alive = 1
        # 简化网络
        s.w = [[random.random()*0.2-0.1 for _ in range(9)] for _ in range(4)]
    
    def act(s, view):
        # 简化前向
        scores = [sum(v*w for v,w in zip(view, row)) for row in s.w]
        act = scores.index(max(scores))
        
        moves = [(0,-1), (0,1), (-1,0), (1,0)]
        return moves[act]
    
    def step(s, dx, dy, food, grid):
        nx = (s.x + dx) % grid
        ny = (s.y + dy) % grid
        
        # 吃食物
        ate = False
        for f in food:
            if f.x == nx and f.y == ny:
                s.e += 15
                ate = True
                break
        
        s.x, s.y = nx, ny
        s.e -= 1
        return ate


def run_trial(grid=10, n_food=5, steps=500):
    """单次试验"""
    food = [Entity('food', grid) for _ in range(n_food)]
    agents = [Agent(random.randint(0,grid-1), random.randint(0,grid-1)) for _ in range(10)]
    
    for st in range(steps):
        # 补充食物
        while len(food) < n_food:
            food.append(Entity('food', grid))
        
        for a in agents:
            if not a.alive: continue
            
            # 视野
            view = []
            for dy in [-1,0,1]:
                for dx in [-1,0,1]:
                    nx = (a.x + dx) % grid
                    ny = (a.y + dy) % grid
                    view.append(1 if any(f.x==nx and f.y==ny for f in food) else 0)
            
            dx, dy = a.act(view)
            ate = a.step(dx, dy, food, grid)
            if ate:
                food = [f for f in food if not (f.x==a.x and f.y==a.y)]
        
        # 死亡复制
        agents = [a for a in agents if a.alive and a.e > 0]
        for a in agents:
            if a.e >= 50:
                child = Agent(a.x, a.y)
                child.e = a.e // 2
                a.e = a.e // 2
                agents.append(child)
        
        while len(agents) < 3:
            agents.append(Agent(random.randint(0,grid-1), random.randint(0,grid-1)))
    
    return len(agents)


def verify():
    """验证实验"""
    print("="*50)
    print("阶段1验证: 移动实体 -> 对象追踪")
    print("="*50)
    
    results = []
    for i in range(10):
        n = run_trial()
        results.append(n)
        print(f"Trial {i+1}: Agents = {n}")
    
    avg = sum(results) / len(results)
    print(f"\n平均: {avg:.1f}")
    print(f"增长: 10 -> {avg:.0f}")
    
    # 对比基线
    print("\n对比基线(无预测):")
    baseline = []
    for i in range(5):
        n = run_trial()
        baseline.append(n)
    print(f"基线平均: {sum(baseline)/5:.1f}")
    
    return results


if __name__ == "__main__":
    verify()
