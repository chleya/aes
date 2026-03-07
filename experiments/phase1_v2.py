"""
AES 阶段1验证 - 完整版(带预测奖励)
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
        s.e = 30; s.alive = 1
        s.w = [[random.random()*0.2-0.1 for _ in range(9)] for _ in range(4)]
        s.predict_success = 0
        s.predict_total = 0
    
    def act(s, view):
        scores = [sum(v*w for v,w in zip(view, row)) for row in s.w]
        act = scores.index(max(scores))
        moves = [(0,-1), (0,1), (-1,0), (1,0)]
        return moves[act]
    
    def step(s, dx, dy, food, before_view, grid):
        nx = (s.x + dx) % grid
        ny = (s.y + dy) % grid
        
        # 吃食物
        for f in food:
            if f.x == nx and f.y == ny:
                s.e += 15
                food.remove(f)
                break
        
        s.x, s.y = nx, ny
        s.e -= 1
        
        # 预测奖励: 比较移动前后视野
        after_view = []
        for dy in [-1,0,1]:
            for dx in [-1,0,1]:
                nx2 = (s.x + dx) % grid
                ny2 = (s.y + dy) % grid
                after_view.append(1 if any(f.x==nx2 and f.y==ny2 for f in food) else 0)
        
        # 简单预测: 如果移动到有食物的位置，预测成功
        pred_success = (before_view[4] == 1)  # 中心点预测
        s.predict_total += 1
        if pred_success:
            s.e += 2
            s.predict_success += 1
        
        return pred_success


def run_trial(grid=10, n_food=5, steps=500):
    food = [Entity('food', grid) for _ in range(n_food)]
    agents = [Agent(random.randint(0,grid-1), random.randint(0,grid-1)) for _ in range(10)]
    
    for st in range(steps):
        while len(food) < n_food:
            food.append(Entity('food', grid))
        
        for a in agents:
            if not a.alive: continue
            
            # 移动前视野
            before_view = []
            for dy in [-1,0,1]:
                for dx in [-1,0,1]:
                    nx = (a.x + dx) % grid
                    ny = (a.y + dy) % grid
                    before_view.append(1 if any(f.x==nx and f.y==ny for f in food) else 0)
            
            dx, dy = a.act(before_view)
            a.step(dx, dy, food, before_view, grid)
        
        agents = [a for a in agents if a.alive and a.e > 0]
        for a in agents:
            if a.e >= 50:
                child = Agent(a.x, a.y)
                child.e = a.e // 2
                a.e = a.e // 2
                agents.append(child)
        
        while len(agents) < 3:
            agents.append(Agent(random.randint(0,grid-1), random.randint(0,grid-1)))
    
    # 统计
    pred_rate = sum(a.predict_success/max(1,a.predict_total) for a in agents) / max(1,len(agents))
    return len(agents), pred_rate


def verify():
    print("="*50)
    print("阶段1验证: 带预测奖励")
    print("="*50)
    
    results = []
    for i in range(10):
        n, pred = run_trial()
        results.append((n, pred))
        print(f"Trial {i+1}: Agents={n}, Pred={pred:.1%}")
    
    avg_agents = sum(r[0] for r in results) / len(results)
    avg_pred = sum(r[1] for r in results) / len(results)
    
    print(f"\n平均: Agents={avg_agents:.1f}, Pred={avg_pred:.1%}")
    print(f"增长: 10 -> {avg_agents:.0f}")
    
    return results


if __name__ == "__main__":
    verify()
