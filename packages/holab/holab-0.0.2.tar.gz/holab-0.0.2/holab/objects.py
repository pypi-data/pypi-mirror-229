from typing import Callable, Union

from jax import numpy as jnp
from jax.nn import sigmoid
from jax.tree_util import register_pytree_node_class
from jaxdf.operators import compose
from jaxtyping import Num
from jwave import Continuous, FourierSeries
from jwave.geometry import Domain, Medium

from .materials import Material, agilus30, veroclear, water


# Constructors
def make_disk(
    domain: Domain,
    radius: float,
    z_pos: float,
    thickness: float,
):
    """Generates a homogeneous disk field, centered laterally

    Args:
        domain (Domain): The domain of the simulation
        radius (float): The radius of the disk
        z_pos (float): The axial position of the disk
        thickness (float): The thickness of the disk

    Returns:
        FourierSeries: The disk field as a binary map
    """
    # Coordinate field
    x = Continuous(None, domain, lambda p, x: x).on_grid
    x, y, z = x[...,0], x[...,1], x[...,2]
    mask = (z < z_pos + thickness)*(z>z_pos)*((x**2 + y**2) < radius**2)
    mask = jnp.expand_dims(mask, -1).astype(jnp.float32)
    return FourierSeries(mask, domain)

def make_thin_disk(
    domain: Domain,
    radius: float,
    z_pos: float,
) -> FourierSeries:
    """Generates a homogeneous disk field, centered laterally

    Args:
        domain (Domain): The domain of the simulation
        radius (float): The radius of the disk
        z_pos (float): The axial position of the disk

    Returns:
        FourierSeries: The disk field as a binary map
    """

      # Define source (just before lens)
    return make_disk(domain,radius,z_pos,1.1*domain.dx[2],)


# Physical objects

class PhysicalObject:
    """Base class for physical objects."""
    @property
    def as_medium(self):
        raise NotImplementedError("This method should be implemented by subclasses")


@register_pytree_node_class
class RawObject(PhysicalObject):
    """A physical object that is represented simply by a `Medium` object."""
    medium: Medium

    def __init__(self, medium: Medium):
        """
        Args:
            medium (Medium): The medium of the object.

        Returns:
            RawObject: The RawObject.
        """
        self.medium = medium

    def tree_flatten(self):
        return (self.medium,), ()

    @classmethod
    def tree_unflatten(cls, aux_data, children):
        return cls(*children)

    def as_medium(self, f0: float):
        """Returns the medium of the object. The input
        frequency is ignored.

        Args:
            f0 (float): The frequency at which the material is used. This
                is ignored but included for compatibility with other objects.

        Returns:
            Medium: The medium of the object.
        """
        return self.medium


@register_pytree_node_class
class Environment(PhysicalObject):
    """An homogeneous medium with a given material.
    """
    material: Material
    domain: Domain

    def __init__(
        self,
        domain: Domain,
        material: Material = water,
    ):
        """
        Args:
            domain (Domain): The domain of the environment.
            material (Material, optional): The material of the environment.

        Returns:
            Environment: The environment.
        """
        self.material = material
        self.domain = domain

    def tree_flatten(self):
        return (self.material, ), (self.domain,)

    @classmethod
    def tree_unflatten(cls, aux_data, children):
        return cls(children[1], children[0])

    def as_medium(self, f0: float):
        """Returns the material of the object as a `jwave` `Medium` object.

        Args:
            f0 (float): The frequency at which the material is used. This

        Returns:
            Medium: The material of the object.
        """
        return self.material.as_medium(self.domain, f0)


