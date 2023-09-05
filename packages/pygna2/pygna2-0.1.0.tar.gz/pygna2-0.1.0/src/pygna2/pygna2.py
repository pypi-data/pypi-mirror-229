#===============================================================================
# pygna2.py
#===============================================================================

"""Gene network analysis"""

# Imports ======================================================================

import logging
from argparse import ArgumentParser
import pygna.statistical_test as st
from pygna2.version import __version__
from pygna2.network import summary, filter_network, cytoscape
from pygna2.matrix import build_rwr_diffusion_matrix
from pygna2.test_topology import test_topology

# Logging ======================================================================

logging.basicConfig(level=logging.INFO)

# Functions ====================================================================

def _summary(args):
    summary(args.network, args.output, genesets=args.genesets,
            setnames=args.setname, net_name=args.network_name,
            max_components=args.max_components,
            min_component_size=args.min_component_size,
            min_set_size=args.min_set_size,
            plot_degree_file=args.plot_degree,
            plot_component_file=args.plot_component,
            filtered_network_file=args.filtered_network)


def _filter_network(args):
    filter_network(args.network, args.output, genesets=args.genesets,
            setnames=args.setname, max_components=args.max_components,
            min_component_size=args.min_component_size,
            min_set_size=args.min_set_size,
            max_output_components=args.max_output_components,
            min_output_component_size=args.min_output_component_size)


def _cytoscape(args):
    cytoscape(args.network, args.output_gml, args.output_gmt,
              genesets=args.genesets, setnames=args.setname,
              max_components=args.max_components,
              min_component_size=args.min_component_size,
              min_set_size=args.min_set_size,
              max_output_components=args.max_output_components,
              min_output_component_size=args.min_output_component_size,
              minimal=args.minimal, full_network=args.full,
              filtered_network_file=args.filtered_network)


def _build_rwr_diffusion_matrix(args):
    build_rwr_diffusion_matrix(args.network, args.output, beta=args.beta,
                               max_components=args.max_components,
                               min_component_size=args.min_component_size,
                               filtered_network_file=args.filtered_network)


def _test_topology_total_degree(args):
    test_topology(args.network, args.genesets, args.output,
        stat=st.geneset_total_degree_statistic,
        stat_name='topology_total_degree',
        setnames=args.setname, max_components=args.max_components,
        min_component_size=args.min_component_size,
        min_set_size=args.min_set_size,
        results_figure=args.results_figure,
        results_figure_type=args.results_figure_type,
        results_figure_significance=args.results_figure_significance,
        results_figure_x_label='Topology Total Degree',
        width=args.width, height=args.height,
        null_distributions=args.null_distributions,
        filtered_network_file=args.filtered_network,
        degree_correction_bins=args.degree_correction_bins,
        permutations=args.permutations, processes=args.cores)


def _test_topology_internal_degree(args):
    test_topology(args.network, args.genesets, args.output,
        setnames=args.setname, max_components=args.max_components,
        min_component_size=args.min_component_size,
        min_set_size=args.min_set_size,
        results_figure=args.results_figure,
        results_figure_type=args.results_figure_type,
        results_figure_significance=args.results_figure_significance,
        width=args.width, height=args.height,
        null_distributions=args.null_distributions,
        filtered_network_file=args.filtered_network,
        degree_correction_bins=args.degree_correction_bins,
        permutations=args.permutations, processes=args.cores)


def _test_topology_module(args):
    test_topology(args.network, args.genesets, args.output,
        stat=st.geneset_module_statistic,
        stat_name='topology_module',
        setnames=args.setname, max_components=args.max_components,
        min_component_size=args.min_component_size,
        min_set_size=args.min_set_size,
        results_figure=args.results_figure,
        results_figure_type=args.results_figure_type,
        results_figure_significance=args.results_figure_significance,
        results_figure_x_label='Largest Module Size',
        width=args.width, height=args.height,
        null_distributions=args.null_distributions,
        filtered_network_file=args.filtered_network,
        degree_correction_bins=args.degree_correction_bins,
        permutations=args.permutations, processes=args.cores)


