import random
import scipy as scp
import numpy as np
import Node

#### Function for generating a command binary tree with random walk messaging
def CommandGeneration(It = 100, levs = 12, ell = 1, dk = 2):
    '''
    Returns an ensemble of binary trees in the form of a list of lists.
    Each sublist contains all the nodes of a given tree structure. 
    Each element of the superlist is a binary tree. The number of elements 
    of the superlist is the ensemble.
    
    It: Optional int>0. Default=100. The number of iterations.
    
    levs: Optional int>0. Default=12. Height of the tree counting from 0.
    
    ell: Optional int>0. Default=1. Ancestor-descendant relation (1 is simple parent-child). Integer>=1.
    
    dk: Optional int>0. Default=2. The level upwards which a given node can substitute. Integer>0.
    '''

    ran = range(It)  # iterations for generating different seeds
    all_nodes_set = []  # for averaging purposes
    n=levs  # height of the tree (index starts at 0). More than 28 would probably not be of much practical application
         # (see Chinese civil service) https://en.wikipedia.org/wiki/Civil_Service_of_the_People%27s_Republic_of_China
         # for a binary tree
    l = ell  # high command take over (whole subtrees connected when l-1). CHANGE FOR DIFFERENT SIMULATIONS
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
        node.depknow = dk
        node.q = 1.
        node.highercmnd = l
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
    #                 mes = previous_node.message+np.random.choice(movesp, p=[0.9, 0.09, 0.01])  # the new message (rnd walk) as broken telephone, i.e. biased, rarely remaining intact and only as a rare event being rectified
                    mes = previous_node.message+np.random.choice(movesp)  # the new message (rnd walk)
                    child_node = Node.Node(nb_nodes, mes)  # generation of child node
                    child_node.levin = i  # set the intial level of the child node
                    child_node.levcur = i  # set the current level of the child node
                    child_node.depknow = dk
                    child_node.parent = previous_node  # connection of generated to parent node
    #                 if i <= n-2:
                    child_node.highercmnd = l  #  assign a high command take over for all the meaningfully commanding nodes
                    if child_node.highercmnd > 1:
                        child_node.survprob = scp.special.binom(n,i)*( (n-child_node.highercmnd)/n )**i \
                        *( child_node.highercmnd/n )**(n-i)   # probability of survival (binomial prob. mass function, p=n-ell)
                    elif child_node.highercmnd == 1:
                        child_node.survprob = 1
                    Node.Node.Efficiency(child_node, child_node.levin, child_node.levcur)  # the efficiency of the node at its position
                    previous_node.MakeChildren(child_node)  # connection of parent to generated node
                    Node.Node.CommandLineUp(child_node, l)  # store the upstream line of nodes for each node for the desired depth
                    nb_nodes += 1  # next unique ID
    #                 mes += np.random.uniform()  # distortion that does not oscillate around the refrence point
    #                 mes += np.random.choice(movesp)  # uniformly pick one of the predefined choices for the distortion
                    next_nodes += [child_node]  # the children which are to become parents in the next round
                    all_nodes += [child_node]

#             if i <= 2:  # customizing to the desired branching.
#                 nchildren = 5
#             else:
#                 nchildren = 10            

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
#     return struct