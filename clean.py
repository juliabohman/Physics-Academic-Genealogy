import pandas as pd
import numpy as np
import re


def relation_info(person,relation,kind):
    """
    Function to put all information about a person's relations (parents, children, or collaborators) into a list of dictionaries
    Paremeters:
        relations: list of dictionaries of the given relation
        person:  string name of the person
        kind: string of type of relation (parent, child, collaborator)
    Returns:
        rel: list of dictionaries of relation
    """
    # Initialize list of to store dictionaries of the relation
    rel = []
    
    # If relation doesn't exist, return empty list
    if len(relation) == 0:
        return rel
    
    # Iterate through each of the passed in relation (ex: iterate through children)
    for r in relation:
        
        # Initialize instance of relation
        instance = {}
        instance['name'] = person
        instance[kind] = r['name']
        instance['relation'] = r['type']
        
        # Check if the year is included, assigning it as NaN if it is not
        if r['year'] != '':
            yr = r['year']
            instance['years'] = yr.split('-')[-1]
        else:
            instance['years'] = np.nan
            
        # Check if the location is included, assigning it as NaN if it is not
        if r['location'] != '':
            instance['location'] = r['location']
        else:
            instance['location'] = np.nan
        
        # Add instance of relation to the relation list
        rel.append(instance)
    return rel

def parse_dictionaries(d):
    """
    Function to clean the information from the scraped dictionary.
    Parameters:
        d: dicitonary of scraped data
    Returns:
        personal_info: list of dictionaries storing personal info about each person
        parents: list of dictionaries storing information about each person's parents
        children: list of dictionaries storing informaiton about each person's children
        collaborators: list of dictionaries storing information about each person's collaborators
    """
    # intialize lists to store dictionaries of information
    personal_info = []
    parents = []
    children = []
    collaborators = []
    
    # define regular expressions to search differen strings
    meandist = re.compile(r"(Mean distance)(.)*(\n)(\d)+(.\d)*")
    cross = re.compile(r"(Cross-listing:)(\s)(\w)+(\s)*([tT]ree)")
    area = re.compile(r"Area:")
    site = re.compile(r"Website:")
    bio = re.compile(r"Bio:")
    
    # iterate through each person
    for k in d.keys():
        per = {}
        
        # get the name 
        name = ' '.join(k.splitlines())
        per['name'] = name
        
        # parse the data from the personal info string, filling in personal info dictionary with appriopriate data
        info = d[k]['personal_info']
        if bool(meandist.search(info)):
            per['Mean_distance'] = float(meandist.search(info).group().splitlines()[1])
        else:
            per['Mean_distance'] = np.nan
        if bool(cross.search(info)):
            per['Cross_tree'] = cross.search(info).group().split(':')[1]
        else:
            per['Cross_tree'] = np.nan
        if bool(area.search(info)):
            per['Area'] = 1
        else:
            per['Area'] = 0
        if bool(site.search(info)):
            per['Website'] = 1
        else:
            per['Website'] = 0
        if bool(bio.search(info)):
            per['Bio'] = 1
        else:
            per['Bio'] = 0
            
        # fill in how many parents, children, and collaborators each person has
        per['Parents_num'] = len(d[k]['parents'])
        per['Children_num'] = len(d[k]['children'])
        per['Collaborators_num'] = len(d[k]['collaborators'])
        
        # add the personal info dictionary to the appropriate list
        personal_info.append(per)
        
        # call the relation_info function to get lists of dictionaries for parents, children, and collaborators
        par = relation_info(name,d[k]['parents'],'parent')
        chil = relation_info(name,d[k]['children'],'child')
        coll = relation_info(name,d[k]['collaborators'],'collaborator')
        
        # add parent, child, and collaborator info the appropriate list
        parents.extend(par)
        children.extend(chil)
        collaborators.extend(coll)
        
    return personal_info,parents,children,collaborators

def clean_df(df):
    """
    Clean the relational dataframes. Performs inplace cleaning.
    Parameters:
        collaborators: df
    """
    # clean all the location strings to get rid of cross tree listings
    for s in set(df.location):
        try:
            check = s.split('(')
            check = check[0]
            check = ''.join(check).split(' ')
            val = ''.join(check)
            df.loc[df.location==s,'location']=val
        except AttributeError as e:
            continue
            
    # convert years column to datetime object
    df['years'] = pd.to_datetime(df['years'])
        
    # replace all empty strings with NaNs
    df.replace('',np.nan,inplace=True)
    
   