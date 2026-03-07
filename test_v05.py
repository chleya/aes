"""
AES v0.5 - 测试版
"""

import numpy as np
import random


class Agent:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.energy = 30
        self.alive = True
        self.w1 = np.random.randn(9, 8) * 0.1
        self.b1 = np.zeros(8)
        self.w2_act = np.random.randn(8, 4) * 0.1
        self.w2_pred = np.random.randn(8, 9) * 0.1
        self.b2 = np.zeros(4)

print("Agent创建测试")
a = Agent(5, 5)
print(f"OK: {a.x}, {a.y}, {a.energy}")

# 测试forward
obs = np.random.randn(9)
h = np.tanh(np.dot(obs, a.w1) + a.b1)
act_logits = np.dot(h, a.w2_act) + a.b2
pred = np.tanh(np.dot(h, a.w2_pred))
print(f"Forward OK: act={np.argmax(act_logits)}, pred shape={pred.shape}")
