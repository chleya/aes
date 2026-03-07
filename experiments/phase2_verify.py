"""
AES 阶段2验证实验
目标: 验证Agent能否理解因果(推拉、阻挡)
"""

import numpy as np
import random


class Entity:
    """可交互实体"""
    def __init__(self, etype, x, y):
        self.type = etype  # box, wall, food, goal
        self.x = x
        self.y = y
        self.pushed = False


class Agent:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.energy = 30
        self.alive = True
        
        # 网络: 9视野 + 4交互特征 -> 隐藏 -> 4动作 + 9预测
        self.w1 = np.random.randn(13, 8) * 0.1
        self.w2_act = np.random.randn(8, 4) * 0.1
        self.w2_pred = np.random.randn(8, 9) * 0.1
        
        self.predict_success = 0
        self.predict_total = 0
    
    def get_obs(self, entities, grid_size=10):
        """获取视野+交互特征"""
        view = np.zeros(9)      # 物体
        interact = np.zeros(4)  # [box, wall, food, goal]
        
        idx = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                nx = (self.x + dx) % grid_size
                ny = (self.y + dy) % grid_size
                
                for e in entities:
                    if e.x == nx and e.y == ny:
                        if e.type == 'box':
                            view[idx] = 0.5
                            interact[0] = 1
                        elif e.type == 'wall':
                            view[idx] = -0.5
                            interact[1] = 1
                        elif e.type == 'food':
                            view[idx] = 1
                            interact[2] = 1
                        elif e.type == 'goal':
                            interact[3] = 1
                idx += 1
        
        return np.concatenate([view, interact])
    
    def act(self, obs):
        h = np.tanh(np.dot(obs, self.w1))
        act = np.argmax(np.dot(h, self.w2_act))
        pred = np.tanh(np.dot(h, self.w2_pred))
        
        moves = [(0,-1), (0,1), (-1,0), (1,0)]
        return moves[act], pred
    
    def move(self, dx, dy, grid_size=10):
       self.x + dx self.x = () % grid_size
        self.y = (self.y + dy) % grid_size


def try_push(agent, dx, dy, entities, grid_size):
    """尝试推动"""
    nx = (agent.x + dx) % grid_size
    ny = (agent.y + dy) % grid_size
    
    # 找箱子
    box = None
    for e in entities:
        if e.type == 'box' and e.x == nx and e.y == ny:
            box = e
            break
    
    if not box:
        return False
    
    # 推动方向
    push_x = (nx + dx) % grid_size
    push_y = (ny + dy) % grid_size
    
    # 检查阻挡
    for e in entities:
        if e.type in ['wall', 'box'] and e.x == push_x and e.y == push_y:
            return False  # 被阻挡
    
    # 成功推动
    box.x = push_x
    box.y = push_y
    box.pushed = True
    return True


def run_trial(grid_size=8, n_agents=5, n_steps=300):
    """运行单次试验"""
    # 初始化: 箱子在中间，目标在角落
    box = Entity('box', grid_size//2, grid_size//2)
    goal = Entity('goal', grid_size-1, grid_size-1)
    wall = Entity('wall', grid_size//2, 0)  # 障碍
    
    entities = [box, goal, wall]
    
    # Agent从角落出发
    agents = [Agent(0, 0) for _ in range(n_agents)]
    
    for step in range(n_steps):
        for a in agents:
            if not a.alive:
                continue
            
            obs = a.get_obs(entities, grid_size)
            (dx, dy), pred = a.act(obs)
            
            # 尝试推动
            pushed = try_push(a, dx, dy, entities, grid_size)
            
            # 移动
            a.move(dx, dy, grid_size)
            a.energy -= 1
            
            # 推动奖励
            if pushed:
                a.energy += 5
            
            # 到达目标奖励
            if a.x == goal.x and a.y == goal.y:
                a.energy += 20
            
            # 预测奖励
            future = a.get_obs(entities, grid_size)
            err = np.mean((pred - future[:9])**2)
            a.predict_total += 1
            if err < 0.5:
                a.energy += 2
                a.predict_success += 1
        
        # 死亡
        agents = [a for a in agents if a.alive and a.energy > 0]
    
    # 结果
    box_moved = (box.x != grid_size//2 or box.y != grid_size//2)
    goal_reached = any(a.x == goal.x and a.y == goal.y for a in agents)
    pred_rate = np.mean([a.predict_success/max(1,a.predict_total) for a in agents]) if agents else 0
    
    return {
        'box_moved': box_moved,
        'goal_reached': goal_reached,
        'pred_rate': pred_rate,
        'survived': len(agents),
    }


def run_experiments(n_trials=10):
    """运行多次实验"""
    print("="*50)
    print("阶段2验证实验: 因果理解")
    print("="*50)
    
    results = []
    
    for trial in range(n_trials):
        r = run_trial()
        results.append(r)
        
        print(f"Trial {trial+1}: box_moved={r['box_moved']}, goal={r['goal_reached']}, pred={r['pred_rate']:.1%}, survived={r['survived']}")
    
    # 统计
    box_moved_rate = sum(r['box_moved'] for r in results) / n_trials
    goal_reached_rate = sum(r['goal_reached'] for r in results) / n_trials
    avg_pred = np.mean([r['pred_rate'] for r in results])
    avg_survived = np.mean([r['survived'] for r in results])
    
    print("\n=== 统计结果 ===")
    print(f"箱子推动率: {box_moved_rate:.0%}")
    print(f"目标达成率: {goal_reached_rate:.0%}")
    print(f"预测准确率: {avg_pred:.1%}")
    print(f"平均存活: {avg_survived:.1f}")
    
    return results


if __name__ == "__main__":
    run_experiments(10)
