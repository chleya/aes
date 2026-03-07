"""
AES 阶段3验证 - 极简版
"""

import random


class A:
    def __init__(s,x,y,t):s.x=x;s.y=y;s.t=t;s.e=30;s.alive=1


# 运行
print("Phase3 验证")

for trial in range(10):
    ag=[A(random.randint(0,9),random.randint(0,9),i%2)for i in range(10)]
    
    for st in range(300):
        for a in ag:
            if not a.alive:continue
            # 简单: 向食物走
            dx=1 if 5>a.x else-1 if 5<a.x else 0
            dy=1 if 5>a.y else-1 if 5<a.y else 0
            a.x=(a.x+dx)%10;a.y=(a.y+dy)%10;a.e-=1
            if(a.x,a.y)==(5,5):a.e+=20
        
        ag=[a for a in ag if a.alive and a.e>0]
        for a in ag:
            if a.e>=50:ag.append(A(a.x,a.y,a.t))
        for t in[0,1]:
            if len([a for a in ag if a.t==t])<2:ag.append(A(5,5,t))
    
    b=len([a for a in ag if a.t==0])
    r=len([a for a in ag if a.t==1])
    print(f"Trial {trial+1}: B={b}, R={r}")

print("Done")
