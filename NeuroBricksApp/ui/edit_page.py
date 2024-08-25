import sys
from PyQt6 import QtWidgets, QtGui, QtCore


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1920, 1080)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.topScene = QtWidgets.QGraphicsScene()
        self.topView = QtWidgets.QGraphicsView(self.topScene, self.centralwidget)
        self.topView.setGeometry(QtCore.QRect(0, 0, 1920, 110))
        self.topView.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop)

        self.mainScene = QtWidgets.QGraphicsScene()
        self.mainView = QtWidgets.QGraphicsView(self.mainScene, self.centralwidget)
        self.mainView.setGeometry(QtCore.QRect(0, 110, 1920, 970))

        self.setupButtonsAndTabs()

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)

    def setupButtonsAndTabs(self):
        self.addButtons()

        tools_tab = QtWidgets.QTabWidget()
        edit_tab = QtWidgets.QTabWidget()
        tools_tab.setGeometry(QtCore.QRect(0, 0, 241, 950))
        edit_tab.setGeometry(QtCore.QRect(246, 0, 1670, 950))

        tool_layer_widget = QtWidgets.QWidget()
        tool_data_widget = QtWidgets.QWidget()
        tool_custom_widget = QtWidgets.QWidget()

        tools_tab.addTab(tool_layer_widget, "Layer")
        tools_tab.addTab(tool_data_widget, "Data")
        tools_tab.addTab(tool_custom_widget, "Custom")

        # Creating tabs for Preprocessing, DNN, and Pipeline
        for category in ["Preprocessing", "DNN", "Pipeline"]:
            tab_widget = QtWidgets.QTabWidget()
            editor_widget = QtWidgets.QWidget()
            code_widget = QtWidgets.QWidget()

            # Setting layouts and adding graphics views
            editor_layout = QtWidgets.QVBoxLayout(editor_widget)
            code_layout = QtWidgets.QVBoxLayout(code_widget)

            editor_layout.addWidget(QtWidgets.QGraphicsView())
            code_layout.addWidget(QtWidgets.QGraphicsView())

            tab_widget.addTab(editor_widget, "Editor")
            tab_widget.addTab(code_widget, "Code")

            edit_tab.addTab(tab_widget, category)

        self.mainScene.addWidget(tools_tab)
        self.mainScene.addWidget(edit_tab)

    def addButtons(self):
        icons = [
            "icons8-folder-48.png", "icons8-save-48.png", "icons8-export-32.png",
            "icons8-process-48.png", "icons8-brain-48.png", "icons8-pipeline-48.png",
            "icons8-sort-48.png", "icons8-pipeline-32.png"
        ]
        captions = ["Load", "Save", "Export", "Preprocess", "DNN", "Pipeline", "Sort", "Absorb"]
        x = 0
        y = 10
        for icon, caption in zip(icons, captions):
            button = QtWidgets.QPushButton(caption)
            button.setIcon(QtGui.QIcon(f"./image/{icon}"))
            button.setIconSize(QtCore.QSize(64, 64))
            buttonProxy = self.topScene.addWidget(button)
            buttonProxy.setPos(x, y)
            x += 110


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
