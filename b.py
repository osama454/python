import triton
import triton.language as tl

@triton.jit
def calculate_gravity(
    density_ptr,
    gx_ptr,
    gy_ptr,
    gz_ptr,
    N: tl.constexpr,
    ds: tl.constexpr,
    G: tl.constexpr,
):
    """
    Calculates the gravitational acceleration at each point in a 3D grid.

    Args:
        density_ptr: Pointer to the density array.
        gx_ptr: Pointer to the x-component of the gravitational acceleration array.
        gy_ptr: Pointer to the y-component of the gravitational acceleration array.
        gz_ptr: Pointer to the z-component of the gravitational acceleration array.
        N: The size of the grid (NxNxN).
        ds: The distance between adjacent grid points.
        G: The gravitational constant.
    """

    pid = tl.program_id(axis=0)
    i = pid // (N * N)
    j = (pid % (N * N)) // N
    k = pid % N

    # Calculate gravitational acceleration components
    gx = 0.0
    gy = 0.0
    gz = 0.0
    for ii in range(N):
        for jj in range(N):
            for kk in range(N):
                if (i != ii) or (j != jj) or (k != kk):
                    dx = (ii - i) * ds
                    dy = (jj - j) * ds
                    dz = (kk - k) * ds
                    r2 = dx * dx + dy * dy + dz * dz
                    r = tl.math.sqrt(r2)
                    force = G * density_ptr[ii, jj, kk] / r2
                    gx += force * dx / r
                    gy += force * dy / r
                    gz += force * dz / r

    # Store the results
    gx_ptr[i, j, k] = gx
    gy_ptr[i, j, k] = gy
    gz_ptr[i, j, k] = gz


def gravity_grid(density, ds, G=6.674e-11):
    """
    Calculates the gravitational acceleration on a 3D grid using Triton.

    Args:
        density: A NumPy array of shape (N, N, N) representing the density at each grid point.
        ds: The distance between adjacent grid points.
        G: The gravitational constant.

    Returns:
        A tuple of NumPy arrays (gx, gy, gz) representing the gravitational acceleration components.
    """

    N = density.shape[0]
    assert N % 8 == 0, "N must be a multiple of 8"

    # Allocate output arrays
    gx = tl.zeros((N, N, N), dtype=tl.float32)
    gy = tl.zeros((N, N, N), dtype=tl.float32)
    gz = tl.zeros((N, N, N), dtype=tl.float32)

    # Launch the kernel
    grid = (N * N * N,)
    calculate_gravity[grid](density, gx, gy, gz, N=N, ds=ds, G=G)

    return gx.to_numpy(), gy.to_numpy(), gz.to_numpy()
  
import numpy as np

# Generate a random density grid
N = 64
density = np.random.rand(N, N, N).astype(np.float32)
ds = 1.0  # Distance between grid points

# Calculate gravity
gx, gy, gz = gravity_grid(density, ds)

print(gx.shape, gy.shape, gz.shape)  # Output: (64, 64, 64) (64, 64, 64) (64, 64, 64)