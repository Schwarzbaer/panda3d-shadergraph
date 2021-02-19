import sys

from direct.showbase.ShowBase import ShowBase 

import samplers


# import basic
# import transform
# import blend

# heightmap = basic.random_value()
# 
# flat_bark = transform.band(0.95, 1, heightmap)
# # tree_radius = blend.linear(0.3, 0.1, basic.y)
# tree_radius = blend.segmented(
#     {
#         0.0: blend.Linear(0.1, 0.1),
#         0.3: blend.Linear(0.1, 0.5),
#         0.7: blend.Linear(0.5, 0.1),
#     },
#     basic.y,
# )
# bark_vertex = transform.polar_y(
#     basic.merge(
#         basic.xy,
#         transform.multiply(
#             flat_bark,
#             tree_radius,
#         ),
#     ),
# )


from comp_env import CompEnv
from comp_env import Constant
from comp_env import RandomNoise
from comp_env import PolarY
from comp_env import GraphInput
from comp_env import Connect
from comp_env import Blend

import blend


def make_surface():
    samples_x, samples_y = 128, 128

    heightmap = RandomNoise(
        Connect(
            ((0, 0), ),
            GraphInput('xy'),
        ),
    )

    high_plane = Connect(
        ((0, 0), (0, 1), (1, 0)),
        GraphInput('xy'),
        Constant(0.3),
    )

    tree_radius = Blend(
        {
            0.0: blend.Linear(0.1, 0.1),
            0.3: blend.Linear(0.1, 0.4, blend.Exponential(0.5)),
            0.7: blend.Linear(0.4, 0.0, blend.Exponential(2)),
        },
        Connect(
            ((0, 1), ),
            GraphInput('xy'),
        ),
    )

    bark_shape = PolarY(
        Connect(
            ((0, 0), (0, 1), (1, 0)),
            GraphInput('xy'),
            tree_radius,
        ),
    )

    rgba = Connect(
        ((0, 0), (0, 1), (1, 0), (2, 0)),
        GraphInput('xy'),
        heightmap,
        Constant(1),
    )

    bark_color = Connect(
        ((2, 0), (1, 0), (0, 0), (2, 0)),
        heightmap,
        Constant(0),
        Constant(1),
    )

    comp_env = CompEnv(
        dict(
            vertex=bark_shape,
            color=bark_color,
        ),
        outputs=['vertex', 'color'],
    )
    sampler = samplers.GridSquareSampler(comp_env)
    surface = sampler.sample(
        (samples_x, samples_y),
        wrap_x=True,
        two_sided=True,
    )
    return surface


def main():
    ShowBase()
    base.accept('escape', sys.exit)
    base.disable_mouse()
    base.cam.set_pos(0.5, -2.5, 0.5)
    base.cam.look_at(0.5, 0, 0.5)
    base.set_frame_rate_meter(True)

    obj = base.render.attach_new_node(make_surface())
    obj.set_pos(0.5, 0, 0)
    obj.set_p(90)
    base.run()


if __name__== '__main__':
    main()
