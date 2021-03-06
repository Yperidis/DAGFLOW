import random
import networkx as nx
import numpy as np
import Node

#### Function for generating a command binary tree with random walk messaging
def CommandGeneration(It = 100, levs = 12, ell = 1, branchf = 2):
    '''
    Returns an ensemble of binary trees as a list of network X graph objects.
    
    It: Optional int>0. Default=100. The size of the ensemble.
    
    levs: Optional int>0. Default=12. Height of the trees counting from 0.
    
    ell: Optional int>0. Default=1. Predecessor-successor relation (1 is simple parent-child). Integer>=1.

    branchf: Optional int >=1. Default=2. The branching factor of the (n-ary) tree.
         For ell-1>1 there are short-circuits between the roots, the leaves and all nodes in between. 
    '''

    ran = range(It)  # iterations for generating different seeds
    ensemble = []  # for averaging purposes
    n=levs  # height of the tree (index starts at 0).
    movesp = [-1, 1]  # the basis for the message distortion (random walk)

    for j in ran:
        G=nx.Graph()
        mes = 0  # the offset (original message). The ansatz is that it should be correlated with system parameters.
        node = Node.Node(0,mes)  # ID arbitrarily set to 0 for the root
        node.highercmnd = ell
        node.lev = 0
        next_nodes = [node]  # initialize the descendant tree
        nb_nodes = 1  # increment for the node ID allocation
        G.add_node(node.ID, Pknow=1/2**((node.highercmnd-1)*np.abs(mes)), ID=node.ID, lev=0)
        # all_nodes = [node]  # initializer for the tree structure
        movesp = [-1, 1]  # the basis for the message distortion (random walk)

        for i in range(1,levs):
            previous_nodes0 = next_nodes.copy()  # nodes from previous level stored for the generation of their children
            next_nodes = []
            for previous_node in previous_nodes0:  # generation of descendants and connections up and downstream in level
                for j in range(branchf):
                    mes = previous_node.message+np.random.choice(movesp)  # the new message (rnd walk with memory)
                    child_node = Node.Node(nb_nodes, mes)  # generation of child node
                    child_node.parent = previous_node  # connection of generated to parent node
                    child_node.highercmnd = ell  # assigning different spans of knowledge to different nodes
                    child_node.lev = i
                    Node.Node.CommandLineUp(child_node, ell)  # node and predecessors up to ell
                    nb_nodes += 1  # next unique ID
                    next_nodes += [child_node]  # the children which are to become parents in the next round
#                     G.add_node(child_node.ID, Pknow=1/( 1 + np.exp( (child_node.highercmnd-1)*np.abs(mes) ) ), ID=child_node.ID,
#                               lev=child_node.lev)  # logistic survival probability
                    G.add_node(child_node.ID, Pknow=1/2**((child_node.highercmnd-1)*np.abs(mes)), ID=child_node.ID,
                              lev=child_node.lev)  # inverse exponential survival probability
                    G.add_edge(previous_node.ID, child_node.ID)
                    for j in child_node.cmndlineup:  # adding the short-circuits
                        G.add_edge(j, child_node.ID)

        ensemble.append(G)    
    
    return ensemble

def PrunedEnsemble(hmin=3, hmax=7, hstep=3, ExtF=0.1, ExtBias=False, branchf=2, It=100): 
    '''
    Returns a dictionary of ensembles of network X graph objects (pruned trees) due to external 
    (site percolation) and internal (stochastic from a combination of connectivity and node values 
    of the trees) failures, as well as a dictionary for the average number of internal failures for each ensemble, 
    for specified tree heights and ell values. Each ensemble element's size within the 
    ensemble is determined by the minimum and maximum height of the trees scanned. For each height, 
    all its available ell values are scanned. The size of the returned ensemble is hmin+(hmin+hstep)+
    (hmin+2hstep)+...+hmax.
    
    It: Optional. Reference CommandGeneration function
    
    branchf: Optional. Reference CommandGeneration function
    
    hmin: Optional, int>1. The minimal value of the heights of the trees
    
    hmax: Optional, int>hmin. The maximal value of the heights of the trees
    
    ExtBias: Optional, boolean. Whether a uniform or an exponential distribution, dependent on node position, should be chosen for the site percolation selection.
    '''
    PrunedEnsembles, IntFails = {}, {}
    for h in range(hmin,hmax,hstep):
        temp = []
        for ell in range(1,h):
            TreeEnsemble = CommandGeneration(levs=h, ell=ell, branchf=2, It=100)

            NoExt = int(ExtF*TreeEnsemble[0].number_of_nodes())
            AllNodes = list(TreeEnsemble[0].nodes())
            FailEnsemb = Failures(TreeEnsemble, NoExt, ExtBias, AllNodes)

            # Removal of failed nodes
            for i in enumerate(TreeEnsemble):
                for rmv in FailEnsemb[0][i[0]]:
                    i[1].remove_node(rmv)
            
            kwd = 'h=' + str(h) + ', ell=' + str(ell)
            PrunedEnsembles[kwd] = TreeEnsemble
            temp.append( FailEnsemb[1] )
        IntFails[h] = temp  # keeping track of the internal failures per height
                    
    return PrunedEnsembles, IntFails

