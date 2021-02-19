import math
import random

from panda3d.core import Vec2
from panda3d.core import Vec3
from panda3d.core import Vec4


class CompEnv:
    def __init__(self, funcs, values=None, outputs=None):
        self.funcs = funcs
        if values is None:
            values = {}
        self.values = values
        if outputs is None:
            outputs = funcs.keys()
        self.outputs = outputs

    def reset(self):
        self.values = {}
        for func in self.funcs.values():
            func.reset()

    def set_value(self, name, value):
        self.values[name] = value

    def compute(self):
        for func in self.funcs.values():
            inputs = func.get_inputs()
            for input_node in inputs:
                input_name = input_node.input_name
                if input_name in self.values:
                    input_node.value = self.values[input_name]
        for name, func in self.funcs.items():
            self.set_value(name, func())


class Constant:
    def __init__(self, value):
        self.value = value

    def get_inputs(self):
        pass

    def reset(self):
        pass

    def __call__(self):
        return self.value


class GraphInput:
    def __init__(self, input_name):
        self.input_name = input_name
        self.value = None

    def get_inputs(self):
        return {self, }

    def reset(self):
        self.value = None

    def __call__(self):
        return self.value


class FuncNode:
    def __init__(self, *inputs):
        self.inputs = inputs

    def get_inputs(self):
        inputs = set()
        for i in self.inputs:
            ni = i.get_inputs()
            if ni is not None:
                inputs.update(ni)
        return inputs

    def reset(self):
        for input_node in self.inputs:
            input_node.reset()

    def __call__(self):
        return NotImplementedError


class Connect(FuncNode):
    def __init__(self, connectivity, *inputs):
        self.connectivity = connectivity
        self.inputs = inputs
        if len(connectivity) == 1:
            self.dtype_out = float
        elif len(connectivity) == 2:
            self.dtype_out = Vec2
        elif len(connectivity) == 3:
            self.dtype_out = Vec3
        elif len(connectivity) == 4:
            self.dtype_out = Vec4
        else:
            raise Exception("Don't know how to deal with the data.")
        

    def __call__(self):
        values = [input_node() for input_node in self.inputs]
        swizzled = []
        for node, slot in self.connectivity:
            node_result = values[node]
            if isinstance(node_result, (int, float)):
                assert slot == 0
                swizzled.append(node_result)
            elif isinstance(node_result, (Vec2, Vec3, Vec4)):
                if slot == 0:
                    swizzled.append(node_result.x)
                elif slot == 1:
                    swizzled.append(node_result.y)
                elif slot == 2:
                    swizzled.append(node_result.z)
                elif slot == 3:
                    swizzled.append(node_result.w)
                else:
                    raise Exception
            else:
                raise Exception

        if issubclass(self.dtype_out, (int, float)):
            return swizzled[0]
        elif issubclass(self.dtype_out, (Vec2, Vec3, Vec4)):
            return self.dtype_out(*swizzled)
        else:
            raise Exception


class PolarY(FuncNode):
    dtype_out = Vec3

    def __call__(self):
        coord = self.inputs[0]()
        x = math.sin(2 * math.pi * coord.x) * coord.z
        y = coord.y
        z = math.cos(2 * math.pi * coord.x) * coord.z
        return Vec3(x, y, z)


class RandomNoise(FuncNode):
    dtype_out = float

    def __init__(self, *inputs):
        self.inputs = inputs
        self.samples = {}

    def __call__(self):
        sample_coord = self.inputs[0]()
        if sample_coord in self.samples:
            return self.samples[sample_coord]
        value = random.random()
        self.samples[sample_coord] = value
        return value


class Blend(FuncNode):
    dtype_out = float

    def __init__(self, segments, *inputs):
        self.segments = segments
        self.inputs = inputs

    def __call__(self):
        value = self.inputs[0]()
        lower_bound = 0.0
        upper_bound = 1.0

        for bound in self.segments:
            if bound <= value:
                lower_bound = bound
            if bound > value:
                upper_bound = bound
                break
        func = self.segments[lower_bound]
        ratio = (value - lower_bound) / (upper_bound - lower_bound)
        blended_value = func(ratio)
        return blended_value
