import functools
import itertools
import os
import pathlib
import typing

import cv2
import magicgui
import napari
import numpy as np
import qtpy.QtWidgets
import skimage

__author__ = "Florian Aymanns"
__email__ = "florian.aymanns@epfl.ch"


def _extract_img_data(img: napari.layers.Image, view_only: bool = False) -> np.ndarray:
    """
    Extracts the img data from a napari image layer and converts it
    to gray scale if the image is RGB.
    """
    if img.multiscale:
        raise ValueError(
            "napari-hough-circle-detector does not support multiscale data"
        )
    if view_only:
        img_data = img._data_view
    else:
        img_data = img.data
    if img.rgb:
        img_data = cv2.cvtColor(img_data, cv2.COLOR_RGB2GRAY)
    return img_data


def _compute_edges_and_circles(
    img: np.ndarray,
    dp: float,
    minDist: float,
    param1: float,
    param2: float,
    minRadius: int,
    maxRadius: int,
    contrast_limits: tuple[float, float],
) -> tuple[np.ndarray, np.ndarray]:
    """
    Computes and edge map using canny edge detection and detects circles using the
    Hough transform. For more information see the documentation of opencv's
    HoughCircles function.

    Parameters
    ----------
    img : np.ndarray
        Gray scale image used for the computation.
    dp : float
        Inverse of the resolution of the accumulator array.
    minDist : float
        Minimum distance between centers of circles.
    param1 : float
        The sensitivity of the edge detection.
    param2 : float
        Threshold for number of intersetions in Hough space.
    minRadius: int
        Minimum radius of the circles detected.
    maxRadius : int
        Maximum radius of the circles detected.
    contrast_limits : (float, float)
        The input image values are cliped to the range given and
        then streched to 0 to 255 before the edge map is computed
        and the circles are detected.

    Returns
    -------
    edges : np.ndarray
        A binary image showing the edges detected.
    circles : np.ndarray
        A numpy array of shape (n, 3), where n is the number
        of circles detected. Each row corresponds to the
        center x, center y, radius of a detected circle.
    """
    img = np.clip(img, *contrast_limits)
    img = (img - contrast_limits[0]) / (contrast_limits[1] - contrast_limits[0]) * 255
    img = img.astype(np.uint8)
    edges = cv2.Canny(img, param1 / 2, param1)
    circles = cv2.HoughCircles(
        img,
        cv2.HOUGH_GRADIENT,
        dp,
        minDist,
        param1=param1,
        param2=param2,
        minRadius=minRadius,
        maxRadius=maxRadius,
    )
    if circles is not None:
        circles = circles[0]
    return edges, circles


def median_filter(
    img: napari.layers.Image, median_filter_strength: int = 5
) -> napari.types.LayerDataTuple:
    """
    Median filters the input image with kernel size `2 * median_filter_strength - 1` and returns
    a napari LayerDataTuple that creates a new image layer named 'Median filtered' or replaces
    image of a layer with that name.

    Parameters
    ----------
    img : napari.layers.Image
        Image to be filtered.
    median_filter_strength : int
        The strength of the filter.
        The actual kernel size is `2 * median_filter_strength -1 `.

    Returns
    -------
    layer_data_tuple : napari.types.LayerDataTuple
        The data tuple has the form `(filtered_img, {"name": "Median filtered"}, "image")`,
        where filtered_img is the filtered gray scale input image in the form of a
        numpy array.
    """
    if img is None:
        return
    name = img.name
    img_data = _extract_img_data(img, view_only=False)
    median_filter_strength = median_filter_strength * 2 - 1
    filtered_img = np.zeros_like(img_data)
    ndim = img_data.ndim
    if ndim == 2:
        filtered_img = cv2.medianBlur(img_data, median_filter_strength)
    else:
        for indices in itertools.product(*[range(n) for n in img_data.shape[:-2]]):
            filtered_img[indices] = cv2.medianBlur(
                img_data[indices], median_filter_strength
            )
    return (filtered_img, {"name": f"{name}_median_filtered"}, "image")


