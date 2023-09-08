from __future__ import annotations

import glob
import logging as log
import math
import os
import textwrap
from pathlib import Path
from typing import List, Union

import numpy as np
import torch
from rich.progress import track
from scipy.io import loadmat, savemat
from torch.utils.data import Dataset

import lidar_camera_calibration.general as gn
from lidar_camera_calibration.tools import dataset, image, point_cloud2, rosbag
from lidar_camera_calibration.tools.timestamp_np import TimeStamp


def expected_directory_structure(root: Path = None) -> str:
    if root is None:
        root = "."
    else:
        assert root.is_dir(), f"Expected {root} to be a directory!"
    sub_dirs = ["raw", "compressed", "results"]
    sub_notes = [
        "Raw bag file(s) and camera_params.yaml initial calibration file.",
        "(generated) Data compressed into calibration frames that have been associated in time. Data files are .mat files with img, rPLl, and intensities fields.",
        "(generated) Directory containing the results of the calibration.",
    ]
    title = f"The expected directory structure within {root} is"
    lines = []
    max_len = 0
    for dir in sub_dirs:
        max_len = max(max_len, len(dir))
    for i in range(len(sub_dirs)):
        sub_dir = sub_dirs[i]
        sub_note = sub_notes[i]
        line_start = "{val:>{len}s}: ".format(len=max_len, val=sub_dir)

        line = f"{line_start}{sub_note}"
        line_wrapped = textwrap.wrap(
            line, width=80, subsequent_indent=" " * len(line_start)
        )
        for l in line_wrapped:
            lines.append(l)
    outstr = f"{title}:\n" + "\n".join(lines)
    return outstr


def is_file_with_extension(data_path: Path, ext: str) -> bool:
    if data_path.is_file():
        if data_path.name.split(".")[-1] in ext:
            return True
    return False


def expand_bag_path(data_path: Path) -> Union[Path, List[Path]]:
    """Guess which dataloader to use in case the user didn't specify with --dataloader flag.

    TODO: Avoid having to return again the data Path. But when guessing multiple .bag files or the
    metadata.yaml file, we need to change the Path specified by the user.
    """
    if is_file_with_extension(data_path, "bag"):
        return data_path
    elif data_path.is_dir():
        bagfiles = [Path(path) for path in glob.glob(os.path.join(data_path, "*.bag"))]
        if len(bagfiles) > 0:
            return bagfiles
    else:
        raise Exception(
            f'Input argument "data" does not point to a file or a directory. Ensure {data_path} exists!'
        )


class CalibrationFrame:
    def __init__(self, img: np.ndarray, rPLl: np.ndarray, intensities: np.ndarray):
        rPLl_size_str = "x".join([f"{s}" for s in rPLl.shape])
        assert (
            rPLl.shape[0] == 3
        ), f"Expected rPLl to be a 3xN array, but it has size {rPLl_size_str}"

        intensity_size_str = "x".join(f"{s}" for s in intensities.shape)
        assert (
            intensities.shape[0] == 1
        ), f"Expected intensity to be a 1xN array, but it has size {intensity_size_str}"

        self.img = img
        self.rPLl = rPLl
        self.intensities = intensities

    def toMATLAB(self, file_path: Path):
        data = dict()
        data["img"] = self.img
        data["rPLl"] = self.rPLl
        data["intensities"] = self.intensities
        savemat(gn.add_extension(file_path, "mat"), data)

    @staticmethod
    def fromMATLAB(file_path: Path) -> CalibrationFrame:
        data = loadmat(gn.add_extension(file_path, "mat"))
        img = data["img"]
        rPLl = data["rPLl"]
        intensities = data["intensities"]
        return CalibrationFrame(img, rPLl, intensities)


