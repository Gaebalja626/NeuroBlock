import sys
from PyQt6.QtGui import QPainter, QCursor
from PyQt6.QtWidgets import QApplication, QPushButton, QHBoxLayout, QLabel, QGraphicsScene, QGraphicsView, \
    QGraphicsItem, QStyleOptionGraphicsItem, QWidget
from PyQt6.QtCore import Qt, QRectF, QPointF

class _Ports(QWidget):
    def __init__(self, num: int):
        super().__init__()
        self.num = num
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)

        for _ in range(self.num):
            port = _HoverableLabel()
            port.setFixedSize(10, 10)
            layout.addWidget(port)

        self.setLayout(layout)
        self.setFixedSize(300, 10)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background-color: transparent;")


class _HoverableLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            background-color: white;
            border: 1px solid black;
            border-radius: 5px;
        """)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

    def enterEvent(self, event):
        self.setStyleSheet("""
            background-color: black;
            border: 1px solid black;
            border-radius: 5px;
        """)

    def leaveEvent(self, event):
        self.setStyleSheet("""
            background-color: white;
            border: 1px solid black;
            border-radius: 5px;
        """)


class _Block(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.setFixedSize(300, 90)
        self.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 2px solid black;
                border-radius: 36px;
            }
            QPushButton:pressed {
                background-color: #C0C0C0;
            }
        """)

class BlockUI(QGraphicsItem):
    def __init__(self, name: str, num_in: int, num_out: int, block_ui_width: int = 300, block_ui_height: int = 100, parent=None):
        super().__init__(parent)

        self.block_width = block_ui_width
        self.block_height = int(block_ui_height*0.9)
        self.port_height = int(block_ui_height*0.1)

        self._block = _Block(name)
        self._block.setFixedSize(self.block_width, self.block_height)
        self._inPorts = _Ports(num_in)
        self._inPorts.setFixedSize(self.block_width, self.port_height)
        self._outPorts = _Ports(num_out)
        self._outPorts.setFixedSize(self.block_width, self.port_height)

        self._dragging = False
        self._offset = QPointF()

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

    def boundingRect(self):
        return QRectF(0, 0, self.block_width, self.block_height + self.port_height)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None):
        pass

    def addToScene(self, scene):
        scene.addItem(self)
        block_proxy = scene.addWidget(self._block)
        in_ports_proxy = scene.addWidget(self._inPorts)
        out_ports_proxy = scene.addWidget(self._outPorts)

        block_proxy.setParentItem(self)
        in_ports_proxy.setParentItem(self)
        out_ports_proxy.setParentItem(self)

        in_ports_proxy.setPos(0, 0)
        block_proxy.setPos(0, self.port_height/2)
        out_ports_proxy.setPos(0, self.block_height)

        block_proxy.setZValue(0)
        in_ports_proxy.setZValue(1)
        out_ports_proxy.setZValue(1)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._offset = event.pos()
            self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if self._dragging:
            self.setPos(self.mapToScene(event.pos() - self._offset))

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

if __name__ == "__main__":
    app = QApplication(sys.argv)

    view = QGraphicsView()
    scene = QGraphicsScene()
    view.setScene(scene)

    block_ui = BlockUI("attention", num_in=3, num_out=2)
    block_ui.addToScene(scene)
    block_ui.setPos(100, 0)

    view.setGeometry(100, 100, 800, 600)
    view.show()

    sys.exit(app.exec())
