import numpy as np
from jax import numpy as jnp
from jwave import Domain, FourierSeries
from scipy.io import savemat
from skimage.io import imread
from skimage.transform import resize

from .objects import PhysicalObject


def load_image(
    domain: Domain,
    image_name: str,
    normalize: bool = True,
    folder: str = "experiments/images",
) -> FourierSeries:
    """Loads an image from the `experiments/images` folder and returns it as a `FourierSeries`. It takes care of resizing
    it to the grid size of the domain.

    Args:
        domain (Domain): The domain of the simulation.
        image_name (str): The name of the image to load.
        normalize (bool, optional): Whether to normalize the image.
        folder (str, optional): The folder to load the image from.

    Returns:
        FourierSeries: The image as a FourierSeries.
    """
    # Load image
    im = imread(folder + image_name)
    im = np.squeeze(im[:,:,0]/255.)  # Takes only one channel

    if normalize:
        im = im / np.sqrt(jnp.sum(jnp.abs(im)**2))

    # Resize image to the same size as the pressure plane
    im = resize(im, domain.N, anti_aliasing=True)

    return FourierSeries(im, domain)

def save_simulation_to_mat(
    filename: str,
    lens: PhysicalObject,
    source: FourierSeries,
    far_field: FourierSeries,
    lossval: float,
    f0: float,
  ):
    """Saves the lens parameters to a .mat file. The file will contain the
    following variables:

    Variables:
      - `sound_speed`: The sound speed field
      - `density`: The density field
      - `absorption_coefficient`: The absorption coefficient field
      - `source`: The source field
      - `frequency`: The transducer frequency
      - `dx`: The grid spacing
      - `loss`: the loss value
      - `far_field`: The far field pattern

    Args:
        filename (str): The filename to save the lens parameters to, the
          extension '.mat' will be added automatically
        lens (Lens): The lens object
        source (FourierSeries): The source field
        far_field (FourierSeries): The far field
        lossval (float): The loss value
        settings (dict): The settings dictionary
    """
    # Make arrays
    medium = lens.as_medium

    savemat(
      filename + ".mat",
      {
        'sound_speed': np.asarray(medium.sound_speed.on_grid[...,0]),
        'density': np.asarray(medium.density.on_grid[...,0]),
        'absorption_coefficient': np.asarray(medium.attenuation.on_grid[...,0]),
        'source': np.abs(source.on_grid[...,0]).astype(jnp.bool_),
        'frequency': f0,
        'dx': lens.domain.dx,
        'loss': -lossval,
        'far_field': np.asarray(far_field.on_grid[...,0]),
      }
    )
