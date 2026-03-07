"""
AES 阶段2验证 - 能量调整版
"""

import random


class Box:
    def __init__(s,x,y):s.x=x;s.y=y


class Agent:
    def __init__(s,x,y):
        s.x=x;s.y=y;s.e=50;s.a=1
    
    def step(s,box,gx,gy):
        # 策略: 推向目标
        to_box_dx=1 if box.x>s.x else -1 if box.x<s.x else 0
        to_box_dy=1 if box.y>s.y else -1 if box.y<s.y else 0
        
        nx,ny=(s.x+to_box_dx)%8,(s.y+to_box_dy)%8
        
        # 推箱子
        if nx==box.x and ny==box.y:
            push_to_goal=1 if gx>box.x else -1 if gx<box.x else 0
            push_dy=1 if gy>box.y else -1 if gy<box.y else 0
            
            box.x=(box.x+push_to_goal)%8
            box.y=(box.y+push_dy)%8
            s.e+=10
        
        s.x,s.y=nx,ny
        s.e-=0.5


# 实验
print("Phase2 验证")
results=[]

for trial in range(10):
    box=Box(3,3)
    goal=(6,6)
    agents=[Agent(2,2),Agent(4,4)]
    
    for st in range(300):
        for a in agents:
            a.step(box,*goal)
            if a.x==goal[0] and a.y==goal[1]:
                a.e+=30
        
        agents=[a for a in agents if a.e>0]
        if a.e>=80:agents.append(Agent(goal[0],goal[1]))
    
    moved=box.x!=3 or box.y!=3
    reached=any(a.x==goal[0] and a.y==goal[1] for a in agents)
    results.append((moved,reached,len(agents)))
    print(f"Trial {trial+1}: moved={moved}, reached={reached}, alive={len(agents)}")

print(f"\n推动率: {sum(r[0] for r in results)/10:.0%}")
print(f"达成率: {sum(r[1] for r in results)/10:.0%}")
