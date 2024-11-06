class MarkerItem:
    """Base class for all marker items"""
    def __init__(self, marker_id, world, label):
        self.id = marker_id
        self.world = world
        self.label = label
        
class PointMarker(MarkerItem):
    def __init__(self, marker_id, world, label, x, y, z, icon):
        super().__init__(marker_id, world, label)
        self.x = x
        self.y = y
        self.z = z
        self.icon = icon

class LineMarker(MarkerItem):
    def __init__(self, marker_id, world, label, points_xyz, stroke_weight, stroke_color, stroke_opacity):
        super().__init__(marker_id, world, label)
        self.points_xyz = points_xyz  # List of (x,y,z) tuples
        self.stroke_weight = stroke_weight
        self.stroke_color = stroke_color
        self.stroke_opacity = stroke_opacity

class AreaMarker(MarkerItem):
    def __init__(self, marker_id, world, label, points_xz, y_top, y_bottom,
                 stroke_weight, stroke_color, stroke_opacity,
                 fill_color, fill_opacity):
        super().__init__(marker_id, world, label)
        self.points_xz = points_xz  # List of (x,z) tuples
        self.y_top = y_top
        self.y_bottom = y_bottom
        self.stroke_weight = stroke_weight
        self.stroke_color = stroke_color
        self.stroke_opacity = stroke_opacity
        self.fill_color = fill_color
        self.fill_opacity = fill_opacity
