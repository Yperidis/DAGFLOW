import random

class Node:
    def __init__(self, ID, message, 
                 parent=None, childNo=None, children_list=None, depknow=None, levin=None, levcur=None, 
                cmndlineup=None, cmndnodes=None, q=None, highercmnd=None, survprob=None, ancestor_list=None,
                descendant_list=None):
        self.ID = ID  # an integer ascending from 0 to the number of the nodes minus 1)
        self.message = message  # some integer number representing an initial message

        self.depknow = depknow  # an integer ascending from 0 indicating how many levels up a node can replace
                            # cannot be greater than the number of levels
        self.levin = levin  # an integer between 0 and the height of the hierarchy before an iteration
        self.levcur = levcur  # as levin but for the update after the iteration
        self.parent = parent  # an integer if applicable (non applicable to the root node)
        self.q = q  # an efficiency factor for maintaining a position in a superiour level coming from an inferior
        self.highercmnd = highercmnd  # an integer ascending from 1 to the height minus 2 indicating up to which 
        # level commanding nodes upstream can take over their subordinates' command
        self.children_list = []
        self.cmndlineup = []  # initialization for the full line of command including the node in question
        self.cmndnodes = []
        self.survprob = survprob  # the node's survival probability
        self.ancestor_list = []  # a list of the node's direct ancestors
        self.descendant_list = []  # a list of the node's direct descendants
        
    def MakeChildren(self, child):
        '''
        Instantiation of a child node. Needs the node in question.
        '''
        self.children_list.append(child)
        
    def HasChildren(self):
        '''
        Boolean determining whether the node in question has a child or not.
        '''
        if len(self.children_list) != 0:
            return True
        else:
            return False
        
    def MakeDescendants(self, descendant):
        '''
        Instantiation of a direct descendant node. Needs the node in question.
        '''
        self.descendant_list.append(descendant)
        
    def children(self):
        return self.children_list
    
    def parent(self):
        return self.parent
    
# This function gathers all the ancestors of the node in question in a list, including the node.
    def CommandLineUp(self, l):  # n is assumed to be a gloabal variable and equal to the height of the tree
        '''
        This function gathers all the ancestors of the node in question in a list, including the node. The list
        is returned.
        '''
        self.cmndlineup = [self, self.parent]  # minimal upstream communication
        temp = self.parent
        
#         finished = False
#         while finished is False:  # ATTENTION! CHANGE TO A FOR LOOP IF THE GRAPH IS NOT A TREE ANYMORE
#             if temp.parent is not None:
#                 temp = temp.parent
#                 self.cmndlineup.append(temp)
#             else:
#                 finished = True
        for i in range(l):  # depth of message: for l=0 leaf sees only parent. For l=n-1 leaf sees all ancestors
            if temp.parent is not None:
                temp = temp.parent
                self.cmndlineup.append(temp)
            else:
                break  # reached the root
        return self.cmndlineup  # the final ancestry of the node (or its upstream communication)
    
    def CommandedNodes(self):  # attaches to cmndnodes of the node its whole subtree
        '''
        Attaches to cmndnodes of the node its whole subtree (the node in question is not included).
        '''
        self.cmndnodes = self.children_list
        
        ncmndnodes = len(self.cmndnodes)
        ii = 0  # ATTENTION! CHANGE TO A FOR LOOP IF THE GRAPH IS NOT A TREE ANYMORE
        while ii < ncmndnodes:
            child = self.cmndnodes[ii]
            for childchild in child.children_list:
                self.cmndnodes.append(childchild)
            ncmndnodes = len(self.cmndnodes)
            ii += 1
    
    def Efficiency(self, levin, levcur):
        '''
        A function to compute the exponential drop in efficiency with level of
        a node substitution from another in its subtree.
        
        levin: Int>=0. The substitute's initial level.
        
        levcur: Int>=0. The level on which the candidate node is called to substitute.
        '''
        self.q = 1/2.**(levin-levcur)