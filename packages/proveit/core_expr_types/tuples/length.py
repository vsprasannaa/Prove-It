from proveit import (Expression, Lambda, Operation, Literal, safe_dummy_var,
                     single_or_composite_expression, ExprTuple,
                     ExprRange, InnerExpr, defaults, USE_DEFAULTS,
                     equality_prover)
from proveit import a, b, c, d, e, f, g, h, i, j, k, n, x, y


class Len(Operation):
    # operator of the Length operation.
    _operator_ = Literal(string_format='length', theory=__file__)

    def __init__(self, operand, *, styles=None):
        '''
        Len takes a single operand which should properly be an
        ExprTuple or an expression (such as a variable) that
        represents a tuple.
        '''
        operand = single_or_composite_expression(operand)
        if isinstance(operand, ExprTuple):
            # Nest an ExprTuple operand in an extra ExprTuple as
            # a clear indication that Len has a single operand
            # that is an ExprTuple rather than multiple operands.
            operand = ExprTuple(operand)
        # In order to always recognize that Len only takes a single
        # operand, we must wrap it as an ExprTuple with one entry.
        Operation.__init__(self, Len._operator_, operand, styles=styles)

    @staticmethod
    def extract_init_arg_value(
            arg_name,
            operator_or_operators,
            operand_or_operands):
        if arg_name == 'operand':
            if isinstance(operand_or_operands, ExprTuple):
                return operand_or_operands[0]
            else:
                return operand_or_operands

    def string(self, **kwargs):
        return '|' + self.operand.string() + '|'

    def latex(self, **kwargs):
        return '|' + self.operand.latex() + '|'

    @equality_prover('computed', 'compute')
    def computation(self, **defaults_config):
        '''
        Compute this Len expression, returning the equality
        between self and the expression for its computed value.
        Examples:
            |(a, b, c)| = 3
            |(x_1, ..., x_n, y)| = n+1
            |(f(i), ..., f(j), x_1, ..., x_n)| = (j-i+1) + (n-1+1)
            |x| = |x|
        In the last case, the 'x' represents an unknown tuple,
        so there is not anything we can do to compute it.
        '''
        # Currently not doing anything with must_evaluate
        # What it should do is make sure it evaluates to a number
        # and can circumvent any attempt that will not evaluate to
        # number.
        from proveit.numbers import one
        if not isinstance(self.operand, ExprTuple):
            # Don't know how to compute the length if the operand is
            # not a tuple. For example, it could be a variable that
            # represent a tuple.  So just return the self equality.
            from proveit.logic import Equals
            return Equals(self, self).prove()
        entries = self.operand.entries
        has_range = any(isinstance(entry, ExprRange) for entry in entries)
        if (len(entries) == 1 and has_range
                and not isinstance(entries[0].body, ExprRange)):
            # Compute the length of a single range.  Examples:
            # |(f(1), ..., f(n))| = n
            # |(f(i), ..., f(j))| = j-i+1
            range_entry = entries[0]
            start_index = range_entry.start_index
            end_index = range_entry.end_index
            lambda_map = range_entry.lambda_map
            if start_index == one:
                from proveit.core_expr_types.tuples import \
                    range_from1_len
                return range_from1_len.instantiate(
                    {f: lambda_map, i: end_index})
            else:
                from proveit.core_expr_types.tuples import range_len
                return range_len.instantiate(
                    {f: lambda_map, i: start_index, j: end_index})
        elif not has_range:
            # Case of all non-range entries.
            if len(entries) == 0:
                # zero length.
                from proveit.core_expr_types.tuples import tuple_len_0
                return tuple_len_0
            elif len(entries) < 10:
                # Automatically get the count and equality with
                # the length of the proper iteration starting from
                # 1.  For example,
                # |(a, b, c)| = 3
                # |(a, b, c)| = |(1, .., 3)|
                import proveit.numbers.numerals.decimals
                _n = len(entries)
                len_thm = proveit.numbers.numerals.decimals\
                    .__getattr__('tuple_len_%d' % _n)
                repl_map = dict()
                for param, entry in zip(len_thm.explicit_instance_params(),
                                        entries):
                    repl_map[param] = entry
                return len_thm.instantiate(repl_map)
            else:
                # raise NotImplementedError("Can't handle length computation "
                #                        ">= 10 for %s"%self)
                from proveit.core_expr_types.tuples import tuple_len_incr
                from proveit.numbers import num
                from proveit.logic import Equals

                eq = tuple_len_incr.instantiate({i: num(
                    len(entries) - 1), a: entries[:-1], b: entries[-1]})

                rhs_simp = eq.rhs._integerBinaryEval()

                return rhs_simp.sub_right_side_into(eq)
                # return Equals(eq.lhs, eq.rhs._integerBinaryEval(assumptions=assumptions).rhs).prove(assumptions=assumptions)
                # raise NotImplementedError("Can't handle length computation "
                #                         ">= 10 for %s"%self)
        elif (len(entries) == 2 and not isinstance(entries[1], ExprRange)
                and not isinstance(entries[0].body, ExprRange)):
            # Case of an extended range:
            # |(a_1, ..., a_n, b| = n+1
            from proveit.core_expr_types.tuples import \
                extended_range_len, extended_range_from1_len
            assert isinstance(entries[0], ExprRange)
            range_lambda = entries[0].lambda_map
            range_start = entries[0].start_index
            range_end = entries[0].end_index
            if range_start == one:
                return extended_range_from1_len.instantiate(
                    {f: range_lambda, b: entries[1], i: range_end})
            else:
                return extended_range_len.instantiate(
                    {f: range_lambda, b: entries[1],
                     i: range_start, j: range_end})
        else:
            # Handle the general cases via general_len_val,
            # len_of_ranges_with_repeated_indices,
            # len_of_ranges_with_repeated_indices_from_1,
            # or len_of_empty_range_of_range
            from proveit.core_expr_types.tuples import (
                general_len, len_of_ranges_with_repeated_indices,
                len_of_ranges_with_repeated_indices_from_1,
                len_of_empty_range_of_ranges)
            _x = safe_dummy_var(self)
            preserved_exprs = defaults.preserved_exprs

            def entry_map(entry):
                # Don't auto-simplify the entry.
                preserved_exprs.add(entry)
                if isinstance(entry, ExprRange):
                    if isinstance(entry.body, ExprRange):
                        # Return an ExprRange of lambda maps.
                        return ExprRange(entry.parameter,
                                         entry.body.lambda_map,
                                         entry.start_index,
                                         entry.end_index)
                    else:
                        return entry.lambda_map
                # For individual elements, just map to the
                # elemental entry.
                return Lambda(_x, entry)

            def entry_start(entry):
                if isinstance(entry, ExprRange):
                    if isinstance(entry.body, ExprRange):
                        # Return an ExprRange of lambda maps.
                        return ExprRange(entry.parameter,
                                         entry.body.start_index,
                                         entry.start_index,
                                         entry.end_index)
                    else:
                        return entry.start_index
                return one  # for individual elements, use start=end=1

            def entry_end(entry):
                if isinstance(entry, ExprRange):
                    if isinstance(entry.body, ExprRange):
                        # Return an ExprRange of lambda maps.
                        return ExprRange(entry.parameter,
                                         entry.body.end_index,
                                         entry.start_index,
                                         entry.end_index)
                    else:
                        return entry.end_index
                return one  # for individual elements, use start=end=1

            def empty_range(_i, _j, _f):
                # If the start and end are literal ints and form an
                # empty range, then it should be straightforward to
                # prove that the range is empty.
                from proveit.numbers import is_literal_int, Add
                from proveit.logic import Equals
                from proveit import m
                _m = entries[0].start_index
                _n = entries[0].end_index
                empty_req = Equals(Add(_n, one), _m)
                if is_literal_int(_m) and is_literal_int(_n):
                    if _n.as_int() + 1 == _m.as_int():
                        empty_req.prove()
                if empty_req.proven():
                    _f = Lambda(
                        (entries[0].parameter,
                         entries[0].body.parameter),
                        entries[0].body.body)
                    _i = entry_map(_i)
                    _j = entry_map(_j)
                    return len_of_empty_range_of_ranges.instantiate(
                        {m: _m, n: _n, f: _f, i: _i, j: _j})

            _f = [entry_map(entry) for entry in entries]
            _i = [entry_start(entry) for entry in entries]
            _j = [entry_end(entry) for entry in entries]
            _n = Len(_i).computed()

            from proveit.numbers import is_literal_int
            if len(entries) == 1 and isinstance(entries[0], ExprRange):
                if (is_literal_int(entries[0].start_index) and 
                        is_literal_int(entries[0].end_index)):
                    if (entries[0].end_index.as_int() + 1 
                            == entries[0].start_index.as_int()):
                        return empty_range(_i[0], _j[0], _f)

            if all(_ == _i[0] for _ in _i) and all(_ == _j[0] for _ in _j):
                if isinstance(_i[0], ExprRange):
                    if _i[0].is_parameter_independent:
                        # A parameter independent range means they
                        # are all the same.
                        _i = [_i[0].body]
                if isinstance(_j[0], ExprRange):
                    if _j[0].is_parameter_independent:
                        # A parameter independent range means they
                        # are all the same.
                        _j = [_j[0].body]
                if (not isinstance(_i[0], ExprRange) and
                        not isinstance(_j[0], ExprRange)):
                    # special cases where the indices are repeated
                    if _i[0] == one:
                        thm = len_of_ranges_with_repeated_indices_from_1
                        return thm.instantiate(
                            {n: _n, f: _f, i: _j[0]})
                    else:
                        thm = len_of_ranges_with_repeated_indices
                        return thm.instantiate(
                            {n: _n, f: _f, i: _i[0], j: _j[0]})

            return general_len.instantiate(
                {n: _n, f: _f, i: _i, j: _j}, 
                preserved_exprs=preserved_exprs,
                auto_simplify=True)

    @equality_prover('typical_form', 'typify')
    def typical_eq(self, **defaults_config):
        '''
        Attempt to prove that this Len expression is equal to
        something of the form |(i, ..., j)|.
        More generally, use "deduce_equality" (which calls this
        method when it can).
        Examples of handled cases:
            |(a, b, c)| = |(1, ..., 3)|
            |(x_i, ..., x_j)| = |i, ..., j|
        These are typically useful equalities for proving matching
        length requirements when instantiating a range of parameters.
        '''
        from proveit.numbers import one
        if not isinstance(self.operand, ExprTuple):
            raise ValueError("Len.typical_eq may only be performed "
                             "on a Len operating on an ExprTuple, not %s"
                             % self)

        entries = self.operand.entries
        if (len(entries) == 1 and isinstance(entries[0], ExprRange) and
                not isinstance(entries[0].body, ExprRange)):
            # Treat the special case something of the form
            # |(f(i), ..., f(j))}.  For example:
            # |(f(i), ..., f(j)| = (i, ..., j)
            range_entry = entries[0]
            start_index = range_entry.start_index
            end_index = range_entry.end_index
            lambda_map = range_entry.lambda_map
            if start_index == one:
                from proveit.core_expr_types.tuples import \
                    range_from1_len_typical_eq
                return range_from1_len_typical_eq.instantiate(
                    {f: lambda_map, i: end_index})
            else:
                from proveit.core_expr_types.tuples import \
                    range_len_typical_eq
                return range_len_typical_eq.instantiate(
                    {f: lambda_map, i: start_index, j: end_index})
        elif not any(isinstance(entry, ExprRange) for entry in entries):
            if len(entries) == 0:
                from proveit.core_expr_types.tuples import \
                    tuple_len_0_typical_eq
                return tuple_len_0_typical_eq
            elif len(entries) < 10:
                # Get a "typical equality" for the case when there
                # are no ExprRange's.  For example,
                # |(a, b, c)| = |(1, .., 3)|
                import proveit.numbers.numerals.decimals
                n = len(entries)
                eq_thm = proveit.numbers.numerals.decimals\
                                .__getattr__('tuple_len_%d_typical_eq' % n)
                repl_map = dict()
                for param, entry in zip(eq_thm.explicit_instance_params(),
                                        entries):
                    repl_map[param] = entry
                return eq_thm.instantiate(repl_map)
        elif (len(entries) == 2 and not isinstance(entries[1], ExprRange)
                and not isinstance(entries[0].body, ExprRange)):
            # Case of an extended range:
            # |(a_1, ..., a_n, b| = n+1
            from proveit.core_expr_types.tuples import \
                (extended_range_len_typical_eq,
                 extended_range_from1_len_typical_eq)
            assert isinstance(entries[0], ExprRange)
            range_lambda = entries[0].lambda_map
            range_start = entries[0].start_index
            range_end = entries[0].end_index
            if range_start == one:
                return extended_range_from1_len_typical_eq.instantiate(
                    {f: range_lambda, b: entries[1], i: range_end})
            else:
                return extended_range_len_typical_eq.instantiate(
                    {f: range_lambda, b: entries[1],
                     i: range_start, j: range_end})
        raise NotImplementedError("Len.typical_eq not implemented for "
                                  "this case: %s.  Try Len.deduce_equality "
                                  "instead." % self)

    @equality_prover('equated', 'equate')
    def deduce_equality(self, equality, **defaults_config):
        '''
        Prove the given equality with self on the left-hand side.
        
        '''
        from proveit.logic import Equals
        if not isinstance(equality, Equals):
            raise ValueError("The 'equality' should be an Equals expression")
        if equality.lhs != self:
            raise ValueError("The left side of 'equality' should be 'self'")
        with defaults.temporary() as temp_defaults:
            # Auto-simplify everything except the left and right sides
            # of the equality.
            temp_defaults.preserved_exprs={equality.lhs, equality.rhs}
            temp_defaults.auto_simplify=True

            # Try a special-case "typical equality".
            if isinstance(equality.rhs, Len):
                if (isinstance(equality.rhs.operand, ExprTuple)
                        and isinstance(self.operand, ExprTuple)):
                    if (equality.rhs.operand.num_entries() == 1 and
                            isinstance(equality.rhs.operand[0], ExprRange)):
                        try:
                            eq = self.typical_eq()
                            if eq.expr == equality:
                                return eq
                        except (NotImplementedError, ValueError):
                            pass
    
            # Next try to compute each side, simplify each side, and
            # prove they are equal.
            lhs_computation = equality.lhs.computation()
            if isinstance(equality.rhs, Len):
                # Compute both lengths and see if we can prove that they
                # are equal.
                rhs_computation = equality.rhs.computation()
                eq = Equals(lhs_computation.rhs, rhs_computation.rhs)
                if eq.lhs == eq.rhs:
                    # Trivial reflection -- automation is okay for that.
                    eq = eq.conclude_via_transitivity()
                else:
                    eq = eq.prove()
                return Equals.apply_transitivities(
                    [lhs_computation, eq, rhs_computation])
            else:
                # Compute the lhs length and see if we can prove that it is
                # equal to the rhs.
                eq = Equals(lhs_computation.rhs, equality.rhs)
                if eq.lhs == eq.rhs:
                    # Trivial reflection -- automation is okay for that.
                    eq = eq.conclude_via_reflection()
                else:
                    eq = eq.prove()
                return lhs_computation.apply_transitivity(eq)

    @equality_prover('evaluated', 'evaluate')
    def evaluation(self, **defaults_config):
        '''
        Returns a proven evaluations equation for this Len
        expression assuming.  Performs the "computation" of the
        Len expression and then evaluates the right side.
        '''
        computation = self.computation()
        return computation.inner_expr().rhs.evaluate()

    @equality_prover('simplified', 'simplify')
    def simplification(self, **defaults_config):
        '''
        Returns a proven simplification equation for this Len
        expression assuming.  Performs the "computation" of the
        Len expression and then simplifies the right side.
        '''
        computation = self.computation()
        return computation.inner_expr().rhs.simplify()

    def deduce_in_number_set(self, number_set, assumptions=USE_DEFAULTS):
        from proveit.core_expr_types.tuples import (
            range_len_is_nat, range_from1_len_is_nat)
        from proveit.numbers import Natural, one
        operand = self.operand
        if number_set == Natural:
            if (operand.num_entries() == 1
                    and isinstance(operand[0], ExprRange)):
                # Special case of proving that the length
                # of a single range is in the set of Natural numbers.
                range_start = operand[0].start_index
                range_end = operand[0].end_index
                range_lambda = operand[0].lambda_map
                if range_start == one:
                    return range_from1_len_is_nat.instantiate(
                        {f: range_lambda, i: range_end},
                        assumptions=assumptions)
                else:
                    return range_len_is_nat.instantiate(
                        {f: range_lambda, i: range_start, j: range_end},
                        assumptions=assumptions)

