from util.plot_util import Plot

# if __name__ == '__main__':
#     # Plotting utility or other side tasks can be run using this
#     # alternative main.py.
#     # To use the plotting utility, check out the methods defined in
#     # the package and import the class.
#     plotter = Plot()

if __name__ == '__main__':
    Plot().plotComputationTimeVsN()
    Plot().plotPercentErrorVsN()
    Plot().plotAggConvergence()