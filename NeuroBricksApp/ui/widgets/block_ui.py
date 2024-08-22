import sys
from PyQt6.QtGui import QPainter, QCursor
from PyQt6.QtWidgets import QApplication, QPushButton, QHBoxLayout, QLabel, QGraphicsScene, QGraphicsView, \
    QGraphicsItem, QStyleOptionGraphicsItem, QWidget
from PyQt6.QtCore import Qt, QRectF, QPointF, QPoint, pyqtSignal


class _Ports(QWidget):
    def __init__(self, num: int):
        super().__init__()
        self.num = num
        self.drawPorts()

    def drawPorts(self):
        layout = QHBoxLayout()
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)

        for _ in range(self.num):
            port = _Port()
            port.setFixedSize(10, 10)
            layout.addWidget(port)

        self.setLayout(layout)
        self.setFixedSize(300, 10)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background-color: transparent;")


class _Port(QLabel):
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
    positionChanged = pyqtSignal(QPoint)

    def __init__(self, text):
        super().__init__(text)
        self.diff:QPoint = None
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
        self.dragging = False
        self._drag_start_point = None

# todo 1. 드래그 이동을 오래하면 마우스 위치와 블럭 위치가 벌어짐
#  -> 마우스 위치는 QPointF(float, float)인데 블럭 이동은 QPoint(int, int)라 소수점 버림하면서 생기는 차이인 듯. (..반올림을 할까?)
#   -> 그냥 처음부터 모든 위치를 QPoint()로 통일해 해결(maybe.?)
# todo 2. 아래처럼 마우스 위치는 크게 안 변함에도 블럭 위치가 갑자기 크게 이동하는 경우 생김.
#  두번째 드래그 이후부터 해당 현상이 발생하는 걸로 보아 마우스 위치와 블럭의 origin 위치(좌측 상단) 간의.. 뭔가 차이에 의해 발생하는 걸로 의심 됨.
#  이를 해결하기 위해 mouseReleaseEvent 때 다 None으로 초기화해줬지만 그럼에도 해결되지 않음. 일단 보류.

    # PyQt6.QtCore.QPointF(1036.0, 502.0) - 마우스 위치
    # PyQt6.QtCore.QPoint(629, 343)       - 블럭 위치
    # PyQt6.QtCore.QPointF(1036.0, 501.0)
    # PyQt6.QtCore.QPoint(629, 343)
    # PyQt6.QtCore.QPointF(1037.0, 501.0)
    # PyQt6.QtCore.QPoint(1115, 557)

    def mousePressEvent(self, e):
        self.dragging = True
        self._drag_start_point = e.globalPosition().toPoint()
        print("=============clicked=============")
        print('start_pos =', self._drag_start_point)

    def mouseMoveEvent(self, e):
        if self.dragging:
            diff = e.globalPosition().toPoint()-self._drag_start_point
            self.move(diff)
            self.positionChanged.emit(diff)
            print('=========moving============')
            print('diff =', diff)

    def mouseReleaseEvent(self, e):
        self.dragging = False
        self.diff = None
        self._drag_start_point = None
        print('==========released============')
        pass

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

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

        self._block.positionChanged.connect(self.updatePortsPosition)


    def boundingRect(self):
        return QRectF(0, 0, self.block_width, self.block_height+self.port_height)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None):
        pass

    def addToScene(self, scene):
        scene.addItem(self)
        self._block_proxy = scene.addWidget(self._block)
        self._in_ports_proxy = scene.addWidget(self._inPorts)
        self._out_ports_proxy = scene.addWidget(self._outPorts)

        self._block_proxy.setParentItem(self)
        self._in_ports_proxy.setParentItem(self)
        self._out_ports_proxy.setParentItem(self)

        self._block_proxy.setPos(0, self.port_height/2)
        self.updatePortsPosition()
        # print(self._block.dragging)
        # if self._block.dragging:
        #     print('======================')
        #     self.updatePortsPosition()

        self._block_proxy.setZValue(0)
        self._in_ports_proxy.setZValue(1)
        self._out_ports_proxy.setZValue(1)

    # todo 3. ports 위치를 block에 상대적으로 정하기 위해 아래처럼 코드를 짰고
    #   실제로도 블럭을 움직일 시 상대적으로 함께(?) 움직이는 걸 확인 했으나
    #   그 움직임이 뭔가 다름...
    #   근데 또 출력된 로그 확인해보면 좌표값은 다 잘 정해져있음이 보임.. 그냥 gui 상에 표시되는 모습만 이상한 거 같음.

    #   원하는 모습(port w=300, h=10(5씩 블럭과 겹침-ui 관련은 figma 파일 참고) / block w=300, h=90)
    #   block(x,y)
    #   in(x, y-5)
    #   out(x, y+95)
    def updatePortsPosition(self, diff=None):
        if diff is None:
            block_pos = self._block_proxy.widget().pos()
        else:
            block_pos = self._block_proxy.widget().pos()+diff

        self._in_ports_proxy.setPos(block_pos.x(), block_pos.y()-self.port_height/2)
        self._out_ports_proxy.setPos(block_pos.x(), block_pos.y()+self.block_height-self.port_height/2)
        print("block:", block_pos)
        print("in: ",self._in_ports_proxy.pos())
        print("out: ", self._out_ports_proxy.pos())

    # def itemChange(self, change, value):
    #     if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
    #         self.updatePortsPosition()
    #         print("===============changed==================")
    #     return super().itemChange(change, value)
    # BlockUI가 바뀌는 게 아니라서 이 메소드로는(QGraphicsItem의 변화를 감지) 원하는 바를 못 이룸.

    # def mousePressEvent(self, event):
    #     super().mousePressEvent(event)
    #     if event.button() == Qt.MouseButton.LeftButton:
    #         self._dragging = True
    #         self._offset = event.pos()
    #         self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
    #
    # def mouseMoveEvent(self, event):
    #     super().mouseMoveEvent(event)
    #     if self._dragging:
    #         self.setPos(self.mapToScene(event.pos() - self._offset))
    #
    # def mouseReleaseEvent(self, event):
    #     super().mouseReleaseEvent(event)
    #     if event.button() == Qt.MouseButton.LeftButton:
    #         self._dragging = False
    #         self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

if __name__ == "__main__":
    app = QApplication(sys.argv)

    view = QGraphicsView()
    scene = QGraphicsScene()
    view.setScene(scene)

    block_ui = BlockUI(name="attention", num_in=3, num_out=2)
    block_ui.addToScene(scene)
    block_ui.setPos(100, 0)

    view.setGeometry(100, 100, 800, 600)
    view.show()

    sys.exit(app.exec())
