"""
AES 多Agent对抗 - 简化版
"""

import numpy as np, random


class Agent:
    def __init__(s,x,y,t):s.x=x;s.y=y;s.t=t;s.e=25;s.a=1
    def view(s,ag,f):
        v=np.zeros(9);i=0
        for dy in[-1,0,1]:
            for dx in[-1,0,1]:
                nx,ny=(s.x+dx)%10,(s.y+dy)%10
                if(nx,ny)in f:v[i]=1
                for a in ag:
                    if a.a and a.x==nx and a.y==ny:v[i]=2 if a.t==s.t else -1
                i+=1
        return v
    def act(s,o):
        h=np.tanh(np.dot(o,s.w1))
        a=np.argmax(np.dot(h,s.w2))
        return(0,-1)if a==0 else(0,1)if a==1else(-1,0)if a==2else(1,0)
    def mut(s):
        c=Agent(s.x,s.y,s.t);c.e=s.e//2;s.e//=2;return c


# 运行
print("AES Multi-Agent")
ag=[Agent(random.randint(0,9),random.randint(0,9),i%2)for i in range(10)]
f=[(random.randint(0,9),random.randint(0,9))for _ in range(4)]

for st in range(500):
    while len(f)<4:f.append((random.randint(0,9),random.randint(0,9)))
    
    for a in ag:
        if not a.a:continue
        v=a.view(ag,f)
        dx,dy=a.act(v)
        a.x=(a.x+dx)%10;a.y=(a.y+dy)%10;a.e-=1
        if(a.x,a.y)in f:a.e+=10;f.remove((a.x,a.y))
    
    ag=[a for a in ag if a.a and a.e>0]
    for a in ag:
        if a.e>=40:ag.append(a.mut())
    for t in[0,1]:
        if len([a for a in ag if a.t==t])<2:ag.append(Agent(9,9,t))
    
    if st%100==0:
        t0=len([a for a in ag if a.t==0]);t1=len([a for a in ag if a.t==1])
        print(f"Step {st}: Blue={t0}, Red={t1}")

print(f"Done! Agents: {len(ag)}")
