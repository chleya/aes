"""
AES - 对抗涌现系统
最小实验实现 v0.2 (简化版)
"""

import numpy as np
import random


# ==================== 配置 ====================
CONFIG = {
    'grid_size': 12,
    'n_agents': 15,
    'n_food': 6,
    'steps': 2000,
    'energy_init': 30,
    'energy_per_step': 1,
    'food_energy': 15,
    'mutation_strength': 0.2,
    'reproduce_threshold': 50,
}


# ==================== 环境 ====================
class Environment:
    def __init__(self):
        self.size = CONFIG['grid_size']
        self.food = []
        self.init_food()
    
    def init_food(self):
        for _ in range(CONFIG['n_food']):
            self.add_food()
    
    def add_food(self):
        x = random.randint(0, self.size-1)
        y = random.randint(0, self.size-1)
        self.food.append((x, y))
    
    def step(self):
        # 补充食物
        while len(self.food) < CONFIG['n_food']:
            self.add_food()
    
    def get_local(self, x, y):
        """局部视野 3x3"""
        view = np.zeros((3, 3))
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                nx = (x + dx) % self.size
                ny = (y + dy) % self.size
                for fx, fy in self.food:
                    if fx == nx and fy == ny:
                        view[dy+1, dx+1] = 1
        return view.flatten()


# ==================== Agent ====================
class Agent:
    next_id = 0
    
    def __init__(self, x, y):
        self.id = Agent.next_id
        Agent.next_id += 1
        self.x = x
        self.y = y
        self.energy = CONFIG['energy_init']
        self.alive = True
        
        # 简单网络
        self.w = np.random.randn(9, 4) * 0.1
        self.fitness = 0
    
    def act(self, obs):
        """根据观察行动"""
        logits = np.dot(obs, self.w)
        action = np.argmax(logits)
        
        if action == 0:
            dx, dy = 0, -1
        elif action == 1:
            dx, dy = 0, 1
        elif action == 2:
            dx, dy = -1, 0
        else:
            dx, dy = 1, 0
        
        return dx, dy
    
    def move(self, dx, dy):
        self.x = (self.x + dx) % CONFIG['grid_size']
        self.y = (self.y + dy) % CONFIG['grid_size']
    
    def mutate(self):
        child = Agent(self.x, self.y)
        child.energy = self.energy // 2
        self.energy = self.energy // 2
        child.w = self.w + np.random.randn(9, 4) * CONFIG['mutation_strength']
        return child


# ==================== 实验 ====================
def run():
    print("=" * 50)
    print("AES 最小实验 v0.2")
    print("=" * 50)
    
    env = Environment()
    agents = []
    
    # 初始化Agent
    for _ in range(CONFIG['n_agents']):
        x = random.randint(0, CONFIG['grid_size']-1)
        y = random.randint(0, CONFIG['grid_size']-1)
        agents.append(Agent(x, y))
    
    for step in range(CONFIG['steps']):
        env.step()
        
        for a in agents:
            if not a.alive:
                continue
            
            # 观察
            obs = env.get_local(a.x, a.y)
            
            # 行动
            dx, dy = a.act(obs)
            a.move(dx, dy)
            
            # 能量
            a.energy -= CONFIG['energy_per_step']
            
            # 吃食物
            for f in list(env.food):
                if f[0] == a.x and f[1] == a.y:
                    a.energy += CONFIG['food_energy']
                    env.food.remove(f)
            
            # 适应度
            a.fitness += a.energy / 100.0
        
        # 死亡和复制
        agents = [a for a in agents if a.alive and a.energy > 0]
        
        for a in agents:
            if a.energy >= CONFIG['reproduce_threshold']:
                agents.append(a.mutate())
        
        # 防止灭绝
        while len(agents) < 5:
            x = random.randint(0, CONFIG['grid_size']-1)
            y = random.randint(0, CONFIG['grid_size']-1)
            agents.append(Agent(x, y))
        
        if step % 200 == 0:
            print(f"Step {step}: Agent数={len(agents)}, "
                  f"平均能量={np.mean([a.energy for a in agents]):.1f}")
    
    print("\n完成!")
    print(f"最终Agent数: {len(agents)}")
    return agents


if __name__ == "__main__":
    agents = run()
