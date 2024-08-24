import math
import sys

from PyQt6.QtCore import QRectF, Qt, QLineF, QPointF
from PyQt6.QtGui import QPainter, QPolygonF
from PyQt6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QApplication, QGraphicsView, QGraphicsScene


class ConnectionUI(QGraphicsItem):
    def __init__(self, start_pos: QPointF, end_pos: QPointF):
        super().__init__()
        self.tail = start_pos
        self.head = end_pos

    def boundingRect(self):
        return QRectF(self.head, self.tail).normalized()

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        arrow_size = 20
        painter.setPen(Qt.GlobalColor.black)
        painter.setBrush(Qt.GlobalColor.black)

        line = QLineF(self.head, self.tail)

        angle = math.atan2(-line.dy(), line.dx())

        arrow_p1 = line.p1() + QPointF(math.sin(angle + math.pi / 4) * arrow_size,
                                       math.cos(angle + math.pi / 4) * arrow_size)
        arrow_p2 = line.p1() + QPointF(math.sin(angle + math.pi - math.pi / 4) * arrow_size,
                                       math.cos(angle + math.pi - math.pi / 4) * arrow_size)

        # arrow_head_shape == line (default)
        arrow_l1 = QLineF(line.p1(), arrow_p1)
        arrow_l2 = QLineF(line.p1(), arrow_p2)

        painter.drawLine(line)
        painter.drawLine(arrow_l1)
        painter.drawLine(arrow_l2)

        # arrow_head_shape == triangle:
        # arrow_head = QPolygonF()
        # arrow_head.append(line.p1())
        # arrow_head.append(arrow_p1)
        # arrow_head.append(arrow_p2)
        #
        # painter.drawLine(line)
        # painter.drawPolygon(arrow_head)

class MainSpace(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.drawing = False
        self.start_pos = None
        self.end_pos = None
        self.setSceneRect(0, 0, 800, 600)


    def mousePressEvent(self, event):
        if self.drawing:
            self.end_pos = event.scenePos()
            connection = ConnectionUI(self.start_pos, self.end_pos)
            self.addItem(connection)
            self.drawing = False
            print(self.end_pos)

        else:
            self.start_pos = event.scenePos()
            self.drawing = True
            print(self.start_pos)



if __name__ == "__main__":
    app = QApplication(sys.argv)

    view = QGraphicsView()
    # scene = QGraphicsScene()
    scene = MainSpace()
    view.setScene(scene)

    connection_ui = ConnectionUI(QPointF(0,0), QPointF(100,100))
    scene.addItem(connection_ui)

    view.setGeometry(100, 100, 800, 600)
    view.show()

    sys.exit(app.exec())
