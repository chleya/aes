"""
AES - 对抗涌现系统
v0.3 - 加入预测压缩机制

核心：
- 预测未来状态 → 获得能量
- 表征涌现
"""

import numpy as np
import random


CONFIG = {
    'grid_size': 12,
    'n_agents': 20,
    'n_food': 5,
    'steps': 3000,
    'energy_init': 25,
    'energy_per_step': 1,
    'food_energy': 12,
    'mutation_strength': 0.15,
    'reproduce_threshold': 40,
    'predict_reward': 2,  # 预测正确奖励
    'predict_window': 3,  # 观察窗口
}


class Env:
    def __init__(self):
        self.size = CONFIG['grid_size']
        self.food = []
        for _ in range(CONFIG['n_food']):
            self.add_food()
    
    def add_food(self):
        x = random.randint(0, self.size-1)
        y = random.randint(0, self.size-1)
        self.food.append((x, y))
    
    def step(self):
        while len(self.food) < CONFIG['n_food']:
            self.add_food()
    
    def get_view(self, x, y):
        """3x3视野 + 食物热力"""
        view = np.zeros(9)
        idx = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                nx = (x + dx) % self.size
                ny = (y + dy) % self.size
                for fx, fy in self.food:
                    if fx == nx and fy == ny:
                        view[idx] = 1
                idx += 1
        return view
    
    def get_full_state(self):
        """完整状态（用于预测目标）"""
        state = np.zeros(self.size * self.size)
        for fx, fy in self.food:
            state[fy * self.size + fx] = 1
        return state


class Agent:
    next_id = 0
    
    def __init__(self, x, y):
        self.id = Agent.next_id
        Agent.next_id += 1
        self.x = x
        self.y = y
        self.energy = CONFIG['energy_init']
        self.alive = True
        
        # 观察历史（用于预测）
        self.obs_history = []
        
        # 网络：输入9 → 隐藏8 → 输出4（动作）+ 9（预测）
        self.w1 = np.random.randn(9, 8) * 0.1
        self.b1 = np.zeros(8)
        self.w2_act = np.random.randn(8, 4) * 0.1
        self.w2_pred = np.random.randn(8, 9) * 0.1
        self.b2 = np.zeros(4)
        
        self.fitness = 0
        self.predict_success = 0
        self.predict_total = 0
    
    def forward(self, obs):
        h = np.tanh(np.dot(obs, self.w1) + self.b1)
        act_logits = np.dot(h, self.w2_act) + self.b2
        pred = np.tanh(np.dot(h, self.w2_pred))
        return act_logits, pred
    
    def act(self, obs):
        act_logits, pred = self.forward(obs)
        action = np.argmax(act_logits)
        
        if action == 0:
            dx, dy = 0, -1
        elif action == 1:
            dx, dy = 0, 1
        elif action == 2:
            dx, dy = -1, 0
        else:
            dx, dy = 1, 0
        
        return dx, dy, pred
    
    def move(self, dx, dy):
        self.x = (self.x + dx) % CONFIG['grid_size']
        self.y = (self.y + dy) % CONFIG['grid_size']
    
    def mutate(self):
        child = Agent(self.x, self.y)
        child.energy = self.energy // 2
        self.energy = self.energy // 2
        
        # 变异
        child.w1 = self.w1 + np.random.randn(9, 8) * CONFIG['mutation_strength']
        child.b1 = self.b1 + np.random.randn(8) * CONFIG['mutation_strength']
        child.w2_act = self.w2_act + np.random.randn(8, 4) * CONFIG['mutation_strength']
        child.w2_pred = self.w2_pred + np.random.randn(8, 9) * CONFIG['mutation_strength']
        
        return child


def run():
    print("=" * 50)
    print("AES v0.3 - 预测压缩机制")
    print("=" * 50)
    
    env = Env()
    agents = []
    
    # 初始化
    for _ in range(CONFIG['n_agents']):
        x = random.randint(0, CONFIG['grid_size']-1)
        y = random.randint(0, CONFIG['grid_size']-1)
        agents.append(Agent(x, y))
    
    stats = {'steps': [], 'n_agents': [], 'avg_energy': [], 'predict_rate': []}
    
    for step in range(CONFIG['steps']):
        env.step()
        
        for a in agents:
            if not a.alive:
                continue
            
            # 观察
            obs = env.get_view(a.x, a.y)
            a.obs_history.append(obs)
            if len(a.obs_history) > CONFIG['predict_window']:
                a.obs_history.pop(0)
            
            # 行动 + 预测
            dx, dy, pred = a.act(obs)
            a.move(dx, dy)
            
            # 能量消耗
            a.energy -= CONFIG['energy_per_step']
            
            # 吃食物
            for f in list(env.food):
                if f[0] == a.x and f[1] == a.y:
                    a.energy += CONFIG['food_energy']
                    env.food.remove(f)
            
            # 预测奖励（核心机制！）
            if len(a.obs_history) >= CONFIG['predict_window']:
                # 下一步的真实观察
                next_obs = env.get_view(a.x, a.y)
                
                # 预测误差
                pred_error = np.mean((pred - next_obs) ** 2)
                a.predict_total += 1
                
                # 预测好 → 能量奖励
                if pred_error < 0.3:
                    a.energy += CONFIG['predict_reward']
                    a.predict_success += 1
                    a.fitness += 1
                else:
                    a.fitness -= pred_error
        
        # 死亡
        agents = [a for a in agents if a.alive and a.energy > 0]
        
        # 复制
        new_agents = []
        for a in agents:
            if a.energy >= CONFIG['reproduce_threshold']:
                new_agents.append(a.mutate())
        agents.extend(new_agents)
        
        # 防止灭绝
        while len(agents) < 5:
            x = random.randint(0, CONFIG['grid_size']-1)
            y = random.randint(0, CONFIG['grid_size']-1)
            agents.append(Agent(x, y))
        
        # 记录
        if step % 300 == 0:
            n = len(agents)
            avg_e = np.mean([a.energy for a in agents]) if agents else 0
            pred_rate = np.mean([a.predict_success/max(1,a.predict_total) for a in agents]) if agents else 0
            
            stats['steps'].append(step)
            stats['n_agents'].append(n)
            stats['avg_energy'].append(avg_e)
            stats['predict_rate'].append(pred_rate)
            
            print(f"Step {step}: Agent数={n}, "
                  f"平均能量={avg_e:.1f}, "
                  f"预测准确率={pred_rate:.2%}")
    
    print("\n完成!")
    print(f"最终Agent数: {len(agents)}")
    
    # 最终统计
    if agents:
        pred_rates = [a.predict_success/max(1,a.predict_total) for a in agents]
        print(f"预测准确率: {np.mean(pred_rates):.2%}")
        
        # 检查是否有涌现
        print("\n=== 涌现检查 ===")
        print(f"Agent数: {len(agents)}")
        print(f"预测准确率分布: min={min(pred_rates):.2%}, max={max(pred_rates):.2%}")
        
        # 权重分化检查
        weights = [np.mean(a.w2_pred) for a in agents]
        print(f"预测权重分化: {np.std(weights):.4f}")
    
    return stats, agents


if __name__ == "__main__":
    stats, agents = run()
