from __future__ import annotations

import torch
from torch import Tensor
from torch.nn.functional import conv2d
from torch.nn.functional import pad as torch_pad
from torchvision.transforms._functional_tensor import (_cast_squeeze_in,
                                                       _cast_squeeze_out,
                                                       _max_value, _rgb2hsv,
                                                       invert)
from torchvision.transforms.functional import convert_image_dtype

from torchaug.transforms._utils import (_assert_channels, _assert_image_tensor,
                                        _assert_tensor,
                                        get_channels_height_width,
                                        is_tensor_on_cpu,
                                        transfer_tensor_on_device)
from torchaug.utils import _log_api_usage_once


def _hsv2rgb(img: Tensor) -> Tensor:
    # From Torchvision nlgranger pull request to speed conversion: https://github.com/pytorch/vision/pull/7754
    h, s, v = img.unbind(dim=-3)
    h6 = h.mul(6)
    i = torch.floor(h6)
    f = h6.sub_(i)
    i = i.to(dtype=torch.int32)

    sxf = s * f
    one_minus_s = 1.0 - s
    q = (1.0 - sxf).mul_(v).clamp_(0.0, 1.0)
    t = sxf.add_(one_minus_s).mul_(v).clamp_(0.0, 1.0)
    p = one_minus_s.mul_(v).clamp_(0.0, 1.0)
    i.remainder_(6)

    vpqt = torch.stack((v, p, q, t), dim=-3)

    # vpqt -> rgb mapping based on i
    select = torch.tensor(
        [[0, 2, 1, 1, 3, 0], [3, 0, 0, 2, 1, 1], [1, 1, 3, 0, 0, 2]], dtype=torch.long
    )
    select = select.to(device=img.device, non_blocking=True)

    select = select[:, i]
    if select.ndim > 3:
        # if input.shape is (B, ..., C, H, W) then
        # select.shape is (C, B, ...,  H, W)
        # thus we move C axis to get (B, ..., C, H, W)
        select = select.moveaxis(0, -3)

    return vpqt.gather(-3, select)


def _get_gaussian_kernel1d(
    kernel_size: int, sigma: float | Tensor, dtype: torch.dtype, device: torch.device
) -> Tensor:
    ksize_half = (kernel_size - 1) * 0.5

    x = torch.linspace(
        -ksize_half, ksize_half, steps=kernel_size, dtype=dtype, device=device
    )
    pdf = torch.exp(-0.5 * (x / sigma).pow(2))
    kernel1d = pdf / pdf.sum()

    return kernel1d


def _get_gaussian_kernel2d(
    kernel_size: list[int],
    sigma: list[float] | Tensor,
    dtype: torch.dtype,
    device: torch.device,
) -> Tensor:
    kernel1d_x = _get_gaussian_kernel1d(kernel_size[0], sigma[0], dtype, device)
    kernel1d_y = _get_gaussian_kernel1d(kernel_size[1], sigma[1], dtype, device)
    kernel2d = torch.mm(kernel1d_y[:, None], kernel1d_x[None, :])
    return kernel2d


