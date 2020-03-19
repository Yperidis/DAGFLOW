# Information Flow in Directed Acyclic Graphs (DAG)
The following code is an implementation of random walk diffusion on a directed acyclic graph. It is possible to short-circuit the DAG with any level so as to study the effect of the message distortion as it propagates to the different levels of the graph.

### Dependencies
There are a few dependencies of the pure code. For visualizations consider using matplotlib and Graphviz (the latter is needed for visualizing the example in the Jupyter notebook).

* random
* scipy (checked with 1.4.1)
* numpy (checked with 1.18.1)
