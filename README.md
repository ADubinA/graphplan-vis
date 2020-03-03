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

## Install:
1. install all the requirements in the requirements.txt file
2. run python main.py

## Usage:
1. load a Domain pddl file using file-> load domain.
2. load a problem pddl file using file-> load problem.
3. if successful, one can do the following actions
    1. expand a level, by pressing action->expand level
    2. Try and solve, by pressing action->solve
    3. expand as much as require until a solution, if any, is found, by pressing action->expand and solve.
    4. reset the graph, by pressing action->reset.
    5. change the stopping condition for expand and solve, by pressing action->change stopping condition.
4. in addition, one can visualize better with the following:
    1. by pressing view->show no-op, you can choose if to visualize the no-op actions.
    2. by pressing view-> show mutexes, you can click on any action on the graph.
     The program will then visualize any mutexex for that action.
5. The program has visualization using the matplotlib module.
 Below the menu, there is a figure menu for:
   1. returning to the original layout
   2. undoing a zoom or move action
   3. redoing a zoom or move action
   4. moving mode, left clicking will move the viewport in the figure.
   5. zoom mode.
  
    


