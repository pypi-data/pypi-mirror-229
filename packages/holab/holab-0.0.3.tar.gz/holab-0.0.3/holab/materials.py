from typing import Any

from jax.tree_util import register_pytree_node_class
from jwave.geometry import Domain, Medium

_vero_agiuls_paper = """@article{10.1121/10.0006668,
    author = {Bakaric, Marina and Miloro, Piero and Javaherian, Ashkan and Cox, Ben T. and Treeby, Bradley E. and Brown, Michael D.},
    title = "{Measurement of the ultrasound attenuation and dispersion in 3D-printed photopolymer materials from 1 to 3.5 MHz}",
    journal = {The Journal of the Acoustical Society of America},
    volume = {150},
    number = {4},
    pages = {2798-2805},
    year = {2021},
    month = {10},
    issn = {0001-4966},
    doi = {10.1121/10.0006668},
    url = {https://doi.org/10.1121/10.0006668},
}"""

@register_pytree_node_class
class Material:
    """The generic interface for representing an acoustic material. The material
    is defined by its sound speed, density and attenuation coefficient.

    Attributes:
        name (str): The name of the material.
        reference (str): The bibliographic reference for the measured values.
        sound_speed (float): The sound speed of the material.
        density (float): The density of the material.
        attenuation (float): The attenuation coefficient of the material.
    """
    name: str
    reference: str
    sound_speed: float
    density: float
    attenuation: float
    aux: Any

    def __init__(
        self,
        name: str,
        reference: str,
        sound_speed: float,
        density: float,
        attenuation: float,
        aux: Any = None
    ):
        self.name = name
        self.reference = reference
        self.sound_speed = sound_speed
        self.density = density
        self.attenuation = attenuation
        self.aux = aux

    def __repr__(self):
        return f"Material[{self.name}]: sound_speed={self.sound_speed}, density={self.density}, attenuation={self.attenuation}"

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        return (
            self.name == other.name
            and self.sound_speed == other.sound_speed
            and self.density == other.density
            and self.attenuation == other.attenuation
        )

    def tree_flatten(self):
        return (
            (self.sound_speed, self.density, self.attenuation),
            (self.name, self.reference, self.aux)
        )

    @classmethod
    def tree_unflatten(cls, aux_data, children):
        return cls(aux_data[0], aux_data[1], *children, aux=aux_data[2])

    def _citation(self):
        return self.reference

    def as_medium(self, domain: Domain, f0: float = 1.0) -> Medium:
        """Returns the material as a jwave Medium object.

        Args:
            domain (Domain): The domain of the medium.
            f0 (float): The frequency at which the material is used. This
                is because the attenuation coefficient is frequency-dependent, and
                jwave uses a y=2 attenuation model (Stokes attenuation), so we need
                to make sure that the attenuation coefficient is correctly scaled for
                the frequency of interest.

        Returns:
            Medium: The material as a jwave Medium object.
        """
        return Medium(
            domain=domain,
            sound_speed=self.sound_speed,
            density=self.density,
            attenuation=self.attenuation
        )

@register_pytree_node_class
class PowerLawAttenuation(Material):
    """A material with a power law attenuation coefficient.
    """
    def __init__(
        self,
        name: str,
        reference: str,
        sound_speed: float,
        density: float,
        attenuation: float,
        y: float,
    ):
        """Initialize a material with a power law attenuation coefficient.

        Args:
            name (str): The name of the material.
            reference (str): The bibliographic reference for the measured values.
            sound_speed (float): The sound speed of the material in $m/s$.
            density (float): The density of the material in $kg/m^3$.
            attenuation (float): The attenuation coefficient of the material in $dB/cm/MHz$.
            y (float): The exponent of the power law.
        """
        super().__init__(name, reference, sound_speed, density, attenuation)
        self.y = y

    def as_medium(self, domain: Domain, f0: float) -> Medium:
        # Correct the attenuation coefficient for the frequency
        attenuation = self.attenuation * (f0/1e6)**self.y
        squared_freq = (f0/1e6)**2
        attenuation = attenuation / squared_freq
        return Medium(
            domain=domain,
            sound_speed=self.sound_speed,
            density=self.density,
            attenuation=attenuation
        )

    def tree_flatten(self):
        return (
            (self.sound_speed, self.density, self.attenuation, self.y),
            (self.name, self.reference)
        )

    @classmethod
    def tree_unflatten(cls, aux_data, children):
        sos, density, attenuation, y = children
        name, reference = aux_data
        return cls(
            name=name,
            reference=reference,
            sound_speed=sos,
            density=density,
            attenuation=attenuation,
            y=y
        )


### Material library
agilus30 = PowerLawAttenuation(
    "Agilus30", _vero_agiuls_paper, 2034.9, 1180.0, 9.109, y=1.017)
"""Agilus30 material from Stratasys. The attenuation coefficient is measured from 1 to 3.5 MHz."""

veroclear = PowerLawAttenuation(
    "VeroClear", _vero_agiuls_paper, 2474.5,1128.0, 3.696, y=0.9958)
"""VeroClear material from Stratasys. The attenuation coefficient is measured from 1 to 3.5 MHz."""

water = Material("water", "", 1480.0, 1000.0, 0.0)
"""Water at 20°C. Note that the attenuation coefficient is 0."""
