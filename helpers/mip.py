import numpy as np
import mip 

def get_quadratic_appx(model ,
                        var,
                        id_name = None,
                        min_interval = 0,
                        max_interval = 100, 
                        num_linspace = 100,
                        M = 1e7 ):
  """ add to a model `model` a quadratic approximation to a `var => return var^2` ~ newvar 
      WARNING: this function will mutate the object model
  
  Arguments:
      model {mip.Model} -- mip.Model where the variable is originated
      var {mip.Variable} -- variable to get quadratic app x -> (x)**2
  
  Keyword Arguments:
      id_name {str} -- [optional] string to identify the new variables added (default: {None})
      min_interval {float} -- lower bound where the approximation will be valid (default: {0})
      max_interval {float} -- upper bound where the approximation will be valid (default: {100})
      num_linspace {int} -- number of discretization intervals (more will increase the time of solving) (default: {100})
      M {float} -- big M that contains the sum of all convex intervals (default: {1e7})
  
  Returns:
      [type] -- [description]
  """    
  if id_name == None:
      id_name = id(var) # this is not a readable id

  x0_vector = np.linspace(start = min_interval,
                          stop = max_interval,
                          num = num_linspace,
                          endpoint = True)


  # assuming a linearization around the point x0 
  # where L(x0) = bx+a then we estimate a and b for each x0
  # we will create as many functions as points in vector x0
  # (or linearization points) then lid = range(len(x0_vector))
  # for a quadratic function a = 2*x0 , b = -x0^2

  l_params ={}
  max_code_b = {}
  max_var = model.add_var(name='max_var_{}'.format(id_name), 
                          var_type=mip.CONTINUOUS, 
                          lb = 0) # the lb is defined to keep the dom(x) constraint 
  for lid in range(len(x0_vector)):
      l_params[lid] = {}
      l_params[lid]['a'] = 2* x0_vector[lid] 
      l_params[lid]['b'] = -1 * x0_vector[lid]**2
      # add the max function over the linearizations
      # https://math.stackexchange.com/a/3568461/756404
      
      max_code_b[lid] = model.add_var(name='max_cod_{0}_{1}'.format(lid, id_name), var_type=mip.BINARY)

      # add codification constraint (1) (max_var  >= li(x) = ai*x+bi)
      model.add_constr(max_var >=  l_params[lid]['a'] * var + l_params[lid]['b'], 
                  name='min_cota_max_formulation_{0}_{1}'.format(lid, id_name))
      
      # add codification constraint (2) (max_var  <= li(x) + (1-byi)*M )
      model.add_constr(max_var <=  l_params[lid]['a'] * var + l_params[lid]['b'] + (1- max_code_b[lid]) * M, 
                  name='max_cota_max_formulation_{0}_{1}'.format(lid, id_name))


  # add codification constraint (3) 
  model.add_constr(mip.xsum([ max_code_b[lid] for lid in range(len(x0_vector))]) == 1, 
                  name='codification_constraint_bin_{0}'.format(id_name))
  
  return max_var
