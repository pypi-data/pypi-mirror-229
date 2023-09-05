##################################################################################################
# Based on https://gitlab.cern.ch/atlas-physics/stat/tools/StatisticsTools by Stefan Gadatsch
# Author: Alkaid Cheng
# Email: chi.lung.cheng@cern.ch
##################################################################################################
from typing import Union, Optional, List, Dict
import math

import numpy as np
import ROOT

import quickstats
from quickstats import AbstractObject

class ExtendedMinimizer(AbstractObject):
    _SCAN_EXCLUDE_CONFIG_ = ['scan', 'minos', 'save']
    _NLL_COMMANDS_ = ['NumCPU', 'Constrain', 'CloneData', 'GlobalObservables', 
                      'GlobalObservablesTag', 'OffsetLikelihood', 'Offset']

    _DEFAULT_MINIMIZER_OPTION_ = {
        'minimizer_type': 'Minuit2',
        'minimizer_algo': 'Migrad',        
        'optimize': 2,
        'verbose': 0,
        'save': 0,
        'timer': 0,
        'hesse': 0,
        'minos': 0,
        'scan': 0,
        'improve': 0,
        'num_ee': 5,
        'do_ee_wall': 1,
        'minimizer_offset': 1,
        'retry': 1,
        'eigen': 0,
        'reuse_minimizer': 0,
        'reuse_nll': 0,
        'eps': 1.0,
        'max_calls': -1,
        'max_iters': -1,
        'n_sigma': 1,
        'precision': 0.001,
        'strategy': 1,
        'print_level': -1
    }
    
    _DEFAULT_NLL_OPTION_ = {
        'num_cpu': 1,
        'offset': True,
        'batch_mode': False,
        'int_bin_precision': -1
    }
    
    @property
    def config(self):
        return self._config
    
    def __init__(self, minimizer_name:str, pdf:"ROOT.RooAbsPdf", data:"ROOT.RooAbsData",
                 minimizer_options:Optional[Dict]=None,
                 verbosity:Optional[Union[int, str]]="INFO",
                 **kwargs):
        super().__init__(verbosity=verbosity)
        """
            Minimizr Options:
                precision: precision for the find sigma algorithm
        """
        self.name = minimizer_name
        self.pdf = pdf
        self.data = data
        self.minimizer = None
        self.nll = None
        self.fit_result = None
        self.status = None
        
        self._config = self._DEFAULT_MINIMIZER_OPTION_ 
        if minimizer_options is not None:
            self._config.update(minimizer_options)
        self.minos_set = ROOT.RooArgSet()
        self.cond_set  = ROOT.RooArgSet()
        self.scan_set  = ROOT.RooArgSet()         
        
        self.Hessian_matrix = None
        self.min_nll = None
        
        self.eigen_values = ROOT.TVectorD()
        self.eigen_vectors = ROOT.TMatrixD()
        
        self.fit_options = {}
        self.scan_options = {}
        #self.nll_command_list = ROOT.RooLinkedList()
        self.nll_commands = {}
        
        self.configure_default_minimizer_options()
        
        self.stdout.info(f'Created ExtendedMinimizer("{self.name}") instance')
        
    @property
    def data(self):
        return self._data
    
    @data.setter
    def data(self, val):
        assert isinstance(val, ROOT.RooAbsData)
        self._data = val
        self.nll = None
    
    @property
    def pdf(self):
        return self._pdf

    @pdf.setter
    def pdf(self, val):
        assert isinstance(val, ROOT.RooAbsPdf)
        self._pdf = val 
            
    @staticmethod
    def _configure_default_minimizer_options(minimizer_type='Minuit2', minimizer_algo='Migrad',
                                             strategy=0, print_level=-1,
                                             debug_mode=False):
        ROOT.Math.MinimizerOptions.SetDefaultMinimizer(minimizer_type, minimizer_algo)
        ROOT.Math.MinimizerOptions.SetDefaultStrategy(strategy)
        ROOT.Math.MinimizerOptions.SetDefaultPrintLevel(print_level)
        if debug_mode:
            ROOT.Math.MinimizerOptions.SetDefaultPrintLevel(1)
        else:
            ROOT.Math.MinimizerOptions.SetDefaultPrintLevel(-1)
            ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.FATAL)
        if ROOT.Math.MinimizerOptions.DefaultPrintLevel() < 0:
            ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.FATAL)
        return None
            
    def configure_default_minimizer_options(self):
        self._configure_default_minimizer_options(self.config['minimizer_type'],
                                                  self.config['minimizer_algo'],
                                                  self.config['strategy'],
                                                  self.config['print_level'])
        return None
    
    def set_data(self, data:"ROOT.RooAbsData"):
        self.data = data
        
    def _bug_fix_create_nll(self, dataset:"ROOT.RooDataSet", nll_commands:List["ROOT.RooCmdArg"]):
        # fix range bug
        use_named_range = any([i.GetName() == "RangeWithName" for i in nll_commands])
        use_split_range = any([i.GetName() == "SplitRange" for i in nll_commands])
        if (use_named_range and use_split_range) and isinstance(self.pdf, ROOT.RooSimultaneous):
            named_range_cmd = [i for i in nll_commands if i.GetName() == "RangeWithName"][0]
            named_ranges = named_range_cmd.getString(0).split(",")
            index_cat = self.pdf.indexCat()
            n_cat = index_cat.size()
            for named_range in named_ranges:
                for i in range(n_cat):
                    index_cat.setIndex(i)
                    cat_label = index_cat.getLabel()
                    pdf_cat = self.pdf.getPdf(cat_label)
                    observable = pdf_cat.getObservables(dataset).first()
                    range_name = f"{named_range}_{cat_label}"
                    if observable.hasRange(range_name):
                        value_range = observable.getRange(range_name)
                        observable.setRange(named_range, value_range[0], value_range[1])
            index = [i for i, cmd in enumerate(nll_commands) if cmd.GetName() == "SplitRange"][0]
            nll_commands.pop(index)
            self.stdout.warning("Renamed observable ranges to fix a bug in ROOT")
    
    def _create_nll(self, nll_commands:List["ROOT.RooCmdArg"]=None, 
                    dataset:Optional["ROOT.RooDataSet"]=None):
        if nll_commands is None:
            nll_commands = list(self.nll_commands.values())
        #self.nll = self.pdf.createNLL(self.data, nll_command_list)
        for command in nll_commands:
            if command.GetName() == "RangeWithName":
                range_name = command.getString(0)
                self.stdout.info(f"Using the range \"{range_name}\" for NLL calculation")
        if dataset is None:
            dataset = self.data
        if quickstats.root_version >= (6, 26, 0):
            self._bug_fix_create_nll(dataset, nll_commands)
            nll_command_list = ROOT.RooLinkedList()
            for command in nll_commands:
                nll_command_list.Add(command)
            #nll = self.pdf.createNLL(dataset, *nll_commands)
            nll = self.pdf.createNLL(dataset, nll_command_list)
        else:
            if len(nll_commands) <= 6:
                nll = self.pdf.createNLL(dataset, *nll_commands)
            # bug: can't have more than 6 arguments
            elif len(nll_commands) == 7:
                reduced_command_list = [i for i in nll_commands if i.GetName() != 'NumCPU']
                self.stdout.warning("Maximum number (6) of NLL commands reached. "
                                    "Will remove `NumCPU` from the command list")
                if len(reduced_command_list) <= 6:
                    nll = self.pdf.createNLL(dataset, *reduced_command_list)
                else:
                    raise RuntimeError("due to a bug in ROOT, nll can not have more than 6 arguments")
            elif len(nll_commands) == 8:
                reduced_command_list = [i for i in nll_commands if i.GetName() not in ['NumCPU', 'IntegrateBins']]
                self.stdout.warning("Maximum number (6) of NLL commands reached. "
                                    "Will remove `NumCPU` and `IntegrateBins` from the command list")
                if len(reduced_command_list) <= 6:
                    nll = self.pdf.createNLL(dataset, *reduced_command_list)
                else:
                    raise RuntimeError("due to a bug in ROOT, nll can not have more than 6 arguments")
            else:
                raise RuntimeError("due to a bug in ROOT, nll can not have more than 6 arguments")
        if not nll.GetName():
            nll_name = f"nll_{self.pdf.GetName()}_{dataset.GetName()}"
            nll.SetName(nll_name)
        # fix memory leak
        ROOT.SetOwnership(nll, True)
        return nll
            
    def create_nll(self, nll_commands:List["ROOT.RooCmdArg"]=None, 
                   dataset:Optional["ROOT.RooDataSet"]=None):
        if (not self.nll) or (not self.config['reuse_nll']):
            self.nll = self._create_nll(nll_commands, dataset)
        
    def create_minimizer(self):
        
        if not self.nll:
            raise RuntimeError('NLL not initialized')

        if (self.minimizer is None) or (not self.config['reuse_minimizer']):
            self.configure_default_minimizer_options()
            self.minimizer = ROOT.RooMinimizer(self.nll)
            self.minimizer.setOffsetting(self.config['minimizer_offset'])
            self.minimizer.setPrintLevel(self.config['print_level'])
            self.minimizer.optimizeConst(self.config['optimize'])
            self.minimizer.setMinimizerType(self.config['minimizer_type'])
            self.minimizer.setEvalErrorWall(self.config['do_ee_wall'])
            self.minimizer.setPrintEvalErrors(self.config['num_ee'])
            self.minimizer.setVerbose(self.config['verbose'])
            self.minimizer.setProfile(self.config['timer'])
            self.minimizer.setStrategy(self.config['strategy'])
            self.minimizer.setEps(self.config['eps'])
            # https://root.cern/doc/master/VariableMetricBuilder_8cxx_source.html
            if self.config['max_calls'] != -1: 
                self.minimizer.setMaxFunctionCalls(self.config['max_calls'])
            else:
                max_calls = 5000 * self.pdf.getVariables().getSize()
                self.minimizer.setMaxFunctionCalls(max_calls)
                
            if self.config['max_iters'] != -1:
                self.minimizer.setMaxIterations(self.config['max_iters'])
    
    def construct_nll_commands(self, constrain=None, global_observables=None, 
                               conditional_observables=None, **kwargs):
        commands = []
        if 'num_cpu' in kwargs:
            commands.append(ROOT.RooFit.NumCPU(kwargs['num_cpu'], 3))
        if 'offset' in kwargs:
            commands.append(ROOT.RooFit.Offset(kwargs['offset']))
        if 'range' in kwargs:
            commands.append(ROOT.RooFit.Range(kwargs['range']))
        if ('split_range' in kwargs) and (kwargs['split_range']):
            commands.append(ROOT.RooFit.SplitRange())
        if ('batch_mode' in kwargs) and hasattr(ROOT.RooFit, "BatchMode"):
            commands.append(ROOT.RooFit.BatchMode(kwargs['batch_mode']))
        if ('int_bin_precision' in kwargs) and hasattr(ROOT.RooFit, "IntegrateBins"):
            commands.append(ROOT.RooFit.IntegrateBins(kwargs['int_bin_precision']))
        if constrain is not None:
            commands.append(ROOT.RooFit.Constrain(constrain))
            #self.stdout.warning("WARNING: Use of `Constrain` option from createNLL is not recommended", "red")
        if global_observables is not None:
            commands.append(ROOT.RooFit.GlobalObservables(global_observables))
        if conditional_observables is not None:
            commands.append(ROOT.RooFit.ConditionalObservables(conditional_observables))
        command_dict = {}
        for command in commands:
            command_dict[command.GetName()] = command
        # temporary fix for ROOT version below 6.22/06
        #nll_command_list = ROOT.RooLinkedList()
        #for command in commands:
        #    nll_command_list.Add(command)
        #return nll_command_list
        return command_dict
    
    def set_nll_commands(self, nll_commands:List["ROOT.RooCmdArg"]):
        command_dict = {}
        for command in nll_commands:
            command_dict[command.GetName()] = command
        self.nll_commands = command_dict
        
    def configure_nll(self, constrain=None, global_observables=None, conditional_observables=None, 
                      update:bool=False, **kwargs):
        command_dict = self.construct_nll_commands(constrain=constrain, 
                                                   global_observables=global_observables,
                                                   conditional_observables=conditional_observables,
                                                   **kwargs)
        if update:
            self.nll_commands.update(command_dict)
        else:
            self.nll_commands = command_dict
        if ('split_range' in kwargs) and (not kwargs['split_range']):
            self.nll_commands.pop("SplitRange", None)
        self.nll = None
    
    def configure(self, **kwargs):
        minos_set = kwargs.pop('minos_set', None)
        cond_set  = kwargs.pop('cond_set' , None)
        scan_set  = kwargs.pop('scan_set' , None)
        if minos_set is not None:
            self.minos_set = minos_set
        if cond_set is not None:
            self.cond_set = cond_set
        if scan_set is not None:
            self.scan_set = scan_set
        # parse nll commands 
        nll_commands = kwargs.pop('nll_commands', [])
        if nll_commands:
            self.nll_commands = {cmd.GetName():cmd for cmd in nll_commands}
        
        # configure minimizer settings
        for arg in kwargs:
            if arg not in self._config:
                raise ValueError('{} is not a valid minimizer config'.format(arg))
            self._config[arg] = kwargs[arg]
        
        self.fit_options = kwargs
        self.scan_options = {k:v for k,v in kwargs.items() if k not in self._SCAN_EXCLUDE_CONFIG_}

    def minimize(self, nll=None, **kwargs):

        self.configure(**kwargs)
        if nll is None:
            self.create_nll()
        else:
            self.nll = nll

        if self.cond_set.size() > 0:
            attached_set = self.nll.getVariables()
            for cond in self.cond_set:
                buffer = attached_set.find(cond.GetName())
                if buffer:
                    buffer.setVal(cond.getVal())
                    buffer.setConstant(1)
                    
        self.create_minimizer()
        status = 0
        attached_set = self.nll.getVariables()
        perform_minimization = any(not attached.isConstant() for attached in attached_set)

        if not perform_minimization:
            self.stdout.info('ExtendedMinimizer::minimize("{}") no floating parameters found'
                         '-- skipping minimization'.format(self.name))
        else:
            status = self.robust_minimize()

        # Evaluate errors with improve
        if self.config['improve']:
            self.minimizer.improve()
            
        # Evaluate errors with Hesse
        if self.config['hesse']:
            self.minimizer.hesse()
        
        # Obtain Hessian matrix either from patched Minuit or after inversion
        # TMatrixDSym G = Minuit2::MnHesse::lastHessian();
        last_fit = self.minimizer.lastMinuitFit()
        if last_fit:
            self.Hessian_matrix = last_fit.covarianceMatrix().Invert()
        else:
            self.Hessian_matrix = None
        
        # Eigenvalue and eigenvector analysis
        if self.config['eigen']:
            self.eigen_analysis()
        
        # Evaluate errors with Minos
        if self.config['minos']:
            if self.minos_set.size() > 0:
                self.minimizer.minos(self.minos_set)
            else:
                self.minimizer.minos()
        
        self.min_nll = self.nll.getVal()
        
        if self.config['scan']:
            self.find_sigma()

        if self.config['save']:
            data_name = self.data.GetName()
            save_name = "fitresult_{}_{}".format(self.name, data_name)
            save_title = "Result of fit of p.d.f. {} to dataset {}".format(self.name, data_name)
            self.stdout.info('ExtendedMinimizer::minimize("{}") saving results as {}'.format(self.name, save_name))
            self.fit_result = self.minimizer.save(save_name, save_title)
        # if the 'scan' option is used, minimizer will get deleted before this line
        elif self.minimizer is not None:
            self.fit_result = self.minimizer.save()

        if self.cond_set.size() > 0:
            attached_set = self.nll.getVariables()
            for cond in self.cond_set:
                buffer = attached_set.find(cond.GetName())
                if buffer:
                    buffer.setVal(cond.getVal())
                    buffer.setConstant(cond.isConstant())

        if not self.config['reuse_minimizer']:
            self.minimizer = None
            
        self.status = status
        return status
    
    def eigen_analysis(self):
        if not isinstance(self.Hessian_matrix, ROOT.TMatrixDSym):
            raise ValueError('invalid Hessian matrix')
        n = self.Hessian_matrix.GetNrows()
        
        # construct reduced Hessian matrix
        Gred = ROOT.TMatrixDSym(n)
        for i in range(n):
            for j in range(n):
                norm = math.sqrt(self.Hessian_matrix(i, i)*self.Hessian_matrix(j, j))
                Gred[i][j] = self.Hessian_matrix(i, j)/norm
        
        # perform eigenvalue analysis using ROOT standard tools
        Geigen = ROOT.TMatrixDSymEigen(Gred)
        
        self.eigen_values = Geigen.GetEigenValues()
        self.eigen_vectors = Geigen.GetEigenVectors()
        
        # simple printing of eigenvalues and eigenvectors
        self.eigen_values.Print()
        self.eigen_vectors.Print()
    
    def robust_minimize(self):

        strategy = self.config['strategy']
        retry    = self.config['retry']
        minimizer_type = self.config['minimizer_type']
        minimizer_algo = self.config['minimizer_algo']

        status = self.minimizer.minimize(minimizer_type, minimizer_algo)
        while ((status != 0) and (status!=1) and (retry>0)):
            if (strategy < 2):
                strategy += 1
            retry -= 1
            self.stdout.error(f'ExtendedMinimizer::robust_minimize("{self.name}") fit failed with status {status}. '
                              f'Retrying with strategy {strategy}')
            self.minimizer.setStrategy(strategy)
            status = self.minimizer.minimize(minimizer_type, minimizer_algo)
        
        if status not in [0, 1]:
            self.stdout.error(f'ExtendedMinimizer::robust_minimize("{self.name}") fit failed with status {status}')
        
        self.minimizer.setStrategy(self.config['strategy'])
        
        return status
    
    def use_limits(self, par:"ROOT.RooRealVar", val:float):
        if (val < par.getMin()):
            self.stdout.warning(f'ExtendedMinimizer::use_limits("{self.name}") {par.GetName()} = {val} '
                                f'limited by minimum at {par.getMin()}')
            return par.getMin()
        elif (val > par.getMax()):
            self.stdout.warning(f'ExtendedMinimizer::use_limits("{self.name}") {par.GetName()} = {val} '
                                f'limited by maximum at {par.getMax()}')
            return par.getMax()
        else:
            return val
    
    def find_sigma(self):
        if self.scan_set.getSize() == 0:
            attached_set = self.nll.getVariables()
            ROOT.RooStats.RemoveConstantParameters(attached_set)
            self.scan_set = attached_set

        for v in self.scan_set:
            variables = self.pdf.getVariables()
            ROOT.RooStats.RemoveConstantParameters(variables)
            variables.add(v, ROOT.kTRUE)
            snapshot = variables.snapshot()
            
            self.config['n_sigma'] = abs(self.config['n_sigma'])
            val = v.getVal()
            err = self.config['n_sigma'] * v.getError()
            
            min_nll = self.min_nll
            hi = self._find_sigma(min_nll, val+err, val, v, 
                                  self.scan_options, self.config['n_sigma'],
                                  self.config['precision'], self.config['eps'])
            variables.__assign__(snapshot)
            lo = self._find_sigma(min_nll, val-err, val, v, 
                                  self.scan_options, -self.config['n_sigma'],
                                  self.config['precision'], self.config['eps'])
            variables.__assign__(snapshot)
            self.min_nll = min_nll
            
            _lo = lo if not math.isnan(lo) else 1.0
            _hi = hi if not math.isnan(hi) else -1.0
            v.setAsymError(_lo, _hi)
            
            self.stdout.info(f'ExtendedMinimizer::minimize("{self.name}")')
            v.Print()

    # _____________________________________________________________________________
    # Find the value of sigma evaluated at a specified nsigma, assuming NLL -2logL is roughly parabolic in par.
    # The precision is specified as a fraction of the error, or based on the Minuit default tolerance.
    # Based on https://svnweb.cern.ch/trac/atlasoff/browser/PhysicsAnalysis/HiggsPhys/HSG3/WWDileptonAnalysisCode/HWWStatisticsCode/trunk/macros/findSigma.C
    # by Aaron Armbruster <aaron.james.armbruster@cern.ch> and adopted by Tim Adye <T.J.Adye@rl.ac.uk>.
    def _find_sigma(self, nll_min:float, val_guess:float, val_mle:float,
                    par:"ROOT.RooRealVar", scan_options:Dict, n_sigma:float,
                    precision:float, fit_tol:float):
        '''
        args:
            precision: fit precision
            fit_tol: fit tolerance
        '''
        max_iter = 25

        param_name = par.GetName()
        val_guess = self.use_limits(par, val_guess)
        direction = +1 if n_sigma >= 0.0 else -1
        n_damping = 1
        damping_factor = 1.0
        guess_to_corr = {}
        t_mu = ROOT.TMath.QuietNaN()
        front_str = f'ExtendedMinimizer::findSigma("{self.name}") '
        
        
        if precision <= 0.0:
            # RooFit default tolerance is 1.0
            tol = fit_tol if fit_tol > 0.0 else 1.0
            eps = 0.001 * tol
            precision = 5.0*eps / (n_sigma**2)
        
        temp_options = {**scan_options}
        snapshot = self.cond_set.snapshot()
        for i in range(max_iter):
            self.stdout.info(f'{front_str} Parameter {par.GetName()} {n_sigma}sigma '
                             f'iteration {i + 1}: start {val_guess} (MLE {val_guess - val_mle})', bare=True)
            val_pre = val_guess
            
            poi_set = ROOT.RooArgSet(par).snapshot()
            poi_set.first().setVal(val_guess)
            
            scan_options['reuse_nll'] = 1
            scan_options['scan']      = 0
    
            self.minimize(cond_set=poi_set, 
                          **scan_options)
            
            self.cond_set = snapshot
            scan_options.clear()
            scan_options.update(temp_options)
            
            nll = self.min_nll
            poi_set = None
            
            t_mu = 2.0 * (nll - nll_min)
            sigma_guess = abs(val_guess-val_mle)
            if (t_mu > 0.01):
                sigma_guess /= math.sqrt(t_mu)
            else:
                sigma_guess *= 10.0 # protect against t_mu <=0 and also don't move too far
            
            corr = damping_factor*(val_pre - val_mle - n_sigma*sigma_guess)
            
            for guess in guess_to_corr:
                if (abs(guess - val_pre) < direction*val_pre*0.02):
                    damping_factor *= 0.8
                    self.stdout.info(f'{front_str} Changing damping factor to {damping_factor}', bare=True)
                    n_damping += 1
                    if n_damping > 10:
                        n_damping = 1
                        damping_factor = 1.0
                    corr *= damping_factor
                    break
            
            # subtract off the difference in the new and damped correction
            val_guess -= corr
            guess_to_corr[val_pre] = corr          
            val_guess = self.use_limits(par, val_guess)
            rel_precision = precision*abs(val_guess-val_mle)
            delta = val_guess - val_pre
            
            
            self.stdout.info('{} {} {:.3f} (MLE {:.3f}) -> {:.3f} (MLE {:.3f}), '
                             'change {:.3f}, precision {:.3f}, -2lnL {:.4f}, sigma(guess) {:.3f})'.format(
                             front_str, param_name, val_pre, val_pre - val_mle, val_guess, val_guess - val_mle,
                             delta, rel_precision, t_mu, sigma_guess), bare=True)
            self.stdout.info('{} NLL:                 {}'.format(front_str, nll), bare=True)
            self.stdout.info('{} delta(NLL):          {}'.format(front_str, nll - nll_min), bare=True)
            self.stdout.info('{} nsigma*sigma(pre):   {}'.format(front_str, abs(val_pre - val_mle)), bare=True)
            self.stdout.info('{} sigma(guess):        {}'.format(front_str, sigma_guess), bare=True)
            self.stdout.info('{} par(guess):          {}'.format(front_str, val_guess + corr), bare=True)
            self.stdout.info('{} best-fit val:        {}'.format(front_str, val_mle), bare=True)
            self.stdout.info('{} tmu:                 {}'.format(front_str, t_mu), bare=True)
            self.stdout.info('{} Precision:           {}'.format(front_str, direction*val_guess*precision), bare=True)
            self.stdout.info('{} Correction:          {}'.format(front_str, -corr), bare=True)
            self.stdout.info('{} nsigma*sigma(guess): {}'.format(front_str, abs(val_guess-val_mle)), bare=True)
            
            if abs(delta) <= rel_precision:
                break
        if i >= max_iter:
            self.stdout.error(f'find_sigma failed after {i + 1} iterations')
            return ROOT.TMath.QuietNan()
        
        err = val_guess - val_mle
        self.stdout.info('{} {} {}sigma = {:.3F} at -2lnL = {:4f} after {} iterations'.format(
                         front_str, par.GetName(), n_sigma, err, t_mu, i+1), bare=True)
        
        return err
    
    def create_profile(self, var:"ROOT.RooRealVar", lo:float, hi:float, n_bins:int):
        map_poi2nll = {}
        
        ROOT.Math.MinimizerOptions.SetDefaultPrintLevel(-1)
        ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.FATAL)
        
        variables = self.pdf.getVariables()
        ROOT.RooStats.RemoveConstantParameters(variables)
        
        # unconditional fit
        buffer_scan_options = deepcopy(scan_options)
        
        buffer_scan_options['reuse_nll'] = 1
        
        self.minimize(**buffer_scan_options)
        
        map_poi2nll[var.getVal()] = 2 * self.min_nll
        snapshot = variables.snapshot()
        
        ## these lines should be improved
        buffer_scan_options.pop('reuse_nll')
        scan_options.clear()
        scan_options.update(buffer_scan_options)
        
        # perform the scan
        delta_x = (hi - lo)/n_bins
        for i in range(n_bins):
            variables.__assign__(snapshot)
            var.setVal(lo + i * delta_x)
            val.setConstant(1)
            
            buffer_scan_options['reuse_nll'] = 1
            
            self.minimize(**buffer_scan_options)
            map_poi2nll[var.getVal()] = 2 * self.min_nll
            
            ## these lines should be improved
            buffer_scan_options.pop('reuse_nll')
            scan_options.clear()
            scan_options.update(buffer_scan_options)
            
            var.setConstant(0)
        variables.__assign__(snapshot)
        graphs = self.prepare_profile(map_poi2nll)
        return graphs
    
    def prepare_profile(self, map_poi2nll:Dict):
        x, y = [], []
        n_bins = len(map_poi2nll) - 1
        
        xlo = float('inf') 
        xhi = float('-inf') 
        
        for nll_prev in map_poi2nll:
            nll = map_poi2nll[nll_prev]
            if (not math.isinf(nll)) and (abs(nll) < 10**20):
                x.append(nll_prev)
                y.append(nll)
        
        nr_points = len(x)
        
        if nr_points == 0:
            raise ValueError("map_poi2nll is empty")
            
        x, y = zip(*sorted(zip(x, y)))
        x = np.array(x, dtype=float)
        y = np.array(y, dtype=float)
            
        if (x[0] < xlo):
            xlo = x[0]
            
        if x[-1] > xhi:
            xhi = x[-1]
        
        g = ROOT.TGraph(nr_points, x, y)
        
        min_nll = ROOT.TMath.Infinity()
        min_nll_x = 0.0
        
        for i in range(g.GetN()):
            tmpX, tmpY = ROOT.Double(0), ROOT.Double(0)
            g.GetPoint(i, tmpX, tmpY)
            if (tmpY < min_nll):
                min_nll = tmpY
                min_nll_x = tmpX
                
        for i in range(g.GetN()):
            tmpX, tmpY = ROOT.Double(0), ROOT.Double(0)
            g.GetPoint(i, tmpX, tmpY)
            tmpY -= min_nll
            g.SetPoint(i, tmpX, tmpY)

        min_nll = ROOT.TMath.Infinity()
        min_nll_x = 0.0
        
        # Make smooth interpolated graph for every folder in poi range, find minimum nll
        x_interpolated_coarse, y_interpolated_coarse = [], []
        
        stepsize_coarse = abs(xhi - xlo) / n_bins
        tmpX = xlo
        while (tmpX <= xhi):
            tmpY = g.Eval(tmpX, 0)
            x_interpolated_coarse.append(tmpX)
            y_interpolated_coarse.append(tmpY)
            tempX += stepsize_coarse
            
        x_interpolated_coarse = np.array(x_interpolated_coarse, dtype=float)
        y_interpolated_coarse = np.array(y_interpolated_coarse, dtype=float)
        nr_points_interpolated_coarse = len(x_interpolated_coarse)
        g_interpolated_coarse = ROOT.TGraph(nr_points_interpolated_coarse,
                                            x_interpolated_coarse,
                                            y_interpolated_coarse)
        
        x_interpolated, y_interpolated = [], []
        two_step_interpolation = False
        stepsize = abs(xhi - xlo) / (10*n_bins)
        while (tmpX <= xhi):
            tmpY = 0.0
            if two_step_interpolation:
                tmpY = g_interpolated_coarse.Eval(tmpX, 0, "S")
            else:
                tmpY = g.Eval(tmpX, 0, "S")
            x_interpolated.append(tmpX)
            y_interpolated.append(tmpY)
            tempX += stepsize
            
        x_interpolated = np.array(x_interpolated, dtype=float)
        y_interpolated = np.array(y_interpolated, dtype=float)
        nr_points_interpolated = len(x_interpolated)
        g_interpolated = ROOT.TGraph(nr_points_interpolated,
                                     x_interpolated,
                                     y_interpolated)
        
        for i in range(g_interpolated.GetN()):
            tmpX, tmpY = ROOT.Double(0), ROOT.Double(0)
            g_interpolated.GetPoint(i, tmpX, tmpY)
            if (tmpY < min_nll):
                min_nll = tmpY
                min_nll_x = tmpX
        
        for i in range(g.GetN()):
            tmpX, tmpY = ROOT.Double(0), ROOT.Double(0)
            g.GetPoint(i, tmpX, tmpY)
            tmpY -= min_nll
            g.SetPoint(i, tmpX, tmpY)
        
        for i in range(g_interpolated.GetN()):
            tmpX, tmpY = ROOT.Double(0), ROOT.Double(0)
            g_interpolated.GetPoint(i, tmpX, tmpY)
            tmpY -= min_nll
            g_interpolated.SetPoint(i, tmpX, tmpY)
        
        g.SetLineWidth(2)
        g.SetMarkerStyle(20)
        
        g_interpolated.SetLineWidth(2)
        g_interpolated.SetMarkerStyle(20)
        
        return (g, g_interpolated)
