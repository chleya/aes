"""
AES 阶段2: 简化版 - 推箱子实验
"""

import random


class Box:
    def __init__(s,x,y):s.x=x;s.y=y


class Agent:
    def __init__(s,x,y):s.x=x;s.y=y;s.e=30
    def act(s,bx,by):
        if bx>s.x:dx,dy=1,0
        elif bx<s.x:dx,dy=-1,0
        elif by>s.y:dx,dy=0,1
        else:dx,dy=0,-1
        return dx,dy


# 运行
print("Phase2: Push Box Experiment")

boxes=[Box(random.randint(1,8),random.randint(1,8))for _ in range(3)]
agents=[Agent(0,0),Agent(9,9)]

for st in range(200):
    for a in agents:
        bx=boxes[0].x;by=boxes[0].y
        dx,dy=a.act(bx,by)
        
        nx,ny=(a.x+dx)%10,(a.y+dy)%10
        
        # 推箱子
        pushed=False
        for b in boxes:
            if b.x==nx and b.y==ny:
                nx2,ny2=(nx+dx)%10,(ny+dy)%10
                # 检查阻挡
                if not any(bb.x==nx2 and bb.y==ny2 for bb in boxes):
                    b.x,b.y=nx2,ny2
                    pushed=True
                break
        
        a.x,a.y=nx,ny
        a.e-=1
    
    # 死亡复制
    agents=[a for a in agents if a.e>0]
    for a in agents:
        if a.e>=50:agents.append(Agent(a.x,a.y))
    
    if st%50==0:
        print(f"Step {st}: Agents={len(agents)}, Box=({boxes[0].x},{boxes[0].y})")

print(f"Done! Agents={len(agents)}")