@register_pytree_node_class
class TwoMaterialsInterpolated(PhysicalObject):
    """An object whose properties are interpolated between two materials. Calling $m_1$ the first material, $m_2$ the second one, $\gamma$ the interpolation coefficient and $f$ the interpolation function, the final material is given by

    $$
    m = f(\gamma) m_1 + (1 - f(\gamma)) m_2
    $$

    It optionally takes a mask $s$, which is a field that is multiplied by the final material properties:

    $$
    m = s \\left[ f(\gamma) m_1 + (1 - f(\gamma)) m_2 \\right]
    $$

    Note that both the materials, the mask and the interpolation coefficient can be
    differentiated using JAX. But probably differentiating the mask is not a good idea.
    """
    domain: Domain
    material1: Material
    material2: Material
    interpolation_coefficient: Union[FourierSeries, Num]
    mask: Union[FourierSeries, Num]
    interp_function: Callable

    def __init__(
        self,
        domain: Domain,
        material1: Material = agilus30,
        material2: Material = veroclear,
        interpolation_coefficient: Union[FourierSeries, Num] = 0.0,
        mask: Union[FourierSeries, Num] = 1.0,
        interp_function: Callable = sigmoid
    ):
        """
        Args:
            domain (Domain): The domain of the object.
            material1 (Material, optional): The first material.
            material2 (Material, optional): The second material.
            interpolation_coefficient (Union[FourierSeries, Num], optional): The interpolation coefficient. Can be a FourierSeries field or a scalar. In the latter case, the scalar is broadcasted to the shape of the domain. Note that this interpolation coefficient is passed through the `interp_function` before being used.
            mask (Union[FourierSeries, Num], optional): The mask of the object. Can be a FourierSeries field or a scalar. In the latter case, the scalar simply acts as a scaling factor.
            interp_function (Callable, optional): The interpolation function: it should be a function $f: \mathbb{R} \\to [0,1]$.
        """
        self.material1 = material1
        self.material2 = material2
        self.interpolation_coefficient = interpolation_coefficient
        self.mask = mask
        self.domain = domain
        self.interp_function = interp_function

    @property
    def coefficient(self):
        """The interpolation coefficient, after being passed through the
        interpolation function."""
        return compose(self.interpolation_coefficient)(self.interp_function)

    def as_medium(self, f0: float):
        """Returns the material of the object as a `jwave` `Medium` object.

        Args:
            f0 (float): The frequency at which the material is used. This

        Returns:
            Medium: The medium representing the object.
        """
        m1 = self.material1.as_medium(self.domain, f0)
        m2 = self.material2.as_medium(self.domain, f0)
        weight1 = self.mask*compose(self.interpolation_coefficient)(self.interp_function)
        weight2 = (1 - weight1)*self.mask

        return Medium(
            domain=self.domain,
            sound_speed=weight1 * m1.sound_speed + weight2 * m2.sound_speed,
            density=weight1 * m1.density + weight2 * m2.density,
            attenuation=weight1 * m1.attenuation + weight2 * m2.attenuation
        )

    def as_medium_on_environment(
        self,
        environment: Environment,
        f0: float,
    ):
        """Returns the material of the object as a `jwave` `Medium` object, but
        immersed in an environment.

        Args:
            environment (Environment): The environment in which the object is immersed.
            f0 (float): The frequency at which the material is used.

        Returns:
            Medium: The medium representing the object and the environment.
        """
        self_medium = self.as_medium(f0)
        environment_medium = environment.material
        inv_mask = 1.0 - self.mask
        sound_speed = environment_medium.sound_speed*inv_mask + self_medium.sound_speed*self.mask
        density = environment_medium.density*inv_mask + self_medium.density*self.mask
        attenuation = environment_medium.attenuation*inv_mask + self_medium.attenuation*self.mask
        medium = Medium(
            self.domain,
            sound_speed = sound_speed,
            density = density,
            attenuation = attenuation
        )
        return medium

    def __repr__(self):
        return f"{self.__class__.__name__}[{self.material1.name}, {self.material2.name}]"

    def __str__(self):
        return self.__repr__()

    def tree_flatten(self):
        return (
            (self.material1, self.material2, self.interpolation_coefficient, self.mask),
            (self.interp_function,self.domain)
        )

    @classmethod
    def tree_unflatten(cls, aux_data, children):
        return cls(
            domain=aux_data[1],
            material1=children[0],
            material2=children[1],
            interpolation_coefficient=children[2],
            mask=children[3],
            interp_function=aux_data[0]
        )

    @classmethod
    def disk(
        cls,
        domain: Domain,
        radius: float,
        thickness: float,
        material1: Material = agilus30,
        material2: Material = veroclear,
    ):
        """Creates `TwoMaterialsInterpolated` object where the mask is a disk.

        Args:
            domain (Domain): The domain of the object.
            radius (float): The radius of the disk.
            thickness (float): The thickness of the disk.
            material1 (Material, optional): The first material.
            material2 (Material, optional): The second material.

        Returns:
            TwoMaterialsInterpolated: The object.
        """
        _disk =make_disk(
            domain,
            radius = radius,
            z_pos = -thickness/2.,
            thickness = thickness
        )
        return cls(
            domain = domain,
            material1 = material1,
            material2 = material2,
            interpolation_coefficient=FourierSeries.empty(domain),
            mask=_disk
        )
