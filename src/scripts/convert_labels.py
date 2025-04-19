import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
import os
import PIL.Image
import src.util.log as log

from typing import List
from labelme import utils as lm_utils
from labelme.label_file import LabelFile
from torchvision.io import read_image
from src.ml.model import get_transform, train_model
from src.ml.NaipDataset import NaipDataset


data_dir = os.path.normpath(f"{__file__}/../../../data")
label_dir = f"{data_dir}/NaipSat/labels"
out_dir = f"{data_dir}/NaipSat"
classes = ["background", "building", "tree"]


def convert_labeled_data(label_dir: str, out_dir: str, classes: List[str]):
    """Convert all JSON label annotations in a given folder to images/masks needed by PyTorch."""

    file_names = [f for f in os.listdir(label_dir) if f.endswith(".json")]
    log.msg(f"Convert {len(file_names)} JSON label files")

    for file_name in file_names:
        file_path = os.path.join(label_dir, file_name)
        file_stub = file_name.split(".")[:-1][0]

        # Adapted from https://github.com/wkentaro/labelme/blob/main/labelme/cli/export_json.py
        label_file: LabelFile = LabelFile(file_path)
        image: npt.NDArray[np.uint8] = lm_utils.img_data_to_arr(label_file.imageData)
        label_name_to_value = dict(zip(classes, range(0, len(classes))))
        # FIX: Correct the point order in rectangles (o/w ImageDraw will complain)
        for shape in label_file.shapes:
            if shape["shape_type"] == "rectangle":
                x0, y0 = shape["points"][0]
                x1, y1 = shape["points"][1]
                if x1 < x0:
                    shape["points"][0][0] = x1
                    shape["points"][1][0] = x0
                if y1 < y0:
                    shape["points"][0][1] = y1
                    shape["points"][1][1] = y0
        # END FIX
        lbl, _ = lm_utils.shapes_to_label(
            image.shape, label_file.shapes, label_name_to_value
        )
        log.info(file_stub)
        PIL.Image.fromarray(image).save(
            os.path.join(out_dir, f"images/{file_stub}.png")
        )
        lm_utils.lblsave(os.path.join(out_dir, f"masks/{file_stub}_mask.png"), lbl)

    log.success("Done")


if __name__ == "__main__":
    convert_labeled_data(label_dir, out_dir, classes)
