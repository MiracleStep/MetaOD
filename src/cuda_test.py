import torch
print(torch.cuda.is_available())
print(torch.__version__)
import tensorflow as tf
print(tf.config.list_physical_devices('GPU'))