import sys
import yaml
import math
import uuid
from PyQt5.QtWidgets import (QApplication, QMainWindow, QGraphicsScene, QGraphicsView, 
                           QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QToolBar,
                           QLabel, QFileDialog, QComboBox, QCheckBox, QLineEdit,
                           QColorDialog, QSpinBox, QDoubleSpinBox, QListWidget,
                           QDockWidget, QGroupBox, QFormLayout, QButtonGroup,
                           QRadioButton, QMessageBox, QListWidgetItem, QDialog, QDialogButtonBox)
from PyQt5.QtCore import Qt, QPointF, QRectF, QLineF
from PyQt5.QtGui import QPen, QBrush, QColor, QPainter, QPolygonF, QTransform


class MarkerScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.view_mode = 'top'
        self.selected_item = None
        self.hover_point = None
        self.setSceneRect(-29999984, -29999984, 2*29999984, 2*29999984)  # 충분히 큰 씬 영역 설정

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        for item in self.selectedItems():
            if item.flags() & item.ItemIsMovable:
                # 현재 위치를 정수 좌표로 반올림
                pos = item.scenePos()
                world_pos = self.parent().screenToWorld(pos.x(), pos.y())
                world_pos = (round(world_pos[0]), world_pos[1], round(world_pos[2]))
                snapped_pos = self.parent().worldToScreen(world_pos[0], world_pos[1], world_pos[2])
                
                # 아이템 위치를 스냅된 위치로 업데이트
                item.setPos(snapped_pos)
        
    def drawBackground(self, painter, rect):
        # 격자 크기 및 범위 설정
        grid_size = 100
        left = int(rect.left()) - (int(rect.left()) % grid_size)
        top = int(rect.top()) - (int(rect.top()) % grid_size)
        
        # 격자 선 그리기
        lines = []
        x = left
        while x < rect.right():
            lines.append(QLineF(x, rect.top(), x, rect.bottom()))
            x += grid_size
            
        y = top
        while y < rect.bottom():
            lines.append(QLineF(rect.left(), y, rect.right(), y))
            y += grid_size
            
        painter.setPen(QPen(QColor(200, 200, 200)))
        painter.drawLines(lines)

        if self.view_mode == 'top':
            
            # 좌표 레이블 그리기
            painter.setPen(QPen(Qt.black))
            font = painter.font()
            font.setPointSize(8)
            painter.setFont(font)
            
            # X좌표 레이블
            x = left
            while x < rect.right():
                painter.drawText(QPointF(x + 2, rect.top() + 12), str(int(x)))
                x += grid_size
                
            # Z좌표 레이블 (반전된 값으로 표시)
            y = top
            while y < rect.bottom():
                painter.drawText(QPointF(rect.left() + 2, y + 12), str(int(y)))
                y += grid_size

        