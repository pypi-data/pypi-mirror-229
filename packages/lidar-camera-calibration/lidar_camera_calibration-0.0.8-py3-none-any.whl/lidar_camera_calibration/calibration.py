import json
import logging
import math
import os
import sys
from datetime import datetime
from typing import List, Tuple

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.optim as optim
import yaml
from rich.progress import Progress, track
from scipy.io import savemat
from torch.utils.data import DataLoader

from lidar_camera_calibration import general as gn
from lidar_camera_calibration import model as camLiDARMI
from lidar_camera_calibration import rotations as rot
from lidar_camera_calibration.tools import dataset

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

log = logging.getLogger(__name__)


def convert_numpy_to_list(data):
    if isinstance(data, dict):
        return {key: convert_numpy_to_list(value) for key, value in data.items()}
    elif isinstance(data, (list, tuple)):
        return [convert_numpy_to_list(item) for item in data]
    elif isinstance(data, np.ndarray):
        return data.tolist()
    else:
        return data


def convert_numpy_to_yaml_dict(x: np.ndarray) -> dict:
    assert len(x.shape) == 2, "Expected numpy object to be 2d!"
    data = dict()
    data["rows"] = x.shape[0]
    data["cols"] = x.shape[1]
    data["data"] = x.flatten().tolist()
    return data


class LiDARCameraCalibrationResults:
    def __init__(
        self,
        Tlc: torch.Tensor,
        camera_matrix: torch.Tensor,
        distortion_coefficients: torch.Tensor,
        is_camera_learned: bool,
        is_using_Lie_group: bool,
        num_epochs: int,
        learning_rate: float,
        calibration_data_dir: str,
        generator_file: str = sys._getframe(1).f_code.co_name,
        git_id: str = gn.get_git_revision_short_hash(),
    ):
        # Set attributes
        self.Tlc = Tlc.detach().cpu()
        self.camera_matrix = camera_matrix.detach().cpu()
        self.distortion_coefficients = distortion_coefficients.detach().cpu()
        self.is_camera_learned = bool(is_camera_learned)
        self.is_using_Lie_group = bool(is_using_Lie_group)
        self.num_epochs = int(num_epochs)
        self.learning_rate = float(learning_rate)
        self.calibration_data_dir = str(calibration_data_dir)

        # Optionally set attributes
        self.generator_file = str(generator_file)
        self.git_id = str(git_id)

        # Internally set attributes
        self.date_time = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

    def toNumpyDict(self) -> dict:
        toSave = dict()
        # Set attributes
        toSave["Tlc"] = self.Tlc.numpy()
        toSave["camera_matrix"] = self.camera_matrix.numpy()
        toSave["distortion_coefficients"] = self.distortion_coefficients.numpy()
        toSave["is_camera_learned"] = self.is_camera_learned
        toSave["is_using_Lie_group"] = self.is_using_Lie_group
        toSave["num_epochs"] = self.num_epochs
        toSave["learning_rate"] = self.learning_rate
        toSave["calibration_data_dir"] = self.calibration_data_dir

        # Optionally set attributes
        toSave["git_id"] = self.git_id
        toSave["generator_file"] = self.generator_file

        # Internally set attributes
        toSave["date_time"] = self.date_time
        return toSave

    def toOpenCVCameraIntrinsicsYAML(self, filepath: str):
        filepath = gn.add_extension(filepath, "yaml")

        if self.is_camera_learned:
            outstr = "# Automatically generated intrinsics from joint calibration\n"
        else:
            outstr = "# Automatically copied intrinsics from camera intrinsics calibration, located in {}\n".format(
                os.path.join(self.calibration_data_dir, "raw")
            )
        outstr = outstr + "#%12s: %s \n" % ("by", self.generator_file)
        outstr = outstr + "#%12s: %s \n" % ("on", self.date_time)
        outstr = outstr + "#%12s: %s \n" % ("git-id", self.git_id)
        outstr = outstr + "#%12s: %s \n" % ("calib. data", self.calibration_data_dir)
        names = [
            "camera_matrix",
            "distortion_coefficients",
        ]
        intrinics = dict()
        tosave = self.toNumpyDict()
        for name in names:
            intrinics[name] = convert_numpy_to_yaml_dict(tosave[name])

        intrinics_str = yaml.dump(intrinics, default_flow_style=None, sort_keys=False)
        content = outstr + "\n\n" + intrinics_str
        with open(filepath, "w") as file:
            file.write(content)

    def toYAML(self, filepath: str):
        filepath = gn.add_extension(filepath, "yaml")
        data = self.toNumpyDict()
        data = convert_numpy_to_list(data)
        with open(filepath, "w") as file:
            yaml.dump(data, file, default_flow_style=None, sort_keys=False)

    def toJSON(self, filepath: str):
        filepath = gn.add_extension(filepath, "json")
        data = self.toNumpyDict()
        data = convert_numpy_to_list(data)
        with open(filepath, "w") as file:
            json.dump(data, file)

    def toMATLAB(self, filepath: str):
        filepath = gn.add_extension(filepath, "mat")
        savemat(filepath, self.toNumpyDict())


