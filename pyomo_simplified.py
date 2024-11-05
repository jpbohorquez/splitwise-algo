import pyomo.environ as pyo

# Parameters
N = 6  # number of players
P = [f'P{i}' for i in range(1,N+1)]  # Set of players, you could use the names if you wanted to.
balances = [-643.16,-602.16,414.80,440.84,1284.84,-895.16] # Be aware that the model would be infeasible if the sum of the balances is not 0.
B = {p:s for p,s in zip(P,balances)}  # Balances as dictionary
Bnum = {i:balances[i-1] for i in range(1,N+1)}  # Balances as dictionary but with player number
M = sum(b for b in balances if b>0)  # Big M

# Model
model = pyo.ConcreteModel()
model.P = pyo.RangeSet(1, N)  # Using indices for sets in Pyomo

# Indexes for variable pairs (i, j) where j > i
var_idx = [(i, j) for i in model.P for j in model.P if j > i]

# Variables
model.x = pyo.Var(var_idx, within=pyo.Reals)
model.u = pyo.Var(var_idx, within=pyo.Binary)

# Objective
def objective_rule(model):  # Define funciton to minimize the number of non-zero transactions
    return sum(model.u[i, j] for (i, j) in var_idx)
model.obj = pyo.Objective(rule=objective_rule, sense=pyo.minimize)

# Constraints
# Symmetry Constraint: x[i, j] == -x[j, i]
# def symmetry_rule(model, i, j):
#     return model.x[i, j] == -model.x[j, i]
# model.symmetry = pyo.Constraint(model.P, model.P, rule=symmetry_rule)

# Self Debt Constraint: x[i, i] == 0
# def self_debt_rule(model, i):
#     return model.x[i, i] == 0
# model.self_debt = pyo.Constraint(model.P, rule=self_debt_rule)

# Balance Constraint: sum of outflows minus inflows should equal balance for each person
def balance_rule(model, i):
    outflow = sum(model.x[i, j] for j in model.P if j > i)
    inflow = sum(model.x[j, i] for j in model.P if j < i)
    return outflow - inflow == Bnum[i]
model.balance = pyo.Constraint(model.P, rule=balance_rule)

# Upper and lower bounds for x[i, j] based on u[i, j]
def upper_bound_rule(model, i, j):
    return model.x[i, j] <= M * model.u[i, j]
model.upper_bound = pyo.Constraint(var_idx, rule=upper_bound_rule)

def lower_bound_rule(model, i, j):
    return model.x[i, j] >= -M * model.u[i, j]
model.lower_bound = pyo.Constraint(var_idx, rule=lower_bound_rule)

# Solve
solver = pyo.SolverFactory('gurobi')  # You can use 'cplex', 'cbc', 'ipopt', etc
solver.solve(model)

# Print results
print("***************** Solution *****************")
print(f"Total number of payments: {pyo.value(model.obj)}")
for (i, j) in var_idx:
    if model.u[i, j].value:
        if model.x[i, j].value < 0:
            print(f"{P[i - 1]} owes {int(-model.x[i, j].value)} to {P[j - 1]}")
        else:
            print(f"{P[j - 1]} owes {int(model.x[i, j].value)} to {P[i - 1]}")
