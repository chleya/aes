"""
AES v0.5 - 测试运行
"""

import numpy as np
import random


class Entity:
    def __init__(self, etype='food'):
        self.x = random.randint(0, 11)
        self.y = random.randint(0, 11)
        self.type = etype
        self.vx, self.vy = 0, 0
    
    def move(self):
        if self.type == 'predator':
            self.vx = random.choice([-1, 0, 1])
            self.vy = random.choice([-1, 0, 1])
        self.x = (self.x + self.vx) % 12
        self.y = (self.y + self.vy) % 12


class Agent:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.energy = 30
        self.alive = True
        self.w1 = np.random.randn(9, 8) * 0.1
        self.w2_act = np.random.randn(8, 4) * 0.1
        self.w2_pred = np.random.randn(8, 9) * 0.1
        self.predict_success = 0
        self.predict_total = 0
    
    def act(self, obs):
        h = np.tanh(np.dot(obs, self.w1))
        act = np.argmax(np.dot(h, self.w2_act))
        pred = np.tanh(np.dot(h, self.w2_pred))
        
        if act == 0: dx, dy = 0, -1
        elif act == 1: dx, dy = 0, 1
        elif act == 2: dx, dy = -1, 0
        else: dx, dy = 1, 0
        
        return dx, dy, pred
    
    def move(self, dx, dy):
        self.x = (self.x + dx) % 12
        self.y = (self.y + dy) % 12
    
    def mutate(self):
        child = Agent(self.x, self.y)
        child.energy = self.energy // 2
        self.energy = self.energy // 2
        child.w1 = self.w1 + np.random.randn(9, 8) * 0.1
        child.w2_act = self.w2_act + np.random.randn(8, 4) * 0.1
        child.w2_pred = self.w2_pred + np.random.randn(8, 9) * 0.1
        return child


# 运行
print("AES v0.5 Test")
food = [Entity('food') for _ in range(6)]
predators = [Entity('predator') for _ in range(3)]
agents = [Agent(random.randint(0,11), random.randint(0,11)) for _ in range(20)]

for step in range(500):
    # 移动实体
    for p in predators:
        p.move()
    
    # 补充食物
    while len(food) < 6:
        food.append(Entity('food'))
    
    # Agent行动
    for a in agents:
        if not a.alive:
            continue
        
        # 视野
        view = np.zeros(9)
        idx = 0
        for dy in [-1,0,1]:
            for dx in [-1,0,1]:
                nx = (a.x + dx) % 12
                ny = (a.y + dy) % 12
                for f in food:
                    if f.x == nx and f.y == ny:
                        view[idx] = 1
                for p in predators:
                    if p.x == nx and p.y == ny:
                        view[idx] = -1
                idx += 1
        
        dx, dy, pred = a.act(view)
        a.move(dx, dy)
        a.energy -= 1
        
        # 吃食物
        for f in list(food):
            if f.x == a.x and f.y == a.y:
                a.energy += 15
                food.remove(f)
        
        # 捕食者
        for p in predators:
            if p.x == a.x and p.y == a.y:
                a.energy = -30
        
        # 预测
        future = np.zeros(9)
        idx = 0
        for dy in [-1,0,1]:
            for dx in [-1,0,1]:
                nx = (a.x + dx) % 12
                ny = (a.y + dy) % 12
                for f in food:
                    if f.x == nx and f.y == ny:
                        future[idx] = 1
                for p in predators:
                    if p.x == nx and p.y == ny:
                        future[idx] = -1
                idx += 1
        
        err = np.mean((pred - future)**2)
        a.predict_total += 1
        if err < 0.4:
            a.energy += 2
            a.predict_success += 1
    
    # 死亡复制
    agents = [a for a in agents if a.alive and a.energy > 0]
    
    for a in agents:
        if a.energy >= 50:
            agents.append(a.mutate())
    
    while len(agents) < 5:
        agents.append(Agent(random.randint(0,11), random.randint(0,11)))
    
    if step % 100 == 0:
        n = len(agents)
        rate = np.mean([a.predict_success/max(1,a.predict_total) for a in agents]) if agents else 0
        print(f"Step {step}: Agent={n}, 预测={rate:.1%}")

print(f"完成! 最终Agent: {len(agents)}")