def param_sliders(
    img: napari.layers.Image,
    dp: float = 0.1,
    minDist: float = 10,
    param1: float = 300,
    param2: float = 40,
    minRadius: int = 10,
    maxRadius: int = 50,
) -> typing.List[napari.types.LayerDataTuple]:
    """
    Command for widget with sliders.
    Computes and edge image and detects circles which
    are returned in the form of a napari point layer.
    For a more detail description of the parameters
    see the documentation of opencv's HoughCircles.

    Parameters
    ----------
    img : napari.layers.Image
        Input image layer.
    dp : float
        Inverse of the resolution of the accumulator array.
    minDist : float
        Minimum distance between centers of circles.
    param1 : float
        The sensitivity of the edge detection.
    param2 : float
        Threshold for number of intersetions in Hough space.
    minRadius: int
        Minimum radius of the circles detected.
    maxRadius : int
        Maximum radius of the circles detected.

    Returns
    -------
    edge_layer_data_tuple : napary.types.LayerDataTuple
        Data tuple of the form `(edges, {"name": "edges"}, "image")`,
        where `edges` is an edge map in the form of a numpy array.
    points_layer_data_tuple : napary.types.LayerDataTuple
        Data tuple of the form `(circles, {"name": "Circles"}, "points")`,
        where `circles` is an empty list if no circles were detected and
        a numpy array of shape (n, 2) containing the centers of the circles.
        The sizes, i.e. radii, edge, and facecolor are specified as additional
        entries in the dictionary of the layer data tuple.
    """
    if img is None:
        return
    img_data = _extract_img_data(img, view_only=True)
    edges, circles = _compute_edges_and_circles(
        img_data,
        dp,
        minDist,
        param1,
        param2,
        minRadius,
        maxRadius,
        contrast_limits=img.contrast_limits,
    )
    layer_data_tuples = [
        (edges, {"name": "edges"}, "image"),
    ]
    if circles is None:
        layer_data_tuples.append(
            (
                [],
                {"name": "Circles", "canvas_size_limits": (2, 10000)},
                "points",
            )
        )
    else:
        layer_data_tuples.append(
            (
                circles[:, (1, 0)],
                {
                    "name": "Circles",
                    "size": circles[:, 2] * 2,
                    "edge_color": "red",
                    "face_color": [
                        0,
                    ]
                    * 4,
                },
                "points",
            )
        )
    return layer_data_tuples


def export(
    sliders_widget,
    napari_viewer: napari.Viewer,
    output_type: str,
    export_stack: bool,
    folder: pathlib.Path = pathlib.Path("."),
    filename: str = "circles.csv",
):
    stack = sliders_widget.img.value
    img_data = _extract_img_data(stack, view_only=False)

    n_dims = len(napari_viewer.dims.nsteps)
    if n_dims == 2:
        img_data = img_data[None, None, :, :]
        current_slice = 0
        channel = 0
        slice_indices = (current_slice,)
    else:
        n_slices = napari_viewer.dims.nsteps[0]
        current_slice = napari_viewer.dims.current_step[0]

        if n_dims == 3:
            img_data = img_data[:, None, :, :]
            channel = 0
        elif n_dims == 4:
            channel = napari_viewer.dims.current_step[1]
        else:
            raise ValueError(
                "Only 2D, 3D and 4D data is supported. You tried to export {n_dims}D data."
            )

        if export_stack:
            slice_indices = np.arange(n_slices)
        else:
            slice_indices = (current_slice,)

    slice_results = []
    for slice_idx in slice_indices:
        _, circles = _compute_edges_and_circles(
            img_data[slice_idx, channel],
            sliders_widget.dp.value,
            sliders_widget.minDist.value,
            sliders_widget.param1.value,
            sliders_widget.param2.value,
            sliders_widget.minRadius.value,
            sliders_widget.maxRadius.value,
            contrast_limits=stack.contrast_limits,
        )
        indices = np.array([[slice_idx, channel]] * circles.shape[0])
        circles = np.concatenate([indices, circles], axis=1)
        slice_results.append(circles)
    slice_results = np.concatenate(slice_results, axis=0)

    if output_type == "csv":
        np.savetxt(
            filename,
            slice_results,
            delimiter=",",
            header="frame, channel, center x, center y, radius",
            fmt="%.1f",
        )
        print(f"Saved file to {filename}.")
    elif output_type == "mask":
        masks = []
        for slice_idx in slice_indices:
            mask = np.zeros(img_data.shape[-2:], dtype=np.uint8)
            slice_mask = slice_results[:, 0] == slice_idx
            slice_circles = slice_results[slice_mask, 2:].astype(int)
            for center_x, center_y, radius in slice_circles:
                mask = cv2.circle(mask, (center_x, center_y), radius, 255, -1)
            masks.append(mask)
        mask = np.stack(masks, axis=0)
        mask = np.squeeze(mask)
        skimage.io.imsave(str(filename), mask)
        print(f"Saved file to {filename}.")


