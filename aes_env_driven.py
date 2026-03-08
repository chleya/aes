"""
AES 环境驱动涌现
只调环境，看Agent结构泛化能力
"""

import random


class Agent:
    def __init__(s, x, y):
        s.x, s.y = x, y
        s.e = 30
        s.w = [[random.random()*0.2-0.1 for _ in range(9)] for _ in range(4)]
    
    def act(s, view):
        scores = [sum(v*w for v,w in zip(view,row)) for row in s.w]
        moves = [(0,-1),(0,1),(-1,0),(1,0)]
        return moves[scores.index(max(scores))]
    
    def mutate(s):
        child = Agent(s.x, s.y)
        child.w = [[w + random.random()*0.1-0.05 for w in row] for row in s.w]
        return child


def run_env_experiment(env_config, steps=500):
    """运行环境配置"""
    grid = env_config['grid']
    n_food = env_config['food']
    
    food = [(random.randint(0,grid-1),random.randint(0,grid-1)) for _ in range(n_food)]
    agents = [Agent(random.randint(0,grid-1),random.randint(0,grid-1)) for _ in range(10)]
    
    for st in range(steps):
        while len(food) < n_food:
            food.append((random.randint(0,grid-1),random.randint(0,grid-1)))
        
        for a in agents:
            view = []
            for dy in [-1,0,1]:
                for dx in [-1,0,1]:
                    view.append(1 if ((a.x+dx)%grid,(a.y+dy)%grid) in food else 0)
            
            dx, dy = a.act(view)
            nx, ny = (a.x+dx)%grid, (a.y+dy)%grid
            
            if (nx, ny) in food:
                a.e += 15
                food.remove((nx, ny))
            
            a.x, a.y = nx, ny
            a.e -= 1
        
        agents = [a for a in agents if a.e > 0]
        for a in agents:
            if a.e >= 50:
                agents.append(a.mutate())
                a.e //= 2
        
        while len(agents) < 3:
            agents.append(Agent(random.randint(0,grid-1),random.randint(0,grid-1)))
    
    return len(agents)


# 不同环境配置
envs = [
    {'name': '简单', 'grid': 5, 'food': 3},
    {'name': '中等', 'grid': 10, 'food': 5},
    {'name': '困难', 'grid': 15, 'food': 8},
    {'name': '极难', 'grid': 20, 'food': 10},
]

print("="*50)
print("环境驱动涌现实验")
print("只调环境，看Agent适应能力")
print("="*50)

results = []
for env in envs:
    n = run_env_experiment(env, 500)
    results.append((env['name'], n))
    print(f"{env['name']}: {n} agents")

print("\n结论:")
print("环境越难，Agent需要更强的结构泛化能力")
