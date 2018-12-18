#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import networkx as nx
import numpy as np
from collections import OrderedDict
from tqdm import tqdm
import json



# CREATION of the dictionary containing all the categories. The info are taken from a file .txt
def category_creation(V):
    
    o = open('wiki-topcats-categories.txt', 'r')
    categories = {}
    categories_not_filtered = {}
    for line in o :
        line = line.replace('\n','')
        l = line.split(' ')
        l[0] = l[0].replace('Category:', '').replace(';','')
        if len(l[1:]) >= 3500:
            categories[l[0]] = set(list(map(int, l[1:]))).intersection(set(V))
            
    return(categories)



# CREATION of the dictionary containing all the names of the articles. The info are taken from a file .txt
def name_creation():  
    
    o = open('wiki-topcats-page-names.txt', 'r')
    names = {}
    for line in o :
        line = line.replace('\n','')
        l = line.split(' ')
        names[int(l[0])] =  ' '.join(l[1:])
        
    return names



#CLASS used to run the BFS algorith starting from an initial category
class BFS:

    def bfs(self, dic):
        node = dic
        dist = 0
        l = list(self.graph[node])
        actual_visited = [node]
        while len(l) > 0:
            dist += 1 
            children = []
            for i in l:
                children += (self.graph[i])
                self.visited[i] += [dist]  
                actual_visited += ([i])
                
            l = set(children).difference(set(actual_visited))
                
    
    def __init__(self, graph, categories, input_category):
        
        self.graph = graph
        self.nodes = categories
        self.initial = input_category
        self.visited = {}
        for i in self.graph.nodes:
            self.visited[i] = []
        for i in tqdm(self.initial):
            self.visited[i] = [0]
            self.bfs(i)

        for i in self.initial:
                self.visited[i] = [0]


                
# CALCULATION of the median of the shortest path between an input category and the other categories.
def median_calculation(categories, input_category, data):
    #categories: dictionary wich keys are the name of the categories and the values are the list of articles 
                  #(only the ones present in a dataframe)
    #input_category: name of the initial category 
    #data: dict of nodes with their shortest paths calculated from the input category
    
    median = {}
    for category in categories:
        if category != input_category:
            shortest_path={}
            sh=[]
            if len(set(categories[category]).intersection(set(list(map(int,data.keys())))))> 0:
                for node in set(categories[category]).intersection(set(list(map(int,data.keys())))):
                    if len(data[str(node)]) > 0:
                        sh += (list(data[str(node)]))
                shortest_path[0] = sorted(sh)
                shortest_path[1] = (len(categories[category])*len(categories[input_category]) - len(shortest_path[0]))
                l = len(shortest_path[0]) + shortest_path[1]
                if shortest_path[1] >= int(l/2)+1:
                    median[category] = 10000
                elif l%2 == 0:
                    median[category] = np.mean([shortest_path[0][int(l/2)], shortest_path[0][int(l/2 +1)]])
                else:
                    median[category] = shortest_path[0][int(l/2) +1]
            else:
                median[category] = 100**100
    median[input_category] = -1
    
    return median



#CALCULATION of the ranking of all the nodes in the graph DG.  

def subgraph_calculation(DG, block_ranking, categories_after_ranking):
    #DG : direfcted graph with integer as vertex's labels
    #block_ranking: dictionary with the categories' names as keys
    #categories_after_ranking: dictionary with categories' names as keys and articles as values.
                                #An articles can be present in only one category. 
    
    idx = 0
    edges = nx.to_dict_of_lists(DG)

    for name in tqdm(block_ranking):
        if idx == 0:
            weight_dict = {}
            subgraph = DG.subgraph(categories_after_ranking[name])
            weight_dict[name] = {}
            for node in (subgraph.in_degree):
                for arr in edges[node[0]]:
                        DG[node[0]][arr]['weight'] = node[1]
            idx = 1
            for  node in subgraph.in_degree:
                weight_dict[name][node[0]] = node[1]
        else:
            try:
                subgraph = DG.subgraph(categories_after_ranking[name])
                weight_dict[name] = {}

                for node in subgraph.in_degree:
                    cumsum = node[1]
                    for arr in edges[node[0]]:
                            try:
                                cumsum+=(list(DG.edges[arr,node[0]].values()))[0]
                            except:
                                pass
                    weight_dict[name][node[0]] = cumsum


                for node in subgraph.in_degree:
                    for arr in edges[node[0]]:
                            DG[node[0]][arr]['weight'] = weight_dict[name][node[0]]
            except:
                pass
            
    return weight_dict

