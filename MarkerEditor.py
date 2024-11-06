import sys
import yaml
import math
import uuid
from PyQt5.QtWidgets import (QApplication, QMainWindow, QGraphicsScene, QGraphicsView, 
                           QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QToolBar,
                           QLabel, QFileDialog, QComboBox, QCheckBox, QLineEdit,
                           QColorDialog, QSpinBox, QDoubleSpinBox, QListWidget,
                           QDockWidget, QGroupBox, QFormLayout, QButtonGroup, QGridLayout,
                           QRadioButton, QMessageBox, QListWidgetItem, QDialog, QDialogButtonBox, QGraphicsTextItem)
from PyQt5.QtCore import Qt, QPointF, QRectF, QLineF, QPoint
from PyQt5.QtGui import QPen, QBrush, QColor, QPainter, QPolygonF, QTransform

from MarkerScene import MarkerScene
from MarkerView import MarkerView

class MarkerEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.marker_data = None
        self.current_file = None
        self.selected_item = None
        self.dragging_item = None
        self.drag_start_pos = None
        self.adding_marker = None
        self.adding_vertex = None
        self.file_loaded = False
        self.temp_properties = {}
        self.default_icons = ['default', 'house', 'bighouse', 'church', 'bank', 'building', 
                'factory', 'lighthouse', 'tower', 'temple', 'bookshelf', 'theater',
                'beer', 'drink', 'cutlery', 'cup', 'camera', 'tree', 'basket',
                'cart', 'scales', 'coins', 'chest', 'hammer', 'bricks', 'flower',
                'skull', 'anchor', 'minecart', 'truck', 'gear', 'portal', 'door',
                'sign', 'king', 'queen', 'up', 'down', 'left', 'right', 'pointup',
                'pointdown', 'pointleft', 'pointright', 'pin', 'redflag', 
                'orangeflag', 'yellowflag', 'greenflag', 'blueflag', 'purpleflag',
                'pinkflag', 'pirateflag', 'walk', 'goldstar', 'silverstar',
                'bronzestar', 'goldmedal', 'silvermedal', 'bronzemedal', 'diamond',
                'ruby', 'world', 'caution', 'construction', 'warning', 'lock',
                'exclamation', 'cross', 'fire', 'tornado', 'bomb', 'shield', 'sun',
                'star', 'key', 'comment', 'dog', 'wrench', 'compass', 'lightbulb',
                'heart', 'cake']

        self.initUI()
        self.updatePropertiesPanel()
        self.updateUIState()

    def updateUIState(self):
        # UI 요소들의 활성화/비활성화 상태 설정
        enabled = self.file_loaded
        self.save_action.setEnabled(enabled)
        self.world_combo.setEnabled(enabled)
        self.set_combo.setEnabled(enabled)

        self.add_point.setEnabled(enabled)
        self.add_line.setEnabled(enabled)
        self.add_area.setEnabled(enabled)

        self.properties_dock.setEnabled(enabled)
        for btn in self.view_buttons.buttons():
            btn.setEnabled(enabled)

        self.point_check.setEnabled(enabled)
        self.line_check.setEnabled(enabled)
        self.area_check.setEnabled(enabled)
        self.label_check.setEnabled(enabled)

        self.world_list.setEnabled(enabled)
        self.set_list.setEnabled(enabled)
        
    def initUI(self):
        self.setWindowTitle('Minecraft Dynamic Map Marker Editor')
        self.setGeometry(100, 100, 1200, 800)
        
        # 메인 위젯 및 레이아웃 설정
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        
        # 툴바 생성
        self.createToolbar()
        
        # 좌측 필터 패널
        filter_dock = QDockWidget('Display', self)
        filter_dock.setWidget(self.createFilterPanel())
        self.addDockWidget(Qt.LeftDockWidgetArea, filter_dock)
        
        # 중앙 뷰어
        self.scene = MarkerScene(self)
        self.view = MarkerView(self.scene)
        main_layout.addWidget(self.view)
        
        # 우측 속성 패널
        self.properties_dock = QDockWidget('Properties', self)
        self.properties_widget = QWidget()
        self.properties_layout = QFormLayout(self.properties_widget)
        self.properties_dock.setWidget(self.properties_widget)
        self.properties_dock.setMinimumWidth(250)
        self.properties_dock.setMaximumWidth(500)
        self.addDockWidget(Qt.RightDockWidgetArea, self.properties_dock)

        self.coord_label = QLabel("X: 0, Z: 0")
        self.statusBar().addPermanentWidget(self.coord_label)

        self.zoom_label = QLabel("100%")
        self.statusBar().addPermanentWidget(self.zoom_label)
        
        # 이벤트 연결
        self.connectSignals()
        
    def createToolbar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # 파일 작업
        self.open_action = toolbar.addAction('Open')
        self.open_action.triggered.connect(self.openFile)
        self.save_action = toolbar.addAction('Save')
        self.save_action.triggered.connect(self.saveFile)
        toolbar.addSeparator()

        # World 선택 콤보박스
        world_label = QLabel("World: ")
        toolbar.addWidget(world_label)
        self.world_combo = QComboBox()
        self.world_combo.setMinimumWidth(150)
        toolbar.addWidget(self.world_combo)
        toolbar.addSeparator()
        
        # Set 선택 콤보박스
        set_label = QLabel("Set: ")
        toolbar.addWidget(set_label)
        self.set_combo = QComboBox()
        self.set_combo.setMinimumWidth(150)
        toolbar.addWidget(self.set_combo)
        toolbar.addSeparator()
        
        # 새 마커 추가 버튼
        self.add_point = toolbar.addAction('Add Point')
        self.add_point.triggered.connect(lambda: self.startAddingMarker('point'))
        self.add_line = toolbar.addAction('Add Line')
        self.add_line.triggered.connect(lambda: self.startAddingMarker('line'))
        self.add_area = toolbar.addAction('Add Area')
        self.add_area.triggered.connect(lambda: self.startAddingMarker('area'))

        # About 버튼 추가
        toolbar.addSeparator()
        about_action = toolbar.addAction('About')
        about_action.triggered.connect(self.showAboutDialog)

    def showAboutDialog(self):
        about_text = """
        <h3>Minecraft Dynamic Map Marker Editor</h3>
        <p>A tool for visualizing and editing marker data of Minecraft <a href="https://www.spigotmc.org/resources/dynmap%C2%AE.274/">Dynamic Map</a> plugin.</p>
        <p>Features:</p>
        <ul>
            <li>Edit point, line and area markers</li>
            <li>Multiple view modes (Top view, Isometric view)</li>
            <li>Filter markers by marker type, world and set</li>
            <li>Customize marker properties</li>
        </ul>

        <p>Version 0.0.1</p>
        <p>ⓒ 2024 <a href="https://www.youtube.com/@moonsvr">MoonServer Studios</a>. All rights reserved.</p>
        <hr>
        <p>
        <a href="https://github.com/moon44432">License and source code</a><br>
        
        </p>
        """
        QMessageBox.about(self, "About", about_text)
        
    def createViewControls(self):
        view_widget = QGroupBox('View Mode')
        view_layout = QVBoxLayout()
        
        self.view_buttons = QButtonGroup()
        views = [
            ('Top', 'top'),
            ('Isometric (NE)', 'iso_ne'),
            ('Isometric (NW)', 'iso_nw'),
            ('Isometric (SE)', 'iso_se'),
            ('Isometric (SW)', 'iso_sw')
        ]
        
        for text, mode in views:
            radio = QRadioButton(text)
            self.view_buttons.addButton(radio)
            view_layout.addWidget(radio)
            # 람다 함수에서 mode 인자를 명시적으로 전달하도록 수정
            radio.clicked.connect(lambda checked, m=mode: self.updateViewMode(m))
            
        self.view_buttons.buttons()[0].setChecked(True)
        view_widget.setLayout(view_layout)
        return view_widget
        
    def createFilterPanel(self):
        filter_widget = QWidget()
        filter_layout = QVBoxLayout()

                
        # 뷰 모드 컨트롤
        view_group = self.createViewControls()
        filter_layout.addWidget(view_group)
        
        # 마커 타입 필터
        types_group = QGroupBox('Display Options')  # 이름을 더 명확하게 변경
        types_layout = QVBoxLayout()
        self.point_check = QCheckBox('Show Points')
        self.line_check = QCheckBox('Show Lines')
        self.area_check = QCheckBox('Show Areas')
        self.label_check = QCheckBox('Show Labels')  # 새로 추가

        for check in [self.point_check, self.line_check, 
                 self.area_check, self.label_check]:  # label_check 추가
            check.setChecked(True)
            check.stateChanged.connect(self.updateDisplay)
            types_layout.addWidget(check)

        types_group.setLayout(types_layout)
        filter_layout.addWidget(types_group)
        
        # 월드 필터
        worlds_group = QGroupBox('Worlds')
        worlds_layout = QVBoxLayout()
        self.world_list = QListWidget()
        self.world_list.setMaximumWidth(200)
        self.world_list.setSelectionMode(QListWidget.MultiSelection)
        self.world_list.itemSelectionChanged.connect(self.updateDisplay)
        worlds_layout.addWidget(self.world_list)
        worlds_group.setLayout(worlds_layout)
        filter_layout.addWidget(worlds_group)
        
        # 세트 필터
        sets_group = QGroupBox('Sets')
        sets_layout = QVBoxLayout()
        self.set_list = QListWidget()
        self.set_list.setMaximumWidth(200)
        self.set_list.setSelectionMode(QListWidget.MultiSelection)
        self.set_list.itemSelectionChanged.connect(self.updateDisplay)
        sets_layout.addWidget(self.set_list)
        sets_group.setLayout(sets_layout)
        filter_layout.addWidget(sets_group)
        
        filter_widget.setLayout(filter_layout)
        return filter_widget
        
    def connectSignals(self):
        self.scene.selectionChanged.connect(self.handleSelection)
        
    def openFile(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Open YAML file', '', 'YAML files (*.yml)')
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as file:
                    self.marker_data = yaml.safe_load(file)
                self.current_file = filename
                self.file_loaded = True  # 파일 로드 성공
                self.updateWorldList()
                self.updateSetList()
                self.updateDisplay()
                self.updateUIState()  # UI 상태 업데이트
            except Exception as e:
                self.file_loaded = False
                print(f"Error loading file: {e}")
                self.updateUIState()
                
    def saveFile(self):
        if not self.current_file:
            self.current_file, _ = QFileDialog.getSaveFileName(
                self, 'Save YAML file', '', 'YAML files (*.yml)')
        if self.current_file:
            try:
                with open(self.current_file, 'w', encoding='utf-8') as file:
                    yaml.safe_dump(self.marker_data, file, allow_unicode=True)
            except Exception as e:
                print(f"Error saving file: {e}")
                
    def updateWorldList(self):
        if not self.marker_data:
            return
            
        self.world_list.clear()
        worlds = set()
        
        for set_data in self.marker_data['sets'].values():
            for markers in [set_data.get('markers', {}), 
                          set_data.get('lines', {}), 
                          set_data.get('areas', {})]:
                for marker in markers.values():
                    worlds.add(marker['world'])
                    
        for i, world in enumerate(sorted(worlds)):
            item = QListWidgetItem(world)
            self.world_list.addItem(item)
            if i == 0:
                item.setSelected(True)

        self.world_combo.clear()
        self.world_combo.addItems(sorted(worlds))
            
    def updateSetList(self):
        if not self.marker_data:
            return
            
        self.set_list.clear()
        for set_id in sorted(self.marker_data['sets'].keys()):
            item = QListWidgetItem(set_id)
            self.set_list.addItem(item)
            item.setSelected(True)

        self.set_combo.clear()
        self.set_combo.addItems(sorted(self.marker_data['sets'].keys()))
            
    def updateViewMode(self, mode):
        self.scene.view_mode = mode
        self.updateDisplay()
        
    def updateDisplay(self):
        print("Updating display")
        if not self.marker_data:
            return
            
        self.scene.clear()
        
        # 선택된 월드와 세트 가져오기
        selected_worlds = [item.text() for item in 
                         self.world_list.selectedItems()]
        selected_sets = [item.text() for item in 
                        self.set_list.selectedItems()]
        
        for set_id, set_data in self.marker_data['sets'].items():
            if set_id not in selected_sets:
                continue
                
            # 점 마커 그리기
            if self.point_check.isChecked():
                for marker_id, marker in set_data.get('markers', {}).items():
                    if marker['world'] not in selected_worlds:
                        continue
                    self.drawPointMarker(set_id, marker_id, marker)
                    
            # 선 마커 그리기
            if self.line_check.isChecked():
                for line_id, line in set_data.get('lines', {}).items():
                    if line['world'] not in selected_worlds:
                        continue
                    self.drawLineMarker(set_id, line_id, line)
                    
            # 영역 마커 그리기
            if self.area_check.isChecked():
                for area_id, area in set_data.get('areas', {}).items():
                    if area['world'] not in selected_worlds:
                        continue
                    self.drawAreaMarker(set_id, area_id, area)
                    
    def drawPointMarker(self, set_id, marker_id, marker):
        selected = self.selected_item and self.selected_item == ('point', set_id, marker_id)

        pos = self.worldToScreen(marker['x'], marker['y'], marker['z'])
        point = self.scene.addEllipse(
            pos.x() - 5, pos.y() - 5, 10, 10,
            QPen(Qt.black), 
            QBrush(Qt.red if selected else Qt.blue)
        )
        
        point.setData(0, ('point', set_id, marker_id))
        if not selected:
            point.setFlag(point.ItemIsSelectable)
        
        # 마커 라벨 추가
        if self.label_check.isChecked():
            label = self.scene.addText(marker['label'])
            label.setPos(pos.x() + 10, pos.y() - 10)
            label.setDefaultTextColor(Qt.black)
        
    def drawLineMarker(self, set_id, line_id, line):
        selected = self.selected_item and self.selected_item == ('line', set_id, line_id)

        points = []
        # 먼저 선을 그림
        for i in range(len(line['x'])):
            pos = self.worldToScreen(line['x'][i], line['y'][i], line['z'][i])
            points.append(pos)

        pen = QPen(QColor.fromRgb(line['strokeColor']), 
               line['strokeWeight'], 
               Qt.SolidLine)
        pen.setCapStyle(Qt.RoundCap)  # 선분의 끝을 둥글게 처리
        pen.setJoinStyle(Qt.RoundJoin)  # 선분이 만나는 부분도 둥글게 처리

        # 선택된 경우 윤곽선 먼저 그리기
        if selected:
            outline_pen = QPen(Qt.black, line['strokeWeight'] + 2, Qt.SolidLine)
            outline_pen.setCapStyle(Qt.RoundCap)
            outline_pen.setJoinStyle(Qt.RoundJoin)
            for i in range(len(points) - 1):
                outline = self.scene.addLine(
                    points[i].x(), points[i].y(),
                    points[i + 1].x(), points[i + 1].y(), outline_pen
                )
                # outline.setZValue(-1)
        
        # 선분들을 개별적으로 그리기
        for i in range(len(points) - 1):
            path = self.scene.addLine(
                points[i].x(), points[i].y(),
                points[i + 1].x(), points[i + 1].y(), pen
            )
            path.setData(0, ('line', set_id, line_id))
            path.setFlag(path.ItemIsSelectable)
        
        # 그 다음 정점들을 그림
        for i, pos in enumerate(points):
            vertex = self.scene.addEllipse(
                pos.x() - 3, pos.y() - 3, 6, 6,
                QPen(Qt.black),
                QBrush(Qt.green if i == 0 else QColor('#FF7F00') if i == len(points) - 1 else Qt.yellow)
            )
            # 선택된 경우 정점 윤곽선
            if selected:
                highlight = self.scene.addEllipse(
                    pos.x() - 3, pos.y() - 3, 6, 6,
                    QPen(Qt.blue),
                    QBrush(Qt.green if i == 0 else QColor('#FF7F00') if i == len(points) - 1 else Qt.red)
                )
                
            vertex.setData(0, ('line_vertex', set_id, line_id, i))
            vertex.setFlag(vertex.ItemIsSelectable)
        
        # 라벨 추가
        if points and self.label_check.isChecked():
            label = self.scene.addText(line['label'])
            label.setPos(points[0].x() + 10, points[0].y() - 10)
            label.setDefaultTextColor(Qt.black)

    def drawAreaMarker(self, set_id, area_id, area):
        selected = self.selected_item and self.selected_item == ('area', set_id, area_id)
    
        points = []
        for i in range(len(area['x'])):
            pos = self.worldToScreen(
                area['x'][i],
                (area['ytop'] + area['ybottom']) / 2,
                area['z'][i]
            )
            points.append(pos)

        # 선택된 경우 윤곽선 먼저 그리기
        if selected:
            outline_pen = QPen(Qt.yellow, area['strokeWeight'] + 4, Qt.DashLine)
            outline_polygon = self.scene.addPolygon(
                QPolygonF(points + [points[0]]),
                outline_pen,
                QBrush(Qt.transparent)
            )
            outline_polygon.setZValue(-1)
        
        # 영역 그리기
        polygon = self.scene.addPolygon(
            QPolygonF(points + [points[0]]),  # 첫 점을 마지막에 추가하여 다각형 완성
            QPen(QColor.fromRgb(area['strokeColor']),
                 area['strokeWeight'],
                 Qt.SolidLine),
            QBrush(QColor.fromRgb(area['fillColor']))
        )
        polygon.setOpacity(area['fillOpacity'])
        polygon.setData(0, ('area', set_id, area_id))
        polygon.setFlag(polygon.ItemIsSelectable)

        # 정점 그리기
        for i, pos in enumerate(points):
            vertex = self.scene.addEllipse(
                pos.x() - 3, pos.y() - 3, 6, 6,
                QPen(Qt.black),
                QBrush(Qt.green if i == 0 else QColor('#FF7F00') if i == len(points) - 1 else Qt.yellow)
            )
            # 선택된 경우 정점 윤곽선
            if selected:
                highlight = self.scene.addEllipse(
                    pos.x() - 3, pos.y() - 3, 6, 6,
                    QPen(Qt.blue),
                    QBrush(Qt.green if i == 0 else QColor('#FF7F00') if i == len(points) - 1 else Qt.red)
                )

            vertex.setData(0, ('area_vertex', set_id, area_id, i))
            vertex.setFlag(vertex.ItemIsSelectable)
        
        # 라벨 추가
        if points and self.label_check.isChecked():
            label = self.scene.addText(area['label'])
            label.setPos(points[0].x() + 10, points[0].y() - 10)
            label.setDefaultTextColor(Qt.black)

    
    def drawSelectedVertex(self, type, set_id, area_or_line_id, vertex_index):
        if type == 'area_vertex':
            area = self.marker_data['sets'][set_id]['areas'][area_or_line_id]
            pos = self.worldToScreen(
                area['x'][vertex_index],
                (area['ytop'] + area['ybottom']) / 2,
                area['z'][vertex_index]
            )
        elif type == 'line_vertex':
            line = self.marker_data['sets'][set_id]['lines'][area_or_line_id]
            pos = self.worldToScreen(line['x'][vertex_index], line['y'][vertex_index], line['z'][vertex_index])
        
        vertex = self.scene.addEllipse(
            pos.x() - 3, pos.y() - 3, 6, 6,
            QPen(Qt.blue),
            QBrush(Qt.red)
        )


    def worldToScreen(self, x, y, z):
        if self.scene.view_mode == 'top':
            return QPointF(x, z)
        else:
            # Isometric 투영 각도 정의
            # NE: 우측 상단, NW: 좌측 상단, SE: 우측 하단, SW: 좌측 하단
            angle = {
                'iso_sw': -math.pi / 4,  # 30도
                'iso_nw': -3 * math.pi / 4,  # 150도
                'iso_se': math.pi / 4,  # -30도
                'iso_ne': 3 * math.pi / 4,  # -150도
            }[self.scene.view_mode]
            
            # 각 방향별 isometric 투영
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            
            # Isometric 투영 계산
            # x' = x * cos(angle) - z * sin(angle)
            # y' = x * sin(angle) + z * cos(angle) - y
            iso_x = x * cos_a - z * sin_a
            iso_y = (x * sin_a + z * cos_a) * 0.5 - y  # 0.5를 곱해 y축 비율 조정
            
            return QPointF(iso_x, iso_y)

    def screenToWorld(self, screen_x, screen_y):
        if self.scene.view_mode == 'top':
            return (screen_x, 65, screen_y)
        else:
            angle = {
                'iso_sw': -math.pi / 4,
                'iso_nw': -3 * math.pi / 4,
                'iso_se': math.pi / 4,
                'iso_ne': 3 * math.pi / 4,
            }[self.scene.view_mode]
            
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            
            # Isometric 투영의 역변환
            # 행렬식을 이용한 역변환
            det = cos_a * cos_a + sin_a * sin_a
            x = (screen_x * cos_a + screen_y * 2 * sin_a) / det  # 2를 곱해 y축 비율 보정
            z = (-screen_x * sin_a + screen_y * 2 * cos_a) / det
            
            return (x, 0, z)

    def handleSelection(self):
        selected_items = self.scene.selectedItems()
        if not selected_items:
            self.selected_item = None
            self.updateDisplay()
            self.updatePropertiesPanel()
            return

        for item in self.scene.items():
            # QGraphicsTextItem은 남기고
            # ItemIsSelectable 플래그가 없는 요소들만 제거
            if not isinstance(item, QGraphicsTextItem) and not (item.flags() & item.ItemIsSelectable):
                self.scene.removeItem(item)
            
            
        item = selected_items[0]
        if item.data(0):
            self.selected_item = item.data(0)
            print(f"Selected item: {self.selected_item}")
            item_type, set_id, marker_id = self.selected_item[:3]

            if item_type == 'point':
                marker = self.marker_data['sets'][set_id]['markers'][marker_id]
                self.drawPointMarker(set_id, marker_id, marker)
            elif item_type == 'line':
                lines = self.marker_data['sets'][set_id]['lines'][marker_id]
                self.drawLineMarker(set_id, marker_id, lines)
            elif item_type == 'area':
                area = self.marker_data['sets'][set_id]['areas'][marker_id]
                self.drawAreaMarker(set_id, marker_id, area)
            elif item_type == 'area_vertex' or item_type == 'line_vertex':
                vertex_index = self.selected_item[3]
                self.drawSelectedVertex(item_type, set_id, marker_id, vertex_index)

            self.updatePropertiesPanel()


    def updatePropertiesPanel(self):
        # 기존 위젯 제거
        while self.properties_layout.count():
            child = self.properties_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        if not self.selected_item:
            label = QLabel("No selected item")
            label.setStyleSheet("color: gray; padding: 20px;")
            label.setAlignment(Qt.AlignCenter)
            self.properties_layout.addRow(label)
            return
        
        item_type, set_id, item_id = self.selected_item[:3]
        vertex_index = self.selected_item[3] if len(self.selected_item) > 3 else None
        
        try:
            self.properties_layout.blockSignals(True)
            if item_type == 'point':
                self.setupPointProperties(set_id, item_id)
            elif item_type == 'line':
                self.setupLineProperties(set_id, item_id)
            elif item_type == 'area':
                self.setupAreaProperties(set_id, item_id)
            elif item_type in ['line_vertex', 'area_vertex']:
                self.setupVertexProperties(set_id, item_id, item_type, vertex_index)
        finally:
            self.properties_layout.blockSignals(False)

    
    def getWorldList(self):
        return sorted(
            set (
                [marker['world'] for markers in 
                self.marker_data['sets'].values()
                for marker in markers.get('markers', {}).values()] +
                [line['world'] for lines in 
                self.marker_data['sets'].values()
                for line in lines.get('lines', {}).values()] +
                [area['world'] for areas in 
                self.marker_data['sets'].values()
                for area in areas.get('areas', {}).values()]
                )
            )


    def setupPointProperties(self, set_id, point_id):
        marker = self.marker_data['sets'][set_id]['markers'][point_id]
        self.temp_properties = {
            'set_id': set_id,
            'marker_id': point_id,
            'type': 'markers',
            'properties': marker.copy()  # 현재 속성값 복사
        }
        
        # ID
        self.properties_layout.addRow('ID:', QLabel(point_id))
        
        # Label
        label_edit = QLineEdit(marker['label'])
        label_edit.textChanged.connect(
            lambda text: self.temp_properties['properties'].update({'label': text}))
        self.properties_layout.addRow('Label:', label_edit)

        # World dropdown
        world_combo = QComboBox()
        world_combo.addItems(self.getWorldList())
        world_combo.setCurrentText(marker['world'])
        world_combo.currentTextChanged.connect(
            lambda text: self.temp_properties['properties'].update({'world': text}))
        self.properties_layout.addRow('World:', world_combo)

        # Set dropdown
        set_combo = QComboBox()
        set_combo.addItems(sorted(self.marker_data['sets'].keys()))
        set_combo.setCurrentText(set_id)
        set_combo.currentTextChanged.connect(
            lambda text: self.temp_properties.update({'new_set_id': text}))
        self.properties_layout.addRow('Set:', set_combo)
        
        # Coordinates
        for coord in ['x', 'y', 'z']:
            spin = QSpinBox()
            if coord in ['x', 'z']:
                spin.setRange(-29999984, 29999984)
            else:
                spin.setRange(-64, 319)
            spin.setValue(marker[coord])
            spin.valueChanged.connect(
                lambda val, c=coord: self.temp_properties['properties'].update({c: val}))
            self.properties_layout.addRow(f'{coord.upper()}:', spin)
        
        # Icon
        icon_combo = QComboBox()
        
        icon_combo.addItems(self.default_icons)
        icon_combo.addItems(sorted(self.marker_data['icons'].keys()))
        icon_combo.setCurrentText(marker['icon'])
        icon_combo.currentTextChanged.connect(
            lambda text: self.temp_properties['properties'].update({'icon': text}))
        self.properties_layout.addRow('Icon:', icon_combo)

        # "속성 업데이트" 버튼 추가
        update_btn = QPushButton('Update Properties')
        update_btn.clicked.connect(lambda: self.applyProperties())
        self.properties_layout.addRow(update_btn)
        
        # Delete button
        delete_btn = QPushButton('Delete Marker')
        delete_btn.clicked.connect(
            lambda: self.deleteMarker(set_id, point_id, 'markers'))
        self.properties_layout.addRow(delete_btn)

        

    def setupLineProperties(self, set_id, line_id):
        line = self.marker_data['sets'][set_id]['lines'][line_id]
        self.temp_properties = {
            'set_id': set_id,
            'marker_id': line_id,
            'type': 'lines',
            'properties': line.copy()  # 현재 속성값 복사
        }
        
        # ID
        self.properties_layout.addRow('ID:', QLabel(line_id))
        
        # Label
        label_edit = QLineEdit(line['label'])
        label_edit.textChanged.connect(
            lambda text: self.temp_properties['properties'].update({'label': text}))
        self.properties_layout.addRow('Label:', label_edit)

        # World dropdown
        world_combo = QComboBox()
        world_combo.addItems(self.getWorldList())
        world_combo.setCurrentText(line['world'])
        world_combo.currentTextChanged.connect(
            lambda text: self.temp_properties['properties'].update({'world': text}))
        self.properties_layout.addRow('World:', world_combo)

        # Set dropdown
        set_combo = QComboBox()
        set_combo.addItems(sorted(self.marker_data['sets'].keys()))
        set_combo.setCurrentText(set_id)
        set_combo.currentTextChanged.connect(
            lambda text: self.temp_properties.update({'new_set_id': text}))
        self.properties_layout.addRow('Set:', set_combo)
        
        # Style properties
        color_btn = QPushButton('Change Color')
        color_btn.clicked.connect(lambda: self.selectColor('strokeColor'))
        self.properties_layout.addRow('Stroke Color:', color_btn)
        
        weight_spin = QSpinBox()
        weight_spin.setRange(1, 20)
        weight_spin.setValue(line['strokeWeight'])
        weight_spin.valueChanged.connect(
            lambda val: self.temp_properties['properties'].update({'strokeWeight': val}))
        self.properties_layout.addRow('Stroke Weight:', weight_spin)
        
        opacity_spin = QDoubleSpinBox()
        opacity_spin.setRange(0, 1)
        opacity_spin.setSingleStep(0.1)
        opacity_spin.setValue(line['strokeOpacity'])
        opacity_spin.valueChanged.connect(
            lambda val: self.temp_properties['properties'].update({'strokeOpacity': val}))
        self.properties_layout.addRow('Opacity:', opacity_spin)
        
        # Vertices list
        vertices_label = QLabel('Vertices:')
        vertices_list = QListWidget()
        for i in range(len(line['x'])):
            vertices_list.addItem(
                f"({line['x'][i]}, {line['y'][i]}, {line['z'][i]})")
        self.properties_layout.addRow(vertices_label, vertices_list)
        
        # Add vertex button
        add_vertex_btn = QPushButton('Add Vertex')
        add_vertex_btn.clicked.connect(
            lambda: self.startAddingVertex(set_id, line_id, 'lines'))
        self.properties_layout.addRow(add_vertex_btn)
        
        # Split line button
        split_btn = QPushButton('Split Line')
        split_btn.clicked.connect(
            lambda: self.splitLine(set_id, line_id))
        self.properties_layout.addRow(split_btn)

        # "속성 업데이트" 버튼 추가
        update_btn = QPushButton('Update Properties')
        update_btn.clicked.connect(self.applyProperties)
        self.properties_layout.addRow(update_btn)
        
        # Delete button
        delete_btn = QPushButton('Delete Line')
        delete_btn.clicked.connect(
            lambda: self.deleteMarker(set_id, line_id, 'lines'))
        self.properties_layout.addRow(delete_btn)


    def setupAreaProperties(self, set_id, area_id):
        area = self.marker_data['sets'][set_id]['areas'][area_id]
        self.temp_properties = {
            'set_id': set_id,
            'marker_id': area_id,
            'type': 'areas',
            'properties': area.copy()  # 현재 속성값 복사
        }
        
        # ID
        self.properties_layout.addRow('ID:', QLabel(area_id))
        
        # Label
        label_edit = QLineEdit(area['label'])
        label_edit.textChanged.connect(
            lambda text: self.temp_properties['properties'].update({'label': text}))
        self.properties_layout.addRow('Label:', label_edit)

        # World dropdown
        world_combo = QComboBox()
        world_combo.addItems(self.getWorldList())
        world_combo.setCurrentText(area['world'])
        world_combo.currentTextChanged.connect(
            lambda text: self.temp_properties['properties'].update({'world': text}))
        self.properties_layout.addRow('World:', world_combo)

        # Set dropdown
        set_combo = QComboBox()
        set_combo.addItems(sorted(self.marker_data['sets'].keys()))
        set_combo.setCurrentText(set_id)
        set_combo.currentTextChanged.connect(
            lambda text: self.temp_properties.update({'new_set_id': text}))
        self.properties_layout.addRow('Set:', set_combo)
        
        # Style properties
        stroke_color_btn = QPushButton('Change Stroke Color')
        stroke_color_btn.clicked.connect(lambda: self.selectColor('strokeColor'))
        self.properties_layout.addRow('Stroke Color:', stroke_color_btn)
        
        fill_color_btn = QPushButton('Change Fill Color')
        fill_color_btn.clicked.connect(lambda: self.selectColor('fillColor'))
        self.properties_layout.addRow('Fill Color:', fill_color_btn)
        
        for prop in ['strokeWeight', 'strokeOpacity', 'fillOpacity']:
            spin = QDoubleSpinBox() if 'Opacity' in prop else QSpinBox()
            if 'Opacity' in prop:
                spin.setRange(0, 1)
                spin.setSingleStep(0.1)
            else:
                spin.setRange(1, 20)
            spin.setValue(area[prop])
            spin.valueChanged.connect(
                lambda val, p=prop: self.temp_properties['properties'].update({p: val}))
            self.properties_layout.addRow(prop + ':', spin)
            
        # Height range
        for prop in ['ytop', 'ybottom']:
            spin = QSpinBox()
            spin.setRange(-64, 319)
            spin.setValue(area[prop])
            spin.valueChanged.connect(
                lambda val, p=prop: self.temp_properties['properties'].update({p: val}))
            self.properties_layout.addRow(prop + ':', spin)
            
        # Vertices list
        vertices_label = QLabel('Vertices:')
        vertices_list = QListWidget()
        for i in range(len(area['x'])):
            vertices_list.addItem(
                f"({area['x'][i]}, {area['z'][i]})")
        self.properties_layout.addRow(vertices_label, vertices_list)
        
        # Add vertex button
        add_vertex_btn = QPushButton('Add Vertex')
        add_vertex_btn.clicked.connect(
            lambda: self.startAddingVertex(set_id, area_id, 'areas'))
        self.properties_layout.addRow(add_vertex_btn)

        # "속성 업데이트" 버튼 추가
        update_btn = QPushButton('Update Properties')
        update_btn.clicked.connect(self.applyProperties)
        self.properties_layout.addRow(update_btn)
        
        # Delete button
        delete_btn = QPushButton('Delete Area')
        delete_btn.clicked.connect(
            lambda: self.deleteMarker(set_id, area_id, 'areas'))
        self.properties_layout.addRow(delete_btn)

        

    def setupVertexProperties(self, set_id, marker_id, marker_type, vertex_index):
        base_type = 'lines' if marker_type == 'line_vertex' else 'areas'
        marker = self.marker_data['sets'][set_id][base_type][marker_id]

        self.temp_properties = {
            'set_id': set_id,
            'marker_id': marker_id,
            'vertex_index': vertex_index,
            'type': base_type,
            'properties': marker.copy()  # 현재 속성값 복사
        }

        def update_coord(val, c):
            self.temp_properties['properties'][c][vertex_index] = val
        
        # Vertex position
        for coord in ['x', 'y', 'z'] if base_type == 'lines' else ['x', 'z']:
            spin = QSpinBox()
            if coord in ['x', 'z']:
                spin.setRange(-29999984, 29999984)
            else:
                spin.setRange(-64, 319)
            spin.setValue(marker[coord][vertex_index])
            spin.valueChanged.connect(
                lambda val, c=coord: update_coord(val, c)
            )
            self.properties_layout.addRow(f'{coord.upper()}:', spin)

        # "속성 업데이트" 버튼 추가
        update_btn = QPushButton('Update Properties')
        update_btn.clicked.connect(lambda: self.applyProperties())
        self.properties_layout.addRow(update_btn)
            
        # Delete vertex button
        delete_btn = QPushButton('Delete Vertex')
        delete_btn.clicked.connect(
            lambda: self.deleteVertex(set_id, marker_id, base_type, vertex_index))
        self.properties_layout.addRow(delete_btn)


    def selectColor(self, color_type):
        current_color = self.temp_properties['properties'].get(color_type, 0)
        color = QColorDialog.getColor(
            QColor.fromRgb(current_color),
            self,
            f'Select {color_type}'
        )
        if color.isValid():
            self.temp_properties['properties'][color_type] = color.rgb()


    def applyProperties(self):
        if not self.temp_properties:
            return
            
        set_id = self.temp_properties['set_id']
        marker_id = self.temp_properties['marker_id']
        marker_type = self.temp_properties['type']
        
        # 세트 변경 처리
        if 'new_set_id' in self.temp_properties and self.temp_properties['new_set_id'] != set_id:
            new_set_id = self.temp_properties['new_set_id']
            marker = self.temp_properties['properties']
            self.marker_data['sets'][new_set_id][marker_type][marker_id] = marker
            del self.marker_data['sets'][set_id][marker_type][marker_id]
            set_id = new_set_id
        else:
            # 정점 속성 업데이트
            if 'vertex_index' in self.temp_properties:
                vertex_index = self.temp_properties['vertex_index']

                for coord in ['x', 'y', 'z'] if self.temp_properties['type'] == 'lines' else ['x', 'z']:
                    if self.temp_properties['properties'][coord]:
                        print(self.marker_data['sets'][set_id][marker_type][marker_id]['x'])
                        self.marker_data['sets'][set_id][marker_type][marker_id][coord][vertex_index] = \
                            self.temp_properties['properties'][coord][vertex_index]
            # 일반 마커 속성 업데이트
            else:
                self.marker_data['sets'][set_id][marker_type][marker_id] = \
                    self.temp_properties['properties']
                
        
        if marker_type == 'markers':
            marker_item_type = 'point'
        elif marker_type == 'lines':
            marker_item_type = 'line'
        elif marker_type == 'areas':
            marker_item_type = 'area'
        
        if 'vertex_index' in self.temp_properties:
            if marker_item_type == 'line':
                current_selection = ('line_vertex', set_id, marker_id, self.temp_properties['vertex_index'])
            elif marker_item_type == 'area':
                current_selection = ('area_vertex', set_id, marker_id, self.temp_properties['vertex_index'])
        else:
            current_selection = (marker_item_type, set_id, marker_id)

        self.selected_item = current_selection

        print(f"Applying properties: {current_selection}")
        
        self.updateDisplay()

        QApplication.processEvents()
        
        # 선택 상태 복원
        for item in self.scene.items():
            if item.data(0) == current_selection:
                print("Restoring selection")
                item.setFlag(item.ItemIsSelectable)
                item.setSelected(True)
                break

    def updateVertexProperty(self, set_id, marker_id, marker_type, vertex_index, coord, value):
        # 속성 업데이트
        self.marker_data['sets'][set_id][marker_type][marker_id][coord][vertex_index] = value
        
        # 현재 선택된 아이템 저장
        current_selection = self.selected_item
        
        # 선택 상태 복원
        self.selected_item = current_selection
        
        # 선택된 아이템을 다시 시각적으로 강조
        for item in self.scene.items():
            if item.data(0) == current_selection:
                item.setSelected(True)
                break

    def changeMarkerColor(self, set_id, marker_id, marker_type, color_type='stroke'):
        marker = self.marker_data['sets'][set_id][marker_type][marker_id]
        prop = 'strokeColor' if color_type == 'stroke' else 'fillColor'
        
        color = QColorDialog.getColor(
            QColor.fromRgb(marker[prop]),
            self,
            f'Select {color_type} color'
        )
        
        if color.isValid():
            self.marker_data['sets'][set_id][marker_type][marker_id][prop] = color.rgb()
            self.updateDisplay()

    def deleteMarker(self, set_id, marker_id, marker_type):
        reply = QMessageBox.question(
            self,
            'Delete Marker',
            f'Are you sure you want to delete this {marker_type[:-1]}?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            del self.marker_data['sets'][set_id][marker_type][marker_id]
            self.selected_item = None
            self.updateDisplay()
            self.updatePropertiesPanel()

    def deleteVertex(self, set_id, marker_id, marker_type, vertex_index):
        marker = self.marker_data['sets'][set_id][marker_type][marker_id]
        
        # 최소 2개의 정점은 유지되어야 함
        if len(marker['x']) <= 2:
            QMessageBox.warning(
                self,
                'Cannot Delete Vertex',
                f'{marker_type[:-1].capitalize()} must have at least 2 vertices.'
            )
            return
            
        # 모든 좌표 리스트에서 해당 정점 제거
        coords = ['x', 'y', 'z'] if marker_type == 'lines' else ['x', 'z']
        for coord in coords:
            marker[coord].pop(vertex_index)
            
        self.selected_item = None
        self.updateDisplay()
        self.updatePropertiesPanel()

    def startAddingMarker(self, marker_type):
        self.adding_marker = {
            'type': marker_type,
            'points': []
        }
        
        msg = {
            'point': 'Click to place the point marker',
            'line': 'Click to place vertices. Right click to finish',
            'area': 'Click to place vertices. Right click to close the area'
        }[marker_type]
        
        self.statusBar().showMessage(msg)
        
    def startAddingVertex(self, set_id, marker_id, marker_type):
        self.adding_vertex = {
            'set_id': set_id,
            'marker_id': marker_id,
            'type': marker_type
        }
        
        self.statusBar().showMessage('Click to add new vertex')

    def mousePressEvent(self, event):
        if self.adding_marker:
            pos = self.view.mapToScene(self.view.mapFromGlobal(event.globalPos()))
            world_pos = self.screenToWorld(pos.x(), pos.y())

            world_pos = (round(world_pos[0]), round(world_pos[1]), round(world_pos[2]))
            
            self.adding_marker['points'].append(world_pos)

            if event.button() == Qt.LeftButton:
                if self.adding_marker['type'] == 'point':
                    self.finishAddingMarker()
            
            elif event.button() == Qt.RightButton:
                if len(self.adding_marker['points']) >= 2:
                    self.finishAddingMarker()
                    
        elif self.adding_vertex:
            pos = self.view.mapToScene(self.view.mapFromGlobal(event.globalPos()))
            world_pos = self.screenToWorld(pos.x(), pos.y())
            
            if event.button() == Qt.LeftButton:
                self.addVertex(world_pos)
                self.adding_vertex = None
                self.statusBar().clearMessage()
                
        else:
            super().mousePressEvent(event)

    def finishAddingMarker(self):
        if not self.adding_marker['points']:
            self.adding_marker = None
            self.statusBar().clearMessage()
            return
        
        # print point coords
        for i, point in enumerate(self.adding_marker['points']):
            print(f'Point {i + 1}: {point}')
            
        # 현재 선택된 world와 set 가져오기
        selected_world = self.world_combo.currentText()
        selected_set = self.set_combo.currentText()

        # 새로운 마커 ID 생성
        marker_id = self.generateUniqueId()
        
        # 기본 마커 데이터 생성
        if self.adding_marker['type'] == 'point':
            marker_id = "marker_" + marker_id
            x, y, z = self.adding_marker['points'][0]
            marker_data = {
                'world': selected_world,  # 선택된 world 사용
                'x': x,
                'y': y,
                'z': z,
                'icon': 'default',
                'label': f'New Point {marker_id}'
            }
            marker_type = 'markers'
            
        elif self.adding_marker['type'] == 'line':
            marker_id = "line_" + marker_id
            points = self.adding_marker['points']
            marker_data = {
                'world': selected_world,  # 선택된 world 사용
                'x': [p[0] for p in points],
                'y': [p[1] for p in points],
                'z': [p[2] for p in points],
                'strokeWeight': 2,
                'strokeColor': 0x000000,
                'strokeOpacity': 1.0,
                'label': f'New Line {marker_id}'
            }
            marker_type = 'lines'
            
        else:  # area
            marker_id = "area_" + marker_id
            points = self.adding_marker['points']
            marker_data = {
                'world': selected_world,  # 선택된 world 사용
                'x': [p[0] for p in points],
                'z': [p[2] for p in points],
                'ytop': 70,
                'ybottom': 65,
                'strokeWeight': 2,
                'strokeColor': 0x000000,
                'strokeOpacity': 1.0,
                'fillColor': 0x0000FF,
                'fillOpacity': 0.3,
                'label': f'New Area {marker_id}'
            }
            marker_type = 'areas'
            
        # 첫 번째 세트에 마커 추가
        self.marker_data['sets'][selected_set][marker_type][marker_id] = marker_data

        print(f'Added new {self.adding_marker["type"]}: {marker_id}')
        
        self.adding_marker = None
        self.statusBar().clearMessage()
        self.updateDisplay()

    def addVertex(self, world_pos):
        marker = self.marker_data['sets'][self.adding_vertex['set_id']][
            self.adding_vertex['type']][self.adding_vertex['marker_id']]
        
        if self.adding_vertex['type'] == 'lines':
            # 소수점 첫째 자리에서 반올림
            marker['x'].append(world_pos[0])
            marker['y'].append(world_pos[1])
            marker['z'].append(world_pos[2])
        else:  # areas
            marker['x'].append(world_pos[0])
            marker['z'].append(world_pos[2])
            
        self.updateDisplay()

    def splitLine(self, set_id, line_id):
        line = self.marker_data['sets'][set_id]['lines'][line_id]
        if len(line['x']) < 3:
            QMessageBox.warning(
                self,
                'Cannot Split Line',
                'Line must have at least 3 vertices to split.'
            )
            return
            
        # Split point selection dialog
        dialog = QDialog(self)
        dialog.setWindowTitle('Split Line')
        layout = QVBoxLayout(dialog)
        
        label = QLabel('Select vertex to split at:')
        layout.addWidget(label)
        
        vertex_list = QListWidget()
        for i in range(1, len(line['x']) - 1):  # Skip first and last vertices
            vertex_list.addItem(
                f"Vertex {i}: ({line['x'][i]}, {line['y'][i]}, {line['z'][i]})")
        layout.addWidget(vertex_list)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            dialog
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec_() == QDialog.Accepted and vertex_list.currentRow() != -1:
            split_index = vertex_list.currentRow() + 1
            new_line_id = self.generateUniqueId()
            
            # Create new line with vertices after split point
            new_line = {
                'world': line['world'],
                'x': line['x'][split_index:],
                'y': line['y'][split_index:],
                'z': line['z'][split_index:],
                'strokeWeight': line['strokeWeight'],
                'strokeColor': line['strokeColor'],
                'strokeOpacity': line['strokeOpacity'],
                'label': f"{line['label']} (split)"
            }
            
            # Truncate original line
            line['x'] = line['x'][:split_index + 1]
            line['y'] = line['y'][:split_index + 1]
            line['z'] = line['z'][:split_index + 1]
            
            # Add new line to set
            self.marker_data['sets'][set_id]['lines'][new_line_id] = new_line
            self.updateDisplay()

    def generateUniqueId(self):
        return f'{uuid.uuid4().hex[:8]}'

if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = MarkerEditor()
    editor.show()
    sys.exit(app.exec_())