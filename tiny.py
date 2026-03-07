"""AES v0.5 - 极简测试"""
import numpy as np, random

class A:
    def __init__(s,x,y):s.x=x;s.y=y;s.e=30;s.a=1

print("Test start")
agents=[A(random.randint(0,11),random.randint(0,11))for _ in range(20)]
print(f"Agents: {len(agents)}")
print("OK")