def get_factors(x: int) -> List[int]:
    factors_ = []
    for i in range(1, x + 1):
        if x % i == 0:
            factors_.append(i)
    return factors_


def showLiDARCameraCorrelation(fig_num: int, train_loader, model, title: str):
    I_lidar = []
    I_image = []
    for batch_idx, data in enumerate(train_loader):
        Il, Ii = model.forward(data)
        I_lidar.append(Il.flatten())
        I_image.append(Ii.flatten())
    I_lidar, I_image = (
        torch.hstack(I_lidar).detach().cpu(),
        torch.hstack(I_image).detach().cpu(),
    )

    hist_lidar = torch.histogram(I_lidar, density=True)
    hist_image = torch.histogram(I_image, density=True)

    plt.figure(fig_num)
    plt.subplot(1, 4, 1)
    x = (hist_lidar[1][0:-1] + hist_lidar[1][1:]) / 2
    plt.plot(x, hist_lidar[0])
    plt.xlabel("Intensity")
    plt.title("LiDAR")
    plt.ylim([0, hist_lidar[0].max() * 1.25])

    plt.subplot(1, 4, 2)
    x = (hist_image[1][0:-1] + hist_image[1][1:]) / 2
    plt.plot(x, hist_image[0])
    plt.xlabel("Intensity")
    plt.title("Camera")
    plt.ylim([0, hist_image[0].max() * 1.25])

    plt.subplot(1, 4, (3, 4))

    plt.hist2d(
        I_image.numpy(),
        I_lidar.numpy(),
        density=True,
        bins=100,
        cmap=mpl.colormaps["plasma"],
    )
    plt.ylabel("LiDAR Intensities")
    plt.xlabel("Camera Intensities")

    plt.suptitle(title, fontsize=14)


