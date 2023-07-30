import tensorflow as tf
import json
import numpy as np
from matplotlib import pyplot as plt
import os

gpus = tf.config.experimental.list_physical_devices('GPU')
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)


### Load image into TF data pipeline

IMAGES_PATH = os.path.join(os.path.dirname(__file__),'data','images')
print(IMAGES_PATH)

images = tf.data.Dataset.list_files(IMAGES_PATH + '/*.jpg', shuffle=False)
# print(images.as_numpy_iterator().next())

def load_image(x): 
    byte_img = tf.io.read_file(x)
    img = tf.io.decode_jpeg(byte_img)
    return img

images = images.map(load_image)
images.as_numpy_iterator().next()
# print(type(images)) 

### Viewing raw images using matplotlib

image_generator = images.batch(4).as_numpy_iterator()
plot_images = image_generator.next()
fig, ax = plt.subplots(ncols=4, figsize=(20,20))
for idx, image in enumerate(plot_images):
    ax[idx].imshow(image) 
plt.show()