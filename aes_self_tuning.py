"""
AES Self-Tuning System
系统自己调整，不是人工调参
"""

import random


class SelfTuningAgent:
    """自调Agent"""
    def __init__(s, x, y):
        s.x, s.y = x, y
        s.e = 30  # 能量作为"投票"
        
        # 初始策略参数（让系统自己调整）
        s.learning_rate = 0.1  # 自己调整
        s.explore_rate = 0.2   # 自己调整
        s.predict_weight = 0.5  # 自己调整
        
        # 网络权重
        s.w = [[random.random()*0.2-0.1 for _ in range(9)] for _ in range(4)]
    
    def act(s, view):
        # 探索 vs 利用
        if random.random() < s.explore_rate:
            # 探索：随机动作
            moves = [(0,-1),(0,1),(-1,0),(1,0)]
            return random.choice(moves)
        else:
            # 利用：基于权重
            scores = [sum(v*w for v,w in zip(view,row)) for row in s.w]
            moves = [(0,-1),(0,1),(-1,0),(1,0)]
            return moves[scores.index(max(scores))]
    
    def adjust(s, energy_delta):
        """根据能量反馈自动调整参数"""
        if energy_delta > 0:
            # 奖励：强化当前策略
            if s.explore_rate > 0.05:
                s.explore_rate *= 0.95  # 减少探索
        else:
            # 惩罚：增加探索
            if s.explore_rate < 0.5:
                s.explore_rate *= 1.1
    
    def mutate(s):
        """变异：调整参数+权重"""
        child = SelfTuningAgent(s.x, s.y)
        
        # 参数变异
        child.learning_rate = s.learning_rate + random.random()*0.02-0.01
        child.explore_rate = s.explore_rate + random.random()*0.1-0.05
        child.predict_weight = s.predict_weight + random.random()*0.1-0.05
        
        # 权重变异
        child.w = [[w + random.random()*0.1-0.05 for w in row] for row in s.w]
        
        return child


def run_self_tuning(steps=1000):
    print("AES Self-Tuning System")
    print("="*40)
    print("系统自己调整参数，不是人工")
    
    food = [(random.randint(0,9),random.randint(0,9)) for _ in range(6)]
    agents = [SelfTuningAgent(random.randint(0,9),random.randint(0,9)) for _ in range(10)]
    
    for st in range(steps):
        # 补充食物
        while len(food) < 6:
            food.append((random.randint(0,9),random.randint(0,9)))
        
        # Agent行动
        for a in agents:
            view = []
            for dy in [-1,0,1]:
                for dx in [-1,0,1]:
                    view.append(1 if ((a.x+dx)%10,(a.y+dy)%10) in food else 0)
            
            dx, dy = a.act(view)
            nx, ny = (a.x+dx)%10, (a.y+dy)%10
            
            # 吃食物
            energy_delta = -1  # 默认消耗
            if (nx, ny) in food:
                energy_delta = 19  # 奖励
                food.remove((nx, ny))
            
            a.x, a.y = nx, ny
            a.e += energy_delta
            
            # 自调参数
            a.adjust(energy_delta)
        
        # 死亡复制
        agents = [a for a in agents if a.e > 0]
        for a in agents:
            if a.e >= 50:
                agents.append(a.mutate())
                a.e //= 2
        
        # 维持
        while len(agents) < 5:
            agents.append(SelfTuningAgent(random.randint(0,9),random.randint(0,9)))
        
        # 记录
        if st % 200 == 0:
            n = len(agents)
            avg_exp = sum(a.explore_rate for a in agents) / max(1, n)
            print(f"Step {st}: Agents={n}, Explore={avg_exp:.2f}")

    print(f"\n完成! Agent数: {len(agents)}")


if __name__ == "__main__":
    run_self_tuning()
