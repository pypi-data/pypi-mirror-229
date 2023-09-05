import os
import json
import click

class DelimitedStr(click.Option):
    def type_cast_value(self, ctx, value):
        try:
            return [i.strip() for i in value.split(",")]
        except:
            raise click.BadParameter(value)

@click.command(name='run_pulls')
@click.option('-i', '--input_file', 'filename', required=True, 
              help='Path to the input workspace file')
@click.option('-x', '--poi', 'poi_name', default=None,
              help='POI to measure NP impact on')
@click.option('-o', '--outdir', default="pulls", show_default=True,
              help='Output directory')
@click.option('-w', '--workspace', 'ws_name', default=None, 
              help='Name of workspace. Auto-detect by default.')
@click.option('-m', '--model_config', 'mc_name', default=None, 
              help='Name of model config. Auto-detect by default.')
@click.option('-d', '--data', 'data_name', default='combData', show_default=True,
              help='Name of dataset')
@click.option('--filter', 'filter_expr', default=None, show_default=True,
              help='Filter nuisance parameter(s) to run pulls and impacts on.'+\
                   'Multiple parameters are separated by commas.'+\
                   'Wildcards are accepted. All NPs are included by default.')
@click.option('-r', '--profile', 'profile_param', default=None, show_default=True,
              help='Parameters to profile')
@click.option('-f', '--fix', 'fix_param', default=None, show_default=True,
              help='Parameters to fix')
@click.option('-s', '--snapshot', 'snapshot_name', default=None, show_default=True,
              help='Name of initial snapshot')
@click.option('-t', '--minimizer_type', default="Minuit2", show_default=True,
              help='Minimizer type')
@click.option('-a', '--minimizer_algo', default="Migrad", show_default=True,
              help='Minimizer algorithm')
@click.option('-c', '--num_cpu', type=int, default=1, show_default=True,
              help='Number of CPUs to use per parameter')
@click.option('--binned/--unbinned', 'binned_likelihood', default=True, show_default=True,
              help='Binned likelihood')
@click.option('-q', '--precision', type=float, default=0.001, show_default=True,
              help='Precision for scan')
@click.option('-e', '--eps', type=float, default=1.0, show_default=True,
              help='Convergence criterium')
@click.option('--retry', type=int, default=2, show_default=True,
              help='Maximum number of retries upon a failed fit')
@click.option('--print_level', type=int, default=-1, show_default=True,
              help='Minimizer print level')
@click.option('--strategy', type=int, default=1, show_default=True,
              help='Default strategy')
@click.option('--fix-cache/--no-fix-cache', default=True, show_default=True,
              help='Fix StarMomentMorph cache')
@click.option('--fix-multi/--no-fix-multi', default=True, show_default=True,
              help='Fix MultiPdf level 2')
@click.option('--offset/--no-offset', default=True, show_default=True,
              help='Offset likelihood')
@click.option('--optimize', type=int, default=2, show_default=True,
              help='Optimize constant terms')
@click.option('--max_calls', type=int, default=-1, show_default=True,
              help='Maximum number of function calls')
@click.option('--max_iters', type=int, default=-1, show_default=True,
              help='Maximum number of Minuit iterations')
@click.option('--batch_mode/--no-batch', default=False, show_default=True,
              help='Batch mode when evaluating likelihood')
@click.option('--int_bin_precision', type=float, default=-1., show_default=True,
              help='Integrate the PDF over the bins instead of using the probability '
                   'density at the bin centre')
@click.option('--parallel', type=int, default=-1, show_default=True,
              help='\b\n Parallelize job across the N workers.'
                   '\b\n Case  0: Jobs are run sequentially (for debugging).'
                   '\b\n Case -1: Jobs are run across N_CPU workers.')
@click.option('--cache/--no-cache', default=True, show_default=True,
              help='Cache existing result')
@click.option('--exclude', 'exclude_expr', default=None, show_default=True,
              help='Exclude NPs to run pulls and impacts on. '+\
                   'Multiple parameters are separated by commas.'+\
                   'Wildcards are accepted.')
