"""
AES - 对抗涌现系统
最小实验实现 v0.1

核心思想：
- 预测驱动表征涌现
- 压缩状态预测
- 资源有限 + 能量竞争
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Tuple
import random


# ==================== 配置 ====================
CONFIG = {
    'grid_size': 16,        # 网格大小
    'n_agents': 20,         # Agent数量
    'n_food': 8,            # 食物数量
    'n_predator': 2,        # 捕食者数量
    'steps': 10000,         # 运行步数
    'energy_init': 50,      # 初始能量
    'energy_per_step': 1,   # 每步消耗
    'food_energy': 20,      # 食物能量
    'mutation_rate': 0.1,   # 变异率
    'mutation_strength': 0.2,  # 变异强度
    'reproduce_threshold': 80,  # 复制阈值
    'predict_delta': 3,    # 预测未来步数
}


# ==================== 环境 ====================
class Entity:
    """实体"""
    def __init__(self, x, y, entity_type='food'):
        self.x = x
        self.y = y
        self.type = entity_type  # 'food', 'predator'
        self.vx = 0
        self.vy = 0
    
    def move(self, dx, dy):
        """移动"""
        self.x = (self.x + dx) % CONFIG['grid_size']
        self.y = (self.y + dy) % CONFIG['grid_size']


class Environment:
    """环境"""
    def __init__(self):
        self.size = CONFIG['grid_size']
        self.food: List[Entity] = []
        self.predators: List[Entity] = []
        self.history = []  # 历史状态（用于预测）
        
        # 初始化食物
        for _ in range(CONFIG['n_food']):
            self.add_food()
        
        # 初始化捕食者
        for _ in range(CONFIG['n_predator']):
            self.add_predator()
    
    def add_food(self):
        x = random.randint(0, self.size-1)
        y = random.randint(0, self.size-1)
        self.food.append(Entity(x, y, 'food'))
    
    def add_predator(self):
        x = random.randint(0, self.size-1)
        y = random.randint(0, self.size-1)
        p = Entity(x, y, 'predator')
        # 随机速度
        p.vx = random.choice([-1, 0, 1])
        p.vy = random.choice([-1, 0, 1])
        self.predators.append(p)
    
    def step(self):
        """环境一步"""
        # 移动捕食者
        for p in self.predators:
            p.move(p.vx, p.vy)
            # 随机改变方向
            if random.random() < 0.2:
                p.vx = random.choice([-1, 0, 1])
                p.vy = random.choice([-1, 0, 1])
        
        # 补充食物
        while len(self.food) < CONFIG['n_food']:
            self.add_food()
        
        # 记录历史（用于预测训练）
        state = self.get_state()
        self.history.append(state)
        if len(self.history) > CONFIG['predict_delta'] + 10:
            self.history.pop(0)
    
    def get_state(self) -> np.ndarray:
        """获取环境状态（压缩表示）"""
        # 简化为：食物位置热力图 + 捕食者位置
        state = np.zeros((self.size, self.size))
        
        for f in self.food:
            state[f.y, f.x] += 1
        
        for p in self.predators:
            state[p.y, p.x] -= 1
        
        return state.flatten()
    
    def get_local_view(self, x: int, y: int, view_size: int = 3) -> np.ndarray:
        """获取局部视野"""
        half = view_size // 2
        view = np.zeros((view_size, view_size))
        
        for dy in range(-half, half+1):
            for dx in range(-half, half+1):
                nx = (x + dx) % self.size
                ny = (y + dy) % self.size
                
                # 检查食物
                for f in self.food:
                    if f.x == nx and f.y == ny:
                        view[dy+half, dx+half] = 1
                
                # 检查捕食者
                for p in self.predators:
                    if p.x == nx and p.y == ny:
                        view[dy+half, dx+half] = -1
        
        return view.flatten()
    
    def get_future_state(self, delta: int) -> np.ndarray:
        """获取未来状态（用于预测目标）"""
        if len(self.history) <= delta:
            return self.get_state()
        return self.history[-delta]


# ==================== Agent ====================
class Agent:
    """Agent"""
    next_id = 0
    
    def __init__(self, x, y):
        self.id = Agent.next_id
        Agent.next_id += 1
        
        self.x = x
        self.y = y
        self.energy = CONFIG['energy_init']
        self.alive = True
        
        # 神经网络权重（可遗传）
        # 输入：局部视野 + 当前能量
        # 输出：动作 + 预测
        input_dim = CONFIG['predict_delta'] * 3 * 3 + 1  # 历史视野 + 能量
        hidden_dim = 8
        output_dim = 5  # 4方向 + 停留
        
        # 初始化权重
        self.w1 = np.random.randn(input_dim, hidden_dim) * 0.1
        self.b1 = np.zeros(hidden_dim)
        self.w2 = np.random.randn(hidden_dim, output_dim) * 0.1
        self.b2 = np.zeros(output_dim)
        
        # 预测网络（预测未来状态）
        self.predict_w = np.random.randn(hidden_dim, input_dim) * 0.1
        
        # 历史记录
        self.observation_history = []
        self.prediction_history = []
        self.fitness = 0
    
    def forward(self, obs: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """前向传播"""
        # 动作网络
        h = np.tanh(np.dot(obs, self.w1) + self.b1)
        action_logits = np.dot(h, self.w2) + self.b2
        
        # 预测网络
        prediction = np.tanh(np.dot(h, self.predict_w))
        
        return action_logits, prediction
    
    def act(self, action_logits: np.ndarray) -> Tuple[int, int]:
        """根据动作 logits 选择动作"""
        # softmax + 采样
        exp_logits = np.exp(action_logits - np.max(action_logits))
        probs = exp_logits / exp_logits.sum()
        
        action = np.random.choice(len(probs), p=probs)
        
        # 动作映射
        if action == 0:
            dx, dy = 0, -1  # 上
        elif action == 1:
            dx, dy = 0, 1   # 下
        elif action == 2:
            dx, dy = -1, 0  # 左
        elif action == 3:
            dx, dy = 1, 0   # 右
        else:
            dx, dy = 0, 0   # 停留
        
        return dx, dy
    
    def move(self, dx, dy):
        """移动"""
        self.x = (self.x + dx) % CONFIG['grid_size']
        self.y = (self.y + dy) % CONFIG['grid_size']
    
    def mutate(self) -> 'Agent':
        """变异复制"""
        child = Agent(self.x, self.y)
        child.energy = self.energy // 2
        self.energy = self.energy // 2
        
        # 复制权重
        child.w1 = self.w1 + np.random.randn(*self.w1.shape) * CONFIG['mutation_strength']
        child.b1 = self.b1 + np.random.randn(*self.b1.shape) * CONFIG['mutation_strength']
        child.w2 = self.w2 + np.random.randn(*self.w2.shape) * CONFIG['mutation_strength']
        child.b2 = self.b2 + np.random.randn(*self.b2.shape) * CONFIG['mutation_strength']
        child.predict_w = self.predict_w + np.random.randn(*self.predict_w.shape) * CONFIG['mutation_strength']
        
        return child
    
    def copy_weights_from(self, other: 'Agent'):
        """从其他Agent复制权重（用于学习）"""
        self.w1 = other.w1.copy()
        self.b1 = other.b1.copy()
        self.w2 = other.w2.copy()
        self.b2 = other.b2.copy()
        self.predict_w = other.predict_w.copy()


# ==================== 实验 ====================
class Experiment:
    """实验"""
    def __init__(self):
        self.env = Environment()
        self.agents: List[Agent] = []
        
        # 初始化Agent
        for _ in range(CONFIG['n_agents']):
            x = random.randint(0, CONFIG['grid_size']-1)
            y = random.randint(0, CONFIG['grid_size']-1)
            self.agents.append(Agent(x, y))
        
        # 统计
        self.stats = {
            'steps': [],
            'n_agents': [],
            'avg_energy': [],
            'avg_fitness': [],
        }
    
    def step(self):
        """一步"""
        # 环境更新
        self.env.step()
        
        # 记录观察历史
        for agent in self.agents:
            if not agent.alive:
                continue
            
            # 获取局部视野
            obs = self.env.get_local_view(agent.x, agent.y)
            agent.observation_history.append(obs)
            
            # 保持历史长度
            if len(agent.observation_history) > CONFIG['predict_delta']:
                agent.observation_history.pop(0)
        
        # Agent决策
        for agent in self.agents:
            if not agent.alive:
                continue
            
            # 构建输入（历史视野 + 当前能量）
            if len(agent.observation_history) >= CONFIG['predict_delta']:
                obs_history = np.concatenate(agent.observation_history[-CONFIG['predict_delta']:])
            else:
                obs_history = np.zeros(CONFIG['predict_delta'] * 9)
            
            obs = np.append(obs_history, agent.energy / 100.0)
            
            # 前向传播
            action_logits, prediction = agent.forward(obs)
            
            # 记录预测
            agent.prediction_history.append(prediction)
            
            # 动作
            dx, dy = agent.act(action_logits)
            agent.move(dx, dy)
            
            # 能量消耗
            agent.energy -= CONFIG['energy_per_step']
            
            # 吃食物
            for f in self.env.food[:]:
                if f.x == agent.x and f.y == agent.y:
                    agent.energy += CONFIG['food_energy']
                    self.env.food.remove(f)
            
            # 遇到捕食者
            for p in self.env.predators:
                if p.x == agent.x and p.y == agent.y:
                    agent.energy = 0  # 死亡
                    agent.alive = False
            
            # 预测奖励
            if len(agent.prediction_history) >= 2 and len(agent.observation_history) >= 2:
                # 比较当前预测和下一时刻观察
                current_pred = agent.prediction_history[-1]
                next_obs = agent.observation_history[-1]
                
                # 对齐维度
                min_len = min(len(current_pred), len(next_obs))
                pred_error = np.mean((current_pred[:min_len] - next_obs[:min_len])**2)
                
                # 预测好 → 能量奖励
                if pred_error < 0.5:
                    agent.energy += 2
                
                agent.fitness += (1 - pred_error)
        
        # 死亡清理
        self.agents = [a for a in self.agents if a.alive and a.energy > 0]
        
        # 复制（能量超阈值）
        new_agents = []
        for agent in self.agents:
            if agent.energy >= CONFIG['reproduce_threshold']:
                child = agent.mutate()
                new_agents.append(child)
        
        self.agents.extend(new_agents)
        
        # 防止灭绝：补充Agent
        while len(self.agents) < 5:
            x = random.randint(0, CONFIG['grid_size']-1)
            y = random.randint(0, CONFIG['grid_size']-1)
            self.agents.append(Agent(x, y))
    
    def run(self):
        """运行实验"""
        print("=" * 50)
        print("AES 最小实验开始")
        print("=" * 50)
        print(f"配置: {CONFIG}")
        
        for step in range(CONFIG['steps']):
            self.step()
            
            if step % 500 == 0:
                n_agents = len(self.agents)
                avg_energy = np.mean([a.energy for a in self.agents]) if self.agents else 0
                avg_fitness = np.mean([a.fitness for a in self.agents]) if self.agents else 0
                
                self.stats['steps'].append(step)
                self.stats['n_agents'].append(n_agents)
                self.stats['avg_energy'].append(avg_energy)
                self.stats['avg_fitness'].append(avg_fitness)
                
                print(f"Step {step}: Agent数={n_agents}, "
                      f"平均能量={avg_energy:.1f}, "
                      f"平均适应度={avg_fitness:.2f}")
        
        print("\n实验完成!")
        return self.stats


# ==================== 主程序 ====================
if __name__ == "__main__":
    exp = Experiment()
    stats = exp.run()
    
    print("\n最终统计:")
    print(f"  Agent数: {stats['n_agents'][-1]}")
    print(f"  平均能量: {stats['avg_energy'][-1]:.1f}")
    print(f"  平均适应度: {stats['avg_fitness'][-1]:.2f}")
