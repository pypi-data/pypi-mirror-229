import torch
from torchvision.transforms import Normalize
from torchvision.transforms.functional import affine, InterpolationMode


def get_transforms(tf, preprocessing, alpha=True):
    if type(preprocessing) is list:
        transforms = [prep for prep in preprocessing]
    elif preprocessing is not None:
        transforms = [preprocessing]
    else:
        transforms = []

    if alpha:
        transforms = [add_alpha()] + transforms

    if tf == "s":
        transforms.append(
            random_transform(degrees=5, translate=(
                0.05, 0.05), scale=(0.95, 1.05))
        )
    if tf == "m":
        transforms.append(
            random_transform(degrees=10, translate=(
                0.05, 0.05), scale=(0.9, 1.1))
        )
    if tf == "l":
        transforms.append(
            random_transform(degrees=20, translate=(
                0.1, 0.1), scale=(0.8, 1.2))
        )
    if tf == "xl":
        transforms.append(
            random_transform(degrees=30, translate=(
                0.2, 0.2), scale=(0.7, 1.3))
        )
    if tf == "best":
        transforms.append(
            random_transform(degrees=30, translate=(
                0.5, 0.5), scale=(0.8, 1.2))
        )

    return transforms


def random_transform(
    degrees=30,
    translate=(0.2, 0.2),
    scale=(0.7, 1.3),
    interpolation=InterpolationMode.NEAREST,
):
    def inner(x):
        tfx = affine(
            x,
            angle=torch.randint(-degrees, degrees, (1,)).item(),
            translate=[
                x.shape[-2] * torch.rand(1) * translate[0],
                x.shape[-1] * torch.rand(1) * translate[1],
            ],
            scale=scale[0] + (torch.rand(1) * (scale[1] - scale[0])),
            shear=0,
            interpolation=interpolation,
            fill=-1,
        )

        transformed = []
        for t in range(tfx.shape[0]):
            transformed.append(
                torch.where(
                    tfx[t] == -1,
                    (torch.rand_like(x[t]) *
                     (x[t].amax() - x[t].amin())) + x[t].amin(),
                    tfx[t],
                )
            )
        del tfx
        return torch.stack(transformed)

    return inner


def sigmoid(x):
    return torch.sigmoid(x)


def add_alpha(sigmoid=False):
    def inner(x):
        bgd = torch.rand_like(x[:1, :-1]) * x.max()
        alpha = x[:, -1:]

        if sigmoid:
            alpha = torch.sigmoid(alpha)
        else:
            alpha = torch.clamp(alpha, 0, 1)

        input = x[:, :-1]
        xa = (input * alpha) + (bgd * (1 - alpha))

        return xa

    return inner


def get_mask(dims):
    dim = max(dims)
    r = torch.arange(dim)
    mask1d = dim - 1 - torch.abs(r - torch.flip(r, [0]))
    mask = torch.outer(mask1d, mask1d)
    mask = normalise(mask)
    return mask


def compose(transforms):
    def inner(x):
        for transform in transforms:
            x = transform(x)
        return x

    return inner


def normalise(x):
    x = (x - x.min()) / (x.max() - x.min() + 1e-9)
    return x


def normalise_each(x):
    min_vals = x.amin(dim=(-1, -2, -3), keepdim=True)
    max_vals = x.amax(dim=(-1, -2, -3), keepdim=True)
    denom = max_vals - min_vals + 1e-9
    normalised = (x - min_vals) / denom
    return normalised


def p_sigmoid(x, c=4):
    return 1 / (1 + torch.exp(-c * x))


def img_normalise(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)):
    normal = Normalize(mean=list(mean), std=list(std))

    def inner(x):
        return normal(x)

    return inner
