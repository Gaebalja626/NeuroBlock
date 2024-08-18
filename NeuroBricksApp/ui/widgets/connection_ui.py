import math
import sys

from PyQt6.QtCore import QRectF, Qt, QLineF, QPointF
from PyQt6.QtGui import QPainter, QPolygonF
from PyQt6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QApplication, QGraphicsView, QGraphicsScene


class ConnectionUI(QGraphicsItem):
    def __init__(self, start_pos: (float, float), end_pos: (float, float)):
        super().__init__()
        self.start = start_pos
        self.end = end_pos

    def boundingRect(self):
        return QRectF(min(self.start[0], self.end[0]), min(self.start[1], self.end[1]),
                      abs(self.start[0] - self.end[0]), abs(self.start[1] - self.end[1]))

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        arrow_size = 20
        painter.setPen(Qt.GlobalColor.black)
        painter.setBrush(Qt.GlobalColor.black)

        line = QLineF(QPointF(self.start[0], self.start[1]), QPointF(self.end[0], self.end[1]))

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



if __name__ == "__main__":
    app = QApplication(sys.argv)

    view = QGraphicsView()
    scene = QGraphicsScene()
    view.setScene(scene)

    connection_ui = ConnectionUI((0, 0), (100, 100))
    scene.addItem(connection_ui)

    view.setGeometry(100, 100, 800, 600)
    view.show()

    sys.exit(app.exec())
