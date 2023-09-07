import cupy as cp
from cupyx.profiler import benchmark

from cucim.skimage import data, morphology

print("| shape | footprint_shape | acceleration |")
print("|-------|-----------------|--------------|")
for size, ndim in [(256, 2), (512, 2), (1024, 2), (2048, 2), (4096, 2),
                   (32, 3), (64, 3), (128, 3), (256, 3)]:
    shape = (size, ) * ndim
    b = data.binary_blobs(size, n_dim=ndim)
    if ndim == 2:
        fp_sizes = [3, 5, 7, 15, 31]
    else:
        fp_sizes = [3, 5, 9, 13]
    for fp_size in fp_sizes:
        fp_shape = (fp_size,) * ndim

        if (ndim == 2 and fp_size > 5) or (ndim == 3 and fp_size > 3):
            if ndim == 2:
                fp = morphology.square(fp_size, decomposition='separable')
                fp_array = tuple((cp.ones(selem, dtype=bool), reps) for selem, reps in fp)
            else:
                fp = morphology.cube(fp_size, decomposition='separable')
                fp_array = tuple((cp.ones(selem, dtype=bool), reps) for selem, reps in fp)
        else:
            fp = fp_shape
            fp_array = cp.ones(fp_shape, dtype=bool)

        kwargs = dict(n_warmup=100, n_repeat=100000, max_duration=2)
        perf = benchmark(morphology.binary_erosion, (b, ), kwargs=dict(footprint=fp), **kwargs)
        t_cpu1 = perf.cpu_times * 1000
        t_gpu1 = perf.gpu_times * 1000
        if False:
            print(f"tuple | {shape} | {t_cpu1.mean():0.4f} +/- {t_cpu1.std(): 0.4f} |  {t_gpu1.mean():0.4f} +/- {t_gpu1.std(): 0.4f}")

        perf_kern = benchmark(morphology.binary_erosion, (b, ), kwargs=dict(footprint=fp_array), **kwargs)
        t_cpu = perf_kern.cpu_times * 1000
        t_gpu = perf_kern.gpu_times * 1000
        if False:
            print(f"array | {shape} | {t_cpu.mean():0.4f} +/- {t_cpu.std(): 0.4f} |  {t_gpu.mean():0.4f} +/- {t_gpu.std(): 0.4f}")

        accel = t_gpu.mean() / t_gpu1.mean()
        print(f"{shape} | {fp_shape} | {accel:0.2f}")

        if False:
            def _binary_erosion(b, fp_shape):
                fp = cp.ones(fp_shape, dtype=bool)
                return morphology.binary_erosion(fp)

            perf_alloc = benchmark(_binary_erosion, (b, shape), **kwargs)
            t_cpu = perf_alloc.cpu_times * 1000
            t_gpu = perf_alloc.gpu_times * 1000
            accel = t_cpu.mean() / t_gpu.mean()
            print(f"new array | {shape} | {t_cpu.mean():0.4f} +/- {t_cpu.std(): 0.4f} |  {t_gpu.mean():0.4f} +/- {t_gpu.std(): 0.4f} | {accel}")

"""
| shape | footprint_shape | acceleration |
|-------|-----------------|--------------|
| (256, 256) | (3, 3) | 3.04 |
| (256, 256) | (5, 5) | 3.06 |
| (256, 256) | (7, 7) | 2.90 |
| (256, 256) | (15, 15) | 2.91 |
| (256, 256) | (31, 31) | 2.88 |
| (512, 512) | (3, 3) | 3.03 |
| (512, 512) | (5, 5) | 2.77 |
| (512, 512) | (7, 7) | 2.88 |
| (512, 512) | (15, 15) | 2.89 |
| (512, 512) | (31, 31) | 2.82 |
| (1024, 1024) | (3, 3) | 2.57 |
| (1024, 1024) | (5, 5) | 2.22 |
| (1024, 1024) | (7, 7) | 2.73 |
| (1024, 1024) | (15, 15) | 2.58 |
| (1024, 1024) | (31, 31) | 2.08 |
| (2048, 2048) | (3, 3) | 1.83 |
| (2048, 2048) | (5, 5) | 1.55 |
| (2048, 2048) | (7, 7) | 1.66 |
| (2048, 2048) | (15, 15) | 1.47 |
| (2048, 2048) | (31, 31) | 1.31 |
| (4096, 4096) | (3, 3) | 1.25 |
| (4096, 4096) | (5, 5) | 1.14 |
| (4096, 4096) | (7, 7) | 1.18 |
| (4096, 4096) | (15, 15) | 1.12 |
| (4096, 4096) | (31, 31) | 1.08 |
| (32, 32, 32) | (3, 3, 3) | 2.99 |
| (32, 32, 32) | (5, 5, 5) | 2.87 |
| (32, 32, 32) | (9, 9, 9) | 2.88 |
| (32, 32, 32) | (13, 13, 13) | 2.86 |
| (64, 64, 64) | (3, 3, 3) | 2.63 |
| (64, 64, 64) | (5, 5, 5) | 2.85 |
| (64, 64, 64) | (9, 9, 9) | 2.89 |
| (64, 64, 64) | (13, 13, 13) | 2.87 |
| (128, 128, 128) | (3, 3, 3) | 1.63 |
| (128, 128, 128) | (5, 5, 5) | 2.17 |
| (128, 128, 128) | (9, 9, 9) | 1.94 |
| (128, 128, 128) | (13, 13, 13) | 1.83 |
| (256, 256, 256) | (3, 3, 3) | 1.09 |
| (256, 256, 256) | (5, 5, 5) | 1.12 |
| (256, 256, 256) | (9, 9, 9) | 1.10 |
| (256, 256, 256) | (13, 13, 13) | 1.09 |
"""