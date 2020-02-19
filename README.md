This project goal is to build an intractable program that loads any pddl file and 
solve the planing problem using graph-plan.
The code uses aima3 code for the algorithm implementation.
By interacting with the program one can
* build and visualize the graph. 
* zoom in and out to get a closer look of the graph.
* click and see what are the different mutexes.
* expand level in the graph.
* Try and solve for a specific level, or solve and expand as needed.

notes:
Will not load problems with action or variable names that are pythons primitives
this means that names like "in" or "import" ect will not load.
 

The examples are from the PDDL4j github https://github.com/pellierd/pddl4j
