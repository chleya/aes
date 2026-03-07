"""
AES 阶段3验证 - 多Agent对抗
验证: 策略涌现
"""

import random


class Agent:
    def __init__(s, x, y, team):
        s.x = x; s.y = y
        s.team = team  # 0=蓝, 1=红
        s.e = 30
        s.alive = 1
    
    def act(s, agents):
        # 简单策略: 追食物,躲敌人
        mx, my = 5, 5  # 食物位置
        ex, ey = None, None
        
        for a in agents:
            if a.team != s.team and a.alive:
                d = abs(a.x-s.x) + abs(a.y-s.y)
                if d < 5:
                    ex, ey = a.x, a.y
        
        # 决策
        if ex is not None and abs(ex-s.x)+abs(ey-s.y) < 3:
            dx = -1 if ex > s.x else 1
            dy = -1 if ey > s.y else 1
        else:
            dx = 1 if mx > s.x else -1 if mx < s.x else 0
            dy = 1 if my > s.y else -1 if my < s.y else 0
        
        return dx, dy
    
    def step(s, dx, dy, agents, grid):
        nx = (s.x + dx) % grid
        ny = (s.y + dy) % grid
        
        # 吃食物
        if (nx, ny) == (5, 5):
            s.e += 20
        
        # 遇到敌人
        for a in agents:
            if a is not s and a.alive and a.team != s.team:
                if a.x == nx and a.y == ny:
                    s.e = -100  # 同归于尽
        
        s.x, s.y = nx, ny
        s.e -= 1


def run_trial(grid=10, steps=500):
    agents = [Agent(random.randint(0,9), random.randint(0,9), i%2) for i in range(10)]
    
    for st in range(steps):
        for a in agents:
            if not a.alive: continue
            dx, dy = a.act(agents)
            a.step(dx, dy, agents, grid)
        
        # 死亡复制
        agents = [a for a in agents if a.alive and a.e > 0]
        for a in agents:
            if a.e >= 50:
                child = Agent(a.x, a.y, a.team)
                child.e = a.e // 2
                a.e //= 2
                agents.append(child)
        
        # 每队至少2个
        for t in [0, 1]:
            if len([a for a in agents if a.team == t]) < 2:
                agents.append(Agent(5, 5, t))
    
    blue = len([a for a in agents if a.team == 0])
    red = len([a for a in agents if a.team == 1])
    return blue, red


def verify():
    print("="*50)
    print("阶段3验证: 多Agent对抗")
    print("="*50)
    
    results = []
    for i in range(10):
        blue, red = run_trial()
        results.append((blue, red))
        print(f"Trial {i+1}: 蓝={blue}, 红={red}")
    
    avg_blue = sum(r[0] for r in results) / len(results)
    avg_red = sum(r[1] for r in results) / len(results)
    
    print(f"\n平均: 蓝={avg_blue:.0f}, 红={avg_red:.0f}")
    
    # 对比
    blue_wins = sum(1 for r in results if r[0] > r[1])
    red_wins = sum(1 for r in results if r[1] > r[0])
    print(f"蓝队胜: {blue_wins}/10")
    print(f"红队胜: {red_wins}/10")
    
    return results


if __name__ == "__main__":
    verify()