def adjust_hue(img: Tensor, hue_factor: float) -> Tensor:
    """Adjust hue of an image.

    The image hue is adjusted by converting the image to HSV and
    cyclically shifting the intensities in the hue channel (H).
    The image is then converted back to original image mode.

    `hue_factor` is the amount of shift in H channel and must be in the
    interval `[-0.5, 0.5]`.

    See `Hue`_ for more details.

    .. _Hue: https://en.wikipedia.org/wiki/Hue

    Args:
        imgs: Image to be adjusted. It is expected to be in [..., 1 or 3, H, W] format,
            where ... means it can have an arbitrary number of dimensions.
            Note: the pixel values of the input image has to be non-negative for conversion to HSV space;
            thus it does not work if you normalize your image to an interval with negative values,
            or use an interpolation that generates negative values before using this function.
        hue_factor:  How much to shift the hue channel. Can be 1 or B elements in
            [-0.5, 0.5]. 0.5 and -0.5 give complete reversal of hue channel in
            HSV space in positive and negative direction respectively.
            0 means no shift. Therefore, both -0.5 and 0.5 will give an image
            with complementary colors while 0 gives the original image.

    Returns:
        Hue adjusted image.
    """

    if not torch.jit.is_scripting() and not torch.jit.is_tracing():
        _log_api_usage_once(adjust_hue)

    if not isinstance(hue_factor, float):
        try:
            hue_factor = float(hue_factor)
        except ValueError:
            raise TypeError(
                f"hue_factor should be a float or convertible to float. Got {type(hue_factor)}."
            )

    if not (-0.5 <= hue_factor <= 0.5):
        raise ValueError(f"hue_factor is not in [-0.5, 0.5].")

    _assert_image_tensor(img)

    _assert_channels(img, [1, 3])
    if get_channels_height_width(img)[0] == 1:  # Match PIL behaviour
        return img

    orig_dtype = img.dtype
    img = convert_image_dtype(img, torch.float32)

    img = _rgb2hsv(img)
    h, s, v = img.unbind(dim=-3)
    h = (h + hue_factor) % 1.0
    img = torch.stack((h, s, v), dim=-3)
    img_hue_adj = _hsv2rgb(img)

    return convert_image_dtype(img_hue_adj, orig_dtype)


def div_255(
    tensor: Tensor,
    inplace: bool = False,
) -> Tensor:
    """Divide the given tensor by 255.

    Args:
        tensor: The input tensor.
        inplace: Whether to perform the operation inplace.

    Returns:
        Scaled tensor by dividing 255.
    """
    tensor = tensor if inplace else tensor.clone()
    tensor.div_(255.0)

    return tensor


