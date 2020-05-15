# Knowledge Efficiency on a Tree
The following code is an implementation of random walk diffusion on a tree upon its generation. The whole simulation starts with a non-Markovian walk on the tree. Then it is possible to short-circuit the tree with nodes further done their paths of their subtrees, thus introducing extra memory effects to study the original message's distortion as it propagates to the different levels of the tree.

The goal of this study is to gain insight on the value of diffusing information to different hierarchical layers in arbitrary management or command structures.

### Dependencies
There are a few dependencies of the pure code. For visualizations consider using matplotlib and Graphviz (the latter is needed for visualizing the example in the Jupyter notebook).

* random
* scipy (checked with 1.4.1)
* numpy (checked with 1.18.1)
* networkx (checked with 2.4)
