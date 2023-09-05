import math
from typing import Tuple

from jax import numpy as jnp
from jaxtyping import Num
from jwave import FourierSeries


def field_intensity(
    field: FourierSeries,
) -> Num:
    """Calculate the intensity of a complex field

    Args:
        field (FourierSeries): The complex field.

    Returns:
        Num: The intensity of the field.
    """
    dV = math.prod(field.domain.dx)
    return jnp.sqrt(jnp.sum(jnp.abs(field.on_grid)**2)) * dV

def normalized_mse(
    predicted: FourierSeries,
    target: FourierSeries,
    pad_value: Num = 0.,
) -> Num:
    """Calculate the normalized mean squared error between two Fourier series.

    Args:
        predicted (FourierSeries): The predicted Fourier series.
        target (FourierSeries): The target Fourier series to which the predicted series is compared.
        pad_value (Num, optional): Value used for padding the target Fourier series if its shape is different from the predicted series. Default is 0.

    Returns:
        Num: The normalized mean squared error.
    """
    # Get them on grid
    predicted = predicted.on_grid[...,0]
    target = target.on_grid[...,0]

    # Pad the target if necessary
    if predicted.shape != target.shape:
        padding_size = (predicted.shape[0] - target.shape[0])//2
        target = jnp.pad(
            target,
            ((padding_size, padding_size), (padding_size, padding_size)),
            'constant',
            constant_values=pad_value
        )

    # Normalize images
    predicted = jnp.abs(predicted) / jnp.sqrt(jnp.sum(jnp.abs(predicted)**2))
    target = jnp.abs(target) / jnp.sqrt(jnp.sum(jnp.abs(target)**2))

    # Calculate correlation
    mse = jnp.sum(jnp.abs(predicted - target)**2)

    return mse

def amplitude_correlation(
    predicted: FourierSeries,
    target: FourierSeries,
    pad_value: Num = 0.,
) -> Num:
    """
    Calculate the amplitude correlation between two Fourier series.

    The function takes two Fourier series, gets them on grid and computes the amplitude correlation. If the shapes of `predicted` and `target` are different, the target is padded to match the shape of the predicted.

    Args:
        predicted (FourierSeries): The predicted Fourier series.
        target (FourierSeries): The target Fourier series to which predicted
            series is compared.
        pad_value (Num, optional): Value used for padding the target Fourier
            series if its shape is different from the predicted series.
            Default is 0.

    Returns:
        Num: The amplitude correlation between the predicted and target
            Fourier series.
    """
    # Get them on grid
    predicted = predicted.on_grid[...,0]
    target = target.on_grid[...,0]

    # Pad the target if necessary
    if predicted.shape != target.shape:
        padding_size = (predicted.shape[0] - target.shape[0])//2
        target = jnp.pad(
            target,
            ((padding_size, padding_size), (padding_size, padding_size)),
            'constant',
            constant_values=pad_value
        )

    # Normalize images
    predicted = predicted / jnp.sqrt(jnp.sum(jnp.abs(predicted)**2))
    target = target / jnp.sqrt(jnp.sum(jnp.abs(target)**2))

    # Calculate correlation
    corr = jnp.abs(jnp.sum(predicted * target))

    return corr

def real_imag_correlation(
    predicted: FourierSeries,
    target: FourierSeries,
    pad_value: Num = 0.,
) -> Num:
    """
    Calculate the amplitude correlation between two Fourier series, considering the real and imaginary parts separately.

    The function takes two Fourier series, gets them on grid and computes the correlation. If the shapes of `predicted` and `target` are different, the target is padded to match the shape of the predicted.

    Args:
        predicted (FourierSeries): The predicted Fourier series.
        target (FourierSeries): The target Fourier series to which predicted
            series is compared.
        pad_value (Num, optional): Value used for padding the target Fourier
            series if its shape is different from the predicted series.
            Default is 0.

    Returns:
        Num: The amplitude correlation between the predicted and target
            Fourier series.
    """
    # Get them on grid
    predicted = predicted.on_grid[...,0]
    target = target.on_grid[...,0]

    # Pad the target if necessary
    if predicted.shape != target.shape:
        padding_size = (predicted.shape[0] - target.shape[0])//2
        target = jnp.pad(
            target,
            ((padding_size, padding_size), (padding_size, padding_size)),
            'constant',
            constant_values=pad_value
        )

    # Get real and imaginary parts
    predicted = jnp.stack([predicted.real, predicted.imag], axis=-1)
    target = jnp.stack([target.real, target.imag], axis=-1)

    # Normalize images
    predicted = jnp.abs(predicted) / jnp.sqrt(jnp.sum(jnp.abs(predicted)**2))
    target = jnp.abs(target) / jnp.sqrt(jnp.sum(jnp.abs(target)**2))

    # Calculate correlation
    corr = jnp.abs(jnp.sum(predicted * target))

    return corr

def point_intensity(
    point: Tuple[float, float],
    pressure_plane: FourierSeries,
) -> Num:
    """Returns the absolute intensity of a 2D field at a point. The
    point coordinates are given in the same units as the domain.

    Points in between grid nodes are calculated using the Band Limited Interpolant of the Fourier Series.

    Args:
        point (Tuple[float, float]): The point coordinates. The point (0,0)
            corresponds to the center of the pressure plane.
        pressure_plane (FourierSeries): The pressure plane.

    Returns:
        Num: The absolute intensity at the point.
    """
    return jnp.abs(pressure_plane(point))
