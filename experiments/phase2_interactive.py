"""
AES 阶段2: 可交互实体实验
目标: 因果理解 - Agent理解推拉、阻挡等交互
"""

import numpy as np
import random


class Entity:
    """可交互实体"""
    def __init__(self, etype='box', x=None, y=None, grid_size=10):
        self.x = x if x is not None else random.randint(0, grid_size-1)
        self.y = y if y is not None else random.randint(0, grid_size-1)
        self.type = etype  # box=可推动, wall=墙壁, food=食物
        self.mass = 1 if etype == 'box' else 0
        self.pushed = False  # 本轮是否被推动


class Agent:
    """能理解因果的Agent"""
    def __init__(self, x, y, grid_size=10):
        self.x = x
        self.y = y
        self.energy = 30
        self.alive = True
        self.grid_size = grid_size
        
        # 网络: 输入(9视野+4交互) → 隐藏8 → 输出(4动作+9预测+4因果)
        self.w1 = np.random.randn(13, 8) * 0.1  # 9视野 + 4交互特征
        self.w2_act = np.random.randn(8, 4) * 0.1
        self.w2_pred = np.random.randn(8, 9) * 0.1
        self.w2_causal = np.random.randn(8, 4) * 0.1  # 因果预测
        
        self.predict_success = 0
        self.predict_total = 0
        self.causal_success = 0
        self.causal_total = 0
    
    def get_view_with_interaction(self, entities):
        """获取视野+交互特征"""
        view = np.zeros(9)  # 物体位置
        interact = np.zeros(4)  # 交互特征: [可推动, 墙壁, 食物, 另一个Agent]
        
        idx = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                nx = (self.x + dx) % self.grid_size
                ny = (self.y + dy) % self.grid_size
                
                for e in entities:
                    if e.x == nx and e.y == ny:
                        if e.type == 'box':
                            view[idx] = 0.5
                            interact[0] = 1  # 可推动
                        elif e.type == 'wall':
                            view[idx] = -0.5
                            interact[1] = 1  # 墙壁
                        elif e.type == 'food':
                            view[idx] = 1
                            interact[2] = 1  # 食物
                
                idx += 1
        
        return np.concatenate([view, interact])
    
    def act(self, obs):
        """行动+预测+因果理解"""
        h = np.tanh(np.dot(obs, self.w1))
        
        act = np.argmax(np.dot(h, self.w2_act))
        pred = np.tanh(np.dot(h, self.w2_pred))
        causal = np.tanh(np.dot(h, self.w2_causal))  # 因果预测
        
        moves = [(0,-1), (0,1), (-1,0), (1,0)]
        return moves[act], pred, causal
    
    def move(self, dx, dy):
        self.x = (self.x + dx) % self.grid_size
        self.y = (self.y + dy) % self.grid_size


def push_entity(agent, dx, dy, entities, grid_size):
    """推动实体 - 因果交互"""
    new_x = (agent.x + dx) % grid_size
    new_y = (agent.y + dy) % grid_size
    
    # 检查是否有可推动物体
    pushed = None
    for e in entities:
        if e.x == new_x and e.y == new_y and e.type == 'box':
            pushed = e
            break
    
    if pushed:
        # 推动物体到下一个位置
        push_x = (new_x + dx) % grid_size
        push_y = (new_y + dy) % grid_size
        
        # 检查是否被阻挡
        blocked = False
        for e in entities:
            if e.x == push_x and e.y == push_y and e.type != 'food':
                blocked = True
                break
        
        if not blocked:
            pushed.x = push_x
            pushed.y = push_y
            pushed.pushed = True
            return True, "pushed"
        else:
            return False, "blocked"
    
    return None, "nothing"


def run_experiment(steps=1000, grid_size=10, n_agents=8, n_boxes=4):
    """运行阶段2实验"""
    print("=" * 50)
    print("AES 阶段2: 可交互实体实验")
    print("=" * 50)
    print("目标: 理解推拉、阻挡等因果关系")
    
    # 初始化
    agents = [Agent(random.randint(0, grid_size-1), random.randint(0, grid_size-1), grid_size) 
              for _ in range(n_agents)]
    
    # 可交互实体: 箱子(可推动) + 墙壁(不可动) + 食物
    entities = [Entity('box', grid_size=grid_size) for _ in range(n_boxes)]
    entities.append(Entity('wall', 0, 0, grid_size))  # 角落墙壁
    entities.append(Entity('wall', grid_size-1, 0, grid_size))
    entities.append(Entity('wall', 0, grid_size-1, grid_size))
    entities.append(Entity('food', grid_size//2, grid_size//2, grid_size))
    
    stats = {
        'steps': [],
        'n_agents': [],
        'pushes': [],
        'causal_acc': [],
    }
    
    total_pushes = 0
    
    for step in range(steps):
        # 重置实体状态
        for e in entities:
            e.pushed = False
        
        for a in agents:
            if not a.alive:
                continue
            
            # 获取视野+交互
            obs = a.get_view_with_interaction(entities)
            
            # 行动
            (dx, dy), pred, causal = a.act(obs)
            
            # 尝试推动
            pushed, result = push_entity(a, dx, dy, entities, grid_size)
            if pushed:
                total_pushes += 1
            
            # 移动
            a.move(dx, dy)
            a.energy -= 1
            
            # 吃食物
            for e in list(entities):
                if e.type == 'food' and e.x == a.x and e.y == a.y:
                    a.energy += 20
                    entities.remove(e)
                    entities.append(Entity('food', grid_size=grid_size))
            
            # 预测奖励
            future = a.get_view_with_interaction(entities)
            pred_err = np.mean((pred - future[:9]) ** 2)
            a.predict_total += 1
            
            if pred_err < 0.5:
                a.energy += 2
                a.predict_success += 1
            
            # 因果理解: 预测推动结果
            causal_err = np.mean(causal ** 2)  # 简化
            a.causal_total += 1
        
        # 死亡和复制
        agents = [a for a in agents if a.alive and a.energy > 0]
        for a in agents:
            if a.energy >= 50:
                child = Agent(a.x, a.y, grid_size)
                child.energy = a.energy // 2
                a.energy = a.energy // 2
                agents.append(child)
        
        # 维持
        while len(agents) < 3:
            agents.append(Agent(random.randint(0, grid_size-1), random.randint(0, grid_size-1), grid_size))
        
        # 记录
        if step % 100 == 0:
            n = len(agents)
            pred_rate = np.mean([a.predict_success/max(1,a.predict_total) for a in agents]) if agents else 0
            
            stats['steps'].append(step)
            stats['n_agents'].append(n)
            stats['pushes'].append(total_pushes)
            stats['causal_acc'].append(pred_rate)
            
            print(f"Step {step}: Agents={n}, 推动次数={total_pushes}, 预测准确率={pred_rate:.1%}")
    
    print("\n" + "=" * 50)
    print("实验完成!")
    print(f"总推动次数: {total_pushes}")
    
    # 分析因果理解
    if agents:
        print("\n=== 因果理解分析 ===")
        print(f"存活Agent: {len(agents)}")
        
        # 检查是否学会推动
        for i, a in enumerate(agents[:3]):
            print(f"Agent{i}: 预测={a.predict_success/max(1,a.predict_total):.1%}")
    
    return stats, agents, total_pushes


if __name__ == "__main__":
    run_experiment()
