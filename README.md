# linear QP code
### Solving a Quadratic Problem (QP) in an open source linear solver (python-mip)
qp-mip-example

## Installation 
    cd qp-mip
    pip install .

## Usage
both models in the example are in `model.py` module, the helper described in the article is in `helpers.mip`. The result plots are in the `result\` folder. 

some of the equations latex code used in the article are in the `model.tex` file 

## Model 

![model definition](medium_img/model_lineal.png "Model")

## Linearization of the quadratic function
![alt text](medium_img/quadratic_function_discrete.png "Model")

## Results linear version
![alt text](results/linear.png "Model")
## Results quadratic version
![alt text](results/quadratic.png "Model")