@click.option('--save_log/--skip_log', default=True, show_default=True,
              help='Save log file.')
@click.option('--constrained_only/--any_nuis', default=True, show_default=True,
              help='Whether to include constrained nuisance parameters only')
@click.option('--version', type=click.Choice(['1', '2']), default='2', show_default=True,
              help='Version of tool to use (Choose between 1 and 2).')
@click.option('-v', '--verbosity', default='INFO', show_default=True,
              type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
              help='Verbosity level.')
def run_pulls(**kwargs):
    """
    Tool for computing NP pulls and impacts
    """
    version = kwargs.pop('version')
    if version == '1':
        from quickstats.components import NuisanceParameterPull
        NuisanceParameterPull().run_pulls(**kwargs)
    elif version == '2':
        from quickstats.concurrent import NuisanceParameterRankingRunner
        init_kwargs = {}
        for key in ['filename', 'filter_expr', 'exclude_expr', 'poi_name',
                    'data_name', 'cache', 'outdir', 'constrained_only',
                    'save_log', 'parallel', 'verbosity']:
            init_kwargs[key] = kwargs.pop(key)
        init_kwargs['config'] = kwargs
        runner = NuisanceParameterRankingRunner(**init_kwargs)
        runner.run()
    
@click.command(name='plot_pulls')
@click.option('-i', '--inputdir', required=True, help='Path to directory containing pull results')
@click.option('-p', '--poi', default=None, help='Parameter of interest for plotting impact')
@click.option('-n', '--n_rank', type=int, default=None, help='Total number of NP to rank')
@click.option('-m', '--rank_per_plot', type=int, default=20, show_default=True,
              help='Number of NP to show in a single plot')
@click.option('--ranking/--no_ranking', default=True, show_default=True,
              help='Rank NP by impact')
@click.option('--threshold', type=float, default=0., show_default=True,
              help='Filter NP by postfit impact threshold')
@click.option('--show_sigma/--hide_sigma', default=True, show_default=True,
              help='Show one standard deviation pull')
@click.option('--show_prefit/--hide_prefit', default=True, show_default=True,
              help='Show prefit impact')
@click.option('--show_postfit/--hide_postfit', default=True, show_default=True,
              help='Show postfit impact')
@click.option('--sigma_bands/--no_sigma_bands', default=False, show_default=True,
              help='Draw +-1, +-2 sigma bands')
@click.option('--sigma_lines/--no_sigma_lines', default=True, show_default=True,
              help='Draw +-1 sigma lines')
@click.option('--ranking_label/--no_ranking_label', default=True, show_default=True,
              help='Show ranking labels')
@click.option('--shade/--no_shade', default=True, show_default=True,
              help='Draw shade')
@click.option('--correlation/--no_correlation', default=True, show_default=True,
              help='Show correlation impact')
@click.option('--onesided/--overlap', default=True, show_default=True,
              help='Show onesided impact')
@click.option('--relative/--absolute', default=False, show_default=True,
              help='Show relative variation')
@click.option('--theta_max', type=float, default=2, show_default=True,
              help='Pull range')
@click.option('-y', '--padding', type=int, default=7, show_default=True,
              help='Padding below plot for texts and legends. NP column height is 1 unit.')
@click.option('-h', '--height', type=float, default=1.0, show_default=True,
              help='NP column height')
@click.option('-s', '--spacing', type=float, default=0., show_default=True,
              help='Spacing between impact box')
@click.option('--label-fontsize', type=float, default=20., show_default=True,
              help='Fontsize of analysis label text')
@click.option('-d', '--display_poi', default=r"$\mu$", show_default=True,
              help='POI name to be shown in the plot')
@click.option('-t', '--extra_text', default=None, help='Extra texts below the ATLAS label. '+\
                                                       'Use "//" as newline delimiter')
@click.option('--elumi_label/--no_elumi_label', default=True, show_default=True,
              help='Show energy and luminosity labels')
