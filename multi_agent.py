"""
AES 多Agent对抗实验
核心：Agent之间相互对抗，预测对方行为
涌现：策略对抗、 Theory of Mind
"""

import numpy as np
import random


CONFIG = {
    'grid_size': 10,
    'n_agents': 10,      # 两组对抗
    'n_food': 4,
    'steps': 1000,
    'energy_init': 25,
    'food_energy': 10,
    'predict_reward': 2,
    'mutual_predict_reward': 3,  # 互相预测奖励
}


class Agent:
    def __init__(self, x, y, team=0):
        self.x = x
        self.y = y
        self.team = team  # 0=蓝队, 1=红队
        self.energy = CONFIG['energy_init']
        self.alive = True
        
        # 网络: 输入9 + 对方视野9 → 隐藏8 → 动作4 + 预测自己+预测对方
        self.w1 = np.random.randn(18, 8) * 0.1
        self.w2_act = np.random.randn(8, 4) * 0.1
        self.w2_pred_self = np.random.randn(8, 9) * 0.1
        self.w2_pred_other = np.random.randn(8, 9) * 0.1
        
        self.predict_success = 0
        self.predict_total = 0
    
    def get_view_with_team(self, agents, food_list, my_team):
        """获取视野，区分敌我"""
        view = np.zeros(9)
        idx = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                nx = (self.x + dx) % 10
                ny = (self.y + dy) % 10
                
                # 食物
                for f in food_list:
                    if f[0] == nx and f[1] == ny:
                        view[idx] = 1
                
                # 队友=2, 敌人=-1
                for a in agents:
                    if a.alive and a.x == nx and a.y == ny:
                        if a.team == my_team:
                            view[idx] = 2
                        else:
                            view[idx] = -1
                
                idx += 1
        return view
    
    def act(self, obs, other_obs):
        # 合并视野
        combined = np.concatenate([obs, other_obs])
        h = np.tanh(np.dot(combined, self.w1))
        
        act = np.argmax(np.dot(h, self.w2_act))
        pred_self = np.tanh(np.dot(h, self.w2_pred_self))
        pred_other = np.tanh(np.dot(h, self.w2_pred_other))
        
        if act == 0: dx, dy = 0, -1
        elif act == 1: dx, dy = 0, 1
        elif act == 2: dx, dy = -1, 0
        else: dx, dy = 1, 0
        
        return dx, dy, pred_self, pred_other
    
    def move(self, dx, dy):
        self.x = (self.x + dx) % 10
        self.y = (self.y + dy) % 10
    
    def mutate(self):
        child = Agent(self.x, self.y, self.team)
        child.energy = self.energy // 2
        self.energy = self.energy // 2
        
        child.w1 = self.w1 + np.random.randn(18, 8) * 0.1
        child.w2_act = self.w2_act + np.random.randn(8, 4) * 0.1
        child.w2_pred_self = self.w2_pred_self + np.random.randn(8, 9) * 0.1
        child.w2_pred_other = self.w2_pred_other + np.random.randn(8, 9) * 0.1
        
        return child


def run():
    print("=" * 50)
    print("AES 多Agent对抗实验")
    print("=" * 50)
    print("目标: 预测对方行为 -> Theory of Mind")
    
    # 初始化：两队对抗
    agents = []
    for i in range(CONFIG['n_agents']):
        team = i % 2
        agents.append(Agent(random.randint(0,9), random.randint(0,9), team))
    
    # 食物
    food = [(random.randint(0,9), random.randint(0,9)) for _ in range(CONFIG['n_food'])]
    
    stats = {'steps': [], 'teams': [], 'avg_energy': [], 'predict_rate': []}
    
    for step in range(CONFIG['steps']):
        # 补充食物
        while len(food) < CONFIG['n_food']:
            food.append((random.randint(0,9), random.randint(0,9)))
        
        # 获取所有视野
        all_views = {}
        for a in agents:
            if a.alive:
                all_views[a] = a.get_view_with_team(agents, food, a.team)
        
        # Agent行动
        for a in agents:
            if not a.alive:
                continue
            
            obs = all_views[a]
            
            # 找最近的敌人
            nearest_enemy = None
            min_dist = 999
            for other in agents:
                if other.alive and other.team != a.team:
                    d = abs(other.x - a.x) + abs(other.y - a.y)
                    if d < min_dist:
                        min_dist = d
                        nearest_enemy = other
            
            # 获取敌人视野
            if nearest_enemy and nearest_enemy in all_views:
                other_obs = all_views[nearest_enemy]
            else:
                other_obs = np.zeros(9)
            
            # 行动
            dx, dy, pred_self, pred_other = a.act(obs, other_obs)
            a.move(dx, dy)
            a.energy -= 1
            
            # 吃食物
            if (a.x, a.y) in food:
                a.energy += CONFIG['food_energy']
                food.remove((a.x, a.y))
            
            # 预测奖励
            future_self = all_views.get(a, np.zeros(9))
            err_self = np.mean((pred_self - future_self) ** 2)
            a.predict_total += 1
            
            if err_self < 0.5:
                a.energy += CONFIG['predict_reward']
                a.predict_success += 1
            
            # 互相预测奖励
            if nearest_enemy and nearest_enemy in all_views:
                future_other = all_views[nearest_enemy]
                err_other = np.mean((pred_other - future_other) ** 2)
                if err_other < 0.5:
                    a.energy += CONFIG['mutual_predict_reward']
        
        # 死亡
        agents = [a for a in agents if a.alive and a.energy > 0]
        
        # 复制
        for a in agents:
            if a.energy >= 40:
                agents.append(a.mutate())
        
        # 防止灭绝
        for team in [0, 1]:
            team_agents = [a for a in agents if a.team == team]
            if len(team_agents) < 2:
                agents.append(Agent(random.randint(0,9), random.randint(0,9), team))
        
        # 记录
        if step % 100 == 0:
            team0 = len([a for a in agents if a.team == 0])
            team1 = len([a for a in agents if a.team == 1])
            avg_e = np.mean([a.energy for a in agents]) if agents else 0
            pred_r = np.mean([a.predict_success/max(1,a.predict_total) for a in agents]) if agents else 0
            
            stats['steps'].append(step)
            stats['teams'].append((team0, team1))
            stats['avg_energy'].append(avg_e)
            stats['predict_rate'].append(pred_r)
            
            print(f"Step {step}: 蓝队={team0}, 红队={team1}, 能量={avg_e:.1f}, 预测={pred_r:.1%}")
    
    print("\n完成!")
    
    # 分析
    if agents:
        team0_final = len([a for a in agents if a.team == 0])
        team1_final = len([a for a in agents if a.team == 1])
        print(f"最终: 蓝队={team0_final}, 红队={team1_final}")
        
        # 检查是否涌现策略
        print("\n=== 涌现检查 ===")
        print(f"存活Agent: {len(agents)}")
        
        # 策略分化
        actions = []
        for a in agents[:5]:
            obs = a.get_view_with_team(agents, a.team)
            h = np.tanh(np.dot(obs, a.w1))
            act = np.argmax(np.dot(h, a.w2_act))
            actions.append(act)
        print(f"策略分化: {len(set(actions))}种")
    
    return stats, agents


if __name__ == "__main__":
    run()
