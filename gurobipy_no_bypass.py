import gurobipy as gp
from gurobipy import GRB

# Parameters
N = 6  # number of players
P = [f'P{i}' for i in range(1,N+1)]  # Set of players, you could use the names if you wanted to.
balances = [-643.16,-602.16,414.80,440.84,1284.84,-895.16] # Be aware that the model would be infeasible if the sum of the balances is not 0.
loosers = [i for i in range(1,N+1) if balances[i-1]<0]  # All players that owe money
winners = [i for i in range(1,N+1) if balances[i-1]>0]  # All players that receive money
var_idx = [(i,j) for i in loosers for j in winners]  # Only model transactions from loosers to winners.
B = {p:s for p,s in zip(P,balances)}  # Balances as dictionary
Bnum = {i:balances[i-1] for i in range(1,N+1)}  # Balances as dictionary but with player number
M = sum(b for b in balances if b>0)  # Big M

# Model
m = gp.Model('debts-no-bypass')

# Variables
x = m.addVars(var_idx, vtype=GRB.CONTINUOUS, lb=-GRB.INFINITY, ub=GRB.INFINITY, name='x')
u = m.addVars(var_idx, vtype=GRB.BINARY, name='u')

# Objective
m.setObjective(u.sum(), sense=GRB.MINIMIZE)

# Constraints
m.addConstrs((sum(u[i,j]*x[i,j] for j in winners) == Bnum[i] for i in loosers), name='balance-loosers')
m.addConstrs((sum(u[i,j]*x[i,j] for i in loosers) == -Bnum[j] for j in winners), name='balance-winners')
m.addConstrs(x[i,j] <= M*u[i,j] for (i,j) in var_idx)
m.addConstrs(x[i,j] >= -M*u[i,j] for (i,j) in var_idx)

# Solve
m.optimize()

# Print results
print("***************** Solution *****************")
print(f"Total number of payments: {m.ObjVal}")
for t in var_idx:
    if u[t].X:
        if x[t].X < 0:
            print(f'{P[t[0]-1]} ows {int(-x[t].X)} to {P[t[1]-1]}')
        else:
            print(f'{P[t[1]-1]} ows {int(x[t].X)} to {P[t[0]-1]}')