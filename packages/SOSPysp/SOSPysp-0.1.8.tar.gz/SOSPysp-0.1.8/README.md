This package is a Python version of MATLAB TOOLBOX -- SOSTOOLS. 

This package contains functions based on **sympy** package. However, in case of a large number of decision variables, **sympy** may take a long time to parse the data.

Demos are in the folder [SOSPy_demos](https://github.com/zm2404/SOSPy/tree/main/SOSPy_demos/Sympy_demos).

### Updates in the current version:

- When creating an SOS program, the code searches for and prints out all installed and available solvers.
- We have added **cvxpy** as a solver. As a result, users can now utilize other solvers through **cvxpy**.
- The solvers we currently support are **mosek** and **cvxpy**.
- It's worth noting that since **cvxpy** acts as a parser, certain results cannot be read after executing with **cvxpy**.
This includes details like the **iteration number**, **primal infeasible**, and **dual infeasible**.



Contributors: 
- James Anderson, email: james.anderson@columbia.edu
- Leonardo Felipe Toso, email: lt2879@columbia.edu
- Zhe Mo, email: zm2404@columbia.edu
