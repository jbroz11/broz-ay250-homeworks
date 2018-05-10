import sys
import pickle
import smtplib
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTreeWidgetItem,
    QComboBox, QFileDialog, QInputDialog)
from PyQt5.QtGui import QIcon
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from simplus_ui import Ui_MainWindow
from generate_tree import GenerateTree
from importlib import import_module
from config import model_dict
from functools import partial
from collections import namedtuple
from mplwidget import *
from numpy import genfromtxt
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class SimplusGUI(QMainWindow):
    def __init__(self):
        super(SimplusGUI, self).__init__()

        # This keeps track of the parameters for different models
        self.parameter_tree = GenerateTree()

        # Set up the user interface generated by Qt Designer
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Can't add in the matplotlib toolbars with QtDesigner,
        # adding by hand here
        self.navi_toolbar1 = NavigationToolbar(
            self.ui.graphicsViewInfoNumerical, self)
        self.ui.NumericalModelInfoLayout.addWidget(self.navi_toolbar1)
        self.navi_toolbar2 = NavigationToolbar(
            self.ui.graphicsViewInfoAnalytical, self)
        self.ui.AnalyticalModelInfoLayout.addWidget(self.navi_toolbar2)
        self.navi_toolbar3 = NavigationToolbar(
            self.ui.AnalyticalModelgraphicsView, self)
        self.ui.AnalyticalModelPlotLayout.addWidget(self.navi_toolbar3)
        self.navi_toolbar4 = NavigationToolbar(
            self.ui.NumericalModelgraphicsView, self)
        self.ui.NumericalModelPlotLayout.addWidget(self.navi_toolbar4)

        # Populate the comboBox's with available models from config
        self.populate_combo_boxes()

        # And populate the parameter dicts with the corresponding parameters
        self.populate_parameter_dict("Analytical")
        self.populate_parameter_dict("Numerical")

        # Connect up the comboboxes
        self.ui.comboBox_ModelAnalytical.activated.connect(
            partial(self.populate_parameter_dict, "Analytical"))
        self.ui.comboBox_ModelAnalytical.activated.connect(
            partial(self.update_model_info, "Analytical"))
        self.ui.comboBox_ModelNumerical.activated.connect(
            partial(self.populate_parameter_dict, "Numerical"))
        self.ui.comboBox_ModelNumerical.activated.connect(
            partial(self.update_model_info, "Numerical"))

        # Connect up the buttons
        self.ui.pushButton_RunNumerical.clicked.connect(
            self.onNumericalRunClicked)
        self.ui.pushButton_RunAnalytical.clicked.connect(
            self.onAnalyticalRunClicked)
        self.ui.showLegendNumerical.clicked.connect(
            partial(self.show_legend, "Numerical"))
        self.ui.showLegendAnalytical.clicked.connect(
            partial(self.show_legend, "Analytical"))
        self.ui.pushButtonEmail1.clicked.connect(
            self.email_notification)
        self.ui.pushButtonEmail2.clicked.connect(
            self.email_notification)

        # These are the matplotlib widgets for the information tabs
        self.mplwidgetinfoanalytic = self.ui.graphicsViewInfoAnalytical
        self.mplwidgetinfonumerical = self.ui.graphicsViewInfoNumerical
        self.update_model_info("Analytical")
        self.update_model_info("Numerical")

        # These are the main matplotlib plots
        self.numericalplot = self.ui.NumericalModelgraphicsView
        self.analyticalplot = self.ui.AnalyticalModelgraphicsView

        # This is where we store current simulation data, in case we want
        # to save it to file.
        self.numerical_data = [0, 0]
        self.analytical_data = [0, 0]

        # Flags determining whether plot legends are displayed or not
        self.show_numerical_legend = False
        self.show_analytical_legend = False

        # Connect the menu items
        self.ui.actionSaveNumerical_2.triggered.connect(
            partial(self.save_data, "Numerical"))
        self.ui.actionSaveAnalytical_2.triggered.connect(
            partial(self.save_data, "Analytical"))
        self.ui.actionCSVNumerical.triggered.connect(
            partial(self.load_csv, "Numerical"))
        self.ui.actionCSVAnalytical.triggered.connect(
            partial(self.load_csv, "Analytical"))
        self.ui.actionPklNumerical.triggered.connect(
            partial(self.load_pkl, "Numerical"))
        self.ui.actionPklAnalytical.triggered.connect(
            partial(self.load_pkl, "Analytical"))

        # Attributes pertaining to email notification
        self.email_toaddr = "none"

    def email_notification(self):
        text, ok = QInputDialog.getText(self, "Input Dialog",
        "Enter the email address where you'd like to receive the notification.\n"
        "If you'd like to turn notifications off, type in 'none'.\n"
        "Note, email recipient is currently set to: {}".format(self.email_toaddr))
        if ok:
            self.email_toaddr = text

    def load_pkl(self, tab):
        '''
        This loads and plots pickled data, assuming that it is in
        the correct format.
        '''
        name, _ = QFileDialog.getOpenFileName(self, "Open File")
        try:
            data = pickle.load(open(name, "rb"))["data"]
        except KeyError:
            # Wrong format
            return
        except FileNotFoundError:
            return
        if tab == "Numerical":
            self.numericalplot.update_figure(data)
        else:
            self.analyticalplot.update_figure(data)

    def load_csv(self, tab):
        '''
        Our data is saved in csv format. So it's convenient to be able
        to load in a csv file and overlay it with the simulation, which
        is what this method does.
        '''
        name, _ = QFileDialog.getOpenFileName(self, "Open File")
        try:
            data = genfromtxt(name, delimiter=",").transpose()
        except FileNotFoundError:
            return
        if tab == "Numerical":
            self.numericalplot.append_csv(data)
        else:
            self.analyticalplot.append_csv(data)

    def save_data(self, tab):
        '''Save simulation data.'''
        if tab == "Numerical":
            data = self.numerical_data
            model_name = str(self.ui.comboBox_ModelNumerical.currentText())
            params = self.current_settings("Numerical", model_name)
        else:
            data = self.analytical_data
            model_name = str(self.ui.comboBox_ModelAnalytical.currentText())
            params = self.current_settings("Analytical", model_name)
        d = {"params": params, "data": data}
        name, _ = QFileDialog.getSaveFileName(self, "Save File")
        pickle.dump(d, open(name + ".pkl", "wb"))

    def show_legend(self, tab):
        '''Toggle the simulation legends ON/OFF.'''
        if tab == "Numerical":
            if self.show_numerical_legend:
                self.show_numerical_legend = False
                self.numericalplot.update_figure(self.numerical_data,
                                                 Legend=False)
            else:
                self.show_numerical_legend = True
                self.numericalplot.update_figure(self.numerical_data,
                                                 Legend=True)
        else:
            if self.show_analytical_legend:
                self.show_analytical_legend = False
                self.analyticalplot.update_figure(self.analytical_data,
                                                  Legend=False)
            else:
                self.show_analytical_legend = True
                self.analyticalplot.update_figure(self.analytical_data,
                                                  Legend=True)

    def update_model_info(self, tab):
        '''Update model information.'''
        if tab == "Analytical":
            model_name = str(self.ui.comboBox_ModelAnalytical.currentText())
        elif tab == "Numerical":
            model_name = str(self.ui.comboBox_ModelNumerical.currentText())
        models = model_dict[tab]
        for module_name, class_name in models:
            name = getattr(import_module(module_name), class_name)().__str__()
            if name == model_name:
                tex = getattr(import_module(module_name),
                              class_name)().model_info()
                if tab == "Analytical":
                    self.mplwidgetinfoanalytic.update_figure(tex)
                else:
                    self.mplwidgetinfonumerical.update_figure(tex)
                break

    def populate_parameter_dict(self, tab):
        '''
        Populates the parameter dictionary based on the parameters
        available for the specific model selected in the appropriate comboBox.
        '''

        if tab == "Analytical":
            model_name = str(self.ui.comboBox_ModelAnalytical.currentText())
            widget = self.ui.treeWidget_Analytical
            p = self.parameter_tree.values["Analytical"][model_name]
        if tab == "Numerical":
            model_name = str(self.ui.comboBox_ModelNumerical.currentText())
            widget = self.ui.treeWidget_Numerical
            p = self.parameter_tree.values["Numerical"][model_name]

        # Connect treeWidget signals
        widget.doubleClicked.connect(partial(self.onDoubleClick, widget))
        widget.itemChanged.connect(partial(self.onItemChanged, widget))

        # Clear current contents from treeWidget
        widget.clear()

        # Iterate through model parameters
        for key in p.keys():
            # Allow a nested depth of 2 to have the option to
            # group related parameters together.
            if type(p[key]) is dict:
                top_level = QTreeWidgetItem([key])
                for item in p[key].items():

                    # If item value is bool, create a checkbox
                    child = QTreeWidgetItem((item[0], str(item[1])))
                    if type(item[1]) == bool:
                        child.setFlags(child.flags() | Qt.ItemIsTristate |
                                                       Qt.ItemIsUserCheckable) # noqa E127
                        child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                        if not item[1]:
                            child.setCheckState(0, Qt.Unchecked)
                        else:
                            child.setCheckState(0, Qt.Checked)
                        top_level.addChild(child)

                    # If item is a list, create combobox
                    elif type(item[1]) == list:
                        cmb = QComboBox()
                        for i in item[1][-1]:
                            cmb.addItem(i, i)
                        child = QTreeWidgetItem(top_level)
                        child.setData(0, Qt.EditRole, item[0])
                        cmb.currentIndexChanged.connect(
                            lambda index, cmb=cmb, child=child:
                                self.onComboBoxChanged(cmb.currentText(), child))
                        widget.setItemWidget(child, 1, cmb)

                    elif type(item[1]) == type:
                        child = QTreeWidgetItem((item[0], str(item[1].value),
                                                 str(item[1].units)))
                        child.setFlags(child.flags() | Qt.ItemIsEditable)
                        top_level.addChild(child)
                    else:
                        # Set item as editable
                        child = QTreeWidgetItem((item[0], str(item[1])))
                        child.setFlags(child.flags() | Qt.ItemIsEditable)
                        top_level.addChild(child)
                widget.addTopLevelItem(top_level)

            else:

                # If item value is bool, create a checkbox
                if type(p[key]) == bool:
                    child = QTreeWidgetItem([key, str(p[key])])
                    child.setFlags(child.flags() | Qt.ItemIsTristate |
                                                   Qt.ItemIsUserCheckable) # noqa E127
                    child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                    if not p[key]:
                        child.setCheckState(0, Qt.Unchecked)
                    else:
                        child.setCheckState(0, Qt.Checked)
                    widget.addTopLevelItem(child)

                # If item is a list, create combobox
                elif type(p[key]) == list:
                    child = QTreeWidgetItem([key, str(p[key])])
                    cmb = QComboBox()
                    for i in p[key][-1]:
                        cmb.addItem(i, i)
                    child = QTreeWidgetItem(widget.invisibleRootItem())
                    child.setData(0, Qt.EditRole, key)
                    cmb.currentIndexChanged.connect(
                        lambda index, cmb=cmb, child=child:
                            self.onComboBoxChanged(cmb.currentText(), child))
                    widget.setItemWidget(child, 1, cmb)

                elif type(p[key]) == type:
                    child = QTreeWidgetItem((key, str(p[key].value),
                                             str(p[key].units)))
                    child.setFlags(child.flags() | Qt.ItemIsEditable)
                    widget.addTopLevelItem(child)

                else:
                    # Set item as editable
                    child = QTreeWidgetItem([key, str(p[key])])
                    child.setFlags(child.flags() | Qt.ItemIsEditable)
                    widget.addTopLevelItem(child)

        # This is a hack to prevent current item from being NoneType, which
        # breaks the code elsewhere.
        if widget.currentItem() is None:
            widget.setCurrentItem(child)

    def onComboBoxChanged(self, selection, item):
        '''
        This handles comboBox selection changes for items in the treeWidget.
        It's just easier to handle it separately.
        '''
        key = item.text(0)
        tab, model_name = self.get_tab()

        if item.parent() is None and item.childCount() == 0:
            self.parameter_tree.values[tab][model_name][key][0] = selection
        else:
            top_level = item.parent().text(0)
            self.parameter_tree.values[tab][model_name][top_level][key][0] = selection


    def populate_combo_boxes(self):
        '''
        Populate the model selection comboBoxes from the models
        specified in the config.
        '''

        analytical = self.ui.comboBox_ModelAnalytical
        numerical = self.ui.comboBox_ModelNumerical
        button_dict = {"Analytical": analytical,
                       "Numerical": numerical}

        for key in model_dict.keys():
            for module_name, class_name in model_dict[key]:
                name = getattr(import_module(module_name),
                               class_name)().__str__()
                button_dict[key].addItem(name)

    def onDoubleClick(self, widget, index):
        '''
        Handles double clike events for the treeWidgets.
        Really, I'm just adjusting the items that are editable here.
        Should really do this during instantiation.
        '''
        item = widget.currentItem()
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        # We only wnat the second column to be editable
        if index.column() != 1 or item.childCount() != 0:
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)

    def onItemChanged(self, widget, item):
        '''
        Handles item changed events for treeWidgets.
        '''

        tab, model_name = self.get_tab()

        # Check if the item is a checkbox and, it it is,
        # record its state.
        checked = None
        if item.flags() & Qt.ItemIsTristate:
            if item.checkState(0) == Qt.Checked:
                checked = True
            else:
                checked = False

        # Check if item has a parent
        if item.parent() is None and item.childCount() == 0:
            has_parent = False
        else:
            has_parent = True
            try:
                top_level = item.parent().text(0)
            except AttributeError:
                # This exception gets thrown if we are accessing a
                # top level item.
                return

        key = item.text(0)

        try:
            if has_parent:
                self.parameter_tree.values[tab][model_name][top_level][key]
                pitem = self.parameter_tree.values[tab][model_name][top_level]
            else:
                self.parameter_tree.values[tab][model_name][key]
                pitem = self.parameter_tree.values[tab][model_name]
        except KeyError:
            # The current tab and current item don't match while initially
            # populating the treewidget.
            return

        if type(pitem[key]) in [float, int]:
            try:
                # Editable params are only allowed to be numbers
                val = float(item.text(1))
                pitem[key] = val
            except ValueError:
                item.setText(1, str(pitem[key].value))

        elif type(pitem[key]) == type:
            try:
                # We only allow editable params to be numbers
                val = float(item.text(1))
                mini, maxi = pitem[key].range
                if val >= mini and val <= maxi:
                    pitem[key].value = val
                else:
                    item.setText(1, str(pitem[key].value))
            except ValueError:
                    item.setText(1, str(pitem[key].value))

        elif type(pitem[key]) == bool:
            if checked:
                pitem[key] = True
                item.setText(1, "True")
            else:
                pitem[key] = False
                item.setText(1, "False")

    def get_tab(self):
        tab = self.ui.tabWidget_Main.tabText(
            self.ui.tabWidget_Main.currentIndex())
        if tab == "Analytical":
            model_name = str(self.ui.comboBox_ModelAnalytical.currentText())
        if tab == "Numerical":
            model_name = str(self.ui.comboBox_ModelNumerical.currentText())

        return tab, model_name

    def onNumericalRunClicked(self):
        _, model_name = self.get_tab()
        models = model_dict["Numerical"]
        solver = str(self.ui.comboBox_EquationSolverType.currentText())
        for module_name, class_name in models:
            name = getattr(import_module(module_name), class_name)().__str__()
            if name == model_name:
                p = self.current_settings("Numerical", model_name)
                if solver == "Master Equation Solver":
                    data = getattr(import_module(module_name),
                                   class_name)().run_master_equation(**p)
                else:
                    data = getattr(import_module(module_name),
                                   class_name)().run_monte_carlo(**p)

        # Send an email when simulation is complete
        if not self.email_toaddr == "none":
            try:
                fromaddr = "simulation.notification1@gmail.com"
                toaddr = self.email_toaddr
                msg = MIMEMultipart()
                msg['From'] = fromaddr
                msg['To'] = toaddr
                msg['Subject'] = "Simulation Complete"

                body = "Your numerical {} simulation is complete.".format(module_name)
                msg.attach(MIMEText(body, 'plain'))

                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(fromaddr, "simulation")
                text = msg.as_string()
                server.sendmail(fromaddr, toaddr, text)
                server.quit()
            except smtplib.SMTPRecipientsRefused:
                # Invalid email address
                pass

        self.numericalplot.update_figure(data)
        self.numerical_data = data

    def onAnalyticalRunClicked(self):
        _, model_name = self.get_tab()
        models = model_dict["Analytical"]
        for module_name, class_name in models:
            name = getattr(import_module(module_name), class_name)().__str__()
            if name == model_name:
                p = self.current_settings("Analytical", model_name)
                print(p)
                data = getattr(import_module(module_name),
                               class_name)().run(**p)

        # Send an email when simulation is complete
        if not self.email_toaddr == "none":
            try:
                fromaddr = "simulation.notification1@gmail.com"
                toaddr = self.email_toaddr
                msg = MIMEMultipart()
                msg['From'] = fromaddr
                msg['To'] = toaddr
                msg['Subject'] = "Simulation Complete"

                body = "Your analytical {} simulation is complete.".format(module_name)
                msg.attach(MIMEText(body, 'plain'))

                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(fromaddr, "simulation")
                text = msg.as_string()
                server.sendmail(fromaddr, toaddr, text)
                server.quit()
            except smtplib.SMTPRecipientsRefused:
                # Invalid email address
                pass

        self.analyticalplot.update_figure(data)
        self.analytical_data = data

    def current_settings(self, tab, model):
        '''Returns a dict of currently selected parameters.'''
        p = self.parameter_tree.values[tab][model]
        p_current = {}
        for key, val in p.items():
            if type(val) == type:
                p_current[key] = val.value
            elif type(val) in [list, tuple]:
                p_current[key] = val[0]
            elif type(val) == dict:
                for key1, val1 in val.items():
                    if type(val1) == type:
                        p_current[key1] = val1.value
                    elif type(val1) in [list, tuple]:
                        p_current[key1] = val1[0]
                    else:
                        p_current[key1] = val1
            else:
                p_current[key] = val

        return p_current

def main():
    '''Run the GUI'''

    app = QApplication(sys.argv)  # instantiate with this program as argument
    gui = SimplusGUI()
    gui.show()  # This actually starts the GUI
    sys.exit(app.exec_())  # Exit the program when you exit the GUI


if __name__ == "__main__":
    main()
