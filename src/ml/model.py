import builtins
import src.util.log as log
import torch
import torchvision
import src.ml.torchvision.utils as tv_utils

from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.models.detection.mask_rcnn import MaskRCNNPredictor, MaskRCNN
from torch.utils.data import Dataset
from torchvision.transforms import v2 as T
from src.ml.torchvision.engine import train_one_epoch, evaluate
from torch._prims_common import DeviceLikeType


# Adapted from https://pytorch.org/tutorials/intermediate/torchvision_tutorial.html
def get_model(num_classes) -> MaskRCNN:
    """Construct a pre-trained segmentation model ready for finetuning."""

    # Load instance segmentation model pre-trained on COCO
    model = torchvision.models.detection.maskrcnn_resnet50_fpn(weights="DEFAULT")

    # Get number of input features for the classifier
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    # Replace pre-trained head with a new one
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)

    # Get the number of input features for the mask classifier
    in_features_mask = model.roi_heads.mask_predictor.conv5_mask.in_channels
    hidden_layer = 256
    # ... and replace the mask predictor with a new one
    model.roi_heads.mask_predictor = MaskRCNNPredictor(in_features_mask, hidden_layer, num_classes)

    return model


# Adapted from https://pytorch.org/tutorials/intermediate/torchvision_tutorial.html
def get_transform(train: bool):
    """Create an image transformation for model testing/training."""
    transforms = []
    if train:
        transforms.append(T.RandomHorizontalFlip(0.5))
    transforms.append(T.ToDtype(torch.float, scale=True))
    transforms.append(T.ToPureTensor())

    return T.Compose(transforms)


def get_device() -> DeviceLikeType:
    """Gets the best device for training/inference - GPU/metal if available, CPU as a fallback."""

    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


# Adapted from https://pytorch.org/tutorials/intermediate/torchvision_tutorial.html
def train_model(ds_train: Dataset, ds_test: Dataset, num_classes: int, num_epochs: int) -> MaskRCNN:
    """Train the segmentation model with the given data."""

    # Train on GPU/Metal if possible, else fall back to the CPU
    device = get_device()
    log.msg(f"Train segmentation model on {device}")

    # Split the dataset into training and test set
    n = len(ds_train)
    train_size = round(n * 0.8)
    indices = torch.randperm(n).tolist()
    dataset_train = torch.utils.data.Subset(ds_train, indices[:train_size])
    dataset_test = torch.utils.data.Subset(ds_test, indices[train_size:])
    log.info(f"{train_size} training images, {n-train_size} test images")

    # define training and validation data loaders
    data_loader = torch.utils.data.DataLoader(
        dataset_train, batch_size=2, shuffle=True, collate_fn=tv_utils.collate_fn
    )
    data_loader_test = torch.utils.data.DataLoader(
        dataset_test, batch_size=1, shuffle=False, collate_fn=tv_utils.collate_fn
    )

    # Get the model and move it to the right device
    model = get_model(num_classes)
    model.to(device)

    # Construct an optimizer and a learning rate scheduler
    params = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.SGD(params, lr=0.005, momentum=0.9, weight_decay=0.0005)
    lr_scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=3, gamma=0.1)

    # Train
    log.info(f"Stochastic gradient descent, {num_epochs} epochs:")
    normal_print = builtins.print
    builtins.print = lambda x, *args, **kwargs: normal_print("   ", x, *args, **kwargs)
    for epoch in range(num_epochs):
        # Print every 10 iterations per epoch
        train_one_epoch(model, optimizer, data_loader, device, epoch, print_freq=10)
        # Update the learning rate
        lr_scheduler.step()
        # Evaluate on the test dataset
        evaluate(model, data_loader_test, device=device)
    builtins.print = normal_print

    log.success("Done")
    return model


def predict_objects(model: MaskRCNN, image: torch.Tensor):
    """Predict which objects (classes, bounding boxes and segmentation masks) are present in a given image."""

    mpsAvailable = torch.backends.mps.is_available()
    device = torch.device("cpu")
    transform = get_transform(train=False)

    with torch.no_grad():
        x = transform(image)
        # Convert RGBA -> RGB and move to device
        x = x[:3, ...].to(device)
        predictions = model(
            [
                x,
            ]
        )
        pred = predictions[0]
        return pred


def save_model(model: MaskRCNN, path: str):
    """Save a trained model to disk."""
    torch.save(model, path)


def load_model(path: str) -> MaskRCNN:
    """Load a trained model from disk."""
    model = torch.load(path, weights_only=False)
    model.eval()
    return model
