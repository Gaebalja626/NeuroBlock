import sys
from PyQt6 import QtWidgets
from welcome_page import Ui_MainWindow as WelcomePage
from edit_page import Ui_MainWindow as EditPage

class MainApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.welcome_ui = WelcomePage()
        self.welcome_ui.setupUi(self)
        self.welcome_ui.btn_newproject.clicked.connect(self.switch_to_edit)

    def switch_to_edit(self):
        self.edit_ui = EditPage()
        self.edit_ui.setupUi(self)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec())