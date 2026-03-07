"""
AES 测试套件
"""

import numpy as np
import sys
sys.path.insert(0, 'F:/aes')

from core import Entity, Environment, Agent, EvolutionEngine


def test_entity():
    """测试实体"""
    e = Entity('food', 10)
    assert 0 <= e.x < 10
    assert 0 <= e.y < 10
    assert e.type == 'food'
    print("[PASS] Entity test")


def test_environment():
    """测试环境"""
    env = Environment(10, 5, 2)
    assert len(env.food) == 5
    assert len(env.predators) == 2
    
    # 测试视野
    view = env.get_view(5, 5)
    assert view.shape == (9,)
    assert -1 <= view.min() <= 0
    assert view.max() <= 1
    
    # 测试step
    env.step()
    assert len(env.food) >= 5
    
    print("[PASS] Environment test")


def test_agent():
    """测试Agent"""
    a = Agent(5, 5, 10)
    assert a.x == 5
    assert a.y == 5
    assert a.energy == 30
    assert a.alive
    
    # 测试行动
    obs = np.random.randn(9)
    move, pred = a.act(obs)
    assert move in [(0,-1), (0,1), (-1,0), (1,0)]
    assert pred.shape == (9,)
    
    # 测试移动
    a.move(1, 0, 10)
    assert a.x == 6
    
    # 测试变异
    child = a.mutate()
    assert child.energy == 15
    assert a.energy == 15
    
    print("[PASS] Agent test")


def test_evolution():
    """测试演化引擎"""
    agents = [Agent(5, 5, 10) for _ in range(5)]
    agents[0].energy = 0  # 死亡
    agents[0].alive = False
    
    # 选择
    selected = EvolutionEngine.select(agents)
    assert len(selected) == 4
    
    # 繁殖
    agents[0].energy = 60
    agents[0].alive = True
    new_agents = EvolutionEngine.reproduce(agents)
    assert len(new_agents) > len(agents)
    
    # 维持
    agents = []
    agents = EvolutionEngine.maintain(agents, 3, 10)
    assert len(agents) == 3
    
    print("[PASS] EvolutionEngine test")


def test_integration():
    """集成测试"""
    env = Environment(10, 3, 1)
    agents = [Agent(5, 5, 10) for _ in range(5)]
    
    for step in range(10):
        env.step()
        
        for a in agents:
            if not a.alive:
                continue
            obs = env.get_view(a.x, a.y)
            move, pred = a.act(obs)
            a.move(move[0], move[1], 10)
        
        agents = EvolutionEngine.select(agents)
        agents = EvolutionEngine.reproduce(agents)
        agents = EvolutionEngine.maintain(agents, 3, 10)
    
    assert len(agents) >= 3
    print("[PASS] Integration test")


def run_all():
    """运行所有测试"""
    print("=" * 40)
    print("AES 测试套件")
    print("=" * 40)
    
    test_entity()
    test_environment()
    test_agent()
    test_evolution()
    test_integration()
    
    print("\nAll tests passed!")


if __name__ == "__main__":
    run_all()
