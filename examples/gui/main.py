import sys

from direct.showbase.ShowBase import ShowBase 

from thecheapestgui.thecheapestgui import *
    

def main():
    ShowBase()
    base.accept('escape', sys.exit)
    base.disable_mouse()
    base.cam.set_pos(0.5, -2.5, 1.5)
    base.cam.look_at(0.5, 0.5, 0.5)
    base.set_frame_rate_meter(True)

    style_gui = {
        Style.SIZE: (Aspects(-1), Aspects(1), Units(-1), Units(1)),
    }
    style_main_frame = {
        Style.RATIOSPLIT: 0.3,
    }
    style_sub_frame = {
        Style.RATIOSPLIT: 0.8,
    }
    style_floating_frame = {}

    # DirectGUI-using demo frames
    demo_frames = {
        Style.RENDERER: Renderers.DIRECTGUI,
    }
    style_red = {
        Style.RENDERSTYLE: {
            DirectGuiStyle.COLOR: (1,0,0,1),
            DirectGuiStyle.TEXTSCALE: 0.1,
        },
        **demo_frames,
    }
    style_green = {
        Style.RENDERSTYLE: {
            DirectGuiStyle.COLOR: (0,1,0,1),
            DirectGuiStyle.TEXTSCALE: 0.1,
        },
        **demo_frames,
    }
    style_blue = {
        Style.RENDERSTYLE: {
            DirectGuiStyle.COLOR: (0,0,1,1),
            DirectGuiStyle.TEXTSCALE: 0.1,
        },
        **demo_frames,
    }

    # Frame that contains an arbitrary node path
    style_node = {
        Style.NODEPATHSIZE: (-1.2, 1.2, -1.2, 1.2),
    }
    rtt_style = {
        Style.RESOLUTION: (128, 128),
        Style.CAMERA_POSITION: (0,-10,0),
        Style.NEAREST: True,
    }

    gui = TCGUI(style_gui,
        TCVerticalSplitFrame(
            style_main_frame,
            TCDemoFrame(style_red),
            TCNodePathFrame(style_node, base.loader.load_model('models/smiley'))
        ),
    )
        #    TCFloatingFrame(
        #        style_floating_frame,
        #        ((0.1, 0.3, 0.3, 0.7), TCDirectGuiFrame(style_red)),
        #    ),
        #    TCDirectGuiFrame(style_red),
        #    TCHorizontalSplitFrame(
        #        style_sub_frame,
        #        TCDirectGuiFrame(style_green),
        #    ),
        #    TCHorizontalSplitFrame(style_main_frame,
        #        TCDisplayRegionFrame(rtt_style,
        #            base.loader.load_model('models/smiley')
        #        ),
        #    ),
    base.run()


if __name__== '__main__':
    main()
