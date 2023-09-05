from typing import Any, Dict, TextIO, Type, Union
from bloqade.builder.base import Builder
from bloqade.codegen.common.json import BloqadeIRSerializer, BloqadeIRDeserializer
from bloqade.builder.start import ProgramStart
from bloqade.builder.sequence_builder import SequenceBuilder

# from bloqade.builder.base import Builder
from bloqade.builder.backend.bloqade import BloqadeDeviceRoute, BloqadeService
from bloqade.builder.backend.braket import BraketDeviceRoute, BraketService
from bloqade.builder.backend.quera import QuEraDeviceRoute, QuEraService
from bloqade.builder.spatial import Location, Scale, Var, Uniform
from bloqade.builder.waveform import (
    Linear,
    Constant,
    Poly,
    Fn,
    Apply,
    Slice,
    Record,
    Sample,
    PiecewiseLinear,
    PiecewiseConstant,
)
from bloqade.builder.field import Detuning, Rabi, RabiAmplitude, RabiPhase
from bloqade.builder.coupling import Rydberg, Hyperfine
from bloqade.builder.parallelize import Parallelize, ParallelizeFlatten
from bloqade.builder.assign import Assign, BatchAssign
from bloqade.builder.flatten import Flatten


class BuilderSerializer(BloqadeIRSerializer):
    def default(self, obj):
        def camel_to_snake(name: str) -> str:
            return "".join("_" + c.lower() if c.isupper() else c for c in name).lstrip(
                "_"
            )

        if isinstance(obj, ProgramStart) and type(obj) is ProgramStart:
            return "program_start"

        match obj:
            case BraketDeviceRoute(parent) | QuEraDeviceRoute(
                parent
            ) | BloqadeDeviceRoute(parent) | BraketService(parent) | QuEraService(
                parent
            ) | BloqadeService(
                parent
            ):
                return {camel_to_snake(obj.__class__.__name__): {"parent": parent}}
            case Parallelize(cluster_spacing, parent):
                return {
                    "parallelize": {"cluster_spacing": cluster_spacing},
                    "parent": parent,
                }
            case ParallelizeFlatten(cluster_spacing, parent):
                return {
                    "parallelize_flatten": {"cluster_spacing": cluster_spacing},
                    "parent": parent,
                }
            case SequenceBuilder(sequence, parent):
                return {
                    "sequence_builder": {
                        "sequence": self.default(sequence),
                        "parent": self.default(parent),
                    }
                }
            case Assign(assignments, parent) | BatchAssign(assignments, parent):
                return {
                    camel_to_snake(obj.__class__.__name__): {
                        "assignments": assignments,
                        "parent": parent,
                    }
                }
            case Flatten(order, parent):
                return {"flatten": {"order": order, "parent": parent}}
            case Constant(value, duration, parent):
                return {
                    "constant": {
                        "value": value,
                        "duration": duration,
                        "parent": parent,
                    }
                }
            case Linear(start, stop, duration, parent):
                return {
                    "linear": {
                        "start": start,
                        "stop": stop,
                        "duration": duration,
                        "parent": parent,
                    }
                }
            case Poly(coeffs, duration, parent):
                return {
                    "poly": {
                        "coeffs": coeffs,
                        "duration": duration,
                        "parent": parent,
                    }
                }
            case Fn():
                raise ValueError(
                    "Bloqade does not support serialization of Python code."
                )
            case Apply(wf, parent):
                return {"apply": {"wf": wf, "parent": parent}}
            case Slice(start, stop, parent):
                return {
                    "slice": {
                        "start": start,
                        "stop": stop,
                        "parent": parent,
                    }
                }
            case Record(name, parent):
                return {
                    "record": {
                        "name": name,
                        "parent": parent,
                    }
                }
            case Sample(dt, interpolation, parent):
                return {
                    "sample": {
                        "dt": dt,
                        "interpolation": interpolation,
                        "parent": parent,
                    }
                }
            case PiecewiseLinear(durations, values, parent):
                return {
                    "piecewise_linear": {
                        "durations": durations,
                        "values": values,
                        "parent": parent,
                    }
                }
            case PiecewiseConstant(durations, values, parent):
                return {
                    "piecewise_constant": {
                        "durations": durations,
                        "values": values,
                        "parent": parent,
                    }
                }
            case Location(label, parent):
                return {
                    "location": {
                        "label": label,
                        "parent": parent,
                    }
                }
            case Scale(value, parent):
                return {
                    "scale": {
                        "value": value,
                        "parent": parent,
                    }
                }
            case Var(name, parent):
                return {"Var": {"name": name, "parent": parent}}
            case Uniform(parent):
                return {"uniform": {"parent": parent}}
            case Detuning(parent) | RabiAmplitude(parent) | RabiPhase(parent) | Rabi(
                parent
            ) | Hyperfine(parent) | Rydberg(parent) | BraketDeviceRoute(
                parent
            ) | QuEraDeviceRoute(
                parent
            ) | BloqadeDeviceRoute(
                parent
            ) | BraketService(
                parent
            ) | QuEraService(
                parent
            ) | BloqadeService(
                parent
            ):
                return {camel_to_snake(obj.__class__.__name__): {"parent": parent}}
            case _:
                return super().default(obj)


class BuilderDeserializer(BloqadeIRDeserializer):
    methods: Dict[str, Type] = {
        "rydberg": Rydberg,
        "hyperfine": Hyperfine,
        "detuning": Detuning,
        "rabi": Rabi,
        "rabi_amplitude": RabiAmplitude,
        "rabi_phase": RabiPhase,
        "var": Var,
        "scale": Scale,
        "location": Location,
        "uniform": Uniform,
        "piecewise_constant": PiecewiseConstant,
        "piecewise_linear": PiecewiseLinear,
        "sample": Sample,
        "record": Record,
        "slice": Slice,
        "apply": Apply,
        "poly": Poly,
        "linear": Linear,
        "constant": Constant,
        "flatten": Flatten,
        "parallelize": Parallelize,
        "parallelize_flatten": ParallelizeFlatten,
        "sequence_builder": SequenceBuilder,
        "assign": Assign,
        "batch_assign": BatchAssign,
        "bloqade_device_route": BloqadeDeviceRoute,
        "bloqade_service": BloqadeService,
        "braket_device_route": BraketDeviceRoute,
        "braket_service": BraketService,
        "quera_device_route": QuEraDeviceRoute,
        "quera_service": QuEraService,
    }

    def object_hook(self, obj: Dict[str, Any]):
        match obj:
            case str("program_start"):
                return ProgramStart(None)
            case dict() if len(obj) == 1:
                ((head, options),) = obj.items()
                if head in self.methods:
                    return self.methods[head](**options)

        return super().object_hook(obj)


def load_program(filename_or_io: Union[str, TextIO]) -> Builder:
    import json

    if isinstance(filename_or_io, str):
        with open(filename_or_io, "r") as f:
            return json.load(f, object_hook=BuilderDeserializer().object_hook)
    else:
        return json.load(filename_or_io, object_hook=BuilderDeserializer().object_hook)


def save_program(filename_or_io: Union[str, TextIO], program: Builder) -> None:
    import json

    if isinstance(filename_or_io, str):
        with open(filename_or_io, "w") as f:
            json.dump(program, f, cls=BuilderSerializer)
    else:
        json.dump(program, filename_or_io, cls=BuilderSerializer)
