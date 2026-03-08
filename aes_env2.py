"""环境驱动涌现"""
import random

class Agent:
    def __init__(s,x,y):s.x,s.y=x,y;s.e=30
    def act(s,v):
        s.s=[sum(vv*w for vv,w in zip(v,r)) for r in s.w]
        m=[(0,-1),(0,1),(-1,0),(1,0)];return m[s.s.index(max(s.s))]
    def w(s):
        return [[random.random()*0.2-0.1 for _ in range(9)]for _ in range(4)]

def run(g,f):
    food=[(random.randint(0,g-1),random.randint(0,g-1))for _ in range(f)]
    agents=[Agent(random.randint(0,g-1),random.randint(0,g-1))for _ in range(10)]
    for _ in range(300):
        while len(food)<f:food.append((random.randint(0,g-1),random.randint(0,g-1)))
        for a in agents:
            v=[1 if((a.x+dx)%g,(a.y+dy)%g)in food else 0 for dy in[-1,0,1]for dx in[-1,0,1]]
            dx,dy=a.act(v);a.x,a.y=(a.x+dx)%g,(a.y+dy)%g
            if(a.x,a.y)in food:a.e+=15;food.remove((a.x,a.y))
            a.e-=1
        agents=[a for a in agents if a.e>0]
        for a in agents:
            if a.e>=50:c=Agent(a.x,a.y);c.w=[[w+random.random()*0.1-0.05 for w in r]for r in a.w];agents.append(c);a.e//=2
        while len(agents)<3:agents.append(Agent(0,0))
    return len(agents)

print("环境驱动涌现")
for name,g,f in[("简单",5,4),("中等",8,5),("困难",10,6)]:
    print(f"{name}: {run(g,f)}")
