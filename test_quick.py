"""
AES v0.3 - 测试版（短步数）
"""

import numpy as np
import random


CONFIG = {
    'grid_size': 8,
    'n_agents': 10,
    'n_food': 4,
    'steps': 500,
    'energy_init': 20,
    'energy_per_step': 1,
    'food_energy': 10,
    'mutation_strength': 0.1,
    'reproduce_threshold': 30,
    'predict_reward': 1,
}


class Env:
    def __init__(self):
        self.size = CONFIG['grid_size']
        self.food = []
        for _ in range(CONFIG['n_food']):
            self.add_food()
    
    def add_food(self):
        self.food.append((random.randint(0, self.size-1), random.randint(0, self.size-1)))
    
    def step(self):
        while len(self.food) < CONFIG['n_food']:
            self.add_food()
    
    def get_view(self, x, y):
        view = np.zeros(9)
        idx = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                nx = (x + dx) % self.size
                ny = (y + dy) % self.size
                if (nx, ny) in self.food:
                    view[idx] = 1
                idx += 1
        return view


class Agent:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.energy = CONFIG['energy_init']
        self.alive = True
        
        self.w1 = np.random.randn(9, 6) * 0.1
        self.w2_act = np.random.randn(6, 4) * 0.1
        self.w2_pred = np.random.randn(6, 9) * 0.1
        
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
    
    def mutate(self):
        child = Agent(self.x, self.y)
        child.energy = self.energy // 2
        self.energy = self.energy // 2
        child.w1 = self.w1 + np.random.randn(9, 6) * CONFIG['mutation_strength']
        child.w2_act = self.w2_act + np.random.randn(6, 4) * CONFIG['mutation_strength']
        child.w2_pred = self.w2_pred + np.random.randn(6, 9) * CONFIG['mutation_strength']
        return child


# 快速测试
env = Env()
agents = [Agent(random.randint(0,7), random.randint(0,7)) for _ in range(10)]

print("开始测试...")

for step in range(50):
    env.step()
    
    for a in agents:
        if not a.alive:
            continue
        
        obs = env.get_view(a.x, a.y)
        dx, dy, pred = a.act(obs)
        a.x = (a.x + dx) % 8
        a.y = (a.y + dy) % 8
        a.energy -= 1
        
        if (a.x, a.y) in env.food:
            a.energy += CONFIG['food_energy']
            env.food.remove((a.x, a.y))
        
        # 预测
        next_obs = env.get_view(a.x, a.y)
        err = np.mean((pred - next_obs) ** 2)
        a.predict_total += 1
        if err < 0.5:
            a.energy += CONFIG['predict_reward']
            a.predict_success += 1
    
    agents = [a for a in agents if a.alive and a.energy > 0]
    
    for a in agents:
        if a.energy >= CONFIG['reproduce_threshold']:
            agents.append(a.mutate())
    
    while len(agents) < 3:
        agents.append(Agent(random.randint(0,7), random.randint(0,7)))

print(f"完成! Agent数: {len(agents)}")
if agents:
    rates = [a.predict_success/max(1,a.predict_total) for a in agents]
    print(f"预测准确率: {np.mean(rates):.2%}")
