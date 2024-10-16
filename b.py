import torch

def get_upper_half_canvas(ds1, idx):
  """
  Extracts the upper half of an image from a dataset.

  Args:
    ds1: The dataset containing the image.
    idx: The index of the image in the dataset.

  Returns:
    A torch.Tensor representing the upper half of the image.
  """
  canvas = ds1[idx]['grid']
  _, height, _ = canvas.shape
  half_height = height // 2
  canvas2 = torch.clone(canvas)  # Create a copy to avoid modifying the original
  canvas2[:, :half_height, :] = ds1[idx - 1]['grid'][:, :half_height, :]
  return canvas2

# Example usage:
# Assuming ds1 is your dataset and idx is the index of the current image
canvas2 = get_upper_half_canvas(ds1, idx)
print(canvas2.shape)  # Output: torch.Size([3, 224, 224])