import sys
import enum

from direct.showbase.ShowBase import ShowBase 
from direct.gui.DirectGui import DirectFrame
from direct.showbase.DirectObject import DirectObject

from panda3d.core import CardMaker
from panda3d.core import NodePath
from panda3d.core import SamplerState


class Aspect:
    def __init__(self, units):
        self.units = units


class Axis:
    def __init__(self, units):
        self.units = units


class Style(enum.Enum):
    SIZE = 1
    RATIOSPLIT = 3
    NODEPATHSIZE = 200
    RESOLUTION = 500
    CAMERA_POSITION = 501
    NEAREST = 502


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
        size = list(self.style[Style.SIZE])
        
        self.resize(self.style[Style.SIZE])

    def resize(self, size):
        self.frame.resize(size)


class TCDirectGuiFrame:
    def __init__(self, style, direct_gui_style):
        self.r = DirectFrame(
            frameColor=direct_gui_style[DirectGuiStyle.COLOR],
            text="foo",
            text_scale=direct_gui_style[DirectGuiStyle.TEXTSCALE],
        )

    def resize(self, size):
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
        self.camera = base.make_camera(buffer)
        self.camera.reparent_to(self.node)
        self.camera.look_at(0,0,0)
        pos = self.style[Style.CAMERA_POSITION]
        self.camera.set_pos(pos)
        self.card = base.aspect2d.attach_new_node(cardmaker.generate())
        self.card.set_texture(texture)

    def resize(self, size):
        frame_left, frame_right, frame_bottom, frame_top = size
        frame_width = frame_right - frame_left
        frame_height = frame_top - frame_bottom
        self.card.set_pos(frame_left, 0, frame_top)
        self.card.set_scale(frame_width, 0, frame_height)
                

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
        split = self.style[Style.RATIOSPLIT]
        left, right, bottom, top = size
        split_pos = top - split * (top - bottom)
        self.upper_frame.resize((left, right, split_pos, top))
        self.lower_frame.resize((left, right, bottom, split_pos))
    

def main():
    ShowBase()
    base.accept('escape', sys.exit)
    base.disable_mouse()
    base.cam.set_pos(0.5, -2.5, 1.5)
    base.cam.look_at(0.5, 0.5, 0.5)
    base.set_frame_rate_meter(True)

    style_gui = {
        #Style.SIZE: (Aspect(-1), Aspect(1), Aspect(-1), Aspect(1)),
        Style.SIZE: (-1, 1, -1, 1),
    }
    style_main_frame = {
        Style.RATIOSPLIT: 0.5,
    }
    style_sub_frame = {
        Style.RATIOSPLIT: 0.8,
    }
    style_floating_frame = {}

    text_frames = {
        DirectGuiStyle.TEXTSCALE: 0.1,
    }
    style_red = {
        DirectGuiStyle.COLOR: (1,0,0,1),
        **text_frames,
    }
    style_green = {
        DirectGuiStyle.COLOR: (0,1,0,1),
        **text_frames,
    }
    style_node = {
        Style.NODEPATHSIZE: (-1.2, 1.2, -1.2, 1.2),
    }
    rtt_style = {
        Style.RESOLUTION: (128, 128),
        Style.CAMERA_POSITION: (0,-10,0),
        Style.NEAREST: True,
    }

    gui = TCGUI(style_gui,
        TCVerticalSplitFrame(style_main_frame,
            #TCFloatingFrame(style_floating_frame,
            #    ((0.1, 0.3, 0.3, 0.7), TCDirectGuiFrame({}, style_red)),
            #),
            TCHorizontalSplitFrame(style_sub_frame,
                TCDirectGuiFrame({}, style_red),
                TCDirectGuiFrame({}, style_green),
            ),
            TCHorizontalSplitFrame(style_main_frame,
                TCNodePathFrame(style_node,
                    base.loader.load_model('models/smiley')
                ),
                TCRenderToTextureFrame(rtt_style,
                    base.loader.load_model('models/smiley')
                ),
            ),
        ),
    )
    base.run()


if __name__== '__main__':
    main()
