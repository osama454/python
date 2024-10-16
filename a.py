import triton_python_backend_utils as pb_utils
import numpy as np

def _get_gx_gy_gz(density, ds):
    """
    Computes the gravitational acceleration components (gx, gy, gz) for each gridpoint 
    in a 3D density grid.

    Args:
        density: A 3D numpy array of shape (N, N, N) representing the density at each 
                 gridpoint, where N is a multiple of 8.
        ds: The distance between any two adjacent gridpoints.

    Returns:
        A tuple containing three 3D numpy arrays of shape (N, N, N) representing gx, gy, and gz 
        respectively.
    """
    N = density.shape[0]
    gx = np.zeros_like(density, dtype=np.float32)
    gy = np.zeros_like(density, dtype=np.float32)
    gz = np.zeros_like(density, dtype=np.float32)
    G = 6.67430e-11  # Gravitational constant

    for i in range(N):
        for j in range(N):
            for k in range(N):
                for ii in range(N):
                    for jj in range(N):
                        for kk in range(N):
                            if (i, j, k) != (ii, jj, kk):
                                dx = (ii - i) * ds
                                dy = (jj - j) * ds
                                dz = (kk - k) * ds
                                dist_sq = dx**2 + dy**2 + dz**2
                                dist = np.sqrt(dist_sq)
                                force = G * density[i, j, k] * density[ii, jj, kk] / dist_sq

                                gx[i, j, k] += force * dx / dist
                                gy[i, j, k] += force * dy / dist
                                gz[i, j, k] += force * dz / dist

    return gx, gy, gz

def triton_python_model_repository(
    model_config,
    repository_path,
    request_header,
    request_body,
):
    """
    Triton Python model that computes gx, gy, and gz for a given density grid.

    Args:
        model_config: The model configuration.
        repository_path: The path to the model repository.
        request_header: The request header.
        request_body: The request body.

    Returns:
        A tuple containing the response header and response body.
    """
    input_tensors = pb_utils.get_input_tensors(request_body)
    density = pb_utils.get_input_tensor_by_name(input_tensors, "density")
    ds = pb_utils.get_input_tensor_by_name(input_tensors, "ds")

    if density is None:
        raise pb_utils.InferenceServerException(
            msg="Missing input tensor 'density'.",
            status=pb_utils.TRITONSERVER_ERROR_INVALID_ARG,
        )
    if ds is None:
        raise pb_utils.InferenceServerException(
            msg="Missing input tensor 'ds'.",
            status=pb_utils.TRITONSERVER_ERROR_INVALID_ARG,
        )

    density = density.as_numpy()
    ds = ds.as_numpy()

    gx, gy, gz = _get_gx_gy_gz(density, ds)

    output_tensors = [
        pb_utils.Tensor("gx", gx),
        pb_utils.Tensor("gy", gy),
        pb_utils.Tensor("gz", gz),
    ]

    inference_response = pb_utils.InferenceResponse(output_tensors=output_tensors)
    return inference_response.http_body(), None