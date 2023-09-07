
def phase_cross_correlation(reference_image, moving_image, *,
                            upsample_factor=1, space="real",
                            return_error=True, reference_mask=None,
                            moving_mask=None, overlap_ratio=0.3,
                            normalization="phase"):
    """Efficient subpixel image translation registration by cross-correlation.

    This code gives the same precision as the FFT upsampled cross-correlation
    in a fraction of the computation time and with reduced memory requirements.
    It obtains an initial estimate of the cross-correlation peak by an FFT and
    then refines the shift estimation by upsampling the DFT only in a small
    neighborhood of that estimate by means of a matrix-multiply DFT [1]_.

    Parameters
    ----------
    reference_image : array
        Reference image.
    moving_image : array
        Image to register. Must be same dimensionality as
        ``reference_image``.
    upsample_factor : int, optional
        Upsampling factor. Images will be registered to within
        ``1 / upsample_factor`` of a pixel. For example
        ``upsample_factor == 20`` means the images will be registered
        within 1/20th of a pixel. Default is 1 (no upsampling).
        Not used if any of ``reference_mask`` or ``moving_mask`` is not None.
    space : string, one of "real" or "fourier", optional
        Defines how the algorithm interprets input data. "real" means
        data will be FFT'd to compute the correlation, while "fourier"
        data will bypass FFT of input data. Case insensitive. Not
        used if any of ``reference_mask`` or ``moving_mask`` is not
        None.
    return_error : bool, optional
        Returns error and phase difference if on, otherwise only
        shifts are returned. Has noeffect if any of ``reference_mask`` or
        ``moving_mask`` is not None. In this case only shifts is returned.
    reference_mask : ndarray
        Boolean mask for ``reference_image``. The mask should evaluate
        to ``True`` (or 1) on valid pixels. ``reference_mask`` should
        have the same shape as ``reference_image``.
    moving_mask : ndarray or None, optional
        Boolean mask for ``moving_image``. The mask should evaluate to ``True``
        (or 1) on valid pixels. ``moving_mask`` should have the same shape
        as ``moving_image``. If ``None``, ``reference_mask`` will be used.
    overlap_ratio : float, optional
        Minimum allowed overlap ratio between images. The correlation for
        translations corresponding with an overlap ratio lower than this
        threshold will be ignored. A lower `overlap_ratio` leads to smaller
        maximum translation, while a higher `overlap_ratio` leads to greater
        robustness against spurious matches due to small overlap between
        masked images. Used only if one of ``reference_mask`` or
        ``moving_mask`` is None.
    normalization : {"phase", None}
        The type of normalization to apply to the cross-correlation. This
        parameter is unused when masks (`reference_mask` and `moving_mask`) are
        supplied.

    Returns
    -------
    shifts : ndarray
        Shift vector (in pixels) required to register ``moving_image``
        with ``reference_image``. Axis ordering is consistent with
        numpy (e.g. Z, Y, X)
    error : float
        Translation invariant normalized RMS error between
        ``reference_image`` and ``moving_image``.
    phasediff : float
        Global phase difference between the two images (should be
        zero if images are non-negative).

    Notes
    -----
    The use of cross-correlation to estimate image translation has a long
    history dating back to at least [2]_. The "phase correlation"
    method (selected by ``normalization="phase"``) was first proposed in [3]_.
    Publications [1]_ and [2]_ use an unnormalized cross-correlation
    (``normalization=None``). Which form of normalization is better is
    application-dependent. For example, the phase correlation method works
    well in registering images under different illumination, but is not very
    robust to noise. In a high noise scenario, the unnormalized method may be
    preferable.

    When masks are provided, a masked normalized cross-correlation algorithm is
    used [5]_, [6]_.

    References
    ----------
    .. [1] Manuel Guizar-Sicairos, Samuel T. Thurman, and James R. Fienup,
           "Efficient subpixel image registration algorithms,"
           Optics Letters 33, 156-158 (2008). :DOI:`10.1364/OL.33.000156`
    .. [2] P. Anuta, Spatial registration of multispectral and multitemporal
           digital imagery using fast Fourier transform techniques, IEEE Trans.
           Geosci. Electron., vol. 8, no. 4, pp. 353–368, Oct. 1970.
           :DOI:`10.1109/TGE.1970.271435`.
    .. [3] C. D. Kuglin D. C. Hines. The phase correlation image alignment
           method, Proceeding of IEEE International Conference on Cybernetics
           and Society, pp. 163-165, New York, NY, USA, 1975, pp. 163–165.
    .. [4] James R. Fienup, "Invariant error metrics for image reconstruction"
           Optics Letters 36, 8352-8357 (1997). :DOI:`10.1364/AO.36.008352`
    .. [5] Dirk Padfield. Masked Object Registration in the Fourier Domain.
           IEEE Transactions on Image Processing, vol. 21(5),
           pp. 2706-2718 (2012). :DOI:`10.1109/TIP.2011.2181402`
    .. [6] D. Padfield. "Masked FFT registration". In Proc. Computer Vision and
           Pattern Recognition, pp. 2918-2925 (2010).
           :DOI:`10.1109/CVPR.2010.5540032`
    """
    if (reference_mask is not None) or (moving_mask is not None):
        return _masked_phase_cross_correlation(reference_image, moving_image,
                                               reference_mask, moving_mask,
                                               overlap_ratio)

    # images must be the same shape
    if reference_image.shape != moving_image.shape:
        raise ValueError("images must be same shape")

    # assume complex data is already in Fourier space
    if space.lower() == 'fourier':
        src_freq = reference_image
        target_freq = moving_image
    # real data needs to be fft'd.
    elif space.lower() == 'real':
        src_freq = fft.fftn(reference_image)
        target_freq = fft.fftn(moving_image)
    else:
        raise ValueError('space argument must be "real" of "fourier"')

    # Whole-pixel shift - Compute cross-correlation by an IFFT
    shape = src_freq.shape
    image_product = src_freq * target_freq.conj()
    if normalization == "phase":
        eps = cp.finfo(image_product.real.dtype).eps
        image_product /= cp.maximum(cp.abs(image_product), 100 * eps)
    elif normalization is not None:
        raise ValueError("normalization must be either phase or None")
    cross_correlation = fft.ifftn(image_product)

    # Locate maximum
    maxima = np.unravel_index(int(cp.argmax(cp.abs(cross_correlation))), cross_correlation.shape)
    midpoints = tuple(float(axis_size // 2) for axis_size in shape)

    float_dtype = image_product.real.dtype
    shifts = np.asarray(maxima, dtype=float_dtype)
    shifts = tuple(_max - axis_size if _max > mid else _max
                   for _max, mid, axis_size in zip(maxima, midpoints, shape))

    if upsample_factor == 1:
        if return_error:
            sabs = cp.abs(src_freq)
            sabs *= sabs
            tabs = cp.abs(target_freq)
            tabs *= tabs
            src_amp = np.sum(sabs) / src_freq.size
            target_amp = np.sum(tabs) / target_freq.size
            CCmax = cross_correlation[maxima]
    # If upsampling > 1, then refine estimate with matrix multiply DFT
    else:
        # Initial shift estimate in upsampled grid
        # shifts = cp.around(shifts * upsample_factor) / upsample_factor
        upsample_factor = float(upsample_factor)
        shifts = (round(s * upsample_factor) / upsample_factor
                  for s in shifts)
        upsampled_region_size = math.ceil(upsample_factor * 1.5)
        # Center of output array at dftshift + 1
        dftshift = float(upsampled_region_size // 2)
        # Matrix multiply DFT around the current shift estimate
        sample_region_offset = tuple(
            dftshift - s * upsample_factor for s in shifts
        )
        cross_correlation = _upsampled_dft(image_product.conj(),
                                           upsampled_region_size,
                                           upsample_factor,
                                           sample_region_offset).conj()

        # Locate maximum and map back to original pixel grid
        maxima = np.unravel_index(int(cp.argmax(cp.abs(cross_correlation))),
                                  cross_correlation.shape)
        CCmax = cross_correlation[maxima]

        maxima = tuple(float(m) - dftshift for m in maxima)
        shifts = tuple(s + m / upsample_factor for s, m in zip(shifts, maxima))

        if return_error:
            src_amp = cp.abs(src_freq)
            src_amp *= src_amp
            src_amp = cp.sum(src_amp)
            target_amp = cp.abs(target_freq)
            target_amp *= target_amp
            target_amp = cp.sum(target_amp)

    # If its only one row or column the shift along that dimension has no
    # effect. We set to zero.
    for dim in range(src_freq.ndim):
        if shape[dim] == 1:
            shifts[dim] = 0

    if return_error:
        # Redirect user to masked_phase_cross_correlation if NaNs are observed
        if cp.isnan(CCmax) or cp.isnan(src_amp) or cp.isnan(target_amp):
            raise ValueError(
                "NaN values found, please remove NaNs from your "
                "input data or use the `reference_mask`/`moving_mask` "
                "keywords, eg: "
                "phase_cross_correlation(reference_image, moving_image, "
                "reference_mask=~np.isnan(reference_image), "
                "moving_mask=~np.isnan(moving_image))")

        return shifts, _compute_error(CCmax, src_amp, target_amp),\
            _compute_phasediff(CCmax)
    else:
        return shifts
