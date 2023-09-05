from dataclasses import dataclass

from jax import random as jrandom
from jwave.geometry import Domain

from .materials import Material, water


@dataclass(frozen=False)
class Settings:
    """This is a dataclass that contains the
    settings for the simulation. It is used to construct the domain
    and to set the random seed for the simulation.

    Attributes:
        random_seed (jrandom.PRNGKey): The random seed for the simulation.
            Defaults to [42](https://www.youtube.com/watch?v=aboZctrHfK8).
        ppw (int): The number of points per wavelength. This is used to
            estimate the size of the simulation. Defaults to 6.
        pml_size (int): The size of the perfectly matched layer. Defaults to 16.
        lateral_padding (float): The amount of padding to add to the lateral
            sides of the simulation. Defaults to 0.005
        axial_padding (float): The amount of padding to add to the axial
            sides of the simulation. Defaults to 0.005.
    """
    random_seed: jrandom.PRNGKey = 42
    ppw: int = 6
    pml_size: int = 16
    lateral_padding: float = 0.005
    axial_padding: float = 0.005

    def construct_domain(
        self,
        f0: float,
        lateral_size: float,            # e.g. lens diameter
        axial_size: float,              # e.g. lens thickness
        background: Material = water,
    ):
        """
        Args:
            f0 (float): The frequency of the acoustic field.
            lateral_size (float): The lateral size of the simulation.
            axial_size (float): The axial size of the simulation.
            background (Material, optional): The background material. It is
                used to estimate the size of the simulation from the `ppw`.

        Returns:
            Domain: The domain of the simulation.
        """
        # Construct dx from ppw
        dx = (background.sound_speed / f0) / self.ppw

        # Estimate the z size of the simulation
        z_size = axial_size + 2*self.axial_padding + 2*self.pml_size*dx

        # Estimate the x and y size of the simulation
        lateral_size = lateral_size + 2*self.lateral_padding + 2*self.pml_size*dx

        # Make them into grid points
        z_size = int(z_size / dx)
        lateral_size = int(lateral_size / dx)

        return Domain(
            N = (lateral_size, lateral_size, z_size),
            dx = (dx, dx, dx),
        )

    @property
    def seed(self):
        """Returns a new random seed and updates the random seed for the
        simulation.

        !!! example
            ```python
            settings = Settings()
            new_seed = settings.seed
            another_seed = settings.seed
            ```
        """
        key, seed = jrandom.split(self.random_seed)
        self.random_seed = key
        return seed
