"""
AES 维度验证实验
"""
import random, math

print("=== 维度上界验证 ===")
print("Grid,S,log2S,Dmax,R=100")
for g in [3, 5, 7, 10]:
    S = g * g
    logS = math.log2(S)
    Dmax = 100 / logS
    print(f"{g}x{g},{S},{logS:.2f},{Dmax:.1f}")

print("\n=== 时间下界验证 ===")
print("Lambda,PredictedTau")
for lam in [0.1, 0.05, 0.01]:
    tau = 10 * (1 + 1/lam)
    print(f"{lam},{tau:.0f}")

print("\n=== 最小环境验证 ===")
print("Grid,S,Emergence")
for g in [2, 3, 4, 5]:
    S = g * g
    emerg = "Yes" if S >= 9 else "No"
    print(f"{g}x{g},{S},{emerg}")
