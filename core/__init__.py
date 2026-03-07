"""
AES 核心模块
"""

import numpy as np
import random


class Entity:
    """环境实体"""
    def __init__(self, etype='food', grid_size=10):
        self.x = random.randint(0, grid_size-1)
        self.y = random.randint(0, grid_size-1)
        self.type = etype
    
    def move(self, grid_size=10):
        if self.type == 'predator':
            self.x = (self.x + random.choice([-1, 0, 1])) % grid_size
            self.y = (self.y + random.choice([-1, 0, 1])) % grid_size


class Environment:
    """环境管理"""
    def __init__(self, grid_size=10, n_food=5, n_predators=2):
        self.size = grid_size
        self.food = [Entity('food', grid_size) for _ in range(n_food)]
        self.predators = [Entity('predator', grid_size) for _ in range(n_predators)]
    
    def step(self):
        """环境一步"""
        for p in self.predators:
            p.move(self.size)
        
        while len(self.food) < 5:
            self.food.append(Entity('food', self.size))
    
    def get_view(self, x, y):
        """获取视野"""
        view = np.zeros(9)
        idx = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                nx, ny = (x + dx) % self.size, (y + dy) % self.size
                for f in self.food:
                    if f.x == nx and f.y == ny:
                        view[idx] = 1
                for p in self.predators:
                    if p.x == nx and p.y == ny:
                        view[idx] = -1
                idx += 1
        return view


class Agent:
    """智能体"""
    def __init__(self, x, y, grid_size=10):
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
        """行动决策"""
        h = np.tanh(np.dot(obs, self.w1))
        act = np.argmax(np.dot(h, self.w2_act))
        pred = np.tanh(np.dot(h, self.w2_pred))
        
        moves = [(0,-1), (0,1), (-1,0), (1,0)]
        return moves[act], pred
    
    def move(self, dx, dy, grid_size=10):
        self.x = (self.x + dx) % grid_size
        self.y = (self.y + dy) % grid_size
    
    def mutate(self):
        """变异复制"""
        child = Agent(self.x, self.y)
        child.energy = self.energy // 2
        self.energy = self.energy // 2
        child.w1 = self.w1 + np.random.randn(9, 8) * 0.1
        child.w2_act = self.w2_act + np.random.randn(8, 4) * 0.1
        child.w2_pred = self.w2_pred + np.random.randn(8, 9) * 0.1
        return child


class EvolutionEngine:
    """演化引擎"""
    @staticmethod
    def select(agents):
        """选择"""
        return [a for a in agents if a.alive and a.energy > 0]
    
    @staticmethod
    def reproduce(agents):
        """繁殖"""
        new_agents = []
        for a in agents:
            if a.energy >= 50:
                new_agents.append(a.mutate())
        return agents + new_agents
    
    @staticmethod
    def maintain(agents, min_count=3, grid_size=10):
        """维持种群"""
        while len(agents) < min_count:
            agents.append(Agent(random.randint(0, grid_size-1), random.randint(0, grid_size-1)))
        return agents


def run(steps=500, grid_size=10, n_agents=15):
    """运行实验"""
    env = Environment(grid_size)
    agents = [Agent(random.randint(0, grid_size-1), random.randint(0, grid_size-1)) for _ in range(n_agents)]
    
    for step in range(steps):
        env.step()
        
        for a in agents:
            if not a.alive: continue
            
            obs = env.get_view(a.x, a.y)
            (dx, dy), pred = a.act(obs)
            a.move(dx, dy, grid_size)
            a.energy -= 1
            
            # 吃食物
            for f in list(env.food):
                if f.x == a.x and f.y == a.y:
                    a.energy += 15
                    env.food.remove(f)
            
            # 预测
            future = env.get_view(a.x, a.y)
            err = np.mean((pred - future) ** 2)
            a.predict_total += 1
            if err < 0.4:
                a.energy += 2
                a.predict_success += 1
        
        agents = EvolutionEngine.select(agents)
        agents = EvolutionEngine.reproduce(agents)
        agents = EvolutionEngine.maintain(agents, grid_size=grid_size)
        
        if step % 100 == 0:
            print(f"Step {step}: Agents={len(agents)}")
    
    return agents


if __name__ == "__main__":
    agents = run()
    print(f"Done! Final: {len(agents)} agents")