# Function for calculating the total failures and especially the internal ones.
def Failures(TreeEnsemble, NoExt, ExtBias, AllNodes):
    '''
    Returns a dictionary of the total failures for every of the ensemble network X graph objects given and 
    the average number of the internal failures for the ensemble.
    
    TreeEnsemble: An ensemble of network X graph objects.
    
    NoExt: int>=0. The number of externally removed nodes (external failures).
    
    ExtBias: Boolean. Determines whether the externally removed nodes will be removed equiprobably (see PrunedEnsemble).
    
    AllNodes: List. A list of all the nodes of an arbitrary sample from the given graph ensemble, given that all
    the graphs of the ensemble have the same number of nodes.
    '''
    FailEnsemb = []
    IntFails = []
    # External failures
    for specimen in TreeEnsemble:
        if ExtBias:  # bias for site percolation choice?
            ExtPPicks = []
            for i in TreeEnsemble[0].nodes():
                ExtPPicks.append( 1-2**(-TreeEnsemble[0].nodes[i]['lev']) )
            ExtPPicks = np.array(ExtPPicks)/np.sum(ExtPPicks)
            Nfail = list(np.random.choice(AllNodes, size=NoExt, replace=False, p=ExtPPicks))
        else:
            Nfail = list(np.random.choice(AllNodes, size=NoExt, replace=False))
        FailEnsemb += [Nfail]

    # Internal failures
    for specimen in enumerate(TreeEnsemble):
        temp = []
        for i in specimen[1].nodes():
            if specimen[1].nodes[i]['Pknow'] < np.random.uniform() and specimen[1].nodes[i]['ID'] not in FailEnsemb[specimen[0]]:
                FailEnsemb[specimen[0]].append( specimen[1].nodes[i]['ID'] )
                temp.append( specimen[1].nodes[i]['ID'] )  # keep track of the internal failures
        IntFails.append( len(temp) )
    return FailEnsemb, int( np.mean(IntFails) )

def CCNosANDSizes(TreeEnsemble, MinCC=1):
    '''
    Returns a dictionary of a list containing the median and average of the Nos of the CCs 
    given an ensemble of graphs (TreeEnsemble), as well as a list of the CC sizes for a 
    sample graph in the given ensemble closest to the aforementioned average. Lastly, the
    average number of nodes surviving the pruning for the ensemble, as the sum of all the CCs' nodes.
    Accepts as an argument a dictionary of ensembles, where each ensemble has been
    generated with a height and ell specified in its key. 
    
    MinCC: Optional, int>=1. The minimal value of the CCs' size retained for the analysis.
    '''
    CCInfo = {}

    for i in TreeEnsemble:
        CCEnsemble, Temp, TotGraphNs = [], [], []
        for j in TreeEnsemble[i]:
            CCs = list( nx.connected_components(j) )  # CCs
            CCs = [x for x in CCs if len(x) >= MinCC]  # keep CCs above a certain size. Default: 1 node.
            CCEnsemble.append( CCs )  # gathering the CCs
            Temp.append( len(CCs) )  # gathering the Nos of CCs
            TotGraphNs.append( len( Expansion(CCs) ) )  # gathering the total nodes of all the CCs for each graph
        MedNoCCs = np.median(Temp)  # Median of CCs' size (sorting implicit)
        AvNoCCs = np.round( np.mean(Temp) )  # Average of CCs' size rounded
        TempValue = find_nearest(Temp,AvNoCCs)  # ensure that the value closest to the one given is in Temp
        AvCCsizesInd = Temp.index(TempValue)  # locating the required CCs' size from the pool within the graph ensemble
        AvTotGraphN = np.round( np.mean(TotGraphNs) )  # Average of total nodes surviving rounded
        

        AvCCsizes = []
        for k in enumerate(CCEnsemble[AvCCsizesInd]):
            AvCCsizes.append( (k[0], len(k[1]) ) )  # gathering the CC sizes of the aforementioned quantity

        CCInfo[i] = [MedNoCCs, int(AvNoCCs), AvCCsizes, int(AvTotGraphN)]  # gathering summaries of the aforementioned quantities
        
    return CCInfo

# Finding the nearest value in a given array
def find_nearest(array, value):
    '''
    Returns the nearest value to the one given from a given iterable of primitives
    '''
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]

def Expansion(Iterable):
    '''
    Returns a list with all the elements of the given iterable.
    '''
    Exp = []
    for i in Iterable:
        for j in i:
            Exp.append(j)
    return Exp

# Function for measuring the GCC sizes
def GCCSize(TreeEnsemble):
    '''
    Returns a dictionary of the average GCC sizes for each height and ell, 
    given an ensemble of graphs (networkX objects).
    '''
    GCCSizes = {}
    for i in TreeEnsemble:
        GCCs = []
        for j in TreeEnsemble[i]:
            temp = list( nx.connected_components(j) )
            GCCs.append( len( max( temp ) ) )
        GCCSizes[i] = int( np.mean(GCCs) )
    return GCCSizes

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

# A function for determining the value that is mapped to a node (its perception) as a function of its predecessor values
def NodesOutF(NodeSet):
    '''
    Assuming a tree structure, returns a dictionary where every node of the tree is a key to a value corresponding to a
    function of the node's predecessors' messages.
    '''

    outf = {NodeSet[0] : 0}  # Initialize the root with a null value
    k = 0

    for i in NodeSet[1:]:
        outfbuf = []
        for j in i.cmndlineup:  
            outfbuf.append(j.message) # the ancestry of node i, gathered for processing
        outf[i] = np.std(outfmabuf)  # the std of the messages of the ancestry of node i (CUSTOMIZE)
    return outf