def gaussian_blur(
    img: Tensor,
    kernel_size: list[int],
    sigma: int | float | list[int] | list[float] | Tensor | None = None,
    value_check: bool = False,
) -> Tensor:
    """Performs Gaussian blurring on the image by given kernel. If is expected to have [..., H, W] shape, where ...
    means an arbitrary number of leading dimensions.

    Args:
        img: Image to be blurred.
        kernel_size: Gaussian kernel size. Can be a sequence of integers
            like ``(kx, ky)`` or a single integer for square kernels.

            .. note::
                In torchscript mode kernel_size as single int is not supported, use a sequence of
                length 1: ``[ksize, ]``.
        sigma: Gaussian kernel standard deviation. Can be a
            sequence of floats like ``(sigma_x, sigma_y)`` or a single float to define the
            same sigma in both X/Y directions. If None, then it is computed using
            ``kernel_size`` as ``sigma = 0.3 * ((kernel_size - 1) * 0.5 - 1) + 0.8``.
        value_check: Bool to perform tensor value check.
            Might cause slow down on some devices because of synchronization.

    Returns:
        Gaussian Blurred version of the image.
    """

    if not torch.jit.is_scripting() and not torch.jit.is_tracing():
        _log_api_usage_once(gaussian_blur)
    if not isinstance(kernel_size, (int, list, tuple)):
        raise TypeError(
            f"kernel_size should be int or a sequence of integers. Got {type(kernel_size)}."
        )

    _assert_tensor(img)
    _assert_image_tensor(img)

    if isinstance(kernel_size, int):
        kernel_size = [kernel_size, kernel_size]
    if len(kernel_size) != 2:
        raise ValueError(
            f"If kernel_size is a sequence its length should be 2. Got {len(kernel_size)}."
        )
    for ksize in kernel_size:
        if ksize % 2 == 0 or ksize < 0:
            raise ValueError(
                f"kernel_size should have odd and positive integers. Got {kernel_size}."
            )

    if sigma is None:
        sigma_t = torch.tensor(
            [ksize * 0.15 + 0.35 for ksize in kernel_size], device=img.device
        )
    else:
        if isinstance(sigma, (list, tuple)):
            length = len(sigma)
            if length == 1:
                s = float(sigma[0])
                sigma_t = torch.tensor([s, s], device=img.device)
            elif length != 2:
                raise ValueError(
                    f"If sigma is a sequence, its length should be 2. Got {length}."
                )
            else:
                sigma_t = torch.tensor(sigma, device=img.device)
        elif isinstance(sigma, (int, float)):
            s = float(sigma)
            sigma_t = torch.tensor([s, s], device=img.device)
        elif isinstance(sigma, Tensor):
            sigma_t = transfer_tensor_on_device(sigma, img.device, non_blocking=True)

            dim_sigma = sigma_t.ndim + 1 if sigma_t.ndim == 0 else sigma_t.ndim
            len_sigma = 1 if sigma_t.ndim == 0 else sigma_t.shape[0]
            if dim_sigma != 1:
                raise ValueError(
                    f"If sigma is a tensor, its dimension should be 1. Got {dim_sigma}."
                )
            if len_sigma == 1:
                sigma_t = sigma_t.expand(2)
            elif len_sigma != 2:
                raise ValueError(
                    f"If sigma is a tensor of multiple values, its length should be 2. Got {len_sigma}."
                )
        else:
            raise TypeError(
                f"sigma should be either int, float or sequence of floats or int or tensor. Got {type(sigma)}."
            )

    if (
        (isinstance(sigma, (float, int)) and sigma <= 0)
        or (isinstance(sigma, (list, tuple)) and any([s <= 0 for s in sigma]))
        or (
            isinstance(sigma, (Tensor))
            and (value_check or is_tensor_on_cpu(sigma))
            and not torch.all(torch.gt(sigma, 0))
        )
    ):
        raise ValueError(f"sigma should have positive values. Got {sigma}.")

    dtype = img.dtype if torch.is_floating_point(img) else torch.float32
    device = img.device
    kernel = _get_gaussian_kernel2d(kernel_size, sigma_t, dtype=dtype, device=device)
    kernel = kernel.expand(img.shape[-3], 1, kernel.shape[0], kernel.shape[1])

    img, need_cast, need_squeeze, out_dtype = _cast_squeeze_in(img, [kernel.dtype])

    # padding = (left, right, top, bottom)
    padding = [
        kernel_size[0] // 2,
        kernel_size[0] // 2,
        kernel_size[1] // 2,
        kernel_size[1] // 2,
    ]
    img = torch_pad(img, padding, mode="reflect")
    img = conv2d(img, kernel, groups=img.shape[-3])

    img = _cast_squeeze_out(img, need_cast, need_squeeze, out_dtype)
    return img


def mixup(
    tensor_1: Tensor, tensor_2: Tensor, lam: float, inplace: bool = False
) -> Tensor:
    """Mix two tensors with linear interpolation.

    The tensors should be floats.

    Args:
        tensor_1: First tensor.
        tensor_2: Second tensor.
        lam: Mixing coefficient.
        inplace: Whether to perform the operation inplace.

    Returns:
        The mixed tensor.
    """
    if not torch.jit.is_scripting() and not torch.jit.is_tracing():
        _log_api_usage_once(mixup)

    _assert_tensor(tensor_1)
    _assert_tensor(tensor_2)

    if not isinstance(lam, float):
        raise TypeError(f"lam should be float. Got {type(lam)}.")

    if not tensor_1.is_floating_point() or not tensor_2.is_floating_point():
        raise TypeError(
            f"Tensors should be float. Got {tensor_1.dtype} and {tensor_2.dtype}."
        )

    tensor_1 = tensor_1 if inplace else tensor_1.clone()
    tensor_2 = tensor_2 if inplace else tensor_2.clone()
    return tensor_1.mul_(lam).add_(tensor_2.mul_(1 - lam))


def mul_255(tensor: Tensor, inplace: bool = False) -> Tensor:
    """Multiply the given tensor by 255.

    Args:
        tensor: The input tensor.
        inplace: Whether to perform the operation inplace.

    Returns:
        Scaled tensor by multiplying 255.
    """
    tensor = tensor if inplace else tensor.clone()
    tensor.mul_(255.0)

    return tensor


