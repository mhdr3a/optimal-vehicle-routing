from pulp.pulp import lpSum
from pulp import LpProblem, LpVariable
import pandas as pd

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def read_data(file_path):
  df = pd.read_csv(file_path)
  print("Input the source and the target indices separated by a whitespace; here are the possible choices:")
  for _, row in df.iterrows():
    print(f"{row['Place_index']}: {row['Place_name']}")
  return df

def get_input():
  s, t = list(map(int, input().split()))
  print("-------------------------------------------------------------------------------------------------")
  if s < 0 or t < 0 or s > (len(df) - 1) or t > (len(df) - 1):
    print("Invalid input, please try again later.")
    return None
  return s, t

def build_paths_and_edges(df):
  paths = {}
  edges = []
  for _, row in df.iterrows():
    origin = row['Place_index']
    destination = list(map(int,row['Neighbors_indice'].split(',')))
    weight = list(map(int,row['Neighbors_weight'].split(',')))
    for d, w in list(zip(destination, weight)):
      paths[(origin, d)] = LpVariable(name=f"m_{origin}_{w}_{d}", lowBound=0, upBound=1, cat='Integer')
      edges.append((origin, d, w))
  return paths, edges

def build_lp_model(df, paths, edges, s, t):
  model = LpProblem(name="Optimal_Vehicle_Routing")
  model += lpSum([w * paths[(u, v)] for u, v, w in edges])
  s_incoming_edges = [paths[(u, s)] for u, v, _ in edges if v == s]
  s_outgoing_edges = [paths[(s, v)] for u, v, _ in edges if u == s]
  model += lpSum(s_incoming_edges) - lpSum(s_outgoing_edges) == -1
  t_incoming_edges = [paths[(u, t)] for u, v, _ in edges if v == t]
  t_outgoing_edges = [paths[(t, v)] for u, v, _ in edges if u == t]
  model += lpSum(t_incoming_edges) - lpSum(t_outgoing_edges) == 1
  for node in range(len(df)):
    if node != s and node != t:
      incoming_edges = [paths[(u, node)] for u, v, _ in edges if v == node]
      outgoing_edges = [paths[(node, v)] for u, v, _ in edges if u == node]
      model += lpSum(incoming_edges) - lpSum(outgoing_edges) == 0
  return model

def build_optimal_path(paths):
  optimal_path = []
  for var in paths.values():
    if var.value() == 1.0:
      begin = int(var.name.split('_')[1])
      end = int(var.name.split('_')[3])
      optimal_path.append((begin, end))
  return optimal_path

def print_results(optimal_path, model, s, t, df):
  print(f"You are now in ({s}) {df.iloc[s]['Place_name']}, right? Well, follow this route:")
  tar = s
  for i in optimal_path:
    for j in optimal_path:
      if j[0] == tar:
        tar = j[1]
        print(f"({tar}) {df.iloc[tar]['Place_name']}", end='')
        if tar == t:
          print('.')
        else:
          print(' -> ', end='')
  print(f"Total cost is also {model.objective.value()} :)")

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

try:
  file_path = "data.csv"
  df = read_data(file_path)
  s, t = get_input()
  paths, edges = build_paths_and_edges(df)
  print(f"It seems that you want to go from ({s}) {df.iloc[s]['Place_name']} to ({t}) {df.iloc[t]['Place_name']}.")
  print("Looking for an optimal route...", end='\n\n')
  model = build_lp_model(df, paths, edges, s, t)
  status = model.solve()
  if status == 1:
    print("We finally found an optimal path:")
    optimal_path = build_optimal_path(paths)
    print_results(optimal_path, model, s, t, df)
  else:
    print(f"There is no way to go from {df.iloc[s]['Place_name']} to {df.iloc[t]['Place_name']}.")
except Exception as err:
  print(err)
