# linear QP code
### Solving a Quadratic Problem (QP) in an open source linear solver (python-mip)
qp-mip-example. This code is more explained in this [medium post](https://towardsdatascience.com/solving-a-quadratic-problem-qp-in-an-open-source-linear-solver-56ed6bb468e8?source=friends_link&sk=93e4433811ed4efc74bd393fe1dffa85)

## Installation 
    cd qp-mip
    pip install .

## Usage
both models in the example are in `model.py` module, the helper described in the article is in `helpers.mip`. The result plots are in the `result\` folder. 

some of the equations latex code used in the article are in the `model.tex` file 

## Model 

<img src="medium_img/model_lineal@2x.png"  alt="model_lineal" width="500"/>

## Linearization of the quadratic function
<img src="medium_img/quadratic_function_discrete.png" alt="quadratic_function_discrete" width="550"/>

## Results linear version
<img src="results/linear.png" alt="linear model" width="550"/>

## Results quadratic version
<img src="results/quadratic.png" alt="quadratic model" width="550"/>
