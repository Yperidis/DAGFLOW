import random
import networkx as nx
import numpy as np
import Node

#### Function for generating a command binary tree with random walk messaging
def CommandGeneration(It = 100, levs = 12, ell = 1):
    '''
    Returns an ensemble of binary trees as a list of network X graph objects.
    
    It: Optional int>0. Default=100. The size of the ensemble.
    
    levs: Optional int>0. Default=12. Height of the trees counting from 0.
    
    ell: Optional int>0. Default=1. Predecessor-successor relation (1 is simple parent-child). Integer>=1.
         For ell-1>1 there are short-circuits between the roots, the leaves and all nodes in between. 
    '''

    ran = range(It)  # iterations for generating different seeds
    ensemble = []  # for averaging purposes
    n=levs  # height of the tree (index starts at 0).
    movesp = [-1, 1]  # the basis for the message distortion (random walk)

#    np.random.seed(3)

    for j in ran:
    #     np.random.seed(j)
        G=nx.Graph()

        mes = 0  # the offset (original message). The ansatz is that it should be correlated with system parameters.
        node = Node.Node(0,mes)  # ID arbitrarily set to 0 for the root
        next_nodes = [node]  # initialize the descendant tree
        nb_nodes = 1  # increment for the node ID allocation
        nchildren = 2  # number of descendants per parent node (for n-ary trees)
        G.add_node(node.ID, Pknow=1/2**mes, ID=node.ID)
        # all_nodes = [node]  # initializer for the tree structure
        movesp = [-1, 1]  # the basis for the message distortion (random walk)

        for i in range(1,levs):
            previous_nodes0 = next_nodes.copy()  # nodes from previous level stored for the generation of their children
            next_nodes = []
            for previous_node in previous_nodes0:  # generation of descendants and connections up and downstream in level
                for j in range(nchildren):
                    mes = previous_node.message+np.random.choice(movesp)  # the new message (rnd walk with memory)
                    child_node = Node.Node(nb_nodes, mes)  # generation of child node
                    child_node.parent = previous_node  # connection of generated to parent node
                    Node.Node.CommandLineUp(child_node, ell)  # node and predecessors up to ell
                    nb_nodes += 1  # next unique ID
                    next_nodes += [child_node]  # the children which are to become parents in the next round
                    G.add_node(child_node.ID, Pknow=1/2**np.abs(mes), ID=child_node.ID)
                    G.add_edge(previous_node.ID, child_node.ID)
                    for j in previous_node.cmndlineup:  # adding the short-circuits
                        G.add_edge(j, child_node.ID)

        ensemble.append(G)    
    
    return ensemble


#### Function for checking the higher node take over and if this fails to remove the subtrees of the nodes in question. 
#### Averaging is taken into account.
def EllCheckSubtreeRmv(buf):
    '''
    Returns an ensemble of lists. 
    Accepts an ensemble of lists of candidate nodes for removal after applying the information distortion
    threshold, checks whether their commanding nodes can take over and if none can, then it removes the
    subtrees of the nodes in question and adds them in the list where they came from.
    
    buf: iterable (typically list). The original ensemble of lists for the node removal.
    '''
    temp = 0

    for it in buf:  # the iterations
        for rem in it:  # the candidates for removal
            for ComUp in rem.cmndlineup[1:]:  # the upstream command of the candidate without the candidate
                if rem.levcur - ComUp.levcur > ComUp.highercmnd:  # if take over from above then check next cand.
                    break
                elif ComUp == rem.cmndlineup[-1]:  # if last ComUp is reached remove candidate's subtree
                    rem.CommandedNodes()
                    for subs in rem.cmndnodes:
                        if subs not in buf[temp]:  # avoid duplicate removals
                            buf[temp].append(subs)
        temp += 1
    return buf

def IncreaseSubTreeConnectivity(struct, ell=2):
    '''
    Returns the given tree with its subtree's descendants being ell-connected with ancestors.
    Adds descendants as children (directed edges) to each node of a given tree of height levs, within its subtree according to a 
    given value (ell)
    '''
    for i in struct:
        j=1
        temp = i.children_list
        while j < ell:
            buf = []
            for k in temp:
                for child in k.children_list:
                    i.MakeDescendants(child)  # add the children of the node as descendants to the original
                    buf.append(child)
            j += 1
            temp = buf  # prepare the children of the next level for iteration

def NodesOutF(NodeSet):
    '''
    Assuming a tree structure, returns a dictionary where every node of the tree is a key to a value corresponding to a
    function of the node's predecessors' messages.
    '''

    outf = {NodeSet[0] : 0}  # Initialize the root with a null std
    k = 0

    for i in NodeSet[1:]:
        outfbuf = []
        for j in i.cmndlineup:  
            outfbuf.append(j.message) # the ancestry of node i, gathered for processing
        outf[i] = np.std(outfmabuf)  # the std of the messages of the ancestry of node i (CUSTOMIZE)
    return outf