@click.option('--ranking_label/--no_ranking_label', default=True, show_default=True,
              help='Show ranking label')
@click.option('--energy', default="13 TeV", show_default=True, 
              help='Beam energy')
@click.option('--lumi', default="140 fb$^{-1}$", show_default=True, 
              help='Luminosity')
@click.option('--status', default="int", show_default=True, 
              help='\b\n Analysis status. Choose from'
                   '\b\n            int : Internal'
                   '\b\n            wip : Work in Progress'
                   '\b\n         prelim : Preliminary'
                   '\b\n          final : *no status label*'
                   '\b\n *custom input* : *custom input*')
@click.option('--combine_pdf/--split_pdf', default=True, show_default=True,
              help='Combine all ranking plots into a single pdf')
@click.option('--outdir', default='ranking_plots', show_default=True,
              help='Output directory')
@click.option('-o', '--outname', default='ranking', show_default=True,
              help='Output file name prefix')
@click.option('--style', default='default', show_default=True,
              help='Plotting style. Built-in styles are "default" and "trex".'+\
                   'Specify path to yaml file to set custom plotting style.')
@click.option('--fix_axis_scale/--free_axis_scale', default=True, show_default=True,
              help='Fix the axis scale across all ranking plots')
@click.option('--version', type=click.Choice(['1', '2']), default='2', show_default=True,
              help='Version of tool to use (Choose between 1 and 2).')
def plot_pulls(**kwargs):
    """
    Tool for plotting NP pulls and impact rankings
    """    
    from quickstats.plots.np_ranking_plot import NPRankingPlot
    inputdir, poi = kwargs.pop('inputdir'), kwargs.pop('poi')
    version = kwargs.pop('version')
    ranking_plot = NPRankingPlot(inputdir, poi, version=version)
    ranking_plot.plot(**kwargs)

@click.command(name='cls_limit')
@click.option('-i', '--input_file', 'filename', required=True, 
              help='Path to the input workspace file')
@click.option('-p', '--poi', 'poi_name', default=None, show_default=True,
              help='POI to scan. If not specified, the first POI from the workspace is used.')
@click.option('-d', '--data', 'data_name', default='combData', show_default=True,
              help='Name of dataset')
@click.option('--asimov_data_name', 'asimov_data_name', default=None,
              help='If given, use custom background asimov dataset instead of generating on the fly.')
@click.option('-o', '--outname', default='limits.json', show_default=True,
              help='Name of output')
@click.option('--mu_exp', type=float, default=0, show_default=True,
              help='Expected signal strengh value to be used for Asimov generation')
@click.option('--blind/--unblind', 'do_blind', default=True, show_default=True,
              help='Blind/unblind analysis')
@click.option('--CL', 'CL', type=float, default=0.95, show_default=True,
              help='CL value to use')
@click.option('--precision', default=0.005, show_default=True,
              help='precision in mu that defines iterative cutoff')
@click.option('--adjust_fit_range/--keep_fit_range', default=True, show_default=True,
              help='whether to adjust the fit range to median limit +- 5 sigma for observed fit')
@click.option('--do_tilde/--no_tilde', default=True, show_default=True,
              help='bound mu at zero if true and do the \tilde{q}_{mu} asymptotics')
@click.option('--predictive_fit/--no_predictive_fit', default=False, show_default=True,
              help='extrapolate best fit nuisance parameters based on previous fit results')
@click.option('--do_better_bands/--skip_better_bands', default=True, show_default=True,
              help='evaluate asymptotic CLs limit for various sigma bands')
@click.option('--better_negative_bands/--skip_better_negative_bands', default=False, show_default=True,
              help='evaluate asymptotic CLs limit for negative sigma bands')
@click.option('--binned/--unbinned', 'binned_likelihood', default=True, show_default=True,
              help='Binned likelihood')
@click.option('--save_summary/--skip_summary', default=True, show_default=True,
              help='Save summary information')
@click.option('-f', '--fix', 'fix_param', default="", show_default=True,
              help='Parameters to fix')
