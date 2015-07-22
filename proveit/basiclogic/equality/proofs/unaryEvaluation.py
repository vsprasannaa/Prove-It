from proveit.basiclogic import Implies, Equals
from proveit.basiclogic.variables import a, c, f, x
from proveit.basiclogic.simpleExpr import fx, fa

# hypothesis = (x=a)
hypothesis = Equals(x, a)
# [f(x) = f(a)] assuming x=a
fx_eq_fa = hypothesis.substitution(x, fx).prove({hypothesis})
# [f(a)=c] => [f(x)=c] assuming x=a
conclusion = fx_eq_fa.transitivityImpl(Equals(fa, c)).prove({hypothesis})
# forall_{f, x, a, c} (x=a) => {[f(a)=c] => [f(x)=c]}
Implies(hypothesis, conclusion).generalize((f, x, a, c)).qed(__file__)