def compressed_data_to_calibration_frames(
    compressed_data_dir: Path,
) -> List[CalibrationFrame]:
    assert (
        compressed_data_dir.is_dir()
    ), f"Expected {compressed_data_dir} to be a directory!"
    mat_files = [
        os.path.join(compressed_data_dir, f)
        for f in os.listdir(compressed_data_dir)
        if os.path.isfile(os.path.join(compressed_data_dir, f))
        and f.startswith("frame-")
        and f.endswith(".mat")
    ]
    mat_files.sort()
    print(f"Retrieving calibration data from MATLAB files in {compressed_data_dir}.")
    data_frames = []
    for mat_file in track(
        mat_files,
        description=f"Loading {len(mat_files)} files.",
    ):
        data = CalibrationFrame.fromMATLAB(mat_file)
        data_frames.append(data)

    return data_frames


def calibration_frames_to_compressed_data(
    compressed_data_dir: Path, calframes: List[CalibrationFrame]
) -> None:
    assert (
        compressed_data_dir.is_dir()
    ), f"Expected {compressed_data_dir} to be a directory!"

    print(f"Saving data into {compressed_data_dir}")
    nframes = len(calframes)
    ndigits = int(math.ceil(math.log10(nframes)))
    for i in track(
        range(nframes),
        description="Writing calibration frames to MATLAB files.",
    ):
        calframe = calframes[i]
        filename = "frame-{val:0{ndigits}d}".format(ndigits=ndigits, val=i)
        filepath = os.path.join(compressed_data_dir, filename)
        calframe.toMATLAB(filepath)


def bagfile_to_calibration_frames(
    bag_file_path: Path, lidar_topic: str, image_topic: str
) -> List[CalibrationFrame]:
    bag_files = expand_bag_path(bag_file_path)

    lidar_bag_data = rosbag.RosbagDataset(
        bag_files, lidar_topic, "lidar_topic", "sensor_msgs/msg/PointCloud2"
    )
    image_bag_data = rosbag.RosbagDataset(
        bag_files, image_topic, "image_topic", "sensor_msgs/msg/Image"
    )

    lidar_msg = lidar_bag_data[0]
    lidar_points, lidar_time = point_cloud2.read_point_cloud(
        lidar_msg, read_intensity=True
    )

    lidar_dataset_points = []
    lidar_dataset_time = []
    for lidar_msg in track(
        lidar_bag_data, description="Retrieving LiDAR data from bag file."
    ):
        lidar_points, lidar_time = point_cloud2.read_point_cloud(
            lidar_msg, read_intensity=True
        )
        lidar_dataset_points.append(lidar_points)
        lidar_dataset_time.append(lidar_time)
    lidar_dataset_points = np.concatenate(lidar_dataset_points, axis=0)

    sec = np.concatenate([t.sec for t in lidar_dataset_time], axis=0)
    nsec = np.concatenate([t.nsec for t in lidar_dataset_time], axis=0)
    lidar_dataset_time = TimeStamp(sec, nsec)
    npoints = lidar_dataset_time.size()

    image_dataset_images = []
    image_dataset_time = []
    for image_msg in track(
        image_bag_data, description="Retrieving image data from bag file."
    ):
        image_data, image_time = image.read_image(image_msg)
        image_dataset_images.append(image_data)
        image_dataset_time.append(image_time)

    sec = np.hstack([t.sec for t in image_dataset_time])
    nsec = np.hstack([t.nsec for t in image_dataset_time])
    image_dataset_time = TimeStamp(sec, nsec)
    nimages = image_dataset_time.size()

    lidar_dataset_image_idx = np.zeros((npoints,), dtype=np.int64)

    t0_lidar = lidar_dataset_time.min()
    t0_camera = image_dataset_time.min()
    tf_camera = image_dataset_time.max()

    min_frequency = nimages / (tf_camera - t0_camera).as_seconds()
    print(f"Camera frame rate is {min_frequency} Hz")

    t0 = min(t0_lidar, t0_camera)
    lidar_dataset_time_ = (lidar_dataset_time - t0).as_seconds()
    image_dataset_time_ = (image_dataset_time - t0).as_seconds()

    for i in track(
        range(npoints),
        description=f"Building time correlation matrix between {npoints} LiDAR points and {nimages} images.",
    ):
        lidar_time = lidar_dataset_time_[i]
        tshift = image_dataset_time_ - lidar_time
        tshift_abs = np.abs(tshift)
        idx_min = np.argmin(tshift_abs)
        if tshift_abs[idx_min] < (0.25 / min_frequency):
            lidar_dataset_image_idx[i] = idx_min
        else:
            lidar_dataset_image_idx[i] = -1

    print("Remove all lidar points that are not associated with an image")
    lidar_idx_keep = lidar_dataset_image_idx != -1
    lidar_dataset_image_idx_red = lidar_dataset_image_idx[lidar_idx_keep]
    lidar_dataset_time_red = lidar_dataset_time_[lidar_idx_keep]
    lidar_dataset_points_red = lidar_dataset_points[lidar_idx_keep]
    print(f"{lidar_dataset_time_red.size} lidar points in reduced set")

    print("Find images that associated with a LiDAR point")
    unique, unique_indices, unique_inv = np.unique(
        lidar_dataset_image_idx_red, return_index=True, return_inverse=True
    )

    data_frames = []
    for i in track(
        range(len(unique)),
        description=f"Generating {len(unique)} data frames from {lidar_dataset_time_red.size} lidar points.",
    ):
        j = unique[i]
        isLiDARInFrame = unique_inv == i

        datai = dataset.CalibrationFrame(
            image_dataset_images[j],
            lidar_dataset_points_red[isLiDARInFrame, 0:3].T,
            lidar_dataset_points_red[isLiDARInFrame, [3]].reshape((1, -1)),
        )
        data_frames.append(datai)
    return data_frames


