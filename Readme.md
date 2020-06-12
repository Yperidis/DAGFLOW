# Knowledge Efficiency on a Tree and Failures
The project is a collection of functions implementating a random walk diffusion on a tree upon its generation with percolation considerations. A simulation should start with a non-Markovian walk on the tree. Then it is possible to short-circuit the tree with nodes further down the paths of their subtrees, thus introducing extra memory effects to study the original message's distortion (potential internal failure) as it propagates to the different levels of the tree.

Percolation is another aspect of the code. Currently, site percolation (node removal) is available as a proxy for external failures.

The goal of this study is to gain insight on adversity (failures) while diffusing information to different hierarchical layers in arbitrary management or command structures.

### Dependencies
There are a few dependencies of the pure code. For visualizations consider using matplotlib and Graphviz (the latter is needed for visualizing the example in the Jupyter notebook).

* random
* scipy (checked with 1.4.1)
* numpy (checked with 1.18.1)
* networkx (checked with 2.4)

### Demonstrations
There are two jupyter notebook with example analysis -Runs.ipynb- and visualizations -Demonstration.ipynb- (employing [graphviz](https://pypi.org/project/graphviz/), which is a Python wrapper of the [DOT language](https://graphviz.org/doc/info/lang.html)) respectively.