@click.option('-r', '--profile', 'profile_param', default="", show_default=True,
              help='Parameters to profile')
@click.option('-w', '--workspace', 'ws_name', default=None, show_default=True,
              help='Name of workspace. Auto-detect by default.')
@click.option('-m', '--model_config', 'mc_name', default=None, show_default=True,
              help='Name of model config. Auto-detect by default.')
@click.option('-s', '--snapshot', 'snapshot_name', default=None, show_default=True,
              help='Name of initial snapshot')
@click.option('-t', '--minimizer_type', default="Minuit2", show_default=True,
              help='Minimizer type')
@click.option('-a', '--minimizer_algo', default="Migrad", show_default=True,
              help='Minimizer algorithm')
@click.option('-e', '--eps', type=float, default=1.0, show_default=True,
              help='Convergence criterium')
@click.option('--retry', type=int, default=2, show_default=True,
              help='Maximum number of retries upon a failed fit')
@click.option('--strategy', type=int, default=1, show_default=True,
              help='Default minimization strategy')
@click.option('--print_level', type=int, default=-1, show_default=True,
              help='Minimizer print level')
@click.option('--timer/--no_timer', default=False, show_default=True,
              help='Enable minimizer timer')
@click.option('-c', '--num_cpu', type=int, default=1, show_default=True,
              help='Number of CPUs to use per parameter')
@click.option('--offset/--no-offset', default=True, show_default=True,
              help='Offset likelihood')
@click.option('--optimize', type=int, default=2, show_default=True,
              help='Optimize constant terms')
@click.option('--improve', type=int, default=0, show_default=True,
              help='Execute improve after each minimization')
@click.option('--minimizer_offset', type=int, default=1, show_default=True,
              help='Enable minimizer offsetting')
@click.option('--fix-cache/--no-fix-cache', default=True, show_default=True,
              help='Fix StarMomentMorph cache')
@click.option('--fix-multi/--no-fix-cache',  default=True, show_default=True,
              help='Fix MultiPdf level 2')
@click.option('--max_calls', type=int, default=-1, show_default=True,
              help='Maximum number of function calls')
@click.option('--max_iters', type=int, default=-1, show_default=True,
              help='Maximum number of Minuit iterations')
@click.option('--batch_mode/--no-batch', default=False, show_default=True,
              help='Batch mode when evaluating likelihood')
@click.option('--int_bin_precision', type=float, default=-1., show_default=True,
              help='Integrate the PDF over the bins instead of using the probability '
                   'density at the bin centre')
@click.option('--constrain/--no-constrain', 'constrain_nuis', default=True, show_default=True,
              help='Use constrained NLL')
@click.option('-v', '--verbosity', default='INFO', show_default=True,
              type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
              help='Verbosity level.')
def cls_limit(**kwargs):
    """
    Tool for evaluating Asymptotic CLs limit
    """
    from quickstats.components import AsymptoticCLs
    outname = kwargs.pop('outname')
    save_summary = kwargs.pop('save_summary')
    asymptotic_cls = AsymptoticCLs(**kwargs)
    asymptotic_cls.evaluate_limits()
    asymptotic_cls.save(outname, summary=save_summary)

@click.command(name='compile')
@click.option('-m', '--macros', default=None, show_default=True,
              help='Macros to compile (separated by commas). By default all macros are compiled.')
def compile_macros(macros):
    """
    Compile ROOT macros
    """
    import quickstats
    quickstats.compile_macros(macros)
    
@click.command(name='add_macro')
@click.option('-i', '--input_path', 'path', required=True,
              help='Path to the directory containing the source file for the macro.')
@click.option('-n', '--name',
              help='Name of the macro. By default, the name of the input directory is used.')
@click.option('-f', '--force', is_flag=True,
              help='Force overwrite existing files.')
@click.option('--copy-files/--do-not-copy-files', 'copy_files', default=True,
              help='Whether to copy files from the input directory (required if not already copied).')
