"""
AES 核心验证: 神经网络版能否涌现表征?
"""

import sys
sys.path.insert(0, 'F:/aes')

from core_v04 import Agent, Env, CONFIG
import numpy as np


def run_core_experiment(steps=500):
    print("="*50)
    print("核心验证: 神经网络版能否涌现表征?")
    print("="*50)
    
    env = Env()
    agents = [Agent(np.random.randint(0,10), np.random.randint(0,10)) for _ in range(CONFIG['n_agents'])]
    
    history = []
    
    for step in range(steps):
        env.step()
        
        for a in agents:
            if not a.alive:
                continue
            
            obs = env.get_view(a.x, a.y)
            dx, dy, pred = a.act(obs)
            a.move(dx, dy)
            a.energy -= CONFIG['energy_per_step']
            
            # 吃食物
            for f in list(env.food):
                if f.x == a.x and f.y == a.y:
                    a.energy += CONFIG['food_energy']
                    env.food.remove(f)
            
            # 捕食者
            for p in env.predators:
                if p.x == a.x and p.y == a.y:
                    a.energy += CONFIG['predator_energy']
            
            # 预测奖励
            future = env.get_view(a.x, a.y)
            err = np.mean((pred - future) ** 2)
            a.predict_total += 1
            
            if err < 0.5:
                a.energy += CONFIG['predict_reward']
                a.predict_success += 1
        
        # 死亡复制
        agents = [a for a in agents if a.alive and a.energy > 0]
        
        for a in agents:
            if a.energy >= CONFIG['reproduce_threshold']:
                agents.append(a.mutate())
        
        # 防止灭绝
        while len(agents) < 5:
            agents.append(Agent(np.random.randint(0,10), np.random.randint(0,10)))
        
        # 记录
        if step % 100 == 0:
            n = len(agents)
            avg_e = np.mean([a.energy for a in agents]) if agents else 0
            pred_r = np.mean([a.predict_success/max(1,a.predict_total) for a in agents]) if agents else 0
            
            history.append((step, n, avg_e, pred_r))
            print(f"Step {step}: Agents={n}, Energy={avg_e:.1f}, Predict={pred_r:.1%}")
    
    print(f"\n完成! 最终Agent数: {len(agents)}")
    
    # 分析
    if agents:
        avg_pred = np.mean([a.predict_success/max(1,a.predict_total) for a in agents])
        print(f"预测准确率: {avg_pred:.1%}")
        
        # 检查涌现
        if len(agents) > 10:
            print("✓ 种群增长: 涌现!")
        else:
            print("✗ 种群未增长")
    
    return history


if __name__ == "__main__":
    run_core_experiment()
