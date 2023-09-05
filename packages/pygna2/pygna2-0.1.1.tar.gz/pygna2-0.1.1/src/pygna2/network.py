#===============================================================================
# network.py
#===============================================================================

"""Network properties"""

# Imports ======================================================================

import logging
import numpy as np
from itertools import chain, combinations, islice
import networkx as nx
from pygna.output import write_graph_summary
from pygna.diagnostic import plot_connected_components, plot_degree
from pygna2.parse_network_genesets import parse_network_and_genesets

# Functions ====================================================================

def summary(network: str, output: str, genesets=None, setnames=None,
            net_name: str = 'network', max_components=None,
            min_component_size: int = 2, min_set_size: int = 20,
            plot_degree_file=None, plot_component_file=None,
            filtered_network_file=None):
    """Generate a text file summarizing either the entire input network or
    a subnetwork defined by one or more gene sets.

    Parameters
    ----------
    network : str
        TSV file defining the input network
    output : str
        Text file containing summary
    genesets
        GMT file containing gene sets (default: None)
    setnames
        List of gene set names (default: None)
    min_set_size : int
        Only consider gene sets with more than n genes (default: 20)
    net_name : str
        Name of network to record in output file (default: network)
    max_components
        Load only n largest components
    min_component_size
        Load only components with at least n genes (default: 2)
    max_output_components
        Store only n largest components
    min_output_component_size
        Store only components with at least n genes (default: 2)
    plot_degree_file
        Output file for degree plot (default: None)
    plot_component_file
        Output file for component plot (default: None)
    filtered_network_file
        Output file for filtered network (default: None)
    """
    
    logging.info("Evaluating network summary, please wait")
    network, genesets = parse_network_and_genesets(network, genesets=genesets,
        setnames=setnames, max_components=max_components,
        min_component_size=min_component_size, min_set_size=min_set_size)
    if genesets:
        genes = set(chain.from_iterable(genesets.values()))
        network = nx.subgraph(network, genes)
    write_graph_summary(network, output, net_name=net_name)
    if plot_degree_file:
        plot_degree(nx.degree(network), plot_degree_file)
    if plot_component_file:
        plot_connected_components(nx.connected_components(network),
                                  plot_component_file)
    if filtered_network_file:
        nx.to_pandas_edgelist(network).to_csv(filtered_network_file,
            sep='\t', header=False, index=False)
    logging.info("Network summary completed")


def filter_network(network: str, output: str, genesets=None, setnames=None,
           max_components=None, min_component_size: int = 2,
           min_set_size: int = 20,
           max_output_components=None, min_output_component_size: int = 2):
    """Filter small components out of the network

    Parameters
    ----------
    network : str
        TSV file defining the input network
    output : str
        TSV file containing filtered network
    genesets
        GMT file containing gene sets (default: None)
    setnames
        List of gene set names (default: None)
    min_set_size : int
        Only consider gene sets with more than n genes (default: 20)
    max_components
        Load only n largest components
    min_component_size
        Load only components with at least n genes (default: 2)
    max_output_components
        Store only n largest components
    min_output_component_size
        Store only components with at least n genes (default: 2)
    """

    network, genesets = parse_network_and_genesets(network, genesets=genesets,
        setnames=setnames, max_components=max_components,
        min_component_size=min_component_size, min_set_size=min_set_size)
    if genesets:
        genes = set(chain.from_iterable(genesets.values()))
        network = nx.subgraph(network, genes)
    if max_output_components or (min_output_component_size > 2):
        filtered_network = nx.Graph()
        for component in filter(lambda c: len(c)>=min_output_component_size,
                                islice(sorted(nx.connected_components(network),
                                    key=len, reverse=True), max_output_components)):
            filtered_network = nx.compose(filtered_network,
                                          network.subgraph(component).copy())
        network = filtered_network
    nx.to_pandas_edgelist(network).to_csv(output,
        sep='\t', header=False, index=False)

def cytoscape(network: str, output_gml: str, output_gmt,
              genesets=None, setnames=None,
              max_components=None, min_component_size: int = 2,
              max_output_components=None, min_output_component_size: int = 2,
              minimal: bool = False, full_network: bool = False,
              filtered_network_file=None):
    """Generate a text file summarizing either the entire input network or
    a subnetwork defined by one or more gene sets.

    Parameters
    ----------
    network : str
        TSV file defining the input network
    output_gml : str
        GraphML file containing annotated network or subnetwork
    output_gmt
        GMT file containing modules
    genesets
        GMT file containing gene sets (default: None)
    setnames
        List of gene set names (default: None)
    max_components
        Load only n largest components
    min_component_size
        Load only components with at least n genes (default: 2)
    max_output_components
        Store only n largest components
    min_output_component_size
        Store only components with at least n genes (default: 2)
    minimal : bool
        Trim all genes that are not part of a path between set members (default: False)
    full_network : bool
        Record the full network (default: False)
    filtered_network_file
        Output file for filtered network (default: None)
    """

    network, genesets = parse_network_and_genesets(network, genesets=genesets,
        setnames=setnames, max_components=max_components,
        min_component_size=min_component_size)
    if not full_network:
        new_network = nx.Graph()
        genes = set(chain.from_iterable(genesets.values()))
        network_nodes = network.nodes()
        if minimal:
            for source, target in combinations((g for g in genes
                                                if g in network_nodes), 2):
                path = nx.shortest_path(network, source=source, target=target)
                if len(path) < np.inf:
                    new_network.add_path(path)
        else:
            for component in (network.subgraph(c).copy()
                            for c in nx.connected_components(network)):
                if set(component.nodes()).intersection(genes):
                    new_network = nx.compose(new_network, component)
        network = new_network
    network_nodes = network.nodes()
    for setname, genes in genesets.items():
        dict_nodes = {n: n in genes for n in network_nodes}
        nx.set_node_attributes(network, dict_nodes, setname)
    nx.write_graphml(network, output_gml)
    if output_gmt:
        with open(output_gmt, 'w') as f:
            for index, component in enumerate(filter(
                                    lambda c: len(c)>=min_output_component_size,
                                    islice(sorted(nx.connected_components(network),
                                    key=len, reverse=True),
                                    max_output_components))):
                f.write('\t'.join((f'module_{index}', str(len(component))
                                  + tuple(component))) + '\n')
    if filtered_network_file:
        if max_output_components or (min_output_component_size > 2):
            filtered_network = nx.Graph()
            for component in filter(lambda c: len(c)>=min_output_component_size,
                                    islice(sorted(nx.connected_components(network),
                                        key=len, reverse=True), max_output_components)):
                filtered_network = nx.compose(filtered_network,
                                            network.subgraph(component).copy())
            network = filtered_network
        nx.to_pandas_edgelist(network).to_csv(filtered_network_file,
            sep='\t', header=False, index=False)
