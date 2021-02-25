import enum

from direct.gui.DirectGui import DirectFrame
from direct.showbase.DirectObject import DirectObject

from panda3d.core import CardMaker
from panda3d.core import NodePath
from panda3d.core import Camera
from panda3d.core import SamplerState


class Aspects:
    def __init__(self, units):
        self.units = units


class Units:
    def __init__(self, units):
        self.units = units


class Renderers(enum.Enum):
    DIRECTGUI = 1


class Style(enum.Enum):
    SIZE = 1
    RENDERER = 2
    RENDERSTYLE = 3
    RATIOSPLIT = 101
    NODEPATHSIZE = 200
    RESOLUTION = 500
    CAMERA_POSITION = 501
    NEAREST = 502
    BACKGROUND_COLOR = 503


class DirectGuiStyle(enum.Enum):
    COLOR = 2
    TEXTSCALE = 100


class TCGUI(DirectObject):
    def __init__(self, style, frame):
        super().__init__()
        self.style = style
        self.frame = frame
        self.accept('aspectRatioChanged', self.trigger_resize)

    def set_style(self, style):
        self.style = style
        self.trigger_resize()

    def trigger_resize(self):
        rel_size = list(self.style[Style.SIZE])
        left, _, bottom = base.aspect2d.find('a2dBottomLeft').get_pos()
        right, _, top = base.aspect2d.find('a2dTopRight').get_pos()
        aspects = [left, right, bottom, top]
        size = []
        for s, a in zip(rel_size, aspects):
            if isinstance(s, Units):
                size.append(s.units)
            elif isinstance(s, Aspects):
                size.append(s.units * abs(a))
            else:
                raise Exception(
                    "Specify GUI size using Units and Aspects"
                )
        self.resize(size)

    def resize(self, size):
        self.frame.resize(size)


class TCDemoFrame:
    def __init__(self, style):
        self.style = style
        if self.style[Style.RENDERER] == Renderers.DIRECTGUI:
            self.setup_direct_gui(style)

    def resize(self, size):
        if self.style[Style.RENDERER] == Renderers.DIRECTGUI:
            self.resize_direct_gui(size)

    def setup_direct_gui(self, style):
            direct_gui_style = style[Style.RENDERSTYLE]
            self.r = DirectFrame(
                frameColor=direct_gui_style[DirectGuiStyle.COLOR],
                text="foo",
                text_scale=direct_gui_style[DirectGuiStyle.TEXTSCALE],
            )

    def resize_direct_gui(self, size):
        self.r['frameSize'] = size
        left, right, bottom, top = size
        center_rl, center_bt = (left + right) / 2.0, (top + bottom) / 2.0
        self.r['text_pos'] = (center_rl, center_bt)


class TCNodePathFrame:
    def __init__(self, style, node):
        self.node = node
        self.node.reparent_to(base.aspect2d)
        self.node_size = style[Style.NODEPATHSIZE]

    def resize(self, size):
        frame_left, frame_right, frame_bottom, frame_top = size
        frame_width = frame_right - frame_left
        frame_height = frame_top - frame_bottom
        frame_aspect = frame_width / frame_height

        node_left, node_right, node_bottom, node_top = self.node_size
        node_width = node_right - node_left
        node_height = node_top - node_bottom
        node_aspect = node_width / node_height

        if frame_aspect >= node_aspect: # Vertical axis matching
            target_height = frame_height
            target_width = target_height * node_aspect
            target_horizontal_padding = (frame_width - target_width) / 2.0
            target_vertical_padding = 0.0
        else: # Horizontal axis matching
            target_width = frame_width
            target_height = target_width / node_aspect
            target_horizontal_padding = 0.0
            target_vertical_padding = (frame_height - target_height) / 2.0

        scale_node_to_target = target_width / node_width
        self.node.set_pos(
            frame_left + target_horizontal_padding - node_left * scale_node_to_target,
            0,
            frame_top - target_vertical_padding - node_top * scale_node_to_target,
        )
        self.node.set_scale(scale_node_to_target)