@click.option('--add-to-workspace-extension/--do-not-add-to-workspace-extension', 'workspace_extension',
              default=True, show_default=True,
              help='Whether to include the macro as part of the workspace extensions.')
def add_macro(**kwargs):
    """
    Add a ROOT macro to the module
    """
    import quickstats
    quickstats.add_macro(**kwargs)
    
@click.command(name='remove_macro')
@click.option('-n', '--name', required=True,
              help='Name of the macro.')
@click.option('-f', '--force', is_flag=True,
              help='Force remove files without notification.')
@click.option('--remove-files/--do-not-remove-files', 'remove_files',
              default=False, show_default=True,
              help='Whether to remove the macro from the workspace extension list only or also remove the files.')
def remove_macro(**kwargs):
    """
    Remove a ROOT macro from the module
    """    
    import quickstats
    quickstats.remove_macro(**kwargs)

@click.command(name='harmonize_np')
@click.argument('ws_files', nargs=-1)
@click.option('-r', '--reference', required=True, help='Path to reference json file containing renaming scheme')
@click.option('-i', '--input_config_path', default=None, show_default=True,
              help='Path to json file containing input workspace paths')
@click.option('-b', '--base_path', default='./', show_default=True,
              help='Base path for input config')
@click.option('-o', '--outfile', default='renamed_np.json', show_default=True,
              help='Output filename')
def harmonize_np(ws_files, reference, input_config_path, base_path, outfile):
    """
    Harmonize NP names across different workspaces
    """
    from quickstats.components import NuisanceParameterHarmonizer
    harmonizer = NuisanceParameterHarmonizer(reference)
    if (len(ws_files) > 0) and input_config_path is not None:
        raise RuntimeError('either workspace paths or json file containing workspace paths should be given')
    if len(ws_files) > 0:
        harmonizer.harmonize(ws_files, outfile=outfile)
    elif (input_config_path is not None):
        harmonizer.harmonize_multi_input(input_config_path, base_path, outfile=outfile)
        
        
@click.command(name='generate_asimov')
@click.option('-i', '--input_file', 'filename', required=True, 
              help='Path to the input workspace file.')
@click.option('-o', '--output_file', 'outname', required=True, 
              help='Name of the output workspace containing the '
                   'generated asimov dataset.')
@click.option('-p', '--poi', required=True, 
              help='Name of the parameter of interest (POI).')
@click.option('--poi_val', type=float, default=None, show_default=True,
              help='Generate asimov data with POI set at the specified value. '
                   'If None, POI will be kept at the post-fit value if a fitting '
                   'is performed or the pre-fit value if no fitting is performed.')
@click.option('--poi_profile', type=float, default=None, show_default=True,
              help='Perform nuisance parameter profiling with POI set at the specified value. '
                   'This option is only effective if do_fit is set to True. If None, POI is '
                   'set floating (i.e. unconditional maximum likelihood estimate).')
@click.option('-f', '--fix', 'fix_param', default="", show_default=True,
              help='Parameters to fix')
@click.option('-r', '--profile', 'profile_param', default="", show_default=True,
              help='Parameters to profile')
@click.option('-s', '--snapshot', 'snapshot_name', default=None, show_default=True,
              help='Name of initial snapshot')
@click.option('--modify-globs/--keep-globs', default=True, show_default=True,
              help='Match the values of nuisance parameters and the corresponding global '
                   'observables when generating the asimov data. This is important for making '
                   'sure the asimov data has the (conditional) minimal NLL.')
@click.option('--do-fit/--no-fit', default=True, show_default=True,
              help='Perform nuisance parameter profiling with a fit to the given dataset.')
@click.option('--asimov_name', default="asimovData_{mu}", show_default=True,
              help='Name of the generated asimov dataset.')
@click.option('--asimov_snapshot', default="asimovData_{mu}", show_default=True,
              help='Name of the snapshot that generates the asimov dataset.')
@click.option('-d', '--data', default='combData', show_default=True,
              help='Name of the dataset used in NP profiling.')
