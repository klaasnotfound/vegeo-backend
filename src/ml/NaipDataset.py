import os
import torch

from torchvision.io import read_image
from torchvision.ops.boxes import masks_to_boxes
from torchvision import tv_tensors
from torchvision.transforms.v2 import functional as F

data_dir = os.path.normpath(f"{__file__}/../../../data")
imgs_dir = f"{data_dir}/NaipSat/images"
masks_dir = f"{data_dir}/NaipSat/masks"


# Adapted from https://pytorch.org/tutorials/intermediate/torchvision_tutorial.html
class NaipDataset(torch.utils.data.Dataset):
    """Dataset loader for NAIP satellite images"""

    def __init__(self, transforms):
        self.transforms = transforms
        self.imgs = [f for f in sorted(os.listdir(imgs_dir)) if f.endswith(".png")]
        self.masks = [f for f in sorted(os.listdir(masks_dir)) if f.endswith(".png")]

    def __getitem__(self, idx):
        # Load image and mask
        img_path = os.path.join(imgs_dir, self.imgs[idx])
        mask_path = os.path.join(masks_dir, self.masks[idx])
        img = read_image(img_path)
        mask = read_image(mask_path)

        # Instances are encoded as different colors
        obj_ids = torch.unique(mask)
        # First id is the background, so we remove it
        obj_ids = obj_ids[1:]
        num_objs = len(obj_ids)

        # Split color-encoded mask into a set of binary masks
        masks = (mask == obj_ids[:, None, None]).to(dtype=torch.uint8)
        # Get the bounding box coordinates for each mask
        boxes = masks_to_boxes(masks)
        # There is only one class
        labels = torch.ones((num_objs,), dtype=torch.int64)

        image_id = idx
        area = (boxes[:, 3] - boxes[:, 1]) * (boxes[:, 2] - boxes[:, 0])
        iscrowd = torch.zeros((num_objs,), dtype=torch.int64)

        # Wrap sample and targets into torchvision tv_tensors:
        img = tv_tensors.Image(img)

        target = {}
        target["boxes"] = tv_tensors.BoundingBoxes(
            boxes, format="XYXY", canvas_size=F.get_size(img)
        )
        target["masks"] = tv_tensors.Mask(masks)
        target["labels"] = labels
        target["image_id"] = image_id
        target["area"] = area
        target["iscrowd"] = iscrowd

        if self.transforms is not None:
            img, target = self.transforms(img, target)

        return img, target

    def __len__(self):
        return len(self.imgs)