def _test_topology_rwr(args):
    test_topology(args.network, args.genesets, args.output, 
        rwr_matrix=args.rwr_matrix,
        stat=st.geneset_RW_statistic,
        stat_name='topology_rwr',
        setnames=args.setname, max_components=args.max_components,
        min_component_size=args.min_component_size,
        min_set_size=args.min_set_size,
        results_figure=args.results_figure,
        results_figure_type=args.results_figure_type,
        results_figure_significance=args.results_figure_significance,
        results_figure_x_label='Topology RWR statistic',
        width=args.width, height=args.height,
        null_distributions=args.null_distributions,
        filtered_network_file=args.filtered_network,
        rwr_matrix_in_memory=args.in_memory,
        degree_correction_bins=args.degree_correction_bins,
        permutations=args.permutations, processes=args.cores)


def add_network_arg(parser):
    parser.add_argument('network', metavar='<network.tsv>',
        help='Table defining network, 1st 2 cols should be gene pairs/edges')


def add_network_args(parser):
    add_network_arg(parser)
    parser.add_argument('--max-components', metavar='<int>', type=int,
        help='Use only n largest components')
    parser.add_argument('--min-component-size', metavar='<int>', type=int,
        default=2,
        help='Use only components with at least n genes (default: 2)')


def add_geneset_args(parser):
    parser.add_argument('--genesets', metavar='<genesets.gmt>',
                        help='GMT file containing gene sets')
    parser.add_argument('--setname', metavar='<name>', nargs='+',
                        help='List of gene set names')
    parser.add_argument('--min-set-size', metavar='<int>', default=20,
                        help='Minimum gene set size (default: 20)')


def construct_network_parser(parser, func):
    parser.set_defaults(func=func)
    add_network_args(parser)
    add_geneset_args(parser)

def add_output_component_args(parser):
    parser.add_argument('--max-output-components', metavar='<int>', type=int,
        help='Store only n largest components')
    parser.add_argument('--min-output-component-size', metavar='<int>',
        type=int, default=2,
        help='Store only components with at least n genes (default: 2)')


def construct_test_parser(parser, func):
    parser.set_defaults(func=func)
    add_network_args(parser)
    parser.add_argument('genesets', metavar='<genesets.gmt>',
                        help='GMT file containing gene sets')
    parser.add_argument('output', metavar='<output.{csv,tsv}>',
                        help='Results table file')
    parser.add_argument('--setname', metavar='<name>', nargs='+',
                        help='List of gene set names')
    parser.add_argument('--min-set-size', metavar='<int>', default=20,
                        help='Minimum gene set size (default: 20)')
    parser.add_argument('--results-figure', metavar='<figure.{pdf,png,svg}>',
                        help='Path to results figure')
    parser.add_argument('--results-figure-type',
                        choices=('box', 'violin', 'strip'), default='box',
                        help='Type of results figure(default: box)')
    parser.add_argument('--results-figure-significance', action='store_true',
                        help='Draw asterisks over significant results')
    parser.add_argument('--width', metavar='<float>', type=float, default=7.0,
                        help='Width of plot in inches')
    parser.add_argument('--height', metavar='<float>', type=float, default=7.0,
                        help='Height of plot in inches')
    parser.add_argument('--null-distributions', metavar='<null.{csv,tsv}>',
                        help='Write null distributions to disk')
    parser.add_argument('--filtered-network', metavar='<filtered.tsv>',
        help='Write TSV file containing filtered network')
    parser.add_argument('--degree-correction-bins', metavar='<int>', type=int,
        default=1, help='Apply degree correction using n bins (default: 1)')
    parser.add_argument('--permutations', metavar='<int>', type=int,
                        default=200,
                        help='Number of permutations (default: 200)')
    parser.add_argument('--cores', metavar='<int>', type=int, default=1,
                        help='Number of cores (default: 1)')
    

