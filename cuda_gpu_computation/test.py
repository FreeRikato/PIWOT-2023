import tensorflow as tf
import sys
print(sys.executable)
print("TensorFlow Version:", tf.__version__)
print("Is GPU Available:", tf.test.is_gpu_available())
print("Is Built With CUDA:", tf.test.is_built_with_cuda())
print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))
print("CUDA version:", tf.sysconfig.get_build_info()["cuda_version"])
print("cuDNN version:", tf.sysconfig.get_build_info()["cudnn_version"])