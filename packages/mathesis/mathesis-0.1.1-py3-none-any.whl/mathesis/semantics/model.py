from mathesis.semantics import truth_table
from mathesis import forms


class State:
    def __init__(
        self, domain=set(), variables=set(), constants=dict(), predicates=dict()
    ):
        self.domain = domain
        self.constants = constants
        self.variables = variables
        predicates = dict(
            map(
                lambda x: (x[0], tuple((v,) for v in x[1]))
                if (len(x[1]) > 0 and type(list(x[1])[0]) is not tuple)
                else x,
                predicates.items(),
            )
        )
        self.predicates = predicates
        self.denotations = self.constants

    def assign_term_denotation(self, term):
        if term in self.variables:
            pass
        elif term in self.constants:
            return self.denotations.get(term, term)

    def valuate(self, fml, term_assignments=dict()):
        if isinstance(fml, forms.Atom):
            term_denotations = []
            for term in fml.terms:
                if term in self.variables:
                    if term in term_assignments:
                        denotation = term_assignments[term]
                    else:
                        values = []
                        for obj in self.domain:
                            value = self.valuate(
                                fml,
                                term_assignments=dict(term_assignments, **{term: obj}),
                            )
                            values.append(value)
                        if all(value == "1" for value in values):
                            return "1"
                        else:
                            return "0"
                elif term in self.constants:
                    denotation = self.constants.get[term]
                elif term in self.domain:
                    denotation = term
                else:
                    raise Exception
                term_denotations.append(denotation)
            term_denotations = tuple(term_denotations)
            extension = self.predicates.get(fml.predicate)
            # print(term_denotations, extension)
            if term_denotations in extension:
                return "1"
            else:
                return "0"
        elif isinstance(fml, forms.Universal):
            # print(fml.sub, fml.variable, fml.sub.free_terms)
            values = []
            for obj in self.domain:
                # print(fml.variable, obj)
                value = self.valuate(
                    fml.sub,
                    term_assignments=dict(term_assignments, **{fml.variable: obj}),
                )
                values.append(value)
            if all(value == "1" for value in values):
                return "1"
            else:
                return "0"
        elif isinstance(fml, forms.Particular):
            values = []
            for obj in self.domain:
                value = self.valuate(
                    fml.sub,
                    term_assignments=dict(term_assignments, **{fml.variable: obj}),
                )
                values.append(value)
            if any(value == "1" for value in values):
                return "1"
            else:
                return "0"
        elif isinstance(fml, forms.Negation):
            return truth_table.NegationClause().apply(
                self.valuate(fml.sub, term_assignments=term_assignments)
            )
        elif isinstance(fml, forms.Conjunction):
            return truth_table.ConjunctionClause().apply(
                *tuple(
                    self.valuate(child, term_assignments=term_assignments)
                    for child in fml.subs
                )
            )
        elif isinstance(fml, forms.Disjunction):
            return truth_table.DisjunctionClause().apply(
                *tuple(
                    self.valuate(child, term_assignments=term_assignments)
                    for child in fml.subs
                )
            )
        elif isinstance(fml, forms.Conditional):
            return truth_table.ConditionalClause().apply(
                *tuple(
                    self.valuate(child, term_assignments=term_assignments)
                    for child in fml.subs
                )
            )

    def validates(self, premises=[], conclusions=[]):
        premise_values = []
        conclusion_values = []

        for fml in premises:
            value = self.valuate(fml)
            premise_values.append(value)

        for fml in conclusions:
            value = self.valuate(fml)
            conclusion_values.append(value)

        if any(value == "1" for value in premise_values):
            return True
        elif all(value == "1" for value in conclusion_values):
            return True
        else:
            return False


World = State
Model = State


class KripkeModel:
    pass
