import torch
print(torch.cuda.is_available())
print(torch.__version__)
import tensorflow as tf
print(tf.test.is_gpu_available(
    cuda_only=False,
    min_cuda_compute_capability=None
))