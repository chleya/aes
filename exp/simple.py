"""
AES 最小环境实验 - 简化版
"""
import random

def trial(grid, steps=100):
    agents = [30] * 3  # 能量
    food = (grid//2, grid//2)
    
    for _ in range(steps):
        new_agents = []
        for e in agents:
            if e <= 0:
                continue
            # 简单移动
            e -= 1
            # 吃食物
            if random.random() < 0.2:
                e += 10
            # 复制
            if e > 50:
                e = e // 2
                new_agents.append(e)
            new_agents.append(e)
        agents = new_agents[:10] if new_agents else [30]
        if len(agents) < 2:
            agents.append(30)
    return len(agents)


print("Grid,Avg,Min,Max")
for g in [2, 3, 4, 5, 10]:
    results = [trial(g) for _ in range(20)]
    avg = sum(results) / len(results)
    print(f"{g},{avg},{min(results)},{max(results)}")
