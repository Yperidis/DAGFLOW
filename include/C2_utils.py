import random
import scipy as scp
import numpy as np
import Node

#### Function for generating a command binary tree with random walk messaging
def CommandGeneration(It = 100, levs = 12, ell = 1):
    '''
    Returns an ensemble of binary trees in the form of a list of lists.
    Each sublist contains all the nodes of a given tree structure. 
    Each element of the superlist is a binary tree. The number of elements 
    of the superlist is the ensemble.
    
    It: Optional int>0. Default=100. The number of iterations.
    
    levs: Optional int>0. Default=12. Height of the tree counting from 0.
    
    ell: Optional int>0. Default=1. Ancestor-descendant relation (1 is simple parent-child). Represents knowledge. Integer>=1.
    '''

    ran = range(It)  # iterations for generating different seeds
    all_nodes_set = []  # for averaging purposes
    n=levs  # height of the tree (index starts at 0). More than 28 would probably not be of much practical application
         # (see Chinese civil service) https://en.wikipedia.org/wiki/Civil_Service_of_the_People%27s_Republic_of_China
         # for a binary tree
    # ell high command take over (whole subtrees connected when l-1). CHANGE FOR DIFFERENT SIMULATIONS
    # also models the interlayer communication conflict from parent-child relation (0) to full ancestry (n-2). Each node is going to have depmes+2 for its std
    dk = dk  # depth of knowledge  CHANGE FOR DIFFERENT SIMULATIONS
    movesp = [-1, 1]  # the basis for the message distortion (random walk)

#    np.random.seed(3)

    for j in ran:
    #     np.random.seed(j)

        mes = levs - ell  # the offset (original message). The ansatz is that it should be correlated with system parameters.
        node = Node.Node(0,mes)  # ID arbitrarily set to 0 for the root
        node.levin = 0
        node.levcur = 0
        node.q = 1.
        node.highercmnd = ell
        node.survprob = 1
        next_nodes = [node]  # initialize the descendant tree
        nb_nodes = 1  # increment for the node ID allocation
        nchildren = 2  # number of descendants per parent node (for n-ary trees)
        all_nodes = [node]  # initializer for the tree structure

        for i in range(1,n):
            previous_nodes0 = next_nodes.copy()  # nodes from previous level stored for the generation of their children
            next_nodes = []
            for previous_node in previous_nodes0:  # generation of descendants and connections up and downstream in level
                for j in range(nchildren):
#                     if ell > 1 and previous_node.levcur > 1:  # in case of ell>1 for a path length from the root >1...
#                         temp = []
#                         for ComUp in previous_node.cmndlineup[:ell]:
#                             temp.append(ComUp.message)
#                         mes = np.mean(temp)  # ... the message shall be the mean of its upper line of command up to ell
#                     else:  # reconsider if the ell is not universal
#                         mes = previous_node.message+np.random.choice(movesp)  # the new message (rnd walk with memory)
                    mes = previous_node.message+np.random.choice(movesp)  # the new message (rnd walk with memory)
                    child_node = Node.Node(nb_nodes, mes)  # generation of child node
                    child_node.levin = i  # set the intial level of the child node
                    child_node.levcur = i  # set the current level of the child node
                    child_node.parent = previous_node  # connection of generated to parent node
    #                 if i <= n-2:
                    child_node.highercmnd = ell  #  assign a high command take over for all the meaningfully commanding nodes
                    if child_node.highercmnd > 1:
                        child_node.survprob = scp.special.binom(n,i)*( (n-child_node.highercmnd)/n )**i \
                        *( child_node.highercmnd/n )**(n-i)   # probability of survival (binomial prob. mass function, p=n-ell)
                    elif child_node.highercmnd == 1:
                        child_node.survprob = 1
                    Node.Node.Efficiency(child_node, child_node.levin, child_node.levcur)  # the efficiency of the node at its position
                    previous_node.MakeChildren(child_node)  # connection of parent to generated node
                    Node.Node.CommandLineUp(child_node, ell)  # store the upstream line of nodes for each node for the desired depth
                    nb_nodes += 1  # next unique ID
                    next_nodes += [child_node]  # the children which are to become parents in the next round
                    all_nodes += [child_node]

        all_nodes_set.append(all_nodes)    
    
    return all_nodes_set


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

def NodesStd(NodeSet):  #### for list version: def NodesStd(NodeSet, N):
    '''
    Returns a dictionary of standard deviation based on current and ancestral values for every node, given
    one structure with assigned messages (signals). For the root (not caluclated) zero is assigned by default.
    '''
    sigma = {NodeSet[0] : 0}  # Initialize the root with a null std
    k = 0

    for i in NodeSet[1:]:
        sigmabuf = []
        for j in i.cmndlineup:  # the ancestry of node i
            sigmabuf.append(j.message)
        sigma[i] = np.std(sigmabuf)  # the std of the messages of the ancestry of node i
    return sigma