@click.option('--constraint_option', default=0, show_default=True,
              help='\b\n Customize the target of nuisance paramaters involved in the profiling.'
                   '\b\n Case 0: All nuisance parameters are allowed to float;'
                   '\b\n Case 1: Constrained nuisance parameters are fixed to 0.'
                   '\b\n         Unconstrained nuisrance parameters are allowed to float.')
@click.option('-c', '--configuration', default=None,
              help='Path to the json configuration file containing'
                   ' the minimizer options for NP profiling.')
@click.option('--rebuild/--do-not-rebuild', default=False, show_default=True,
              help='Rebuild the workspace.')
@click.option('-v', '--verbosity', default='INFO', show_default=True,
              type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
              help='Verbosity level.')
def generate_asimov(**kwargs):
    """
    Generate Asimov dataset
    """
    from quickstats.components import AnalysisBase
    filename      = kwargs.pop('filename')
    data_name     = kwargs.pop('data')
    poi_name      = kwargs.pop('poi')
    outname       = kwargs.pop('outname')
    verbosity     = kwargs.pop('verbosity')
    fix_param     = kwargs.pop('fix_param')
    profile_param = kwargs.pop('profile_param')
    snapshot_name = kwargs.pop('snapshot_name')
    config_file   = kwargs.pop('configuration')
    rebuild       = kwargs.pop('rebuild')
    if config_file is not None:
        config = json.load(open(config_file, 'r'))
    else:
        config = {}
    config['fix_param'] = fix_param
    config['profile_param'] = profile_param
    config['snapshot_name'] = snapshot_name
    asimov_config = {
        "poi_val"         : kwargs.pop("poi_val"),
        "poi_profile"     : kwargs.pop("poi_profile"),
        "do_fit"          : kwargs.pop("do_fit"),
        "modify_globs"    : kwargs.pop("modify_globs"),
        "do_import"       : True,
        "asimov_name"     : kwargs.pop("asimov_name"),
        "asimov_snapshot" : kwargs.pop("asimov_snapshot"),
        "constraint_option" : kwargs.pop("constraint_option"),
        "restore_states"  : 0
    }
    analysis = AnalysisBase(filename, poi_name=poi_name, data_name=data_name,
                            config=config, verbosity=verbosity)
    analysis.generate_asimov(**asimov_config)
    analysis.save(outname, rebuild=rebuild)

@click.command(name='generate_standard_asimov')
@click.option('-i', '--input_file', 'filename', required=True, 
              help='Path to the input workspace file.')
@click.option('-o', '--output_file', 'outname', required=True, 
              help='Name of the output workspace containing the '
                   'generated asimov dataset.')
@click.option('-d', '--data', 'data_name', default='combData', show_default=True,
              help='Name of the dataset used in NP profiling.')
@click.option('-p', '--poi', 'poi_name', required=True, 
              help='Name of the parameter of interest (POI). Multiple POIs are separated by commas.')
@click.option('-s', '--poi_scale', type=float, default=1.0, show_default=True,
              help='Scale factor applied to the poi value')
@click.option('-f', '--fix', 'fix_param', default="", show_default=True,
              help='Parameters to fix')
@click.option('-r', '--profile', 'profile_param', default="", show_default=True,
              help='Parameters to profile')
@click.option('-s', '--snapshot', 'snapshot_name', default=None, show_default=True,
              help='Name of initial snapshot')
@click.option('--rebuild/--do-not-rebuild', default=False, show_default=True,
              help='Rebuild the workspace.')
@click.option('--asimov_names', default=None, show_default=True,
              help='Names of the output asimov datasets (separated by commas). If not specified, '
                   'a default name for the corresponding asimov type will be given.')
@click.option('--asimov_snapshots', default=None, show_default=True,
              help='Names of the output asimov snapshots (separated by commas). If not specified, '
                   'a default name for the corresponding asimov type will be given.')
