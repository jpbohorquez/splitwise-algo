import pyomo.environ as pyo

# Parameters
N = 6  # Number of players
P = [f'P{i}' for i in range(1, N+1)]  # Set of players
balances = [-643.16, -602.16, 414.80, 440.84, 1284.84, -895.16]  # Ensure balances sum to zero for feasibility
loosers = [i for i in range(1, N+1) if balances[i-1] < 0]  # Players who owe money
winners = [i for i in range(1, N+1) if balances[i-1] > 0]  # Players who receive money
var_idx = [(i, j) for i in loosers for j in winners]  # Transactions only from losers to winners
Bnum = {i: balances[i-1] for i in range(1, N+1)}  # Balances as a dictionary by player number
M = sum(b for b in balances if b > 0)  # Big M for constraints

# Model
model = pyo.ConcreteModel()

# Variables
model.x = pyo.Var(var_idx, within=pyo.Reals)  
model.u = pyo.Var(var_idx, within=pyo.Binary)

# Objective: Minimize the number of non-zero transactions
model.obj = pyo.Objective(expr=sum(model.u[i, j] for (i, j) in var_idx), sense=pyo.minimize)

# Constraints
# Balance constraints for loosers: sum of outflows equals each loser's balance
def balance_loosers_rule(model, i):
    return sum(model.u[i, j] * model.x[i, j] for j in winners) == Bnum[i]
model.balance_loosers = pyo.Constraint(loosers, rule=balance_loosers_rule)

# Balance constraints for winners: sum of inflows equals each winner's balance (negated)
def balance_winners_rule(model, j):
    return sum(model.u[i, j] * model.x[i, j] for i in loosers) == -Bnum[j]
model.balance_winners = pyo.Constraint(winners, rule=balance_winners_rule)

# Upper and lower bounds for x[i, j] based on u[i, j]
def upper_bound_rule(model, i, j):
    return model.x[i, j] <= M * model.u[i, j]
model.upper_bound = pyo.Constraint(var_idx, rule=upper_bound_rule)

def lower_bound_rule(model, i, j):
    return model.x[i, j] >= -M * model.u[i, j]
model.lower_bound = pyo.Constraint(var_idx, rule=lower_bound_rule)

# Solving the model
solver = pyo.SolverFactory('gurobi')
solver.solve(model)

# Print results
print("***************** Solution *****************")
print(f"Total number of payments: {pyo.value(model.obj)}")
for (i, j) in var_idx:
    if model.u[i, j].value:
        if model.x[i, j].value < 0:
            print(f"{P[i - 1]} ows {int(-model.x[i, j].value)} to {P[j - 1]}")
        else:
            print(f"{P[j - 1]} ows {int(model.x[i, j].value)} to {P[i - 1]}")
