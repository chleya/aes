"""环境驱动涌现"""
import random

def run(grid, food_n):
    class A:
        def __init__(s,x,y):s.x=s.y=s.e=30
        s.w=[[random.random()-.5 for _ in[9]]for _ in[4]]
    food=[(random.randint(0,grid-1),random.randint(0,grid-1))for _ in[food_n]]
    ag=[A(random.randint(0,grid-1),random.randint(0,grid-1))for _ in[10]]
    for _ in range(300):
        while len(food)<food_n:food.append((random.randint(0,grid-1),random.randint(0,grid-1)))
        for a in ag:
            v=[1 if((a.x+dx)%grid,(a.y+dy)%grid)in food else 0 for dy in[-1,0,1]for dx in[-1,0,1]]
            sc=[sum(vv*w for vv,w in zip(v,r))for r in a.w]
            m=[(0,-1),(0,1),(-1,0),(1,0)];dx,dy=m[sc.index(max(sc))]
            a.x=(a.x+dx)%grid;a.y=(a.y+dy)%grid
            if(a.x,a.y)in food:a.e+=15;food.remove((a.x,a.y))
            a.e-=1
        ag=[a for a in ag if a.e>0]
        for a in ag:
            if a.e>=50:c=A(a.x,a.y);c.w=[[w+.1*random.random()-.05 for w in r]for r in a.w];ag.append(c);a.e//=2
        while len(ag)<3:ag=[A(0,0)]
    return len(ag)

print("环境驱动涌现")
for n,g,f in[("简单",5,4),("中等",10,6),("困难",15,8)]:print(f"{n}: {run(g,f)}")
