from proveit import Function, Literal, equality_prover
from proveit import x
from proveit.numbers import one
from proveit.relation import TransRelUpdater

class Bra(Function):
    '''
    Class to represent a Dirac bra vector of the form ⟨0| or ⟨1|.
    '''
    # the literal operator of the Bra operation
    _operator_ = Literal(string_format='BRA', theory=__file__)

    def __init__(self, label, *, styles=None):
        Function.__init__(self, Bra._operator_, label, styles=styles)
        self.label = self.operands[0]  # might need to change

    def string(self, **kwargs):
        return self.formatted('string', **kwargs)

    def latex(self, **kwargs):
        return self.formatted('latex', **kwargs)
    
    def formatted(self, format_type, **kwargs):
        if format_type == 'latex':
            return (r'\langle '
                    + self.label.formatted(format_type, fence=False)
                    + r' \rvert')
        else:  # using the unicode \u2329 for the left angle bracket
            return (u'\u2329'
                    + self.label.formatted(format_type, fence=False)
                    + '|')

    # could instead use string() or latex() method instead

class Ket(Function):
    '''
    Class to represent a Dirac ket vector of the form |0⟩ or |1⟩.
    '''
    # the literal operator of the Ket operation
    _operator_ = Literal(string_format='KET', theory=__file__)

    def __init__(self, label, *, styles=None):
        Function.__init__(self, Ket._operator_, label, styles=styles)
        self.label = self.operands[0]

    def string(self, **kwargs):
        return self.formatted('string', **kwargs)

    def latex(self, **kwargs):
        return self.formatted('latex', **kwargs)
    
    def formatted(self, format_type, no_lvert=False, **kwargs):
        left_str = r'\lvert ' if format_type == 'latex' else '|'
        if no_lvert:
            left_str = ''
        if format_type == 'latex':
            return (left_str +
                    self.label.formatted(format_type, fence=False) +
                    r' \rangle')
        else:  # using the unicode \u232A for the right angle bracket
            return (left_str
                    + self.label.formatted(format_type, fence=False)
                    + u'\u232A')
    
class NumBra(Function):
    '''
    Class to represent a Dirac bra vector in a computational-basis 
    state (i.e., a Classical state) as the binary representation of 
    its 'num' operand in the number of bits specified by the 'size'
    operand.
    '''
    # the literal operator of the NumBra operation
    _operator_ = Literal(string_format='NUM_BRA', theory=__file__)

    def __init__(self, num, size, *, styles=None):
        Function.__init__(self, NumBra._operator_, (num, size),
                          styles=styles)
        self.num = self.operands[0]   # value
        self.size = self.operands[1]   # size of the register

    def _config_latex_tool(self, lt):
        Function._config_latex_tool(self, lt)
        # Expression._config_latex_tool(self, lt)
        if 'mathtools' not in lt.packages:
            lt.packages.append('mathtools')

    def string(self, **kwargs):
        return self.formatted('string', **kwargs)

    def latex(self, **kwargs):
        return self.formatted('latex', **kwargs)
    
    def formatted(self, format_type, fence=False):
        formatted_label = self.num.formatted(format_type, fence=False)
        formatted_size = self.size.formatted(format_type, fence=False)
        if format_type == 'latex':
            # can't seem to get the \prescript latex to work, so using
            # a temporary work-around with an 'empty' subscript; much
            # googling hasn't uncovered explanation for why \prescript
            # isn't working in the ipynbs
            # return (r'\prescript{}{' + formatted_size + r'}\langle '
            #         + formatted_label + r' \rvert')
            return (r'{_{' + formatted_size + r'}}\langle '
                    + formatted_label + r' \rvert')
        else:
            return '{' + formatted_size + '}_' + \
                u'\u2329' + formatted_label + '|'


class NumKet(Function):
    '''
    Class to represent a Dirac ket vector in a computational-basis 
    state (i.e., a Classical state) as the binary representation of 
    its 'num' operand in the number of bits specified by the 'size'
    operand.
    '''
    # the literal operator of the RegisterKet operation
    _operator_ = Literal(string_format='NUM_KET', theory=__file__)

    def __init__(self, num, size, *, styles=None):
        Function.__init__(self, NumKet._operator_, (num, size),
                          styles=styles)
        self.num = self.operands[0]   # value for the ket
        self.size = self.operands[1]   # size of the register

    def string(self, **kwargs):
        return self.formatted('string', **kwargs)

    def latex(self, **kwargs):
        return self.formatted('latex', **kwargs)
    
    def formatted(self, format_type, fence=False, no_lvert=False):
        formatted_label = self.num.formatted(format_type, fence=False)
        formatted_size = self.size.formatted(format_type, fence=False)
        left_str = r'\lvert ' if format_type == 'latex' else '|'
        if no_lvert:
            left_str = ''
        if format_type == 'latex':
            return (left_str + formatted_label + r' \rangle_{'
                    + formatted_size + '}')
        else:
            return (left_str + formatted_label + u'\u232A' + '_{'
                    + formatted_size + '}')

    @equality_prover('shallow_simplified', 'shallow_simplify')
    def shallow_simplification(self, *, must_evaluate=False,
                               **defaults_config):
        '''
        Returns a proven simplification equation for this RegisterKet
        expression assuming the operands have been simplified.
        
        Currently deals only with:
        (1) simplifying a RegisterKet with register size = 1 to a
            simple Ket. It's not immediately clear that we always want
            to do such a thing, but here goes.
        '''

        if self.size == one:
            from . import single_qubit_register_ket
            return single_qubit_register_ket.instantiate(
                    {x: self.label}, preserve_all=True)

        # Else simply return self=self.
        # Establishing some minimal infrastructure
        # for future development
        expr = self
        # for convenience updating our equation:
        eq = TransRelUpdater(expr)
        # Future processing possible here.
        return eq.relation

    def deduce_in_vec_space(self, vec_space=None, *, field,
                            **defaults_config):
        pass # TODO