def calibrate(
    calibration_data_dir: str,
    eta0: torch.Tensor,
    max_samples: int = 5000,
    num_epochs: int = 300,
    plot_iter: bool = False,
    plot_correlation: bool = True,
    learn_camera: bool = True,
    learning_rate: float = 1e-3,
    max_lidar_range: float = 15,
    entropy_approx: str = "trapz",
    compile_cost_func_model: bool = False,
    device: str = "cpu",
    dtype=torch.float64,
) -> Tuple[
    LiDARCameraCalibrationResults, camLiDARMI.CameraLiDARMutualInformation, DataLoader
]:
    """_summary_

    Args:
        calibration_data_dir (str): Directory that contains calibration data folders:
            calibration_data_dir/raw directory with
            calibration_data_dir/compressed
            calibration_data_dir/results
        eta0 (torch.Tensor): Initial pose [rCLl; Thetalc], where rCLl ∈ ℝ^3 is the translational vector and
            Thetalc ∈ ℝ^3 is the Euler angles that define the relative rotation
        max_samples (int, optional): _description_. Defaults to 5000.
        num_epochs (int, optional): _description_. Defaults to 300.
        plot_iter (bool, optional): _description_. Defaults to False.
        plot_correlation (bool, optional): _description_. Defaults to True.
        learn_camera (bool, optional): _description_. Defaults to True.
        learning_rate (float, optional): _description_. Defaults to 1e-3.
        max_lidar_range (float, optional): _description_. Defaults to 15.
        device (str, optional): _description_. Defaults to "cpu".
        dtype (_type_, optional): _description_. Defaults to torch.float64.

    Returns:
        Tuple[ LiDARCameraCalibrationResults, camLiDARMI.CameraLiDARMutualInformation, DataLoader ]: _description_
    """

    assert os.path.isdir(calibration_data_dir), "Expected {} to be a directory.".format(
        calibration_data_dir
    )
    raw_data_dir = os.path.join(calibration_data_dir, "raw")
    matlab_compressed_data_dir = os.path.join(calibration_data_dir, "compressed")
    calibration_results_dir = os.path.join(calibration_data_dir, "results")

    assert os.path.isdir(raw_data_dir), (
        "Expected " "raw" " to be a directory within {}".format(calibration_data_dir)
    )
    assert os.path.isdir(matlab_compressed_data_dir), (
        "Expected "
        "compressed"
        " to be a directory within {}".format(matlab_compressed_data_dir)
    )

    if not os.path.isdir(calibration_results_dir):
        os.mkdir(calibration_results_dir)

    mat_files = [
        f
        for f in os.listdir(matlab_compressed_data_dir)
        if os.path.isfile(os.path.join(matlab_compressed_data_dir, f))
        and f.startswith("frame-")
    ]

    mat_files.sort()
    log.info(
        "%d frame data files found in %s", len(mat_files), matlab_compressed_data_dir
    )

    assert len(mat_files) > 0, "Expected there to be frame data"

    train_data = dataset.CalibrationDataset(
        matlab_compressed_data_dir, mat_files, max_samples=max_samples
    )

    factors = get_factors(len(train_data))
    factors_oi = [f for f in factors if f < 16]
    batch_size_train = max(factors_oi)

    train_loader = DataLoader(
        train_data,
        batch_size=batch_size_train,
        shuffle=True,
        collate_fn=dataset.my_collate,
    )

    # Load intrinsics
    camera_params_name = "camera_params.yaml"

    camera_params_file = os.path.join(raw_data_dir, camera_params_name)
    assert os.path.isfile(
        camera_params_file
    ), "Expected {} to be a file containing the camera calibration parameters. Could not find the file in {}".format(
        camera_params_name, raw_data_dir
    )

    Tlc0 = rot.getTransformationMatrixFromVector(eta0)
    Rlc0 = Tlc0[0:3, 0:3]
    rCLl0 = Tlc0[0:3, [3]]

    model = camLiDARMI.CameraLiDARMutualInformation(
        rCLl0,
        Rlc0,
        camera_params_file,
        use_Lie_group=False,
        learn_camera=learn_camera,
        max_range=max_lidar_range,
        entropy_approx=entropy_approx,
        device=device,
        dtype=dtype,
    )
    if compile_cost_func_model:
        fname = "cost function model"
        log.info(f"Compiling {fname}")
        try:
            model = torch.compile(model, mode="reduce-overhead")
            log.info(f"Compiled {fname}")
        except Exception as e:
            log.error(f"Failed to compile {fname}: {e}")

    if plot_correlation:
        showLiDARCameraCorrelation(1, train_loader, model, "pre-calibration")

    Kc, dist_theta = model.getCamera()

    train_iter_loss = []
    train_iter_counter = []
    train_epoch_loss = []
    train_epoch_counter = []

    num_batchs = len(train_loader.dataset)
    batch_size = train_loader.batch_size
    ndigits_epoch = math.ceil(math.log10(num_epochs))
    ndigits_batch = math.ceil(math.log10(num_batchs))

    # Calibration
    def train(epoch):
        ndisp = 10
        nmod = math.ceil(len(train_loader) / float(ndisp))

        epoch_cost = 0
        npoints = 0
        npoints_batch = 0

        for batch_idx, data in enumerate(train_loader):
            optimizer.zero_grad()
            Il, Ii = model.forward(data)
            loss = model.cost(Il, Ii)
            loss.backward()
            loss_eval = loss.item()

            optimizer.step()
            npoints_batch = len(Il)
            npoints = npoints + npoints_batch

            assert (
                not model.getRelativePose().detach().cpu().isnan().any()
            ), "Relative pose is nan after optimisation step"

            if batch_idx % nmod == 0:
                res_line = "Train Epoch: {epoch:{ndigits_epoch}d} of {num_epoch} [{batch_num:{ndigits_batch}d}/{num_batchs:{ndigits_batch}d} ({percent_batchs:3.0f}%)] Loss: {loss:.6g}".format(
                    ndigits_epoch=ndigits_epoch,
                    ndigits_batch=ndigits_batch,
                    epoch=epoch,
                    num_epoch=num_epochs,
                    num_batchs=num_batchs,
                    batch_num=batch_idx * batch_size,
                    percent_batchs=100.0 * batch_idx / num_batchs,
                    loss=loss_eval,
                )
                print(res_line)

            train_iter_loss.append(loss_eval)
            epoch_cost += npoints_batch * loss_eval
            epoch_val = (
                1.0 * (batch_idx * batch_size_train)
                + ((epoch - 1) * len(train_loader.dataset))
            ) / len(train_loader.dataset)
            train_iter_counter.append(epoch_val)

        epoch_cost = epoch_cost / npoints
        train_epoch_loss.append(epoch_cost)
        train_epoch_counter.append(epoch)

    optimizer = optim.AdamW(model.parameters(), lr=learning_rate)

    if plot_iter:
        fig, ax = plt.subplots()  # Create figure and axes

        (line_iter,) = ax.plot(
            train_iter_counter, -np.array(train_iter_loss), "r-", label="Train iter MI"
        )
        (line_epoch,) = ax.plot(
            train_epoch_counter, -np.array(train_epoch_loss), "b-x", label="Train MI"
        )
        ax.set_ylabel("Mutual Information")
        ax.set_xlabel("No. of epochs")
        ax.legend()

    with Progress(transient=True) as progress:
        task = progress.add_task("Training model", total=num_epochs)
        for epoch in range(1, 1 + num_epochs):
            train(epoch)
            progress.advance(task)
            if plot_iter:
                line_iter.set_data(train_iter_counter, -np.array(train_iter_loss))

                line_epoch.set_data(train_epoch_counter, -np.array(train_epoch_loss))
                ax.relim()  # Recalculate the data limits
                ax.autoscale_view()  # Auto-scale the axes
                fig.canvas.draw()  # Redraw the figure

                plt.pause(0.01)

    # Post Calibration
    Tlc_final = model.getRelativePose().detach().cpu()

    Kc, dist_theta = model.getCamera()

    res = LiDARCameraCalibrationResults(
        Tlc_final,
        Kc,
        dist_theta,
        model.learn_camera,
        model.use_Lie_group,
        epoch,
        learning_rate,
        calibration_data_dir,
        generator_file=__file__,
    )

    parameterisation = "Lie" if model.use_Lie_group else "Euler"
    calibration_type = "joint" if model.learn_camera else "pose"
    output_file_name = "calibration_{}_{}_{}".format(
        calibration_type, parameterisation, epoch
    ).lower()
    output_file = os.path.join(calibration_results_dir, output_file_name)
    res.toMATLAB(output_file)
    res.toYAML(output_file)

    # Output OpenCV data
    output_file_name = "camera_params"
    output_file = os.path.join(calibration_results_dir, output_file_name)
    res.toOpenCVCameraIntrinsicsYAML(output_file)

    if plot_correlation:
        showLiDARCameraCorrelation(2, train_loader, model, "post-calibration")

    return res, model, train_loader
