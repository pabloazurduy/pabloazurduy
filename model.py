import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# simulate a demand forecast 
# this will simulate the demand of 5 stores with two 
# demand periods, low_season:(p1) and high_season(p2)
# some stores start the high season before others, 
# and the planification horizon is 40 days 
np.random.seed(9)
demand_parameters = {1:{'p1':[10,20],
                        'p2':[60,20]},
                     2:{'p1':[20,20],
                        'p2':[30,20]},
                     3:{'p1':[12,15],
                        'p2':[40,25]},
                     4:{'p1':[13,20],
                        'p2':[50,20]},
                     5:{'p1':[57,10],
                        'p2':[60,30]}    
                        }

demand = {}
for store in demand_parameters.keys():
    first_period = list(np.random.poisson(demand_parameters[store]['p1'][0],
                                          demand_parameters[store]['p1'][1]))
    second_period = list(np.random.poisson(demand_parameters[store]['p2'][0],
                                           demand_parameters[store]['p2'][1]))

    demand[store] = first_period + second_period

demand_df = pd.DataFrame.from_dict(demand)

# plot stores demand 
fig = sns.lineplot(data=demand_df[[1,2,4]], dashes=False)
plt.xlabel("t periods")
plt.ylabel("demand")
plt.title("demand by store ") # You can comment this line out if you don't need title
plt.show(fig)
# the LP model
import mip 

mdl = mip.Model(sense=mip.MINIMIZE, solver_name=mip.CBC)

# sets
days = list(range(len(demand[1])))
stores = list(demand_parameters.keys())

# variables
e = {} # the shiped units the day t to store i 
u = {} # the the number of unfulfilled orders the day t to store i 
s = {} # inventory of units the day t in store i
b_u = {} # binary variable to codificate unfulfilled var
M = 1e7 # big M

for i in stores:
    for t in days:
        e[(i,t)] = mdl.add_var(name='e_{}_{}'.format(i,t), var_type=mip.CONTINUOUS, lb=0)
        u[(i,t)] = mdl.add_var(name='u_{}_{}'.format(i,t), var_type=mip.CONTINUOUS, lb=0)
        s[(i,t)] = mdl.add_var(name='s_{}_{}'.format(i,t), var_type=mip.CONTINUOUS, lb=0)
        b_u[(i,t)] = mdl.add_var(name='b_u_{}_{}'.format(i,t), var_type=mip.BINARY)
        
# initial inventory 
for i in stores:
    mdl.add_constr(s[(i,0)] == 20, name='initial_stock_s{}'.format(i))
        
# IO ecuation definition
for t in days[1:]:
    for i in stores:
        mdl.add_constr(s[(i,t)] == s[(i,t-1)] + e[(i,t-1)] - float(demand[i][t-1]) + u[(i,t-1)], 
                       name='io_s{}_t{}'.format(i,t))

for t in days:
    for i in stores:        
        # codification unfulfilled orders     
        mdl.add_constr(u[(i,t)] >= - s[(i,t)] - e[(i,t)] + float(demand[i][t]), 
                       name='cod_u_lb_s{}_t{}'.format(i,t))
        
        mdl.add_constr(u[(i,t)] <= - s[(i,t)] - e[(i,t)] + float(demand[i][t]) + M*b_u[(i,t)], 
                       name='cod_u_ub_s{}_t{}'.format(i,t))
        
        mdl.add_constr(u[(i,t)] <= M*(1-b_u[(i,t)]), 
                       name='cod_u_ub_b_s{}_t{}'.format(i,t))                                                                                            
        #print(crt)
# max shipments per day
for t in days:
    mdl.add_constr(mip.xsum(e[(i,t)] for i in stores)<= 120, 
                   name='shipment_cap_t{}'.format(t))

# lineal objective
mdl.objective = mip.xsum(u[(i,t)] for i in stores for t in days)
    
status = mdl.optimize(max_seconds=300)
print(status)

rows = []
for i in stores:
    for t in days:    
        rows.append({
            'store':i,
            'day':t,
            'u': u[(i,t)].x,
            'e': e[(i,t)].x,
            's': s[(i,t)].x,
            'bu': b_u[(i,t)].x,
            'd':float(demand[i][t])
        })
        
result = pd.DataFrame(rows)
result['fill_rate'] = (result.d - result.u)/result.d
result['unfulfill_rate'] = result.u/result.d
result['filled_d'] =  result.d - result.u

# plot stores unfulfill 
selected = result[result.store.isin([1,4])]
length_fig, length_ax = plt.subplots()
sns.lineplot(x='day', 
                 y='filled_d',
                 hue="store", 
                 palette ="muted",
                 dashes=[(2, 2), (2, 2)], 
                 style='store',
                 data=selected,
                 ax = length_ax)
sns.lineplot(x='day', y='d',
             hue="store", palette ="muted",
             data=selected,
             ax = length_ax)

length_fig.savefig('lineal.pdf')


# ============================== #
#   now with QP approximization 
# ============================== #

from helpers.mip import get_quadratic_appx
# get a new variable that represents u^2 = qa_u

qa_u = {}
for i in stores:
    for t in days: 
        qa_u[(i,t)] = get_quadratic_appx(model = mdl, 
                                         var = u[(i,t)], 
                                         id_name = 'qpu_{}_{}'.format(i,t),
                                         min_interval = 0, # lower value where we estimate that u will be moving 
                                         max_interval = 100, # lower value where we estimate that u will be moving 
                                         num_linspace = 5 # number of points of discretization 
                                         )

mdl.objective = mip.xsum(qa_u[(i,t)] for i in stores for t in days)

# add some solver options 
mdl.threads = -1
mdl.max_mip_gap_abs = 0.10
status = mdl.optimize(max_seconds=100, )
print(status)
if mdl.status == mip.OptimizationStatus.FEASIBLE:
    print('solver ended up with a gap of {:0.2f} %'.format(mdl.gap * 100))
    

# gatther results again 
rows = []
for i in stores:
    for t in days:    
        rows.append({
            'store':i,
            'day':t,
            'u': u[(i,t)].x,
            'e': e[(i,t)].x,
            's': s[(i,t)].x,
            'bu': b_u[(i,t)].x,
            'd':float(demand[i][t])
        })
        
result = pd.DataFrame(rows)
result['fill_rate'] = (result.d - result.u)/result.d
result['unfulfill_rate'] = result.u/result.d
result['filled_d'] =  result.d - result.u

# plot stores unfulfill 
selected = result[result.store.isin([1,4])]
width_fig, width_ax = plt.subplots()
sns.lineplot(x='day', 
                 y='filled_d',
                 hue="store", 
                 palette ="muted",
                 dashes=[(2, 2), (2, 2)], 
                 style='store',
                 data=selected,
                 ax = width_ax)
sns.lineplot(x='day', y='d',
             hue="store", palette ="muted",
             data=selected,
             ax = width_ax)

length_fig.savefig('quadratic.pdf')