class TCRenderToTextureFrame():
    '''
        Style needs:
            Vec2 RESOLUTION 
            bool NEAREST
            Vec3 CAMERA_POSITION
        Optional:
            Vec4 BACKGROUND_COLOR 
    '''
    def __init__(self, style, node):
        self.node = node
        self.style = style
        cardmaker = CardMaker("card")
        cardmaker.set_frame(0,1,-1,0)
        res_x, res_y= self.style[Style.RESOLUTION]
        buffer = base.win.make_texture_buffer("", res_x, res_y)
        buffer.set_sort(-100)
        texture = buffer.get_texture()
        if self.style[Style.NEAREST]:
            texture.set_magfilter(SamplerState.FT_nearest)
            texture.set_minfilter(SamplerState.FT_nearest)
        if Style.BACKGROUND_COLOR in self.style:
            buffer.set_clear_color_active(True)
            buffer.set_clear_color(self.style[Style.BACKGROUND_COLOR])
        self.camera = base.make_camera(buffer)
        self.camera.reparent_to(self.node)
        pos = self.style[Style.CAMERA_POSITION]
        self.camera.set_pos(pos)
        self.camera.look_at(0,0,0)
        self.card = base.aspect2d.attach_new_node(cardmaker.generate())
        self.card.set_texture(texture)

    def resize(self, size):
        frame_left, frame_right, frame_bottom, frame_top = size
        frame_width = frame_right - frame_left
        frame_height = frame_top - frame_bottom
        self.card.set_pos(frame_left, 0, frame_top)
        self.card.set_scale(frame_width, 0, frame_height)
                

class TCDisplayRegionFrame():
    def __init__(self, style, node):
        self.node = node
        self.style = style
        self.display_region = base.win.make_display_region()
        self.camera = self.node.attach_new_node(Camera(""))
        self.display_region.set_camera(self.camera)
        pos = self.style[Style.CAMERA_POSITION]
        self.camera.set_pos(pos)
        self.camera.look_at(0,0,0)

    def resize(self, size):
        size = list(size)
        for v, value in enumerate(size):
            size[v] = (value+1)/2
        l, r, u, d = size
        self.display_region.set_dimensions((l,r,u,d))


class TCVerticalSplitFrame:
    def __init__(self, style, left_frame, right_frame):
        self.style = style
        self.left_frame = left_frame
        self.right_frame = right_frame

    def resize(self, size):
        split = self.style[Style.RATIOSPLIT]
        left, right, bottom, top = size
        split_pos = left + split * (right - left)
        self.left_frame.resize((left, split_pos, bottom, top))
        self.right_frame.resize((split_pos, right, bottom, top))


class TCHorizontalSplitFrame:
    def __init__(self, style, upper_frame, lower_frame):
        self.style = style
        self.upper_frame = upper_frame
        self.lower_frame = lower_frame

    def resize(self, size):
        split = self.style[Style.RATIOSPLIT]
        left, right, bottom, top = size
        split_pos = top - split * (top - bottom)
        self.upper_frame.resize((left, right, split_pos, top))
        self.lower_frame.resize((left, right, bottom, split_pos))


class TCFloatingFrame:
    def __init__(self, style, *sizes_and_subframes):
        self.style = style
        self.sizes = [size for size, subframe in sizes_and_subframes]
        self.frames = [subframe for size, subframe in sizes_and_subframes]

    def resize(self, size):
        left, right, bottom, top = size
        width, height = right - left, top - bottom

        for frame_size, frame in zip(self.sizes, self.frames):
            # These are fractions of 0 to 1, relative to the floating
            # frame's size
            f_left, f_right, f_bottom, f_top = frame_size
            target_size = (
                left +  width * f_left,
                left +  width * f_right,
                top - height * f_top,
                top - height * f_bottom,
            )
            frame.resize(target_size)
