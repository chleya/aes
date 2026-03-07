"""
AES v0.5 - 优化版
改进：
1. 更高效的Agent网络
2. 更好的预测机制
3. 更稳定的能量循环
"""

import numpy as np
import random


CONFIG = {
    'grid_size': 12,
    'n_agents': 20,
    'n_food': 6,
    'n_predators': 3,
    'steps': 2000,
    'energy_init': 30,
    'energy_per_step': 1,
    'food_energy': 15,
    'predator_energy': -30,
    'mutation_strength': 0.1,
    'reproduce_threshold': 50,
    'predict_reward': 2,
}


class Entity:
    def __init__(self, etype='food'):
        self.x = random.randint(0, CONFIG['grid_size']-1)
        self.y = random.randint(0, CONFIG['grid_size']-1)
        self.type = etype
        self.vx, self.vy = 0, 0
    
    def move(self):
        if self.type == 'predator':
            self.vx = random.choice([-1, 0, 1])
            self.vy = random.choice([-1, 0, 1])
        self.x = (self.x + self.vx) % CONFIG['grid_size']
        self.y = (self.y + self.vy) % CONFIG['grid_size']


class Env:
    def __init__(self):
        self.size = CONFIG['grid_size']
        self.food = [Entity('food') for _ in range(CONFIG['n_food'])]
        self.predators = [Entity('predator') for _ in range(CONFIG['n_predators'])]
    
    def step(self):
        for p in self.predators:
            p.move()
        
        while len(self.food) < CONFIG['n_food']:
            self.food.append(Entity('food'))
    
    def get_view(self, x, y):
        view = np.zeros(9)
        idx = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                nx = (x + dx) % self.size
                ny = (y + dy) % self.size
                
                for f in self.food:
                    if f.x == nx and f.y == ny:
                        view[idx] = 1
                
                for p in self.predators:
                    if p.x == nx and p.y == ny:
                        view[idx] = -1
                
                idx += 1
        return view


class Agent:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.energy = CONFIG['energy_init']
        self.alive = True
        
        # 优化：更小的网络，更快
        self.w1 = np.random.randn(9, 8) * 0.1
        self.b1 = np.zeros(8)
        self.w2_act = np.random.randn(8, 4) * 0.1
        self.w2_pred = np.random.randn(8, 9) * 0.1
        self.b2 = np.zeros(4)
        
        self.predict_success = 0
        self.predict_total = 0
        self.fitness = 0
    
    def forward(self, obs):
        h = np.tanh(np.dot(obs, self.w1) + self.b1)
        act_logits = np.dot(h, self.w2_act) + self.b2
        pred = np.tanh(np.dot(h, self.w2_pred))
        return act_logits, pred
    
    def act(self, obs):
        act_logits, pred = self.forward(obs)
        
        # 优化：添加探索
        if random.random() < 0.1:
            action = random.randint(0, 3)
        else:
            action = np.argmax(act_logits)
        
        if action == 0: dx, dy = 0, -1
        elif action == 1: dx, dy = 0, 1
        elif action == 2: dx, dy = -1, 0
        else: dx, dy = 1, 0
        
        return dx, dy, pred
    
    def move(self, dx, dy):
        self.x = (self.x + dx) % CONFIG['grid_size']
        self.y = (self.y + dy) % CONFIG['grid_size']
    
    def mutate(self):
        child = Agent(self.x, self.y)
        child.energy = self.energy // 2
        self.energy = self.energy // 2
        
        child.w1 = self.w1 + np.random.randn(9, 8) * CONFIG['mutation_strength']
        child.b1 = self.b1 + np.random.randn(8) * CONFIG['mutation_strength']
        child.w2_act = self.w2_act + np.random.randn(8, 4) * CONFIG['mutation_strength']
        child.w2_pred = self.w2_pred + np.random.randn(8, 9) * CONFIG['mutation_strength']
        
        return child


def run():
    print("=" * 50)
    print("AES v0.5 - 优化版")
    print("=" * 50)
    
    env = Env()
    agents = [Agent(random.randint(0,11), random.randint(0,11)) for _ in range(CONFIG['n_agents'])]
    
    stats = {'steps': [], 'n_agents': [], 'avg_energy': [], 'predict_rate': []}
    
    for step in range(CONFIG['steps']):
        env.step()
        
        for a in agents:
            if not a.alive:
                continue
            
            obs = env.get_view(a.x, a.y)
            dx, dy, pred = a.act(obs)
            a.move(dx, dy)
            
            a.energy -= CONFIG['energy_per_step']
            
            # 吃食物
            for f in list(env.food):
                if f.x == a.x and f.y == a.y:
                    a.energy += CONFIG['food_energy']
                    env.food.remove(f)
            
            # 捕食者
            for p in env.predators:
                if p.x == a.x and p.y == a.y:
                    a.energy += CONFIG['predator_energy']
            
            # 预测奖励
            future = env.get_view(a.x, a.y)
            err = np.mean((pred - future) ** 2)
            a.predict_total += 1
            
            if err < 0.4:
                a.energy += CONFIG['predict_reward']
                a.predict_success += 1
                a.fitness += 1
            else:
                a.fitness -= err
        
        # 死亡
        agents = [a for a in agents if a.alive and a.energy > 0]
        
        # 复制
        for a in agents:
            if a.energy >= CONFIG['reproduce_threshold']:
                agents.append(a.mutate())
        
        # 防止灭绝
        while len(agents) < 5:
            agents.append(Agent(random.randint(0,11), random.randint(0,11)))
        
        # 记录
        if step % 200 == 0:
            n = len(agents)
            avg_e = np.mean([a.energy for a in agents]) if agents else 0
            pred_r = np.mean([a.predict_success/max(1,a.predict_total) for a in agents]) if agents else 0
            
            stats['steps'].append(step)
            stats['n_agents'].append(n)
            stats['avg_energy'].append(avg_e)
            stats['predict_rate'].append(pred_r)
            
            print(f"Step {step}: Agent数={n}, 平均能量={avg_e:.1f}, 预测准确率={pred_r:.1%}")
    
    print("\n完成!")
    
    if agents:
        pred_rates = [a.predict_success/max(1,a.predict_total) for a in agents]
        print(f"最终Agent数: {len(agents)}")
        print(f"预测准确率: {np.mean(pred_rates):.1%}")
    
    return stats, agents


if __name__ == "__main__":
    run()