@click.option('-t', '--asimov_types', default="0,1,2", show_default=True,
              help='\b\n Types of asimov dataset to generate separated by commas.'
                   '\b\n 0: fit with POI fixed to 0'
                   '\b\n 1: fit with POI fixed to 1'
                   '\b\n 2: fit with POI free and set POI to 1 after fit'
                   '\b\n 3: fit with POI and constrained NP fixed to 0'
                   '\b\n 4: fit with POI fixed to 1 and constrained NP fixed to 0'
                   '\b\n 5: fit with POI free and constrained NP fixed to 0 and set POI to 1 after fit'
                   '\b\n -1: nominal NP with POI set to 0'
                   '\b\n -2: nominal NP with POI set to 1')
@click.option('-v', '--verbosity', default='INFO', show_default=True,
              type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
              help='Verbosity level.')
def generate_standard_asimov(**kwargs):
    """
    Generate standard Asimov dataset
    """
    from quickstats.components import AsimovGenerator
    from quickstats.utils.string_utils import split_str
    outname = kwargs.pop('outname')
    asimov_types = kwargs.pop('asimov_types')
    try:
        asimov_types = split_str(asimov_types, sep=",", cast=int)
    except:
        asimov_types = split_str(asimov_types, sep=",")
    fix_param = kwargs.pop('fix_param')
    profile_param = kwargs.pop('profile_param')
    snapshot_name = kwargs.pop('snapshot_name')
    poi_scale = kwargs.pop("poi_scale")
    asimov_names = kwargs.pop("asimov_names")
    asimov_snapshots = kwargs.pop("asimov_snapshots")
    verbosity = kwargs.pop("verbosity")
    rebuild = kwargs.pop("rebuild")
    kwargs['poi_name'] = split_str(kwargs.pop('poi_name'), sep=",")
    config = {
        'fix_param': fix_param,
        'profile_param': profile_param,
        'snapshot_name': snapshot_name
    }
    from quickstats.utils.string_utils import split_str
    if asimov_names is not None:
        asimov_names = split_str(asimov_names, sep=",")
    if asimov_snapshots is not None:
        asimov_snapshots = split_str(asimov_snapshots, sep=",")
    generator = AsimovGenerator(**kwargs, config=config, verbosity=verbosity)
    generator.generate_standard_asimov(asimov_types, poi_scale=poi_scale,
                                       asimov_names=asimov_names,
                                       asimov_snapshots=asimov_snapshots)
    generator.save(outname, rebuild=rebuild)

@click.command(name='toy_significance')
@click.option('-i', '--input_file', 'filename', required=True, 
              help='Path to the input workspace file.')
@click.option('-o', '--output_file', 'outname', default="toy_study/results.json", 
              help='Name of the output file containing toy results.')
@click.option('-n', '--n_toys', type=int,
              help='Number of the toys to use.')
@click.option('-b', '--batchsize', type=int, default=100, show_default=True,
              help='Divide the task into batches each containing this number of toys. '
                   'Result from each batch is saved for caching and different batches '
                   'are run in parallel if needed')
@click.option('-s', '--seed', type=int, default=0,  show_default=True,
              help='Random seed used for generating toy datasets.')
@click.option('-p', '--poi', 'poi_name', default=None,
              help='Name of the parameter of interest (POI). If None, the first POI is used.')
@click.option('-v', '--poi_val', type=float, default=0,  show_default=True,
              help='POI value when generating the toy dataset.')
@click.option('--binned/--unbinned', default=True, show_default=True,
              help='Generate binned toy dataset.')
@click.option('--cache/--no-cache', default=True,  show_default=True,
              help='Cache existing batch results.')
@click.option('--fit_options', default=None, help='A json file specifying the fit options.')
@click.option('-v', '--verbosity', default='INFO', show_default=True,
              type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
              help='Verbosity level.')
@click.option('--parallel', type=int, default=-1, show_default=True,
              help='\b\n Parallelize job across the N workers.'
                   '\b\n Case  0: Jobs are run sequentially (for debugging).'
                   '\b\n Case -1: Jobs are run across N_CPU workers.')
