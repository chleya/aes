"""
AES v1.0 - Agent Team版
多Agent分工 + 状态机 + 长时间运行
"""

import random


class PredictorAgent:
    """预测Agent - 预测视野"""
    def __init__(s):
        s.w = [[random.random()*0.2-0.1 for _ in range(9)] for _ in range(4)]
    
    def predict(s, view):
        return [sum(v*w for v,w in zip(view, row)) for row in s.w]


class ActorAgent:
    """行动Agent - 决策移动"""
    def __init__(s):
        s.w = [[random.random()*0.2-0.1 for _ in range(9)] for _ in range(4)]
    
    def act(s, view):
        scores = [sum(v*w for v,w in zip(view, row)) for row in s.w]
        moves = [(0,-1), (0,1), (-1,0), (1,0)]
        return moves[scores.index(max(scores))]


class EvolverAgent:
    """演化Agent - 变异复制"""
    @staticmethod
    def should_reproduce(energy):
        return energy >= 50
    
    @staticmethod
    def mutate(agent):
        child = Agent(agent.x, agent.y)
        child.e = agent.e // 2
        agent.e = agent.e // 2
        # 变异
        child.predictor.w = [[w + random.random()*0.1-0.05 for w in row] for row in agent.predictor.w]
        child.actor.w = [[w + random.random()*0.1-0.05 for w in row] for row in agent.actor.w]
        return child


class Agent:
    """完整Agent - 整合三个角色"""
    def __init__(s, x, y):
        s.x = x; s.y = y
        s.e = 30
        s.state = "idle"  # 状态机: idle→acting→reproducing→dead
        
        # 三个角色
        s.predictor = PredictorAgent()
        s.actor = ActorAgent()
        s.evolver = EvolverAgent()
    
    def step(s, view, food):
        # 状态机转换
        if s.e <= 0:
            s.state = "dead"
            return None
        
        if s.state == "idle":
            s.state = "acting"
        
        if s.state == "acting":
            # 预测
            pred = s.predictor.predict(view)
            # 行动
            dx, dy = s.actor.act(view)
            
            # 移动
            nx = (s.x + dx) % 10
            ny = (s.y + dy) % 10
            
            # 吃食物
            for f in food:
                if f == (nx, ny):
                    s.e += 20
                    food.remove(f)
                    break
            
            s.x, s.y = nx, ny
            s.e -= 1
            
            # 检查是否复制
            if s.evolver.should_reproduce(s.e):
                s.state = "reproducing"
                return s.evolver.mutate(s)
        
        return None


def run_autonomy(steps=1000):
    """长时间无人值守运行"""
    print("AES v1.0 - Agent Team")
    print("="*40)
    
    food = [(random.randint(0,9), random.randint(0,9)) for _ in range(5)]
    agents = [Agent(random.randint(0,9), random.randint(0,9)) for _ in range(10)]
    
    history = []
    
    for step in range(steps):
        # 补充食物
        while len(food) < 5:
            food.append((random.randint(0,9), random.randint(0,9)))
        
        # 获取视野
        views = {}
        for a in agents:
            v = []
            for dy in [-1,0,1]:
                for dx in [-1,0,1]:
                    nx = (a.x + dx) % 10
                    ny = (a.y + dy) % 10
                    v.append(1 if (nx, ny) in food else 0)
            views[a] = v
        
        # Agent步骤
        new_agents = []
        for a in agents:
            if a.state == "dead":
                continue
            child = a.step(views.get(a, [0]*9), food)
            if child:
                new_agents.append(child)
        
        agents = [a for a in agents + new_agents if a.state != "dead" and a.e > 0]
        
        # 维持种群
        while len(agents) < 3:
            agents.append(Agent(random.randint(0,9), random.randint(0,9)))
        
        # 记录
        if step % 100 == 0:
            n = len(agents)
            avg_e = sum(a.e for a in agents) / max(1, n)
            states = {}
            for a in agents:
                states[a.state] = states.get(a.state, 0) + 1
            history.append((step, n, avg_e, states))
            print(f"Step {step}: Agents={n}, Energy={avg_e:.1f}, States={states}")
    
    return history


if __name__ == "__main__":
    run_autonomy()
