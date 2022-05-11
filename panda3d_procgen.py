import sys

from direct.showbase.ShowBase import ShowBase 

import samplers
import blend

from comp_env import CompEnv
from comp_env import Constant
from comp_env import RandomNoise
from comp_env import PolarY
from comp_env import GraphInput
from comp_env import Connect
from comp_env import Blend
from comp_env import Multiply


def make_demo_tree():
    heightmap = RandomNoise(
        Connect(
            ((0, 0), (0, 1)),
            GraphInput('xy'),
        ),
    )

    # Terrain
    unit_square = Connect(
        ((0, 0), (1, 0), (2, 0)),
        Multiply(  # x * 128
            Constant(32),
            Connect(
                ((0, 0), ),
                GraphInput('xy'),
            ),
        ),
        Multiply(  # y * 128
            Constant(32),
            Connect(
                ((0, 1), ),
                GraphInput('xy'),
            ),
        ),
        Blend({0.0: blend.Linear(0.0, 0.5)}, heightmap),
        #Constant(0),
    )

    grass_color = Connect(
        ((0, 0), (1, 0), (2, 0), (3, 0)),
        Blend({0.0: blend.Linear(0.6, 0.0)}, heightmap),
        Blend({0.0: blend.Linear(0.7, 1.0)}, heightmap),
        Blend({0.0: blend.Linear(0.0, 0.0)}, heightmap),
        Constant(1),
    )

    # Tree
    bark = Blend(
        {0.0: blend.Linear(0.15, 1.0)},
        heightmap,
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
            Multiply(
                bark,
                tree_radius,
            ),
        ),
    )

    bark_color = Connect(
        ((2, 0), (3, 0), (0, 0), (1, 0)),
        Constant(0),
        Constant(1),
        heightmap,
        Blend({0.0: blend.Linear(1, 0)}, heightmap),
    )
  
    comp_env = CompEnv(
        dict(
            vertex=unit_square,#bark_shape,
            color=grass_color,#bark_color,
        ),
        outputs=['vertex', 'color'],
    )
    return comp_env


def make_surface(comp_env):
    samples_x, samples_y = 8, 8

    sampler = samplers.GridSquareSampler(comp_env)
    surface = sampler.sample(
        (samples_x, samples_y),
        #wrap_x=True,
        #two_sided=True,
    )
    return surface


def main():
    ShowBase()
    base.accept('escape', sys.exit)
    base.disable_mouse()
    base.cam.set_pos(0.5, -2.5, 0.5)
    base.cam.look_at(0.5, 0, 0.5)
    base.set_frame_rate_meter(True)

    demo_tree_env = make_demo_tree()
    demo_tree = make_surface(demo_tree_env)
    obj = base.render.attach_new_node(demo_tree)
    obj.write_bam_file('output.bam')

    obj.set_pos(0.5, 0, 0)
    obj.set_p(90)

    def rotate_tree(task):
        obj.set_h(obj.get_h() + globalClock.dt * 15)
        return task.cont
    base.taskMgr.add(rotate_tree)

    base.run()


if __name__== '__main__':
    main()