class CircleDetectorWidget(qtpy.QtWidgets.QWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        filter_widget = magicgui.magicgui(
            median_filter,
            auto_call=True,
            median_filter_strength={"widget_type": "IntSlider", "min": 1, "max": 50},
        )
        sliders_widget = magicgui.magicgui(
            param_sliders,
            auto_call=True,
            dp={"widget_type": "FloatSlider", "min": 0.1, "max": 10},
            minDist={"widget_type": "IntSlider", "min": 1, "max": 200},
            param1={"widget_type": "IntSlider", "min": 10, "max": 1000},
            param2={"widget_type": "IntSlider", "min": 10, "max": 300},
            minRadius={"widget_type": "IntSlider", "min": 1, "max": 300},
            maxRadius={"widget_type": "IntSlider", "min": 1, "max": 500},
        )
        export_widget = magicgui.magicgui(
            functools.partial(export, sliders_widget),
            call_button="Export circles",
            folder={"mode": "d"},
            output_type={"choices": ["csv", "mask"]},
        )
        self._children = [
            filter_widget,
            sliders_widget,
            export_widget,
        ]

        self.setLayout(qtpy.QtWidgets.QVBoxLayout())

        self.layout().addWidget(filter_widget.native)
        filter_widget.img.reset_choices()
        napari_viewer.layers.events.inserted.connect(filter_widget.img.reset_choices)
        napari_viewer.layers.events.removed.connect(filter_widget.img.reset_choices)

        self.layout().addWidget(sliders_widget.native)
        sliders_widget.img.reset_choices()
        napari_viewer.layers.events.inserted.connect(sliders_widget.img.reset_choices)
        napari_viewer.layers.events.removed.connect(sliders_widget.img.reset_choices)

        self.layout().addWidget(export_widget.native)

        # Update circles when slice or channel is changes
        napari_viewer.dims.events.current_step.connect(lambda event: sliders_widget())

        def connect_contrast_limits(widget):
            """
            Update circles when contrast limits are changes
            """
            if widget.img.value is not None:
                widget.img.value.events.contrast_limits.connect(lambda event: widget())

        # Establish initial connection with contrast limits
        connect_contrast_limits(sliders_widget)

        # Make sure the connection to the contrast limits persists when the input layer is changed
        sliders_widget.img.changed.connect(
            lambda event: connect_contrast_limits(sliders_widget)
        )

        def update_file_extension(widget):
            output_type = widget.output_type.value
            name = widget.filename.value
            name_wo_extension = os.path.splitext(name)[0]
            if output_type == "csv":
                widget.filename.value = name_wo_extension + ".csv"
            elif output_type == "mask":
                widget.filename.value = name_wo_extension + ".tif"

        export_widget.output_type.changed.connect(
            lambda event: update_file_extension(export_widget)
        )

        # Update default output file names when the layer is changed
        def update_default_file_name(widget):
            if sliders_widget.img.value is None:
                return
            name = sliders_widget.img.value.name
            extension = os.path.splitext(widget.filename.value)[1]
            extension = extension.lstrip(".")
            export_stack = widget.export_stack.value
            if export_stack:
                widget.filename.value = f"{name}_stack.{extension}"
            else:
                step = napari_viewer.dims.current_step[0]
                widget.filename.value = f"{name}_{step:05}.{extension}"

        sliders_widget.img.changed.connect(
            lambda event: update_default_file_name(export_widget)
        )
        napari_viewer.dims.events.current_step.connect(
            lambda event: update_default_file_name(export_widget)
        )
        export_widget.export_stack.changed.connect(
            lambda event: update_default_file_name(export_widget)
        )
