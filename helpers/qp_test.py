# optimization model
import mip
import numpy as np


def get_cuadratic_appx(model,
                       var,
                       id_name=None,
                       min_interval=0,
                       max_interval=3000,
                       num_linspace=4,
                       M=1e6):
    if id_name == None:
        id_name = id(var)  # this is not a readable id

    x0_vector = np.linspace(start=min_interval,
                            stop=max_interval,
                            num=num_linspace,
                            endpoint=True)

    print('linspace = {}'.format([ '{0:0.2f}'.format(x0) for x0 in  x0_vector]))
    # assuming a linealization around the point x0
    # where L(x0) = bx+a then we estimate a and b for each x0
    # we will create as many functions as points in vector x0
    # (or linealization points) then lid = range(len(x0_vector))
    # for a cuadratic function a = 2*x0 , b = -x0^2
    l_params = {}
    max_code_b = {}
    max_var = model.add_var(name='max_var_{}'.format(
        id_name), var_type=mip.CONTINUOUS)
    for lid in range(len(x0_vector)):
        l_params[lid] = {}
        l_params[lid]['a'] = 2 * x0_vector[lid]
        l_params[lid]['b'] = -1 * x0_vector[lid]**2
        # add the max function over the linealizations
        # https://math.stackexchange.com/a/3568461/756404

        max_code_b[lid] = model.add_var(
            name='max_cod_{0}_{1}'.format(lid, id_name), var_type=mip.BINARY)

        # add codification constraint (1) (max_var  >= li(x) = ai*x+bi)
        model.add_constr(max_var >= l_params[lid]['a'] * var + l_params[lid]['b'],
                         name='min_cota_max_formulation_{0}_{1}'.format(lid, id_name))

        # add codification constraint (2) (max_var  <= li(x) + (1-byi)*M )
        model.add_constr(max_var <= l_params[lid]['a'] * var + l_params[lid]['b'] + (1 - max_code_b[lid]) * M,
                         name='max_cota_max_formulation_{0}_{1}'.format(lid, id_name))

    # add codification constraint (3)
    model.add_constr(mip.xsum([max_code_b[lid] for lid in range(len(x0_vector))]) == 1,
                     name='codification_constraint_bin_{0}'.format(id_name))

    return max_var


mdl = mip.Model(sense=mip.MINIMIZE, solver_name=mip.CBC)

x = mdl.add_var(name='myvar_x', var_type=mip.CONTINUOUS, lb=0)
y = mdl.add_var(name='myvar_y', var_type=mip.CONTINUOUS, lb=0)

sx = get_cuadratic_appx(model=mdl, var=x, id_name='x',
                        min_interval=0, max_interval=300, num_linspace=150)
sy = get_cuadratic_appx(model=mdl, var=y, id_name='y',
                        min_interval=0, max_interval=300, num_linspace=150)

mdl.objective = sx+sy  # cost_function
mdl.add_constr(x+y >= 150, name='budget_constraint')


status = mdl.optimize(max_seconds=3000)
print(status)
print('sx={0:0.2f}'.format(sx.x))
print('sy={0:0.2f}'.format(sy.x))
print('x={0:0.2f}'.format(x.x))
print('y={0:0.2f}'.format(y.x))


#for cont in mdl.constrs:
#    print(cont)
