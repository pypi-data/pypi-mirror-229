from jax import numpy as jnp
from jwave import Domain, FourierSeries
from jwave.acoustics.time_harmonic import angular_spectrum, helmholtz_solver
from jwave.geometry import Medium

from .materials import Material, water
from .objects import Environment, PhysicalObject


#TODO: Remember minus sign on the rayleigh projection distance
def project_to_hologram_plane(
    pressure: FourierSeries,
    f0: float,
    lens_thickness: float,
    plane_distance: float,
    remove_padding: bool = True,
    background: Material = water,
):
    """Projects a field to the hologram plane using the [angular
    spectrum method](https://en.wikipedia.org/wiki/Angular_spectrum_method).

    Args:
        pressure (FourierSeries): The field to be projected. This needs to be
            a 3D wavefield from which a planar slice will be extracted.
        f0 (float): The frequency of the field.
        lens_thickness (float): The thickness of the lens. This is used to
            determine the location of the plane used to extract the field to
            be projected.
        plane_distance (float): The distance from the lens to the hologram.
        remove_padding (bool, optional): Whether to remove the padding added
            by the angular spectrum method.
        background (Material, optional): The background material. Defaults to
            water.
    """
    domain = pressure.domain

    # Calculate the location of the input plane
    rayleigh_plane_z_pos = lens_thickness/2. + 2*domain.dx[2]
    plane_z_idx = int(rayleigh_plane_z_pos / domain.dx[2]) + domain.N[2]//2
    # plane_grid = jnp.squeeze(domain.grid[:,:,0]).at[:,:,2].set(0.)

    # Extract the pressure plane as a 2D Fourier Series
    pressure_plane = pressure.on_grid[:,:,plane_z_idx,0]
    plane_domain = Domain(pressure_plane.shape, domain.dx[:2])
    pressure_plane_field = FourierSeries(pressure_plane, plane_domain)

    # Get the projection at the hologram plane using angular spectrum
    padding_size = pressure_plane_field.domain.N[0]//2
    pressure_far = angular_spectrum(
        pressure_plane_field,
        z_pos = -plane_distance,
        f0 = f0,
        medium = background.as_medium(plane_domain),
        padding = padding_size,
        unpad_output=remove_padding,
    )

    # Return the projection and the original plane field
    return pressure_far, pressure_plane_field

def solve_helmholtz(
    medium: Medium,
    source: FourierSeries,
    f0: float,
    maxiter: int = 100,
    tol: float = 0.001,
) -> FourierSeries:
    """A thin wrapper around `jwave.acoustics.time_harmonic.helmholtz_solver`.

    Args:
        medium (Medium): The medium in which the field is to be solved.
        source (FourierSeries): The source field.
        f0 (float): The frequency of the source.
        maxiter (int, optional): The maximum number of GMRES iterations (the internal
            solver used by `helmholtz_solver`).
        tol (float, optional): The tolerance for the GMRES solver (the internal
            solver used by `helmholtz_solver`).

    Returns:
        FourierSeries: The resulting acoustic field.
    """
    omega = 2*jnp.pi*f0

    full_field = helmholtz_solver(
        medium,
        omega,
        source,
        maxiter = maxiter,
        tol = tol,
    )
    return full_field

def compute_hologram(
    lens: PhysicalObject,
    source: FourierSeries,
    f0: float,
    lens_thickness: float,
    projection_distance: float,
    *,
    maxiter_helmholtz_solver: int = 100,
    tol_helmholtz_solver: float = 0.001,
    remove_padding: bool = True,
    background: Material = water,
) -> FourierSeries:
    """Solves the helmholtz equation locally around the lens,
    and projects the field to the hologram plane using the
    [angular spectrum method](https://en.wikipedia.org/wiki/Angular_spectrum_method).

    Args:
        lens (PhysicalObject): The lens object. This needs to be
            a physical object with a "as_medium_on_environment"
            method.
        source (FourierSeries): The source field.
        f0 (float): The frequency of the source.
        lens_thickness (float): The thickness of the lens. This is
            used to determine the location of the plane used to
            extract the field to be projected.
        projection_distance (float): The distance from the lens to
            the hologram plane. This is used to determine the
            location of the plane used to extract the field to be
            projected. It is measured from the output plane of the
            lens.
        maxiter_helmholtz_solver (int, optional): The maximum number
            of GMRES iterations for the helmholtz solver. Defaults to 100.
        tol_helmholtz_solver (float, optional): The tolerance for the
            helmholtz solver. Defaults to 0.001.
        remove_padding (bool, optional): Whether to remove the padding
            added by the angular spectrum method. Defaults to True.
        background (Material, optional): The background material. Defaults
            to water.

    Returns:
        FourierSeries: The hologram field.
    """
    # Make the lens on the environment
    medium = lens.as_medium_on_environment(
        Environment(domain=lens.domain, material=background),
        f0=f0,
    )

    # Solve the helmholtz equation in the volume
    volume_field = solve_helmholtz(
        medium,
        source,
        f0,
        maxiter=maxiter_helmholtz_solver,
        tol=tol_helmholtz_solver)

    # Project the field to the hologram plane
    hologram_plane_field, _ = project_to_hologram_plane(
        volume_field,
        f0,
        lens_thickness,
        projection_distance,
        background=background,
    )

    return hologram_plane_field
