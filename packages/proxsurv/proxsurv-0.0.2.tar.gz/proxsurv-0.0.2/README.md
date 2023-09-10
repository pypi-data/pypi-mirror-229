 

# PBSA : Proximity Based Survival Analysis

[![Documentation Status](https://readthedocs.org/projects/pbsa/badge/?version=latest)](https://pbsa.readthedocs.io/en/latest/?badge=latest)



![PBSA](Population.png)





Proximity Based Survival Analysis are algorithms, designed for survival prediction
using proximity information. The k-NN survival, Random Survival Forest, Kernel Survival
are some examples of proximity based survival analysis. While this package tends 
to provide those algorithms later, currently the package provides the following algorithms:

- COBRA Survival 

For now other algorithms are taken from scikit-survival and np_survival to provide as
a base learner for the ensemble algorithms.

## installation

```
pip install proxsurv
```

The documentation is available at [https://pbsa.readthedocs.io/en/latest/](https://pbsa.readthedocs.io/en/latest/)



## References

- Goswami, Rahul & Dey, Arabin. (2023). Area-norm COBRA on Conditional Survival Prediction. The paper explores a different variation of combined regression strategy to calculate the conditional survival function. We use regression based weak learners to create the proposed ensemble technique. The proposed combined regression strategy uses proximity measure as area between two survival curves. The proposed model shows a construction which ensures that it performs better than the Random Survival Forest. The paper discusses a novel technique to select the most important variable in the combined regression setup. We perform a simulation study to show that our proposition for finding relevance of the variables works quite well. We also use three real-life datasets to illustrate the model. 

