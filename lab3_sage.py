from sage.all import *
task_1_curvers = [EllipticCurve(GF(p), [0,0,0,a,b]) for p,a,b in [(29,6,8), (23,11,3), (31,3,17)]]
task_1_points = [(5,8), (7,25), (7,9), (10,13)]
for E in task_1_curvers:
    print(E, E.is_singular())
    for x,y in task_1_points:
        print(f'({x},{y})', end=' ')
        try:
            P = E(x,y)
            print(True)
        except Exception:
            print(False)
print()
task_2_curve = EllipticCurve(GF(31), [0,0,0,3,17])
P = task_2_curve(12,18)
print(13*P)