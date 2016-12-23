# -*- coding: utf-8 -*-
"""
Created on Mon Nov 21 22:11:42 2016

@author: Beni

----------------------
How to use this module
----------------------
See the bottom of the module for a little example. a bigger example is called example.py

Basic usage:
0. creat a new file and import at least:
	from error_helper import ErrorPropagation, error_symbols, symbols

1. define the varibales and assign sympy symbols to them
1.5 write a python expression and assign a variable. use sympy functions like sqrt, sin, cos, ....
2. use err_symbols from error_helper to define the uncertainty values
3. make to dicts of the form {variable:0.2}
	for all uncertainties and
	for all values
	
4. the class ErrorPropagation needs your formula as 1. arg and for the other args it needs the uncertain values
5. you can now use print_all for example to display latex math expressions and the numerical results.

(other usefull functions:
    set_significant_digits -- specify the sig digits for printing latex
    dict_latex -- takes a dict and returns a string to paste into latex (to document inputs)
    
    
Bugs:
    \\alpha instead of \alpha to symbols
    very long formulas are only split once (for latex page)

"""
from sympy import diff, symbols, Symbol, latex, sqrt, simplify, evalf
from sympy import srepr

precision = 4

aligns = """\\begin{{align*}}\n{}\n\\end{{align*}}"""
base_string1 = "{} = {} = {}"
base_string2 = "{} = {}"
    
def to_scientific_latex(number, sig_digits = 3):
    from math import log10, floor
    exponent = int(floor(log10(abs(number))))
    mantissa = float(number)/10**exponent
    return "{mant:.{prec}f}\\times 10^{{{exponent}}}".format(exponent = exponent, mant = mantissa, prec = sig_digits-1)

def error_symbols(*args):
    return (Symbol("m_{" + str(a) + "}") for a in args)

def dict_latex(values):
    """takes a dict and returns a string to paste into latex (to document inputs)"""
    strings = []
    for k, v in values.items():
        strings.append("{} = {}".format(k, v))

    lat = "\\\\\n".join(strings)
    return aligns.format(lat)
    
    
def percent_error(value, error):
    return round(100.0*error/value, 2)

def set_significant_digits(n):
    global precision
    precision = n