# Datasets
class CalibrationDataset(Dataset):
    def __init__(
        self,
        mat_dir: str,
        files: List[str],
        max_samples: int = -1,
        dtype=torch.float32,
        device: str = "cpu",
    ):
        self.data_dir = mat_dir
        self.files = files
        self.dtype = dtype
        self.device = device
        self.max_samples = max_samples
        if max_samples > 0:
            log.info(
                "Building training dataset where each frame has a maximum "
                + "of {} random samples from each image frame.".format(max_samples)
            )
        else:
            log.info("Building training dataset using all in each frame samples.")

    def __len__(self) -> int:
        return len(self.files)

    def getItemFromFile(self, idx) -> dict:
        mat_path = os.path.join(self.data_dir, self.files[idx])
        data = loadmat(mat_path)
        idxValid = (0 <= data["intensities"]) & (data["intensities"] <= 100)

        rPLl_np = data["rPLl"][:, idxValid.flatten()]
        intensities_np = data["intensities"][:, idxValid.flatten()] * 2.55

        if self.max_samples > 0:
            nValid = intensities_np.shape[1]
            idx_choose = np.random.choice(nValid, self.max_samples)
            intensities_np = intensities_np[:, idx_choose]
            rPLl_np = rPLl_np[:, idx_choose]

        rPLl = torch.from_numpy(rPLl_np).to(device=self.device, dtype=self.dtype)
        lidar_i = torch.from_numpy(intensities_np).to(
            device=self.device, dtype=self.dtype
        )
        img = torch.from_numpy(data["img"]).to(device=self.device, dtype=self.dtype)

        format_data = dict()
        format_data["img"] = img
        format_data["rPLl"] = rPLl
        format_data["intensities"] = lidar_i
        return format_data

    def getItemFromCache(self, idx):
        return self.cache_t[idx], self.cache_z[idx]

    def __getitem__(self, idx):
        return self.getItemFromFile(idx)


def my_collate(batch) -> List:
    data = []
    for packet in batch:
        data.append(packet)
    return data