def normalize(
    tensor: Tensor,
    mean: list[float] | Tensor,
    std: list[float] | Tensor,
    cast_dtype: torch.dtype | None = None,
    inplace: bool = False,
    value_check: bool = False,
) -> Tensor:
    """Normalize a tensor image with mean and standard deviation.

    .. note::
        If tensor is not float, user has to set `cast_dtype` to a float ``torch.dtype``,
        otherwise it will raise an error. The function will cast and scale the tensor
        and return a normalized float tensor.

    See :class:`~torchaug.transforms.Normalize` for more details.

    Args:
        tensor: Tensor image of size (C, H, W) or (B, C, H, W) to be normalized.
        mean: Sequence of means for each channel.
        std: Sequence of standard deviations for each channel.
        cast_dtype: If not None, scale and cast input to dtype. Expected to be a float dtype.
        inplace: Bool to make this operation inplace.
        value_check: Bool to perform tensor value check.
            Might cause slow down on some devices because of synchronization.

    Returns:
        Normalized float Tensor image.
    """

    if not torch.jit.is_scripting() and not torch.jit.is_tracing():
        _log_api_usage_once(normalize)

    _assert_tensor(tensor)
    _assert_image_tensor(tensor)

    if not tensor.is_floating_point() and cast_dtype is None:
        raise TypeError(
            f"Input tensor should be a float tensor or cast_dtype set to a float dtype."
            f" Got {tensor.dtype} and {cast_dtype}."
        )
    elif cast_dtype is not None and tensor.dtype != cast_dtype:
        if not torch.tensor(0, dtype=cast_dtype).is_floating_point():
            raise ValueError(f"cast_dtype should be a float dtype. Got {cast_dtype}.")
        casted = True
        tensor = convert_image_dtype(tensor, dtype=cast_dtype)
    else:
        casted = False

    dtype = tensor.dtype
    mean = torch.as_tensor(mean, dtype=dtype, device=tensor.device)
    std = torch.as_tensor(std, dtype=dtype, device=tensor.device)

    if not inplace and not casted:
        tensor = tensor.clone()

    if (value_check or is_tensor_on_cpu(std)) and not torch.all(torch.gt(std, 0)):
        raise ValueError(f"std contains a zero leading to division by zero.")

    if mean.ndim == 1:
        mean = mean.view(-1, 1, 1)
    if std.ndim == 1:
        std = std.view(-1, 1, 1)

    tensor = tensor.sub_(mean).div_(std)

    return tensor


def solarize(
    img: Tensor, threshold: int | float | Tensor, value_check: bool = False
) -> Tensor:
    """Solarize an RGB/grayscale image by inverting all pixel values above a threshold.

    Args:
        img: Image to have its colors inverted. It is expected to be in [..., 1 or 3, H, W] format,
            where ... means it can have an arbitrary number of dimensions.
            If img is PIL Image, it is expected to be in mode "L" or "RGB".
        threshold: All pixels equal or above this value are inverted.
        value_check: Bool to perform tensor value check.
            Might cause slow down on some devices because of synchronization.
    Returns:
        Solarized image.
    """
    if not torch.jit.is_scripting() and not torch.jit.is_tracing():
        _log_api_usage_once(solarize)

    _assert_tensor(img)
    _assert_image_tensor(img)

    if not isinstance(threshold, (int, float)) and (
        not isinstance(threshold, Tensor) or threshold.numel() > 1
    ):
        raise TypeError("threshold should be a float or a tensor of one element.")

    if img.ndim < 3:
        raise TypeError(
            f"Input image tensor should have at least 3 dimensions, but found {img.ndim}."
        )

    _assert_channels(img, [1, 3])

    if (
        value_check
        or isinstance(threshold, (int, float) or is_tensor_on_cpu(threshold))
    ) and threshold > _max_value(img.dtype):
        raise ValueError("Threshold should be less than bound of img.")

    inverted_img = invert(img)
    return torch.where(img >= threshold, inverted_img, img)
