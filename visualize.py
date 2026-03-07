"""
AES 实时可视化
显示Agent、食物、捕食者在网格上的运动
"""

import numpy as np
import random
import time


CONFIG = {
    'grid_size': 10,
    'n_agents': 15,
    'n_food': 5,
    'n_predators': 2,
    'steps': 500,
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


class Agent:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.energy = 20
        self.alive = True
        self.w1 = np.random.randn(9, 6) * 0.1
        self.w2_act = np.random.randn(6, 4) * 0.1
        self.w2_pred = np.random.randn(6, 9) * 0.1
    
    def act(self, obs):
        h = np.tanh(np.dot(obs, self.w1))
        act = np.argmax(np.dot(h, self.w2_act))
        pred = np.tanh(np.dot(h, self.w2_pred))
        
        if act == 0: dx, dy = 0, -1
        elif act == 1: dx, dy = 0, 1
        elif act == 2: dx, dy = -1, 0
        else: dx, dy = 1, 0
        
        return dx, dy
    
    def mutate(self):
        child = Agent(self.x, self.y)
        child.energy = self.energy // 2
        self.energy = self.energy // 2
        child.w1 = self.w1 + np.random.randn(9, 6) * 0.1
        child.w2_act = self.w2_act + np.random.randn(6, 4) * 0.1
        child.w2_pred = self.w2_pred + np.random.randn(6, 9) * 0.1
        return child


def draw_grid(agents, food, predators, step):
    """绘制网格"""
    grid = [['.' for _ in range(CONFIG['grid_size'])] for _ in range(CONFIG['grid_size'])]
    
    # 食物
    for f in food:
        grid[f.y][f.x] = 'F'
    
    # 捕食者
    for p in predators:
        grid[p.y][p.x] = 'X'
    
    # Agent
    for a in agents:
        if a.alive:
            grid[a.y][a.x] = 'A'
    
    # 打印
    print(f"\n=== Step {step} ===")
    print("  " + " ".join(str(i) for i in range(CONFIG['grid_size'])))
    for y in range(CONFIG['grid_size']):
        print(f"{y} " + " ".join(grid[y]))
    
    print(f"Agents: {len([a for a in agents if a.alive])} | Food: {len(food)} | Predators: {len(predators)}")


def get_view(x, y, food, predators):
    view = np.zeros(9)
    idx = 0
    for dy in [-1, 0, 1]:
        for dx in [-1, 0, 1]:
            nx = (x + dx) % CONFIG['grid_size']
            ny = (y + dy) % CONFIG['grid_size']
            if (nx, ny) in [(f.x, f.y) for f in food]:
                view[idx] = 1
            if (nx, ny) in [(p.x, p.y) for p in predators]:
                view[idx] = -1
            idx += 1
    return view


def run_visual():
    print("=" * 40)
    print("AES 实时可视化")
    print("=" * 40)
    print("图例: A=Agent, F=Food, X=Predator")
    
    # 初始化
    food = [Entity('food') for _ in range(CONFIG['n_food'])]
    predators = [Entity('predator') for _ in range(CONFIG['n_predators'])]
    agents = [Agent(random.randint(0,9), random.randint(0,9)) for _ in range(CONFIG['n_agents'])]
    
    for step in range(CONFIG['steps']):
        # 移动实体
        for p in predators:
            p.move()
        
        # 补充食物
        while len(food) < CONFIG['n_food']:
            food.append(Entity('food'))
        
        # Agent行动
        for a in agents:
            if not a.alive:
                continue
            
            obs = get_view(a.x, a.y, food, predators)
            dx, dy = a.act(obs)
            a.x = (a.x + dx) % CONFIG['grid_size']
            a.y = (a.y + dy) % CONFIG['grid_size']
            a.energy -= 1
            
            # 吃食物
            for f in list(food):
                if f.x == a.x and f.y == a.y:
                    a.energy += 10
                    food.remove(f)
            
            # 捕食者
            for p in predators:
                if p.x == a.x and p.y == a.y:
                    a.alive = False
        
        # 死亡和复制
        agents = [a for a in agents if a.alive and a.energy > 0]
        for a in agents:
            if a.energy >= 30:
                agents.append(a.mutate())
        
        while len(agents) < 3:
            agents.append(Agent(random.randint(0,9), random.randint(0,9)))
        
        # 每50步显示一次
        if step % 50 == 0:
            draw_grid(agents, food, predators, step)
            time.sleep(0.1)
    
    print("\n完成!")


if __name__ == "__main__":
    run_visual()
