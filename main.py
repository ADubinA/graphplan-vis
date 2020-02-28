import sys
import matplotlib
matplotlib.use('Qt5Agg')
import engine
from PyQt5 import QtCore, QtGui, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
DEBUG = False
import networkx as nx


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, fig=None):
        if not fig:
            fig = Figure(figsize=(4, 5), dpi=100)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)



class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.gp = engine.GraphPlanVis()

        self.fig_width = 5
        self.fig_height = 4
        self.mpl = MplCanvas(parent=self, fig=Figure())
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("GraphPlan Visualization by Almog Dubin")

        if DEBUG:
            # self.domain_file_path = "examples/gripper/domain.pddl"
            # self.problem_file_path = "examples/gripper/p01.pddl"
            self.domain_file_path = "examples/blocksworld/domain.pddl"
            self.problem_file_path = "examples/blocksworld/p01.pddl"
        else:
            self.domain_file_path = None
            self.problem_file_path = None

        self._construct_top_menu()
        self._construct_main_menu()
        cid = self.mpl.figure.canvas.mpl_connect('button_press_event', self._onclick)

        self.show()
        if DEBUG:
            self._try_start_graph_plan()
            self.action_expand_level()
            # self.gp.draw_no_op = False

        self.mutex_mode = False

    def _onclick(self, event):
        if not self.mutex_mode:
            return

        clicked = min(self.gp.pos.items(),
                      key=lambda x: pow(x[1][0]-event.xdata, 2) + pow(x[1][1]-event.ydata, 2))
        clicked = clicked[0]

        mutexes = self.gp.get_nx_node_mutexes(self.mpl.axes, clicked)

        self._after_mutex_press(clicked, mutexes)

    def _after_mutex_press(self, clicked, mutexes):
        self._refresh_graph_view()

        nx.draw_networkx_nodes(self.gp.nx_graph, self.gp.pos, [clicked],
                               node_shape="s", node_color="yellow", ax=self.mpl.axes)

        nx.draw_networkx_nodes(self.gp.nx_graph, self.gp.pos, mutexes,
                               node_shape="s", node_color="orange", ax=self.mpl.axes)
        self._refresh_figure()

    def _construct_main_menu(self, fig=None):

        self.mpl = MplCanvas(self, fig)

        # Create toolbar, passing canvas as first parament, parent (self, the MainWindow) as second.
        toolbar = NavigationToolbar(self.mpl, self)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.mpl)

        # Create a placeholder widget to hold our toolbar and canvas.
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def _construct_top_menu(self):
        # File menu
        self.file_menu = QtWidgets.QMenu('&File', self)
        self.file_menu.addAction('&Load Domain', lambda: self.file_load_pddl("domain"))
        self.file_menu.addAction('&Load problem', lambda: self.file_load_pddl("problem"))

        self.file_menu.addAction('&Quit', self.file_quit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        # Action menu
        self.menuBar().addSeparator()
        self.action_menu = QtWidgets.QMenu('&Action', self)
        self.action_menu.addAction('&Expand level', self.action_expand_level,
                                   QtCore.Qt.CTRL + QtCore.Qt.Key_E)
        self.action_menu.addAction('&Solve', self.action_solve,
                                   QtCore.Qt.CTRL + QtCore.Qt.Key_S)
        self.action_menu.addAction('&Expand and solve', self.action_expand_and_solve,
                                   QtCore.Qt.CTRL + QtCore.Qt.Key_X)
        self.action_menu.addAction('&Reset', self.action_reset_graph,
                                   QtCore.Qt.CTRL + QtCore.Qt.Key_R)
        self.action_menu.addAction('&Change stopping condition', self.action_change_max_depth)

        self.action_menu.setDisabled(True)

        self.menuBar().addMenu(self.action_menu)

        # View menu
        self.menuBar().addSeparator()
        self.view_menu = QtWidgets.QMenu('&View', self)
        self.view_menu.addAction('&Show mutexes', self.view_mutexes,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_M)
        self.view_menu.addAction('&Show no-op', self.show_no_ops,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_P)
        self.menuBar().addMenu(self.view_menu)
        self.view_menu.setDisabled(True)

        # Help menu
        self.menuBar().addSeparator()
        self.help_menu = QtWidgets.QMenu('&Help', self)
        self.menuBar().addMenu(self.help_menu)

        self.help_menu.addAction('&About', self.about)

    def closeEvent(self, ce):
        self.file_quit()

    def file_quit(self):
        self.close()

    def file_load_pddl(self, file_type):
        if file_type == "domain":
            self.domain_file_path = self._load_file()
        else:
            self.problem_file_path = self._load_file()

        if self.problem_file_path and self.domain_file_path:
            self._try_start_graph_plan()

    def about(self):
        # TODO this
        QtWidgets.QMessageBox.about(self, "About", "e")

    def action_expand_level(self):
        if not self.gp.is_ready:
            return
        self.gp.expand_level()
        self._refresh_graph_view()

    def action_solve(self):
        if not self.gp.is_ready:
            return
        solution = self.gp.solve(with_expanding=False)
        solution_string = self.gp.format_solution(solution)
        ms = QtWidgets.QMessageBox()
        ms.setText(solution_string)
        ms.exec_()

    def action_expand_and_solve(self):
        if not self.gp.is_ready:
            return
        solution = self.gp.solve()
        self.gp._create_nx_graph()
        self._set_empty_plot()
        solution_nodes = self.gp.get_solution_nx_nodes(solution)

        self.gp.draw_graph(self.mpl.axes, alpha=0.2)
        self.gp.draw_graph(self.mpl.axes, draw_list=solution_nodes, keep_old_layout=True)
        self._refresh_figure()
        # solution_string = self.gp.format_solution(solution)
        # ms = QtWidgets.QMessageBox()
        # ms.setText(solution_string)
        # ms.exec_()

    def action_reset_graph(self):

        self.gp = engine.GraphPlanVis()
        self._set_empty_plot()
        self._try_start_graph_plan()

    def action_change_max_depth(self):
        i, okPressed = QtWidgets.QInputDialog.getInt(self, "Please set the maximal number of equal level\n" +
                                                           "before the algorithm fails", "Maximal equal levels:",
                                                     2, 2, 100, 1)
        if okPressed:
            self.gp.max_depth_checking = i
    def view_mutexes(self):
        if not self.gp.is_ready:
            return
        # self.gp.draw_graph_mutexes(self.mpl.axes)
        self.mutex_mode = not self.mutex_mode

    def show_no_ops(self):
        self.gp.draw_no_op = not self.gp.draw_no_op
        self._refresh_graph_view()

    def _try_start_graph_plan(self):
        try:
            self.gp.create_problem(self.domain_file_path, self.problem_file_path)
            self.action_menu.setDisabled(False)
            self.view_menu.setDisabled(False)

        except Exception as e:
            self.gp = engine.GraphPlanVis()
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage(str(e))

    def _load_file(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()",
                                                             "examples/block-world", "pddl plan files (*.pddl)", options=options)
        if not file_path.endswith(".pddl"):
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage('file is not a .pddl format!')
        return file_path

    def _set_empty_plot(self):
        self.mpl.axes.cla()
        self._refresh_figure()

    def _refresh_figure(self):

        self.mpl.figure.canvas.draw()
        self.mpl.figure.canvas.flush_events()

    def _refresh_graph_view(self):
        self.mpl.axes.cla()
        self.gp.visualize(self.mpl.axes, alpha=1)
        self._refresh_figure()


app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
app.exec_()