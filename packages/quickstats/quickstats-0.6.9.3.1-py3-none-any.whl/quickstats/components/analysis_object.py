from typing import Optional, Union, List

from quickstats import AbstractObject
from quickstats.components import ExtendedModel, ExtendedMinimizer
from quickstats.components.basics import WSArgument
from quickstats.utils.common_utils import get_class_that_defined_method
from quickstats.interface.root import RooArgSet
import ROOT

class AnalysisObject(AbstractObject):
    
    kInitialSnapshotName = "initialSnapshot"
    kCurrentSnapshotName = "currentSnapshot"
    kTempSnapshotName    = "tmpSnapshot"
    
    def __init__(self, filename:Optional[str]=None, poi_name:Optional[Union[str, List[str]]]=None,
                 data_name:str='combData', binned_likelihood:bool=True,
                 fix_param:str='', profile_param:str='', ws_name:Optional[str]=None, 
                 mc_name:Optional[str]=None, snapshot_name:Optional[Union[List[str], str]]=None,
                 minimizer_type:str='Minuit2', minimizer_algo:str='Migrad', precision:float=0.001, 
                 eps:float=1.0, retry:int=1, strategy:int=1, print_level:int=-1, timer:bool=False,
                 num_cpu:int=1, offset:bool=True, optimize:int=2, eigen:bool=False, hesse:bool=False,
                 improve:int=0, fix_cache:bool=True, fix_multi:bool=True, max_calls:int=-1, 
                 max_iters:int=-1, constrain_nuis:bool=True, batch_mode:bool=False,
                 int_bin_precision:float=-1., preset_param:bool=False, minimizer_offset:int=1,
                 minimizer_cls=None, verbosity:Optional[Union[int, str]]="INFO"):
        super().__init__(verbosity=verbosity)
        self.model = None
        self.minimizer = None
        self._use_blind_range = False
        if minimizer_cls is None:
            self.minimizer_cls = ExtendedMinimizer
        else:
            self.minimizer_cls = minimizer_cls
        if filename is not None:
            model_options = {
                "filename"          : filename,
                "ws_name"           : ws_name,
                "mc_name"           : mc_name,
                "data_name"         : data_name,
                "snapshot_name"     : snapshot_name,
                "binned_likelihood" : binned_likelihood,
                "fix_cache"         : fix_cache,
                "fix_multi"         : fix_multi
            }
            self.setup_model(**model_options)
            self.model._load_floating_auxiliary_variables()
            self.save_snapshot(self.kInitialSnapshotName, WSArgument.MUTABLE)
            self.set_poi(poi_name)
            if preset_param:
                self.preset_parameters()
            self.setup_parameters(fix_param, profile_param, update_snapshot=True)
            minimizer_options = {
                "minimizer_type"    : minimizer_type,
                "minimizer_algo"    : minimizer_algo,
                "precision"         : precision,
                "eps"               : eps,
                "retry"             : retry,
                "strategy"          : strategy,
                "num_cpu"           : num_cpu,
                "offset"            : offset,
                "minimizer_offset"  : minimizer_offset,
                "optimize"          : optimize,
                "eigen"             : eigen,
                "hesse"             : hesse,
                "improve"           : improve,
                "max_calls"         : max_calls,
                "max_iters"         : max_iters,
                "print_level"       : print_level,
                "timer"             : timer,
                "constrain_nuis"    : constrain_nuis,
                "batch_mode"        : batch_mode,
                "int_bin_precision" : int_bin_precision,
                "verbosity"         : verbosity
            }
            self.setup_minimizer(**minimizer_options)
            self.sanity_check()
        
    def sanity_check(self):
        aux_vars = self.model.get_variables("auxiliary")
        floating_aux_vars = [v.GetName() for v in aux_vars if not v.isConstant()]
        if len(floating_aux_vars) > 0:
            self.stdout.warning("The following auxiliary variables (variables that are not "
                                "part of the POIs, observables, nuisance parameters and global "
                                f"observables) are floating: {','.join(floating_aux_vars)}. If this is "
                                "not intended, please make sure to fix them before fitting.", "red")            
    
    def preset_parameters(self, fix_pois:bool=True, fix_globs:bool=True, float_nuis:bool=False):
        if fix_pois:
            ROOT.RooStats.SetAllConstant(self.model.pois, True)
            self.stdout.info("Preset POIs as constant parameters.")
        if fix_globs:
            ROOT.RooStats.SetAllConstant(self.model.global_observables, True)
            self.stdout.info("Preset global observables as constant parameters.")
        if float_nuis:
            ROOT.RooStats.SetAllConstant(self.model.nuisance_parameters, False)
            self.stdout.info("INFO: Preset nuisance parameters as floating parameters.")
    
    @property
    def use_blind_range(self):
        return self._use_blind_range
    
    @property
    def minimizer_options(self):
        return self.minimizer.config
    
    @property
    def nll_commands(self):
        return self.minimizer.nll_commands
    
    @property
    def get_poi(self):
        return self.model.get_poi
    
    # black magic
    def _inherit_init(self, init_func, **kwargs):
        import inspect
        this_parameters = list(inspect.signature(AnalysisObject.__init__).parameters)
        if "self" in this_parameters:
            this_parameters.remove("self")
        that_parameters = list(inspect.signature(init_func).parameters)
        is_calling_this = set(this_parameters) == set(that_parameters)
        if is_calling_this:
            init_func(**kwargs)
        else:
            that_kwargs = {k:v for k,v in kwargs.items() if k in that_parameters}
            this_kwargs = {k:v for k,v in kwargs.items() if k not in that_parameters}
            init_func(config=this_kwargs, **that_kwargs)
        
    def set_poi(self, poi_name:Optional[Union[str, List[str]]]=None):
        pois = self.get_poi(poi_name)
        if isinstance(pois, ROOT.RooRealVar):
            poi_text = f'"{pois.GetName()}"'
            n_poi = 1
        elif isinstance(pois, ROOT.RooArgSet) and (len(pois) > 0):
            poi_text = ", ".join([f'"{poi.GetName()}"' for poi in pois])
            n_poi = len(pois)
        else:
            poi_text = None
            n_poi = 0
        if n_poi == 1:
            self.stdout.info(f'POI set to {poi_text}')
        elif n_poi > 1:
            self.stdout.info(f'POIs set to {poi_text}')
        self.poi = pois
        
    def setup_model(self, **kwargs):
        model = ExtendedModel(**kwargs, verbosity=self.stdout.verbosity)
        self.model = model
    
    def setup_parameters(self, fix_param:str='', profile_param:str='', update_snapshot:bool=True):
        if not self.model:
            raise RuntimeError('uninitialized analysis object')
        fixed_parameters = []
        profiled_parameters = []
        if fix_param:
            fixed_parameters = self.model.fix_parameters(fix_param)
        if profile_param:
            profiled_parameters = self.model.profile_parameters(profile_param)
        self._update_floating_auxiliary_variables(fixed_parameters, profiled_parameters)
        if update_snapshot:
            self.save_snapshot(self.kCurrentSnapshotName, WSArgument.MUTABLE)
        self._check_poi_setup(fixed_parameters, profiled_parameters)
    
    def _update_floating_auxiliary_variables(self, fixed_parameters:List, profiled_parameters:List):
        if self.model.floating_auxiliary_variables is None:
            self.model._load_floating_auxiliary_variables()
        fixed_parameters    = RooArgSet.from_list(fixed_parameters)
        profiled_parameters = RooArgSet.from_list(profiled_parameters)
        core_variables = self.get_variables(WSArgument.CORE)
        fixed_parameters.remove(core_variables)
        profiled_parameters.remove(core_variables)
        self.model._floating_auxiliary_variables.add(profiled_parameters)
        self.model._floating_auxiliary_variables.remove(fixed_parameters)
        
    def _check_poi_setup(self, fixed_parameters:List, profiled_parameters:List):
        # pois defined in workspace
        ws_pois  = self.model.pois
        # pois defined in this analysis
        ana_pois = ROOT.RooArgSet(self.poi)
        if ana_pois.size() == 0:
            return None
        aux_pois = ROOT.RooArgSet(ws_pois)
        aux_pois.remove(ana_pois)
        for profiled_param in profiled_parameters:
            if aux_pois.contains(profiled_param):
                param_name = profiled_param.GetName()
                self.stdout.warning(f"Attemping to profile the parameter \"{param_name}\" which is a "
                                    f"POI defined in the workspace but not a POI used in this study. This "
                                    f"parameter will still be fixed during likelihood fit / limit setting. "
                                    f"Please designate the parameter as a POI in this study if intended.", "red")
        for fixed_param in fixed_parameters:
            if ana_pois.contains(fixed_param):
                param_name = fixed_param.GetName()
                self.stdout.warning(f"Attemping to fix the parameter \"{param_name}\" which is a "
                                    f"POI used in this study. This parameter will still be floated during "
                                    f"unconditional likelihood fit / limit setting.", "red")
            
    def setup_minimizer(self, constrain_nuis:bool=True, **kwargs):
        
        minimizer = self.minimizer_cls("Minimizer", self.model.pdf, self.model.data,
                                       workspace=self.model.workspace,
                                       verbosity=self.stdout.verbosity)
        
        nll_options = {k:v for k,v in kwargs.items() if k in ExtendedMinimizer._DEFAULT_NLL_OPTION_}
        
        if constrain_nuis:
            nll_options['constrain'] = self.model.nuisance_parameters
            nll_options['global_observables'] = self.model.global_observables
            conditional_obs = self.model.model_config.GetConditionalObservables()
            if conditional_obs:
                nll_options['conditional_observables'] = conditional_obs
            #nll_commands.append(ROOT.RooFit.ExternalConstraints(ROOT.RooArgSet()))
        
        minimizer_options = {k:v for k,v in kwargs.items() if k in ExtendedMinimizer._DEFAULT_MINIMIZER_OPTION_}
        minimizer.configure_nll(**nll_options)
        minimizer.configure(**minimizer_options)
        self.minimizer = minimizer
        self.default_nll_options = nll_options
        self.default_minimizer_options = minimizer_options
    
    def set_data(self, data_name:str='combData'):
        data = self.model.workspace.data(data_name)
        if not data:
            raise RuntimeError(f'workspace does not contain the dataset "{data_name}"')
        self.minimizer.set_data(data)
        self.model._data = data
        
    def set_blind_range(self, blind_range:List[float], categories:Optional[List[str]]=None):
        self.model.create_blind_range(blind_range, categories)
        sideband_range_name = self.model.get_sideband_range_name()
        self.minimizer.configure_nll(range=sideband_range_name, split_range=True, update=True)
        self._use_blind_range = True
        
    def unset_blind_range(self):
        self.minimizer.nll = None
        self.minimizer.nll_commands.pop("RangeWithName", None)
        self.minimizer.nll_commands.pop("SplitRange", None)
        self.stdout.info("Blind range removed from list of  NLL commands. NLL is reset.")
        self._use_blind_range = False
                
    def restore_prefit_snapshot(self):
        self.load_snapshot(self.kCurrentSnapshotName)
        
    def restore_init_snapshot(self):
        self.load_snapshot(self.kInitialSnapshotName)
        self.save_snapshot(self.kCurrentSnapshotName)
    
    def get_variables(self, variable_type:Union[str, WSArgument], sort:bool=True):
        return self.model.get_variables(variable_type, sort=sort)
    
    def save_snapshot(self, snapshot_name:Optional[str]=None, 
                      variables:Optional[Union[ROOT.RooArgSet, str, WSArgument]]=None):
        self.model.save_snapshot(snapshot_name, variables=variables)
        
    def load_snapshot(self, snapshot_name:Optional[str]=None):
        self.model.load_snapshot(snapshot_name)
        
    def save(self, filename:str, recreate:bool=True, rebuild:bool=True):
        self.model.save(filename, recreate=recreate, rebuild=rebuild)
        self.stdout.info(f'Saved workspace file as "{filename}"')
                
    def decompose_nll(self, fmt:str="pandas"):
        from quickstats.utils.roofit_utils import decompose_nll
        if not self.minimizer.nll:
            self.minimizer.create_nll()
            result = decompose_nll(self.minimizer.nll, self.model.global_observables, fmt=fmt)
            self.minimizer.nll = None
            return result
        return decompose_nll(self.minimizer.nll, self.model.global_observables, fmt=fmt)