import cupy as cp

x = cp.arange(8*16*24).reshape(8, 16, 24)
from cucim.skimage._vendored._ndimage_filters import rank_filter

y = rank_filter(x, size=3, mode='nearest', rank=5)