def parse_arguments():
    parser = ArgumentParser(
        description='Statistical tests on gene networks and gene sets')
    parser.add_argument('--version', action='version',
        version='%(prog)s {version}'.format(version=__version__))
    subparsers = parser.add_subparsers()
    
    # Network parsers
    parser_network = subparsers.add_parser('network',
        help='Report properties of the network')
    network_parsers = parser_network.add_subparsers()
    parser_network_summary = network_parsers.add_parser('summary',
        help='Summarize the network')
    construct_network_parser(parser_network_summary, _summary)
    parser_network_summary.add_argument('output', metavar='<output.txt>',
                              help='Text file containing summary')
    parser_network_summary.add_argument('--network-name', metavar='<name>',
        default='network', help='A name for the network')
    parser_network_summary.add_argument('--plot-degree',
        metavar='<output.{pdf,png}>', help='Plot the degree distribution')
    parser_network_summary.add_argument('--plot-component',
        metavar='<output.{pdf,png}>',
        help='Plot the distribution of component sizes')
    parser_network_summary.add_argument('--filtered-network',
        metavar='<filtered.tsv>',
        help='Write TSV file containing filtered network')
    parser_network_filter = network_parsers.add_parser('filter',
        help='Filter small components out of the network')
    construct_network_parser(parser_network_filter, _filter_network)
    add_output_component_args(parser_network_filter)
    parser_network_filter.add_argument('output', metavar='<output.tsv>',
        help='TSV file containing filtered network')
    parser_network_cytoscape = network_parsers.add_parser('cytoscape',
        help='Generate a GraphML file that can be viewed in cytoscape')
    construct_network_parser(parser_network_cytoscape, _cytoscape)
    add_output_component_args(parser_network_cytoscape)
    parser_network_cytoscape.add_argument('output-gml', metavar='<output.gml>',
        help='GraphML file containing network or subnetwork')
    parser_network_cytoscape.add_argument('output-gmt', metavar='<output.gmt>',
        nargs='?', help='GMT file containing modules')
    completeness_group = parser_network_cytoscape.add_mutually_exclusive_group()
    completeness_group.add_argument('--minimal', action='store_true',
        help='Store a minimal network')
    completeness_group.add_argument('--full', action='store_true',
        help='Store the full network')
    parser_network_cytoscape.add_argument('--filtered-network',
        metavar='<filtered.tsv>',
        help='Write TSV file containing filtered network')
    
    # Build parser
    parser_build = subparsers.add_parser('build',
        help='Build a RWR diffusion matrix')
    parser.set_defaults(func=_build_rwr_diffusion_matrix)
    add_network_args(parser_build)
    parser_build.add_argument('output', metavar='<rwr-matrix.hdf5>',
                         help='Output file for RWR diffusion matrix')
    parser_build.add_argument('--beta', metavar='<float>', type=float,
                         default=0.85, help='Restart probability (default: 0.85)')
    parser_build.add_argument('--filtered-network', metavar='<filtered.tsv>',
                              help='Write TSV file containing filtered network')

    # Test parsers
    parser_test = subparsers.add_parser('test', help='Statistical tests')
    test_parsers = parser_test.add_subparsers()
    parser_ttd = test_parsers.add_parser('ttd',
        help='Topology Total Degree statstic')
    construct_test_parser(parser_ttd, _test_topology_total_degree)
    parser_tid = test_parsers.add_parser('tid',
        help='Topology Internal Degree statstic')
    construct_test_parser(parser_tid, _test_topology_internal_degree)
    parser_tm = test_parsers.add_parser('tm',
        help='Topology Module statstic (largest module size)')
    construct_test_parser(parser_tm, _test_topology_module)
    parser_rwr = test_parsers.add_parser('rwr',
        help='Topology Random Walk with Restart diffusion statistic')
    construct_test_parser(parser_rwr, _test_topology_rwr)
    parser_rwr.add_argument('rwr_matrix', metavar='<rwr-matrix.hdf5>',
        help='RWR diffusion matrix')
    parser_rwr.add_argument('--in-memory', action='store_true',
        help='Load the entire RWR diffusion matrix in memory')
    return parser.parse_args()

def main():
    args = parse_arguments()
    args.func(args)
