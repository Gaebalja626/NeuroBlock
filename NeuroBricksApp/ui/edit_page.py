import sys
from PyQt6 import QtWidgets, QtGui, QtCore

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1920, 1080)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # Graphics View 설정
        self.scene = QtWidgets.QGraphicsScene()
        self.graphicsView = QtWidgets.QGraphicsView(self.scene, self.centralwidget)
        self.graphicsView.setGeometry(QtCore.QRect(0, 0, 1920, 1080))

        # 버튼과 탭을 그래픽스 씬에 추가
        self.setupButtonsAndTabs()

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)

    def setupButtonsAndTabs(self):
        # 도구 탭과 에디터 탭 설정
        tools_tab = QtWidgets.QTabWidget()
        edit_tab = QtWidgets.QTabWidget()
        tools_tab.setGeometry(QtCore.QRect(0, 110, 241, 950))
        edit_tab.setGeometry(QtCore.QRect(246, 110, 1670, 950))

        # 도구 및 에디터 위젯 생성 및 추가
        tool_layer_widget = QtWidgets.QWidget()
        tool_data_widget = QtWidgets.QWidget()
        tool_custom_widget = QtWidgets.QWidget()

        tools_tab.addTab(tool_layer_widget, "Layer")
        tools_tab.addTab(tool_data_widget, "Data")
        tools_tab.addTab(tool_custom_widget, "Custom")
        edit_tab.addTab(QtWidgets.QWidget(), "Editor")

        # QGraphicsProxyWidget을 통해 위젯을 씬에 추가
        tools_proxy = self.scene.addWidget(tools_tab)
        editor_proxy = self.scene.addWidget(edit_tab)

        # 위치 조정
        tools_proxy.setPos(0, 110)
        editor_proxy.setPos(246, 110)

        # 추가 버튼 및 기타 인터페이스 요소 설정
        self.addButtons()

    def addButtons(self):
        # 버튼 위치 및 아이콘 설정
        icons = [
            "icons8-folder-48.png", "icons8-save-48.png", "icons8-export-32.png",
            "icons8-process-48.png", "icons8-brain-48.png", "icons8-pipeline-48.png",
            "icons8-sort-48.png", "icons8-pipeline-32.png"
        ]
        captions = ["Load", "Save", "Export", "Preprocess", "DNN", "Pipeline", "Sort", "Absorb"]
        positions = [(10, 10), (110, 10), (210, 10), (310, 10), (410, 10), (510, 10), (610, 10), (710, 10)]

        for icon, caption, pos in zip(icons, captions, positions):
            button = QtWidgets.QPushButton(caption)
            button.setIcon(QtGui.QIcon(f"./image/{icon}"))
            button.setIconSize(QtCore.QSize(64, 64))
            button_proxy = self.scene.addWidget(button)
            button_proxy.setPos(*pos)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
