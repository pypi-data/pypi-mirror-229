import numpy as np


def autocorr2d(vals, pad_mode="reflect"):
    """
    Compute 2-D autocorrelation of image via the FFT.

    Parameters
    ----------
    vals : py:class:`~numpy.ndarray`
        2-D image.
    pad_mode : str
        Desired padding. See NumPy documentation: https://numpy.org/doc/stable/reference/generated/numpy.pad.html

    Return
    ------
    autocorr : py:class:`~numpy.ndarray`
    """

    shape = vals.shape
    assert len(shape) == 2

    # pad
    vals_padded = np.pad(
        vals,
        pad_width=((shape[0] // 2, shape[0] // 2), (shape[1] // 2, shape[1] // 2)),
        mode=pad_mode,
    )

    # compute autocorrelation via DFT
    X = np.fft.rfft2(vals_padded)
    autocorr = np.fft.ifftshift(np.fft.irfft2(X * X.conj()))

    # remove padding
    return autocorr[shape[0] // 2 : -shape[0] // 2, shape[1] // 2 : -shape[1] // 2]
