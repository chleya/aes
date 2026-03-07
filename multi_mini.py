"""
AES 多Agent对抗 - 极简规则版
"""

import random


# Agent: 简单规则
class Agent:
    def __init__(s,x,y,team):
        s.x=x;s.y=y;s.t=team;s.e=25;s.alive=1
    
    def act(s,f,agents):
        # 找最近的食物
        mf=None;md=99
        for fx,fy in f:
            d=abs(fx-s.x)+abs(fy-s.y)
            if d<md:md=d;mf=(fx,fy)
        
        # 找最近的敌人
        me=None;med=99
        for a in agents:
            if a is not s and a.alive and a.t!=s.t:
                d=abs(a.x-s.x)+abs(a.y-s.y)
                if d<med:med=d;me=a
        
        # 决策：优先食物，其次躲避
        if mf:
            dx=1 if mf[0]>s.x else -1 if mf[0]<s.x else 0
            dy=1 if mf[1]>s.y else -1 if mf[1]<s.y else 0
        else:
            dx,dy=random.choice([(0,1),(0,-1),(1,0),(-1,0)])
        
        # 如果敌人太近，逃跑
        if me and med<3:
            dx=-1 if me.x>s.x else 1
            dy=-1 if me.y>s.y else 1
        
        return dx,dy


# 运行
print("="*40)
print("AES Multi-Agent 对抗实验")
print("="*40)

agents=[Agent(random.randint(0,9),random.randint(0,9),i%2)for i in range(10)]
food=[(random.randint(0,9),random.randint(0,9))for _ in range(4)]

for step in range(500):
    # 补充食物
    while len(food)<4:food.append((random.randint(0,9),random.randint(0,9)))
    
    # 行动
    for a in agents:
        if not a.alive:continue
        dx,dy=a.act(food,agents)
        a.x=(a.x+dx)%10;a.y=(a.y+dy)%10;a.e-=1
        
        # 吃食物
        if(a.x,a.y)in food:
            a.e+=10;food.remove((a.x,a.y))
        
        # 遇到敌人同归于尽
        for b in agents:
            if b is not a and b.alive and b.t!=a.t and b.x==a.x and b.y==a.y:
                a.alive=0;b.alive=0
    
    # 死亡和复制
    agents=[a for a in agents if a.alive and a.e>0]
    for a in agents:
        if a.e>=40:agents.append(Agent(a.x,a.y,a.t))
    
    # 每队至少2个
    for t in[0,1]:
        if len([a for a in agents if a.t==t])<2:
            agents.append(Agent(5,5,t))
    
    if step%100==0:
        t0=len([a for a in agents if a.t==0])
        t1=len([a for a in agents if a.t==1])
        print(f"Step {step}: 蓝队={t0}, 红队={t1}")

t0=len([a for a in agents if a.t==0])
t1=len([a for a in agents if a.t==1])
print(f"\n完成! 蓝队={t0}, 红队={t1}")
