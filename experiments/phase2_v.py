"""
AES 阶段2验证 - 简化版
验证: 推箱子到目标
"""

import random


class Box:
    def __init__(s,x,y):s.x=x;s.y=y


class Agent:
    def __init__(s,x,y):
        s.x=x;s.y=y;s.e=30;s.a=1
        s.sense=0  # 因果理解
    
    def step(s,box,gx,gy):
        # 简单策略: 先去箱子
        dx=1 if box.x>s.x else -1 if box.x<s.x else 0
        dy=1 if box.y>s.y else -1 if box.y<s.y else 0
        
        nx,ny=(s.x+dx)%8,(s.y+dy)%8
        
        # 推箱子
        if nx==box.x and ny==box.y:
            px,py=(box.x+dx)%8,(box.y+dy)%8
            # 推向目标
            if (px-gx)+(py-gy)<(box.x-gx)+(box.y-gy):
                box.x,box.y=px,py
                s.e+=5
                s.sense+=1
        
        s.x,s.y=nx,ny
        s.e-=1


# 实验
print("Phase2 验证实验")
results=[]

for trial in range(10):
    box=Box(4,4)
    goal=(7,7)
    agents=[Agent(0,0),Agent(7,0),Agent(0,7)]
    
    for st in range(200):
        for a in agents:
            a.step(box,*goal)
            if a.x==goal[0] and a.y==goal[1]:
                a.e+=20
        
        agents=[a for a in agents if a.e>0]
        if a.e>=50:agents.append(Agent(0,0))
    
    moved=box.x!=4 or box.y!=4
    reached=any(a.x==goal[0] and a.y==goal[1] for a in agents)
    results.append((moved,reached,len(agents)))
    print(f"Trial {trial+1}: moved={moved}, reached={reached}, alive={len(agents)}")

print(f"\n推动率: {sum(r[0] for r in results)/10:.0%}")
print(f"达成率: {sum(r[1] for r in results)/10:.0%}")
