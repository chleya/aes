"""
AES v0.4 - 简化移动版
"""

import numpy as np
import random


CONFIG = {
    'grid_size': 8,
    'n_agents': 10,
    'n_food': 4,
    'steps': 1000,
}


class Agent:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.energy = 20
        self.alive = True
        self.w1 = np.random.randn(9, 6) * 0.1
        self.w2_act = np.random.randn(6, 4) * 0.1
        self.w2_pred = np.random.randn(6, 9) * 0.1
        self.succ = 0
        self.total = 0
    
    def act(self, obs):
        h = np.tanh(np.dot(obs, self.w1))
        act = np.argmax(np.dot(h, self.w2_act))
        pred = np.tanh(np.dot(h, self.w2_pred))
        
        if act == 0: dx, dy = 0, -1
        elif act == 1: dx, dy = 0, 1
        elif act == 2: dx, dy = -1, 0
        else: dx, dy = 1, 0
        
        return dx, dy, pred
    
    def mutate(self):
        child = Agent(self.x, self.y)
        child.energy = self.energy // 2
        self.energy = self.energy // 2
        child.w1 = self.w1 + np.random.randn(9, 6) * 0.1
        child.w2_act = self.w2_act + np.random.randn(6, 4) * 0.1
        child.w2_pred = self.w2_pred + np.random.randn(6, 9) * 0.1
        return child


def run():
    print("AES v0.4 - 移动实体测试")
    
    # 食物位置
    food = [(random.randint(0,7), random.randint(0,7)) for _ in range(4)]
    # 捕食者位置
    predators = [(random.randint(0,7), random.randint(0,7)) for _ in range(2)]
    
    agents = [Agent(random.randint(0,7), random.randint(0,7)) for _ in range(10)]
    
    for step in range(CONFIG['steps']):
        # 移动捕食者
        predators = [((p[0]+random.choice([-1,0,1]))%8, (p[1]+random.choice([-1,0,1]))%8) for p in predators]
        
        # 补充食物
        while len(food) < 4:
            food.append((random.randint(0,7), random.randint(0,7)))
        
        for a in agents:
            if not a.alive:
                continue
            
            # 视野
            view = np.zeros(9)
            idx = 0
            for dy in [-1,0,1]:
                for dx in [-1,0,1]:
                    nx = (a.x + dx) % 8
                    ny = (a.y + dy) % 8
                    if (nx, ny) in food:
                        view[idx] = 1
                    if (nx, ny) in predators:
                        view[idx] = -1
                    idx += 1
            
            dx, dy, pred = a.act(view)
            a.x = (a.x + dx) % 8
            a.y = (a.y + dy) % 8
            a.energy -= 1
            
            # 吃食物
            if (a.x, a.y) in food:
                a.energy += 10
                food.remove((a.x, a.y))
            
            # 捕食者
            if (a.x, a.y) in predators:
                a.energy = 0
                a.alive = False
            
            # 预测
            future = np.zeros(9)
            idx = 0
            for dy in [-1,0,1]:
                for dx in [-1,0,1]:
                    nx = (a.x + dx) % 8
                    ny = (a.y + dy) % 8
                    if (nx, ny) in food:
                        future[idx] = 1
                    if (nx, ny) in predators:
                        future[idx] = -1
                    idx += 1
            
            err = np.mean((pred - future)**2)
            a.total += 1
            if err < 0.5:
                a.energy += 1
                a.succ += 1
        
        agents = [a for a in agents if a.alive and a.energy > 0]
        
        for a in agents:
            if a.energy >= 30:
                agents.append(a.mutate())
        
        while len(agents) < 3:
            agents.append(Agent(random.randint(0,7), random.randint(0,7)))
        
        if step % 100 == 0:
            n = len(agents)
            rate = np.mean([a.succ/max(1,a.total) for a in agents]) if agents else 0
            print(f"Step {step}: Agent={n}, 预测={rate:.1%}")

run()
