import numpy as np
from keras.applications.inception_v3 import InceptionV3
from keras.models import Sequential, load_model, Model
from keras.layers import Input, Dropout, Flatten, Conv2D, MaxPooling2D, Dense, Activation, GlobalAveragePooling2D
from keras.optimizers import SGD
from keras.utils import np_utils
from keras.preprocessing.image import ImageDataGenerator
from keras.callbacks import TensorBoard
import itertools
# In[1]:import lib
# all images will be converted to this size
ROWS = 256
COLS = 256
CHANNELS = 3
# In[1]:import lib
train_image_generator = ImageDataGenerator(horizontal_flip=True, rescale=1./255, rotation_range=45)
test_image_generator = ImageDataGenerator(horizontal_flip=False, rescale=1./255, rotation_range=0)
# In[1]:import lib
train_generator = train_image_generator.flow_from_directory('train', target_size=(ROWS, COLS), class_mode='categorical')
test_generator = test_image_generator.flow_from_directory('test', target_size=(ROWS, COLS), class_mode='categorical')
# In[1]:import lib
# create the base pre-trained model
base_model = InceptionV3(weights='imagenet', include_top=False)
# In[1]:import lib
# add a global spatial average pooling layer
x = base_model.output
x = GlobalAveragePooling2D()(x)
# add a fully-connected layer
x = Dense(1024, activation='relu')(x)
out_layer = Dense(200, activation='softmax')(x)
# In[1]:import lib
# this is the model we will train
model = Model(inputs=base_model.input, outputs=out_layer)
# In[1]:import lib
# first: train only the top layers (which were randomly initialized)
# i.e. freeze all convolutional InceptionV3 layers
for layer in base_model.layers:
    layer.trainable = False
# In[1]:import lib
model.compile(loss='categorical_crossentropy', optimizer='rmsprop', metrics=['accuracy'])

print(model.summary())
# In[1]:import lib
tensorboard = TensorBoard(log_dir='./logs/inceptionv3')
# In[1]:import lib
model.fit_generator(train_generator, steps_per_epoch=32, epochs=100, callbacks=[tensorboard], verbose=2)
# In[1]:import lib
print(model.evaluate_generator(test_generator, steps=5000))
# In[1]:import lib
# unfreeze all layers for more training
for layer in model.layers:
    layer.trainable = True
# In[1]:import lib
# we need to recompile the model for these modifications to take effect
# we use SGD with a low learning rate
model.compile(optimizer=SGD(lr=0.0001, momentum=0.9), loss='categorical_crossentropy', metrics=['accuracy'])
# In[1]:import lib
model.fit_generator(train_generator, steps_per_epoch=32, epochs=100)
# In[1]:import lib
test_generator.reset()
print(model.evaluate_generator(test_generator, steps=5000))
# In[1]:import lib
model.save("birds-inceptionv3.model")

