'''
inLiteral.py

Creates the IN literal which is used in prove-it's internal logic
(when a forall Operation has a 'domain').
We do not define the In Operation class here.  The standard one is
defined in basiclogic.set.setOps.  The formatMap and operationMaker
of IN should be set, as desired, where the In Operation is defined.
'''

from proveit.expression import Literal

IN = Literal(__package__, 'IN')
