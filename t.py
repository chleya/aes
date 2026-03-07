import random
r=[]
for g in[2,3,4]:
    s=[]
    for _ in range(5):
        a=[3]*3
        for i in range(100):
            for x in a:
                x-=1
                if random.random()<0.3:x+=15
                if x>50:x=25;a.append(x)
        s.append(len(a))
    r.append((g,sum(s)/5))
print(r)
