import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsItem, QGraphicsView

from dev_competition.NeuroBricksApp.ui.widgets.block_ui import BlockUI
from dev_competition.NeuroBricksApp.ui.widgets.connection_ui import ConnectionUI


class MainSpace(QGraphicsView):
    def __init__(self):
        super().__init__()

        screen = QApplication.primaryScreen()
        available_geometry = screen.availableGeometry()
        self.setWindowTitle('Neuro Bricks')
        self.setGeometry(available_geometry)
        self.show()

        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        block1 = BlockUI(name='attention', num_in=3, num_out=2)
        block1.addToScene(self.scene)
        block1.setPos(200, 100)

        connection1 = ConnectionUI((0,0), (100,100))
        self.scene.addItem(connection1)


def main():
    print('main is started')
    app = QApplication(sys.argv)
    window = MainSpace()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()