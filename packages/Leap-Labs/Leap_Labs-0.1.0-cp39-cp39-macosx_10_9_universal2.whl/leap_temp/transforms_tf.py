import tensorflow as tf
import numpy as np


def get_transforms(transf, preprocessing, alpha=True):
    if type(preprocessing) is list:
        transforms = [prep for prep in preprocessing]
    elif preprocessing is not None:
        transforms = [preprocessing]
    else:
        transforms = []

    if alpha:
        transforms = [add_alpha()] + transforms

    if transf == "s":
        transforms.append(
            random_transform(degrees=5, translate=(
                0.05, 0.05), scale=(0.95, 1.05))
        )
    if transf == "m":
        transforms.append(
            random_transform(degrees=10, translate=(
                0.05, 0.05), scale=(0.9, 1.1))
        )
    if transf == "l":
        transforms.append(
            random_transform(degrees=20, translate=(
                0.1, 0.1), scale=(0.8, 1.2))
        )
    if transf == "xl":
        transforms.append(
            random_transform(degrees=30, translate=(
                0.2, 0.2), scale=(0.7, 1.3))
        )
    if transf == "best":
        transforms.append(
            random_transform(degrees=30, translate=(
                0.5, 0.5), scale=(0.8, 1.2))
        )

    return transforms


def random_transform(degrees=30, translate=(0.2, 0.2), scale=(0.7, 1.3)):
    def inner(x):
        angle = np.random.randint(-degrees, degrees)
        factor = angle / 360.0  # Convert angle to a fraction of 360 degrees
        scaling = scale[0] + (np.random.rand() * (scale[1] - scale[0]))

        x = tf.keras.layers.experimental.preprocessing.Rescaling(
            scale=scaling)(x)
        x = tf.keras.layers.experimental.preprocessing.RandomTranslation(
            height_factor=translate[0], width_factor=translate[1]
        )(x)
        x = tf.keras.layers.experimental.preprocessing.RandomRotation(
            factor=abs(factor)
        )(x)
        return x

    return inner


def sigmoid(x):
    return tf.sigmoid(x)


def add_alpha(sigmoid=False):
    def inner(x):
        bgd = tf.random.uniform(
            [1, x.shape[1], x.shape[2], x.shape[3] - 1], dtype=x.dtype
        ) * tf.reduce_max(x)

        alpha = x[:, :, :, -1:]

        if sigmoid:
            alpha = tf.sigmoid(alpha)
        else:
            alpha = tf.clip_by_value(alpha, 0, 1)

        input = x[:, :, :, :-1]

        xa = (input * alpha) + (bgd * (1 - alpha))
        return xa

    return inner


def get_mask(dims):
    dim = max(dims)
    r = tf.range(dim, dtype=tf.float32)
    mask1d = dim - 1 - tf.abs(r - tf.reverse(r, axis=[-1]))
    mask = tf.linalg.matmul(tf.expand_dims(mask1d, -1),
                            tf.expand_dims(mask1d, 0))
    mask = normalise(mask)
    return mask


def compose(transforms):
    def inner(x):
        for transform in transforms:
            x = transform(x)
        return x

    return inner


def normalise(x):
    x_min = tf.reduce_min(x)
    x_max = tf.reduce_max(x)
    return (x - x_min) / (x_max - x_min)


def normalise_each(x):
    return tf.map_fn(
        lambda n: normalise(n) if tf.math.reduce_max(
            n) != tf.math.reduce_min(n) else n,
        x,
    )


def p_sigmoid(x, c=4):
    return 1 / (1 + tf.exp(-c * x))


def img_normalise(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)):
    def inner(x):
        return (x - mean) / std

    return inner
