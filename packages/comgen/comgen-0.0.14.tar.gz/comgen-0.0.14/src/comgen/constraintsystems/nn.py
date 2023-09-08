from comgen.constraintsystems import BaseSolver
from z3 import Int, Real, Bool, And, Or, Not, Implies, Sum, sat
import pymatgen.core as pg
# from comgen import PolyAtomicSpecies
from functools import partial
from comgen.util import composition_to_pettifor_dict
import fractions

