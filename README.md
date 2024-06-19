# RAVEE

The RAVEE project provides a general approach to extract process-mining-conform event logs from unstructured video data in an unsupervised manner.
It targets custom datasets and is an implementation of the RAVEE reference architecture.

## Dependencies

The VideoProcessMining project uses several open source computer vision projects.

- [TW-FINCH](https://github.com/facebookresearch/detectron2) ([License](https://github.com/facebookresearch/detectron2/blob/master/LICENSE)): For object detection
- [Dense improved trajectories](https://github.com/ZQPei/deep_sort_pytorch) ([License](https://github.com/ZQPei/deep_sort_pytorch/blob/master/LICENSE)): For object tracking
- [DTI](https://github.com/facebookresearch/SlowFast) ([License](https://github.com/facebookresearch/SlowFast/blob/master/LICENSE)): For activity recognition
- [PM4Py](https://github.com/pm4py/pm4py-core) ([License](https://github.com/pm4py/pm4py-core/blob/release/LICENSE)): For XES event log generation


## License

The RAVEE project is released under the [GNU General Public License v3.0](LICENSE).

## Functionality

The RAVEE project comprises a GUI that automates and facilitates several tasks:
- Preprocessing of custom video datasets for activity recognition
- Segmentation of video files in activity steps at previously defined granularity
- Extraction of process-mining-conform event logs from unstructured video data

## Installation

Please find installation instructions in [INSTALL.md](INSTALL.md).

## Use RAVEE For Training Or Testing Models

After preparing your dataset, you can follow the instructions in [INSTRUCTIONS.md](INSTRUCTIONS.md) to train and test your models.

You can also extract information from video data.

## Instantiation of RAVEE components

You can find out which components of the RAVEE were instantiated in our software prototype in [CREPE_DEMO.md](CREPE_DEMO.md).
