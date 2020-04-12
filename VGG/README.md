![VGG16_ImageNet](https://www.pyimagesearch.com/wp-content/uploads/2017/03/imagenet_vgg16.png)

Figure 1: A visualization of the VGG architecture [(source)](https://www.cs.toronto.edu/~frossard/post/vgg16/).

The VGG network architecture was introduced by Simonyan and Zisserman in their 2014 paper, 
[Very Deep Convolutional Networks for Large Scale Image Recognition](https://arxiv.org/abs/1409.1556).


This network is characterized by its simplicity, using only 3×3 convolutional layers stacked on top of each other in increasing depth. 
Reducing volume size is handled by max pooling. Two fully-connected layers, each with 4,096 nodes are then followed by a softmax classifier (above).

It's major advantage over AlexNet is all the kernels are of size (3\*3) with Stride = 1 and Padding = ‘Same’ and same case with MaxPool with size (2*2) and stride = 2.


<br></br>
**Application**:

* Given image → find object name in the image
* It can detect any one of 1000 images
* It takes input image of size 224 * 224 * 3 (RGB image)

**Built using**:

* Convolutions layers (used only 3*3 size )
* Max pooling layers (used only 2*2 size)
* Fully connected layers at end
* Total 16 layers

<br></br>
**Model size**: 528 MB

**Pre trained model** [(Tensorflow)](https://www.cs.toronto.edu/~frossard/vgg16/vgg16_weights.npz)

**Top-1 Accuracy**: 70.5%

**Top-5 Accuracy**: 90.0%

**Built by**: [Visual Geometry Group](http://www.robots.ox.ac.uk/~vgg/)

**Variant**: VGG-19
<br></br>
**Description of layers**:

![alt text](https://qphs.fs.quoracdn.net/main-qimg-83c7dee9e8b039c3ca27c8dd91cacbb4)


1.   Convolution using 64 filters
2. Convolution using 64 filters + Max pooling
3. Convolution using 128 filters
4. Convolution using 128 filters + Max pooling
5. Convolution using 256 filters
6. Convolution using 256 filters
6. Convolution using 256 filters + Max pooling
6. Convolution using 512 filters
6. Convolution using 512 filters
6. Convolution using 512 filters + Max pooling
6. Convolution using 512 filters
6. Convolution using 512 filters
6. Convolution using 512 filters + Max pooling
6. Fully connected with 4096 nodes
6. Fully connected with 4096 nodes
6. Output layer with Softmax activation with 1000 nodes

**Code Snippet: (Keras native implementation)**
```
# Block 1
    x = layers.Conv2D(64, (3, 3),
                      activation='relu',
                      padding='same',
                      name='block1_conv1')(img_input)
    x = layers.Conv2D(64, (3, 3),
                      activation='relu',
                      padding='same',
                      name='block1_conv2')(x)
    x = layers.MaxPooling2D((2, 2), strides=(2, 2), name='block1_pool')(x)

    # Block 2
    x = layers.Conv2D(128, (3, 3),
                      activation='relu',
                      padding='same',
                      name='block2_conv1')(x)
    x = layers.Conv2D(128, (3, 3),
                      activation='relu',
                      padding='same',
                      name='block2_conv2')(x)
    x = layers.MaxPooling2D((2, 2), strides=(2, 2), name='block2_pool')(x)

    # Block 3
    x = layers.Conv2D(256, (3, 3),
                      activation='relu',
                      padding='same',
                      name='block3_conv1')(x)
    x = layers.Conv2D(256, (3, 3),
                      activation='relu',
                      padding='same',
                      name='block3_conv2')(x)
    x = layers.Conv2D(256, (3, 3),
                      activation='relu',
                      padding='same',
                      name='block3_conv3')(x)
    x = layers.MaxPooling2D((2, 2), strides=(2, 2), name='block3_pool')(x)

    # Block 4
    x = layers.Conv2D(512, (3, 3),
                      activation='relu',
                      padding='same',
                      name='block4_conv1')(x)
    x = layers.Conv2D(512, (3, 3),
                      activation='relu',
                      padding='same',
                      name='block4_conv2')(x)
    x = layers.Conv2D(512, (3, 3),
                      activation='relu',
                      padding='same',
                      name='block4_conv3')(x)
    x = layers.MaxPooling2D((2, 2), strides=(2, 2), name='block4_pool')(x)

    # Block 5
    x = layers.Conv2D(512, (3, 3),
                      activation='relu',
                      padding='same',
                      name='block5_conv1')(x)
    x = layers.Conv2D(512, (3, 3),
                      activation='relu',
                      padding='same',
                      name='block5_conv2')(x)
    x = layers.Conv2D(512, (3, 3),
                      activation='relu',
                      padding='same',
                      name='block5_conv3')(x)
    x = layers.MaxPooling2D((2, 2), strides=(2, 2), name='block5_pool')(x)

    if include_top:
        # Classification block
        x = layers.Flatten(name='flatten')(x)
        x = layers.Dense(4096, activation='relu', name='fc1')(x)
        x = layers.Dense(4096, activation='relu', name='fc2')(x)
        x = layers.Dense(classes, activation='softmax', name='predictions')(x)
    else:
        if pooling == 'avg':
            x = layers.GlobalAveragePooling2D()(x)
        elif pooling == 'max':
            x = layers.GlobalMaxPooling2D()(x)
```

* Pre-trained model is also readily available in Keras for use

**Sources**:

[Stack Overflow Answer by Yugandhar Nanda](https://qr.ae/pNrI4J)

[VGG in TensorFlow](https://www.cs.toronto.edu/~frossard/post/vgg16/)

[VGG 16 - Keras](https://github.com/keras-team/keras-applications/blob/master/keras_applications/vgg16.py)
