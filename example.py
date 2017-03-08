"""
Praktikum 11 (torsion) as an example by Beni Frölich
"""

from errprop import ErrorPropagation, error_symbols, \
                    set_significant_digits, dict_latex

from sympy import sqrt, symbols, pi


# The variables that you are gonna use
variables = l, g, Rs, R, alpha, b, d = symbols("l g R_s R \\alpha, b, d")

# The variables that have uncertainity need to be put into error_symbols()
err_variables = ml, mg, mRs, mR, malpha, mb, md = error_symbols(
    l, g, Rs, R, alpha, b, d)

# you can now use the variables and invent your formula
formula = (2 * l * g * Rs) / (pi * R**4) * (1 / (alpha))
formula2 = (12 * g * l**3) / (3 * b * d**3) * (1 / alpha)


# the values andd errors as numerical values
values1 = {l: 0.74, g: 9.81, Rs: 0.07, R: 0.002495, alpha: 20.00 * pi / 180}
values2 = {l: 0.75, g: 9.81, Rs: 0.07, R: 0.002480, alpha: 14.08 * pi / 180}
values3 = {l: 0.75, g: 9.81, Rs: 0.07, R: 0.002500, alpha: 6.46 * pi / 180}

# for e modul
values4 = {l: 0.35, g: 9.81, b: 0.00598, d: 0.00797, alpha: 3.34 * 10**(-3)}
values5 = {l: 0.35, g: 9.81, b: 0.006, d: 0.008, alpha: 9.00686 * 10**(-3)}
values6 = {l: 0.35, g: 9.81, b: 0.006, d: 0.008, alpha: 6.44286 * 10**(-3)}


errors = {ml: 0.01, mg: 0.0, mRs: 0.001, mR: 0.00005,
          malpha: 0.0, mb: 0.00001, md: 0.00001}

print("Errors ")
print(dict_latex(errors))
print()

# set the sig digits for printing latex
set_significant_digits(3)

print("Schubmodul Alluminium")
ep = ErrorPropagation(formula, l, g, Rs, R, alpha)
ep.print_all(errors, values1, symbol="G_{Al}", n_split=4)

print("Schubmodul Messing")
ep = ErrorPropagation(formula, l, g, Rs, R, alpha)
ep.print_all(errors, values2, symbol="G_{Ms}", n_split=4)

print("Schubmodul Eisen")
ep = ErrorPropagation(formula, l, g, Rs, R, alpha)
ep.print_all(errors, values3, symbol="G_{Fe}", n_split=4)

print("Elastizitätsmodul Stahl (Stab 3)")
ep = ErrorPropagation(formula2, l, g, alpha, b, d)
ep.print_all(errors, values4, symbol="E_{steel}", n_split=4)

print("Elastizitätsmodul Al (Stab 6)")
ep = ErrorPropagation(formula2, l, g, alpha, b, d)
ep.print_all(errors, values5, symbol="E_{aluminium}", n_split=4)

print("Elastizitätsmodul Messing (Stab 7)")
ep = ErrorPropagation(formula2, l, g, alpha, b, d)
ep.print_all(errors, values6, symbol="E_{brass}", n_split=4)
