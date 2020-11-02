import math
import collections
import json
import re
import os
import sys
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import constants as c

import seaborn as sns
from constants import *
from datetime import datetime
from sklearn.decomposition import PCA
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
from matplotlib.backends.backend_pdf import PdfPages
from pathlib import Path
from dateutil import tz


def assert_equal_dfs(df1, df2):
    assert df1.eq(df2).all().all()


def get_bky_node_types(bky_path):
    """Get node types in a .bky file

    :param bky_path: The path to the .bky file
    :returns: The node types
    :rtype: Dictionary

    """
    node_types = collections.defaultdict(int)
    tree = ET.parse(bky_path)
    root = tree.getroot()
    
    for child in root.iter():
        if BKY_TYPE in child.attrib:
            node_types[child.attrib[BKY_TYPE]] += 1

    return node_types

def traverse_dict_to_get_node_type(iterator, node_types):
    """Determine SCM node types and their frequencies from a dictionary of JSON attributes
    
    Recursively search a dictionary of JSON attributes to define a 
    dictionary pased in as `node_types` that represent the nodes
    in an SCM file and the frequency of which each node type occurs
    
    :param iterator: The current data structure for the function to examine
    :param node_types: The dictionary of node types to append to
    :returns: The node types and their frequencies
    :rtype: Dictionary

    """
    if isinstance(iterator, list):
        for element in iterator:
            traverse_dict_to_get_node_type(element, node_types)
            
    elif isinstance(iterator, dict):
        for key, value in iterator.items():
            if key == SCM_TYPE:
                node_types[value] += 1

            traverse_dict_to_get_node_type(value, node_types)
        
def get_scm_node_types(scm_file_path):
    """Get SCM node types and their frequencies

    Load an SCM file, create a dictionary of it's attributes
    then pass the data to `traverse_dict_to_get_node_type` to
    populate the dictionary `node_types` with each unique SCM
    node type and the number of times each one occurs within
    the file.

    :param scm_file_path: The file to the SCM file
    :returns: SCM node types and the frequency at which they occurr
    :rtype: Dictionary

    """
    with open(scm_file_path, 'r') as fd:
        for line in fd:
            l = line.lstrip() # ensure that we check the relevant first character
            
            if not l.startswith('$') and not l.startswith('#'):
                data = json.loads(line)   
                break

    node_types = collections.defaultdict(int)
    traverse_dict_to_get_node_type(data, node_types)

    return node_types

NODE_FUNCS = {SCM: get_scm_node_types, BKY: get_bky_node_types}

def get_file_name(path):
    """Get the file name from a path.

    :param path: The path to parse
    :returns: The file name
    :rtype: String

    """
    return os.path.splitext(str(path))[0]

def get_time(t):
    return datetime.strptime(t, '%Y-%m-%dT%H:%M:%S%z')

def get_time_from_file_name(f):
    """Get the time from a file object

    Parse a file object for a date in the form %Y-%m-%dT%H:%M:%S%z where
    %Y = year, %m = month, %d = day, T = delimeter, 
    %H = hour, %S = seconds, %z = milliseconds

    :param file: The file object to parse
    :returns: The time parsed
    :rtype: datetime.datetime (as defined in datetime)

    """
    return get_time(f.split(".")[-1])



def convert_to_dataframe_and_sort(data, label):
    """Define a dataframe object from a dictionary of backup info and time created then sort.
    
    Define a dataframe object from a dictionary of backup info, in the 
    form of `{datetime.datetime: {node_type: frequency}, ...}` where the index
    of the dataframe is the time created. Then convert each datetime.datetime
    a numerical format then sort based on it.
    
    :param data: The dictionary of backup info
    :param label: What the index should be labelled
    :returns: The dataframe object of backup info
    :rtype: pandas.DataFrame

    """
    df = pd.DataFrame.from_dict(data, orient='index').fillna(0).sort_index()

    df[label] = [t.ctime() for t in df.index]
    df.set_index(label, inplace=True)
    
    return df


def get_backups_in_path(folder, file_type):
    """Return a collection of all backups of a specified type in a path.
    
    Use the rglob utility function to recursively search
    a directory for all backup files of the type `file_type`.
    Pass an empty string to not spe

    :param folder: The path to search
    :param file_type: The type of files to search for
    :returns: Collection of backups
    :rtype: PosixPath (as defined in pathlib)

    """
    return Path(folder).rglob("*." + file_type + '*.backup')

def get_backups_by_type(folder, file_type):
    """Get all backups and their time created with the extension `file_type` in the path `folder`

    :param folder: The folder to search
    :param file_type: The file extension/type
    :returns: All backups and the times they were created
    :rtype: Dictionary

    """
    backups = {}

    for f in get_backups_in_path(folder, file_type):
        time = get_time_from_file_name(get_file_name(f))
        
        try:
            backups[time] = NODE_FUNCS[file_type](str(f))
        except ET.ParseError as e:
            pass
        
    return backups

def get_directories(folder):    
    """Return a generator expression of the directories in a given folder

    :param folder: The folder to search
    :returns: Generator expression for directories
    :rtype: Generator

    """
    
    for name in os.listdir(folder):
        if '.' in name: continue #TODO ask purpose of this

        dir_name = os.path.join(folder, name)

        for project in os.listdir(dir_name):
            yield os.path.join(dir_name, project)
            
def get_node_info(path, parent_name, file_name):
    tree = ET.parse(path)
    root = tree.getroot()
    node_types = []

    for child in root.iter():
        if DISPLAY_NAME in child.attrib.keys():
            node_types.append({DISPLAY_NAME: child.attrib[DISPLAY_NAME],
                                PARENT_NAME: parent_name,
                                FILE_NAME:   file_name.split('.')[0]})

    return node_types


def get_nodes(t, path):
    nodes = collections.defaultdict(int)
    
    p = Path(path)
    
    for f in p.rglob("*." + t):
        try:
            types = NODE_FUNCS[t](str(f))
            
            for key, value in types.items():
                nodes[key] += value
                
        except ET.ParseError as e:
            pass
    
    return nodes

def plot_nodes(nodes, node_type, scale):
    """Plot every node and their frequencies in a bar graph

    Plot every node and the frequency at which they occur
    across all files. This is a helper function that simply
    plots the nodes, it does not determine the nodes and their
    frequencies

    :param nodes: The nodes and their frequencies
    :param node_type: The type of nodes to plot
    :param scale: The scale for which to plot the data

    """
    data = pd.Series(nodes).sort_values()

    ax = data.plot.barh(
            title='{} node type for all files'.format(node_type), 
            figsize=scale)

    ax.set(xlabel="Frequency", ylabel="Node Type")
    
def reset_style():
    plt.style.use('default')

def save_or_display(title, graph_type="", dpi=None):
    if c.to_file:
        print("Saving graph to file")
        save_plot(title, graph_type=graph_type, dpi=dpi)
    else:
        if dpi:
            mpl.rcParams['figure.dpi'] = dpi

        plt.show()
        
    # Regardless, reset style because Jupyter is a pain
    reset_style()
    
def save_plot(figure_name, graph_type="heatmap", dpi=None):
    if graph_type:
        figure_name = "{} {}.pdf".format(figure_name, graph_type)
    else:
        figure_name += ".pdf"

    figure_path = os.path.join(PLOT_SAVE_PATH, figure_name)
    
    dpi = dpi if dpi else plt.gcf().dpi
    
    plt.savefig(figure_path, bbox_inches='tight', dpi=dpi)
    plt.close()
