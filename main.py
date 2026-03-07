"""
AES 主入口
"""

from core import Environment, Agent, EvolutionEngine, run


if __name__ == "__main__":
    print("AES v0.6 - 模块化版")
    print("=" * 40)
    
    agents = run(steps=500, grid_size=10, n_agents=15)
    
    print(f"\n完成! 最终Agent数: {len(agents)}")
