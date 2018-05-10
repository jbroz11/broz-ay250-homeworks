from __future__ import unicode_literals
from PyQt5 import QtCore, QtWidgets
from numpy import arange, sin, pi
import matplotlib as mpl
# Make sure that we are using QT5, this isn't currently necessary
# mpl.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# Enable use of amsmath latex package for model information tab
mpl.rcParams['text.usetex'] = True
mpl.rcParams['text.latex.preamble'] = [r'\usepackage{amsmath}']


class MyMplCanvas(FigureCanvas):
    '''Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.).'''

    def __init__(self, parent=None, width=5, height=4, dpi=100, tight_layout=True):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig = fig
        self.axes = fig.add_subplot(111)

        self.compute_initial_figure()

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass


class MplWidgetInfo(MyMplCanvas):
    '''Display information about the selected model.'''

    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)

    def compute_initial_figure(self):
        self.axes.axis("off")
        self.axes.annotate("", (0, 0.95))

    def update_figure(self, model_info):
        self.axes.clear()
        self.axes.axis("off")
        self.axes.annotate(model_info, (0, 1))
        # Making sure text fits in visible plot area
        self.fig.subplots_adjust(left=0.1, right=0.9,
                                 bottom=0.1, top=0.75,
                                 hspace=0.2, wspace=0.2)
        self.draw()


class MplWidgetAnalytic(MyMplCanvas):
    """Simple mplWidget implementation."""
    
    def compute_initial_figure(self):
        self.axes.plot([0], [0], linewidth=0)
        self.axes.tick_params(which="both", direction="in", bottom=True,
                              top=True, left=True, right=True)
        self.fig.subplots_adjust(left=0.05, right=0.98,
                                 bottom=0.05, top=0.95,
                                 hspace=0.2, wspace=0.2)
        self.axes.grid(True)

    def update_figure(self, data, Legend=False, append=False):
        if not append:
            self.axes.clear()
        t = data[0]
        for d in data[1:]:
            self.axes.plot(t, d[1], label=d[0])
        self.axes.tick_params(which="both", direction="in", bottom=True,
                              top=True, left=True, right=True)
        self.fig.subplots_adjust(left=0.05, right=0.98,
                                 bottom=0.05, top=0.95,
                                 hspace=0.2, wspace=0.2)
        self.axes.grid(True)
        if Legend:
            self.axes.legend(loc=1)
        self.draw()

    def append_csv(self, data):
        self.axes.plot(data[0], data[1], linewidth=0, marker="o")
        self.draw()


class MplWidgetNumerical(MyMplCanvas):
    """Simple mplWidget implementation."""

    def compute_initial_figure(self):
        self.axes.plot([0], [0], linewidth=0)
        self.axes.tick_params(which="both", direction="in", bottom=True,
                              top=True, left=True, right=True)
        self.fig.subplots_adjust(left=0.05, right=0.98,
                                 bottom=0.05, top=0.95,
                                 hspace=0.2, wspace=0.2)
        self.axes.grid(True)

    def update_figure(self, data, Legend=False, append=False):
        if not append:
            self.axes.clear()
        t = data[0]
        for d in data[1:]:
            self.axes.plot(t, d[1], label=d[0])
        self.axes.tick_params(which="both", direction="in", bottom=True,
                              top=True, left=True, right=True)
        self.fig.subplots_adjust(left=0.05, right=0.98,
                                 bottom=0.05, top=0.95,
                                 hspace=0.2, wspace=0.2)
        self.axes.grid(True)
        if Legend:
            self.axes.legend(loc=1)
        self.draw()

    def append_csv(self, data):
        self.axes.plot(data[0], data[1], linewidth=0, marker="o")
        self.draw()