def toy_significance(**kwargs):
    """
    Generate toys and evaluate significance
    """
    from quickstats.components import PValueToys
    n_toys = kwargs.pop("n_toys")
    batchsize = kwargs.pop("batchsize")
    seed = kwargs.pop("seed")
    cache = kwargs.pop("cache")
    outname = kwargs.pop("outname")
    parallel = kwargs.pop("parallel")
    pvalue_toys = PValueToys(**kwargs)
    pvalue_toys.get_toy_results(n_toys=n_toys, batchsize=batchsize, seed=seed,
                                cache=cache, save_as=outname, parallel=parallel)
    
    
    
@click.command(name='toy_limit')
@click.option('-i', '--input_file', 'filename', required=True, 
              help='Path to the input workspace file.')
@click.option('-d', '--data', 'data_name', default='combData', show_default=True,
              help='Name of the dataset used for computing observed limit.')
@click.option('-o', '--output_file', 'outname', 
              default="toy_study/toy_result_seed_{seed}_batch_{batch}.root",
              show_default=True,
              help='Name of the output file containing toy results.')
@click.option('--poi_max', type=float, default=None,
              help='Maximum range of POI.')
@click.option('--poi_min', type=float, default=None,
              help='Minimum range of POI.')
@click.option('--scan_max', type=float, default=None,
              help='Maximum scan value of POI.')
@click.option('--scan_min', type=float, default=None,
              help='Minimum scan value of POI.')
@click.option('--steps', type=int, default=10, show_default=True,
              help='Number of scan steps.')
@click.option('--mu_val', type=float, default=None,
              help='Value of POI for running a single point')
@click.option('-n', '--n_toys', type=int,
              help='Number of the toys to use.')
@click.option('-b', '--batchsize', type=int, default=50, show_default=True,
              help='Divide the task into batches each containing this number of toys. '
                   'Result from each batch is saved for caching and different batches '
                   'are run in parallel if needed')
@click.option('-s', '--seed', type=int, default=2021,  show_default=True,
              help='Random seed used for generating toy datasets.')
@click.option('-t', '--tolerance', type=float, default=1.,  show_default=True,
              help='Tolerance for minimization.')
@click.option('-p', '--poi', 'poi_name', default=None,
              help='Name of the parameter of interest (POI). If None, the first POI is used.')
@click.option('--minimizer_type', default="Minuit2", show_default=True,
              help='Minimizer type')
@click.option('--strategy', type=int, default=1, show_default=True,
              help='Default minimization strategy')
@click.option('--offset/--no-offset', default=True, show_default=True,
              help='Use NLL offset.')
@click.option('--print_level', type=int, default=-1, show_default=True,
              help='Minimizer print level')
@click.option('-v', '--verbosity', default='INFO', show_default=True,
              type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
              help='Verbosity level.')
@click.option('-f', '--fix', 'fix_param', default="", show_default=True,
              help='Parameters to fix')
@click.option('-r', '--profile', 'profile_param', default="", show_default=True,
              help='Parameters to profile')
@click.option('--snapshot', 'snapshot_name', default=None, help='Name of initial snapshot')
@click.option('--parallel', type=int, default=-1, show_default=True,
              help='\b\n Parallelize job across the N workers.'
                   '\b\n Case  0: Jobs are run sequentially (for debugging).'
                   '\b\n Case -1: Jobs are run across N_CPU workers.')
def toy_limit(**kwargs):
    """
    Generate toys and evaluate limits
    """
    from quickstats.components.toy_limit_calculator import evaluate_batched_toy_limits
    if not (((kwargs['scan_min'] is None) and (kwargs['scan_max'] is None) and (kwargs['mu_val'] is not None)) or \
           ((kwargs['scan_min'] is not None) and (kwargs['scan_max'] is not None) and (kwargs['mu_val'] is None))):
        raise ValueError("please provide either (scan_min, scan_max, steps) for running a scan or (mu_val)"
                         " for running a single point")        
    evaluate_batched_toy_limits(**kwargs)