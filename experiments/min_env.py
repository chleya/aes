"""
AES 最小环境验证
圈1: 2x2网格能否涌现?
"""

import random


class A:
    def __init__(s,x,y,e):
        s.x=x;s.y=y;s.e=e;s.alive=1


# 2x2网格
print("圈1: 最小环境 2x2")
results=[]

for trial in range(20):
    ag=[A(random.randint(0,1),random.randint(0,1),30)for _ in range(3)]
    food=(random.randint(0,1),random.randint(0,1))
    
    for st in range(200):
        for a in ag:
            if not a.alive:continue
            dx=1 if food[0]>a.x else-1 if food[0]<a.x else 0
            dy=1 if food[1]>a.y else-1 if food[1]<a.y else 0
            a.x=(a.x+dx)%2;a.y=(a.y+dy)%2;a.e-=1
            if(a.x,a.y)==food:a.e+=20
        
        ag=[a for a in ag if a.alive and a.e>0]
        for a in ag:
            if a.e>=50:ag.append(A(a.x,a.y,a.e//2));a.e//=2
        while len(ag)<2:ag.append(A(0,0,30))
    
    results.append(len(ag))
    print(f"Trial {trial+1}: {len(ag)}")

print(f"\n2x2结果: 平均{sum(results)/len(results):.1f}")

# 对比3x3
print("\n对比3x3:")
results3=[]
for trial in range(20):
    ag=[A(random.randint(0,2),random.randint(0,2),30)for _ in range(3)]
    food=(random.randint(0,2),random.randint(0,2))
    
    for st in range(200):
        for a in ag:
            if not a.alive:continue
            dx=1 if food[0]>a.x else-1 if food[0]<a.x else 0
            dy=1 if food[1]>a.y else-1 if food[1]<a.y else 0
            a.x=(a.x+dx)%3;a.y=(a.y+dy)%3;a.e-=1
            if(a.x,a.y)==food:a.e+=20
        
        ag=[a for a in ag if a.alive and a.e>0]
        for a in ag:
            if a.e>=50:ag.append(A(a.x,a.y,a.e//2));a.e//=2
        while len(ag)<2:ag.append(A(0,0,30))
    
    results3.append(len(ag))

print(f"3x3结果: 平均{sum(results3)/len(results3):.1f}")
