import click

import fnmatch

from .core import DelimitedStr

kItemChoices = ['workspace', 'dataset', 'snapshot', 'category', 'poi', 
                'detailed_nuisance_parameter', 'nuisance_parameter',
                'global_observable', 'auxiliary']
kDefaultItems = ",".join(['workspace', 'dataset', 'snapshot', 'category',
                 'poi', 'detailed_nuisance_parameter'])
    
@click.command(name='inspect_ws')
@click.option('-i', '--input_file', required=True, help='Path to the input workspace file')
@click.option('-w', '--workspace', 'ws_name', default=None, help='Name of workspace. Auto-detect by default.')
@click.option('-d', '--dataset', 'data_name', default=None, help='Name of dataset. Generally not needed.')
@click.option('-m', '--model_config', 'mc_name', default=None, help='Name of model config. Auto-detect by default.')
@click.option('-o', '--output_file', default=None, help='Export output to text file. If None, no output is saved.')
@click.option('--items', cls=DelimitedStr, type=click.Choice(kItemChoices), show_default=True,
              default=kDefaultItems, help='Items to include in the summary (separated by commas).')
@click.option('--include', 'include_patterns', default=None, 
              help='Match variable names with given patterns (separated by commas).')
@click.option('--exclude', 'exclude_patterns', default=None,
              help='Exclude variable names with given patterns (separated by commas).')
@click.option('--detailed/--name-only', default=True, show_default=True,
              help='Include detailed variable properties or just the variable name in the summary.')
def inspect_ws(input_file, ws_name=None, data_name=None, mc_name=None, output_file=None, items=None,
               include_patterns=None, exclude_patterns=None, detailed=True):
    '''
        Inspect workspace attributes
    '''
    from quickstats.components import ExtendedModel
    model = ExtendedModel(input_file, ws_name=ws_name, mc_name=mc_name, data_name=data_name,
                          verbosity="WARNING")
    from quickstats.utils.string_utils import split_str
    #items = items.split(",") if items is not None else None
    include_patterns = split_str(include_patterns, ',') if include_patterns is not None else None
    exclude_patterns = split_str(exclude_patterns, ',') if exclude_patterns is not None else None
    model.stdout.verbosity = "INFO"
    model.print_summary(items=items, save_as=output_file, detailed=detailed,
                        include_patterns=include_patterns, exclude_patterns=exclude_patterns)