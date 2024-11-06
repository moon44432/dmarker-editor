from PyQt5.QtWidgets import (QApplication, QMainWindow, QGraphicsScene, QGraphicsView, 
                           QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QToolBar,
                           QLabel, QFileDialog, QComboBox, QCheckBox, QLineEdit,
                           QColorDialog, QSpinBox, QDoubleSpinBox, QListWidget,
                           QDockWidget, QGroupBox, QFormLayout, QButtonGroup,
                           QRadioButton, QMessageBox, QListWidgetItem, QDialog, QDialogButtonBox)
from PyQt5.QtCore import Qt, QPointF, QRectF, QLineF
from PyQt5.QtGui import QPen, QBrush, QColor, QPainter, QPolygonF, QTransform


class MarkerView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.NoDrag)  # 기본 드래그 모드 비활성화
        self.setMouseTracking(True)
        self.last_mouse_pos = None
        self.zoom_factor = 1.15
        self.zoom_scale = 1.0
        
    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            if self.zoom_scale >= 15.0:
                return
            self.scale(self.zoom_factor, self.zoom_factor)
            self.zoom_scale *= self.zoom_factor
        else:
            if self.zoom_scale <= 0.05:
                return
            self.scale(1.0 / self.zoom_factor, 1.0 / self.zoom_factor)
            self.zoom_scale /= self.zoom_factor
        self.parent().parent().zoom_label.setText(f"{round(self.zoom_scale*100)}%")

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
        super().mousePressEvent(event)
        
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton:
            self.setDragMode(QGraphicsView.NoDrag)
        super().mouseReleaseEvent(event)
            
    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self.last_mouse_pos:
            delta = event.pos() - self.last_mouse_pos
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y())
            self.last_mouse_pos = event.pos()
        super().mouseMoveEvent(event)
        pos = self.mapToScene(event.pos())
        world_pos = self.parent().parent().screenToWorld(pos.x(), pos.y())
        status_text = f"X: {round(world_pos[0])}, Z: {round(world_pos[2])}"
        self.parent().parent().coord_label.setText(status_text)