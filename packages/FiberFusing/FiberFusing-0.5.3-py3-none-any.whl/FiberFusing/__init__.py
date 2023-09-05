from .geometry import Geometry
from .buffer import Circle
from .background import BackGround
from .instances.Fused1 import Fused1
from .instances.Fused2 import Fused2
from .instances.Fused3 import Fused3
from .instances.Fused4 import Fused4
from .instances.Fused5 import Fused5
from .instances.Fused6 import Fused6
from .instances.Fused7 import Fused7
from .instances.Fused10 import Fused10
from .instances.Fused12 import Fused12
from .instances.Fused19 import Fused19
from .instances.scaling_photonic_lantern_10 import FusedScalingPhotonicLantern10
from .instances.mode_groupe_pl_6 import FusedModeGroupePhotonicLantern6

import numpy

micro = 1e-6


class OpticalStructure():
    def __init__(self, exterior_structure=None, **kwargs):
        self.from_graded = False
        self.from_index = False
        self.from_NA = False
        self.exterior_structure = exterior_structure
        for key, value in kwargs.items():
            setattr(self, key, value)

        if self.from_NA:
            self.compute_index_from_NA()

    def compute_index_from_NA(self):
        self.index = numpy.sqrt(self.NA**2 + self.exterior_structure.index**2)

    def get_V_number(self, wavelength) -> float:
        delta_index = numpy.sqrt(self.index**2 - self.exterior_structure.index**2)

        V = 2 * numpy.pi / wavelength * delta_index * self.radius

        return V


# -