class ErrorPropagation():
    """A simple class to simplify live as an errorpropagator. It should be able to calculate it as a number
        and output relevant formulas in latex format"""
    
    def __init__(self, expression, *args):
        """expression: sympy expression.
            args: the variables from the expression that have uncertainty on them."""
        self.exp = expression  
        self.derivatives = {}  #partial derivatives of the inputs from args
        self.result = None     #the error propagation symbols
        self.errors = {}       #the error symbols (m_{k})

        self.n_errors = 0
        self.exp_numerical = "Not calculated yet"
        self.err_numerical = "Not calculated yet"

        for a in args:
            self.derivatives[a] = diff(self.exp, a)
            
        for a in args:
            self.errors[a] = Symbol( "m_{" + str(a) + "}" )
            
        self._evaluate()

            
    def _evaluate(self):
        result = 0
        for k, esymbol in self.errors.items():
            result += (esymbol*self.derivatives[k])**2
        
        self.result = sqrt(result)
            
    def calculate_exp_numerical(self, values={}):
        '''Numerically evaluate the expression.
            Values need to be the symbol:value used in the expression'''
        self.exp_numerical = self.exp.subs(values).evalf()
        return self.exp_numerical
            
    def calculate_error_numerical(self, errors={}, values={}):
        '''errors = {m_a:3.0, m_b:0.1} values = {a:20, b:10}'''
        r = self.result
        self.err_numerical = r.subs(values).subs(errors).evalf()
        return self.err_numerical

    def calculate(self, errors={}, values={}):
        self.calculate_exp_numerical(values)
        self.calculate_error_numerical(errors, values)
            
    def latex_input_expression(self):
        '''the Formula in Latex format'''
        return latex(self.exp)
        
    def latex_propagated(self):
        '''the error prop formula with errorsympols of the form m_k'''
        return latex(self.result)

    def _split_err_expr_root(self, split_at):
        """no trust in this function pls"""
        part1 = self.result.args[0].args[0:split_at]
        part2 = self.result.args[0].args[split_at:]
        return (sum(part1), sum(part2))

    def print_all(self, errors, values, symbol="values", align=True, n_split=0, filename=None):
        """prints everything (latex formula, result, latex error prop formula, the error)
			with print() in a nice format, ready to paste into a .tex file"""

        end = self.formula_to_latex(align = align, symbol = symbol, values = values)
        err_end = self.error_to_latex(align=align, symbol=symbol, errors=errors, values=values, n_split=n_split)

        err_symb_str = "m_{" + str(symbol) + "}"

        to_print= "\n".join([
                   "------------------------------------------------",
                   end,
                   "",
                   err_end,
                   "\n$${} = {}\\%$$".format(err_symb_str, percent_error(self.exp_numerical, self.err_numerical )),
                    "------------------------------------------------"])
        ## if a filename is give, we append it to the file instead
        if filename: 
            with open(filename, "a") as f:
                f.write(to_print)
        else: print(to_print)

        
    def formula_to_latex(self, align = False, symbol = "value", values = None):
        """returns the input formula as a latex of the form 'a = b'.
            If values are supplied, it is evaluated and
            returnd in the form 'a = b = Number' """

        if values:
            if not type(values) is dict:
                raise TypeError("Wrong type of values. Must be a dict -> example values = {a:1.5, c:3.0}")
            self.calculate_exp_numerical(values)

            latex_equation = base_string1.format(
                symbol,
                self.latex_input_expression(),
                to_scientific_latex(self.exp_numerical, precision) + " = " + str(self.exp_numerical))
        else:
            latex_equation = base_string2.format(
                symbol,
                self.latex_input_expression())

        result = latex_equation if not align else aligns.format(latex_equation)

        return result

        ##Todo: refactor
    def error_to_latex(self, align = False, symbol = "value", values = None, errors = None, n_split=4):
        """returns the error formula as a latex of the form 'a = b'.
            If values and errors are supplied, it is evaluated and
            returnd in the form 'Error of a = some latex = Error' """

        err_symbol_str = "m_{" + str(symbol) + "}"
        err_exp_latex = self.latex_propagated()

        ##check if the error expression is too long, so we split it
        if len(self.errors) > n_split and n_split > 0:
            a, b = self._split_err_expr_root(n_split)
            str_a = latex(sqrt(a))
            str_b = "\\overline{+" + latex(b) + "}"
            err_exp_latex = "{}\\\\\n{}".format(str_a, str_b)

        if values and errors:
            if not type(values) is dict:
                raise TypeError("Wrong type of the argument values. Must be a dict -> example values = {a:1.5, c:3.0}")
            if not type(errors) is dict:
                raise TypeError("Wrong type of rhe argument errors. Must be a dict -> example errors = {a:1.5, c:3.0}")
            
            self.calculate_error_numerical(errors, values)

            latex_equation = base_string1.format(
                err_symbol_str,
                err_exp_latex,
                to_scientific_latex(self.err_numerical, precision) + " = " + str(self.err_numerical))
        elif not values and not errors:
            latex_equation = base_string2.format(
                err_symbol_str,
                err_exp_latex)

        else:
            raise RuntimeError("You need both errors and values to be None or both a dict !!")

        result = latex_equation if not align else aligns.format(latex_equation)

        return result
    

if __name__ == "__main__":
    
    print("you run the module. THIS IS AN EXAMPLE:")
    
    #from errprop import ErrorPropagation, error_symbols, symbols    
    from sympy import sqrt, cos
    
    
    ## The variables that you are gonna use
    variables = a, b, gamma = symbols("a b \\gamma")
    that_have_uncertainty = (a, b, gamma)
    
    ## The variables that have uncertainity need to be put into error_symbols()
    err_variables = ma, mb, mgamma = error_symbols(*that_have_uncertainty)
    
    #you can now use the variables and invent your formula
    formula =  sqrt(a**2 + b**2 + gamma**2 + cos(gamma))
    
    
    #the values and errors as numerical values in a dict
    values = {a: 1.5, b:0.3, gamma:0.5*10**(-3)}
    errors = {ma: 0.2, mb:0.01, mgamma:0.1*10**(-4)}
    
    ##set the sig digits for printing latex
    set_significant_digits(3)
    
    ep = ErrorPropagation(formula, *that_have_uncertainty)
    ep.print_all(errors, values, symbol = "Q'_{\Gamma}")


