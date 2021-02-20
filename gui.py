import sys
import enum

from direct.showbase.ShowBase import ShowBase 
from direct.gui.DirectGui import DirectFrame
from direct.showbase.DirectObject import DirectObject


class Aspect:
    def __init__(self, units):
        self.units = units


class Axis:
    def __init__(self, units):
        self.units = units


class Style(enum.Enum):
    SIZE = 1
    COLOR = 2
    RATIOSPLIT = 3
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


class TCFrame:
    def __init__(self, style):
        self.r = DirectFrame(
            frameColor=style[Style.COLOR],
            text="foo",
            text_scale=style[Style.TEXTSCALE],
        )

    def resize(self, size):
        self.r['frameSize'] = size
        left, right, bottom, top = size
        center_rl, center_bt = (left + right) / 2.0, (top + bottom) / 2.0
        self.r['text_pos'] = (center_rl, center_bt)


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
        Style.RATIOSPLIT: 0.7,
    }
    style_sub_frame = {
        Style.RATIOSPLIT: 0.4,
    }
    all_actual_frames = {
        Style.TEXTSCALE: 0.1,
    }
    style_red = {
        Style.COLOR: (1,0,0,1),
        **all_actual_frames,
    }
    style_green = {
        Style.COLOR: (0,1,0,1),
        **all_actual_frames,
    }
    style_blue = {
        Style.COLOR: (0,0,1,1),
        **all_actual_frames,
    }

    gui = TCGUI(style_gui,
        TCVerticalSplitFrame(style_main_frame,
            TCFrame(style_red),
            TCHorizontalSplitFrame(style_sub_frame,
                TCFrame(style_green),
                TCFrame(style_blue),
            ),
        ),
    )

    base.run()


if __name__== '__main__':
    main()
