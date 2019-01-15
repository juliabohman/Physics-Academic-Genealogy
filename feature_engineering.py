import pandas as pd
import numpy as np
import networkx as nx
from networkx.algorithms import approximation as aprx

def relations_network(df,kind):
    """
    ReCreate the parent child network structure from the parents dataframe.
    Parameters:
        df - dataframe of people with their connection (can be either children, parents, or collaborators)
        kind - string indicates whether dataframe is of children, parents, or collaborators. Must be either 'parent','child',
            or 'collaborator'
    Returns:
        A - ndarray adjacency matrix of connections
        people - dictionary of people keying to which node they are in the adjacency matrix
        
    """
    # initialize dictionary to keep track of people who have been added to the adjacency matrix
    people = {}
    
    # get total number of people referenced in dataframe
    rels = list(set(df[kind]))
    chils = list(set(df.name))
    total = set(rels+chils)
    n = len(total)
    
    # initialize adjacency matrix
    A = np.zeros((n,n))
    
    # iterate through dataframe
    ind = 0
    for i in range(len(df.name)):
        # get the name of the person, and add them to the dictionary of people
        person = df.at[i,'name']
        if person not in people.keys():
            people[person] = ind
            ind +=1
        # get the person's relations
        relations = df[df.name==person][kind].values
        
        # add each parent to the dictionary if they are not added already
        for r in relations:
            if r not in people.keys():
                people[r] = ind
                ind+=1
            # record connection in adjacency matrix
            A[people[r],people[person]] = 1
    network = nx.from_numpy_matrix(A)
    return network,people


def add_groups(parents,children,collabs):
    """
    Add the triangle coefficient, square clustering coefficient, clustering coefficient, and k means coefficient to 
    the parents, children, and collabs dataframes.
    Parameters:
        parents - dataframe of parents
        children - dataframe of children
        collabs - dataframe of collaborators
    Returns:
        new_dfs - list of updated dataframes
    """
    # get networks and dictionaries
    par_net,par_dict = relations_network(parents,'parent')
    chil_net,chil_dict = relations_network(children,'child')
    coll_net,coll_dict = relations_network(collabs,'collaborator')
    
    # track each network and corresponding network
    networks = [par_net,chil_net,coll_net]
    dicts = [par_dict,chil_dict,coll_dict]
    dfs = [parents,children,collabs]
    new_dfs = []
    
    # iterate through networks
    for i,net in enumerate(networks):
        df = dfs[i]
        
        # calculate different clustering coefficients
        triangles = nx.algorithms.cluster.triangles(net)
        clusters = nx.algorithms.cluster.clustering(net)
        sqr_clusters = nx.algorithms.cluster.square_clustering(net)
        
        # create dictionaries keying to the appropriate people
        conns = list(dicts[i].keys())
        tri = {conns[i]: triangles[i] for i in range(len(triangles))}
        clust = {conns[i]:clusters[i] for i in range(len(clusters))}
        sqr = {conns[i]:sqr_clusters[i] for i in range(len(sqr_clusters))}
        
        # convert clustering coefficients to dataframes
        trian = pd.DataFrame.from_dict(tri,orient='index')
        clustrs = pd.DataFrame.from_dict(clust,orient='index')
        sqrs = pd.DataFrame.from_dict(sqr,orient='index')
        
        names = ['triangles','clusters','squares']
        
        # rename columns
        for j,c in enumerate([trian,clustrs,sqrs]):
            c.reset_index(inplace=True)
            c.rename(index=str,columns = {'index':'name',0:names[j]},inplace=True)
            df = pd.merge(df,c,on='name',how='left')
        new_dfs.append(df)
    return new_dfs

def get_current_location(df,children):
    """
    Infer person's current location based on where their children got their degrees
    Parameters:
        df - dataframe of a person's personal info
        children - dataframe of a person's children
    Returns:
        df - dataframe with new column of current location
    """
    df['current_loc'] = np.nan
    for n in df.name.values:
        if n in children.name.values:
            childs = children[children.name==n].child.values
            chil = np.random.choice(childs)
            df.loc[df.name==n,'current_loc'] = children[(children.child==chil)&(children.name==n)].location.values[0]
    return df
            