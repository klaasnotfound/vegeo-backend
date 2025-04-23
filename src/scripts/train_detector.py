import matplotlib.pyplot as plt
import os
import torch

from torchvision.io import read_image
from src.ml.model import (
    get_transform,
    train_model,
    save_model,
    load_model,
    predict_objects,
)
from src.ml.NaipDataset import NaipDataset
from torchvision.utils import draw_bounding_boxes, draw_segmentation_masks


data_dir = os.path.normpath(f"{__file__}/../../../data")
state_dir = f"{data_dir}/model"
classes = ["background", "building", "tree"]
colors = ["black", "red", "green"]
num_epochs = 2
model_path = f"{state_dir}/MaskRCNN_NAIP_{num_epochs}.pt"


def train_and_persist():
    dataset_train = NaipDataset(get_transform(train=True))
    dataset_test = NaipDataset(get_transform(train=False))
    model = train_model(dataset_train, dataset_test, len(classes), num_epochs)
    save_model(model, model_path)


def predict(img_name: str):
    img_path = f"{data_dir}/NaipSat/images/{img_name}.png"
    image = read_image(img_path)
    model = load_model(model_path)
    pred = predict_objects(model, image)

    image = (255.0 * (image - image.min()) / (image.max() - image.min())).to(torch.uint8)
    image = image[:3, ...]
    pred_labels = [f"{classes[label]}: {score:.3f}" for label, score in zip(pred["labels"], pred["scores"])]
    pred_colors = [colors[label] for label in pred["labels"]]
    pred_boxes = pred["boxes"].long()
    output_image = draw_bounding_boxes(image, pred_boxes, pred_labels, pred_colors)

    masks = (pred["masks"] > 0.2).squeeze(1)
    output_image = draw_segmentation_masks(output_image, masks, alpha=0.5, colors="blue")

    plt.figure(figsize=(8, 8))
    plt.imshow(output_image.permute(1, 2, 0))
    plt.show()


def show_masks():
    image = read_image(f"{data_dir}/NaipSat/images/naip_17_49664_34188.png")
    mask = read_image(f"{data_dir}/NaipSat/masks/naip_17_49664_34188_mask.png")

    plt.figure(figsize=(16, 8))
    plt.subplot(121)
    plt.title("Image")
    plt.imshow(image.permute(1, 2, 0))
    plt.subplot(122)
    plt.title("Mask")
    plt.imshow(mask.permute(1, 2, 0))

    plt.show()


if __name__ == "__main__":
    train_and_persist()
    # predict("naip_17_51875_32785")
