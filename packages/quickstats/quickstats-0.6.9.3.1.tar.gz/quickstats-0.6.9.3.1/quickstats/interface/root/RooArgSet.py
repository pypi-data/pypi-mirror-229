from typing import Dict, Union, List, Optional

import numpy as np

from quickstats import semistaticmethod
from quickstats.interface.cppyy.vectorize import as_np_array

class RooArgSet:
    
    @staticmethod
    def from_list(args:List["ROOT.RooAbsArg"]):
        import ROOT
        return ROOT.RooArgSet(*args)
    
    @staticmethod
    def sort(argset:"ROOT.RooArgSet"):
        argset.sort()
        return argset