import gurobipy as gp
from gurobipy import GRB

# Parameters
N = 6  # number of players
P = [f'P{i}' for i in range(1,N+1)]  # Set of players, you could use the names if you wanted to.
balances = [-643.16,-602.16,414.80,440.84,1284.84,-895.16] # Be aware that the model would be infeasible if the sum of the balances is not 0.
B = {p:s for p,s in zip(P,balances)}  # Balances as dictionary
M = sum(b for b in balances if b>0)  # Big M

# Model
m = gp.Model('debts')

# Variables
x = m.addVars(P, P, vtype=GRB.CONTINUOUS, lb=-GRB.INFINITY, ub=GRB.INFINITY, name='x')
u = m.addVars(P, P, vtype=GRB.BINARY, name='u')

# Objective
m.setObjective(u.sum(), sense=GRB.MINIMIZE)

# Constraints
m.addConstrs((x[i,j] == -x[j,i] for i in P for j in P), name='symmetry')
m.addConstrs((x[i,i] == 0 for i in P), name='autopay')
m.addConstrs((sum(u[i,j]*x[i,j] for j in P) == B[i] for i in P), name='balances')
m.addConstrs(x[i,j] <= M*u[i,j] for i in P for j in P)
m.addConstrs(x[i,j] >= -M*u[i,j] for i in P for j in P)

# Solve
m.optimize()

# Print results
print("***************** Solution *****************")
print(f"Total number of payments: {m.ObjVal/2}")  # Divided since model is redundant.
for p1 in P:
    for p2 in P:
        if x[p1,p2].X < 0:
            print(f'{p1} owes {int(-x[p1,p2].X)} to {p2}')