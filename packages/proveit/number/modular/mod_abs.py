from proveit import Literal, Operation
from proveit.number.sets import Reals

class ModAbs(Operation):
    # operator of the ModAbs operation.
    _operator_ = Literal(stringFormat='ModAbs', context=__file__)
    
    def __init__(self, value, divisor):
        Operation.__init__(self, ModAbs._operator_, (value, divisor))
        self.value = value
        self.divisor = divisor
        
    def string(self, **kwargs):
        return '|'+self.value.string(fence=False)+'|_{mod ' + self.divisor.string(fence=False) + '}'

    def latex(self, **kwargs):
        print("self.divisor.string(fence=False) = {}".
            format(self.divisor.string(fence=False)))                           # for testing
        # return r'\left|'+self.value.string(fence=False)+r'\right|_{{\rm mod}~' + self.divisor.string(fence=False) + r'\right}'
        return r'\left|'+self.value.string(fence=False)+r'\right|_{\textup{mod}\thinspace ' + self.divisor.string(fence=False) + r'}'

    def _closureTheorem(self, numberSet):
        from . import theorems
        if numberSet == Reals:
            return theorems.modAbsRealClosure
