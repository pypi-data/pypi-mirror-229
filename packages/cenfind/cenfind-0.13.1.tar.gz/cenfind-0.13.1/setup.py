# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['cenfind',
 'cenfind.cli',
 'cenfind.core',
 'cenfind.publication',
 'cenfind.training']

package_data = \
{'': ['*']}

install_requires = \
['albumentations>=1.3.0,<2.0.0',
 'attrs>=22.2.0,<23.0.0',
 'csbdeep>=0.7.3,<0.8.0',
 'labelbox[data]>=3.46.0,<4.0.0',
 'llvmlite==0.39.1',
 'numba==0.56.4',
 'numpy>=1.23.5,<2.0.0',
 'opencv-python>=4.7.0.72,<5.0.0.0',
 'ortools==9.4.1874',
 'pandas>=1.4.1,<2.0.0',
 'protobuf==3.19.6',
 'python-dotenv>=0.21.1,<0.22.0',
 'pytomlpp>=1.0.10,<2.0.0',
 'scikit-image>=0.19.2,<0.20.0',
 'scikit-learn>=1.2.1,<2.0.0',
 'scipy>=1.7.1,<2.0.0',
 'spotipy-detector>=0.1.0,<0.2.0',
 'stardist>=0.8.3,<0.9.0',
 'tifffile>=2022.5.4,<2023.0.0',
 'tqdm>=4.62.3,<5.0.0']

extras_require = \
{':sys_platform == "darwin"': ['tensorflow-macos==2.9.0'],
 ':sys_platform == "win32" or sys_platform == "linux"': ['tensorflow==2.9.0']}

entry_points = \
{'console_scripts': ['cenfind = cenfind.__main__:main']}

setup_kwargs = {
    'name': 'cenfind',
    'version': '0.13.1',
    'description': 'Score cells for centrioles in IF data',
    'long_description': '# CenFind\n\nA command line interface to score cells for centrioles.\n\n## Introduction\n\n`cenfind` is a command line interface to detect and assign centrioles in immunofluorescence images of human cells.\nSpecifically, it orchestrates:\n\n- the detection of centrioles;\n- the detection of the nuclei;\n- the assignment of the centrioles to the nearest nucleus.\n\nYou can read more on it here: Bürgy, L., Weigert, M., Hatzopoulos, G. et al. CenFind: a deep-learning pipeline for efficient centriole detection in microscopy datasets. BMC Bioinformatics 24, 120 (2023). https://doi.org/10.1186/s12859-023-05214-2\n\n## Installation\n\n1. Install python via pyenv\n2. Download and set up 3.9.5 as local version\n3. Set up Python interpreter\n\n```shell\npyenv local 3.9.5\npyenv global 3.9.5\n```\n\n4. Create a virtual environment for CenFind\n\n```shell\npython -m venv venv-cenfind\nsource venv-cenfind/bin/activate\n```\n\n5. Check that `cenfind` is correctly installed by running:\n\n```shell\ncenfind --help\n```\n\n## Basic usage\n\n`cenfind` assumes a fixed folder structure.\nSpecifically, it expects the max-projection to be under the `projections` folder.\nEach file in projections is a z-max projected field of view (referred to as field, in the following) containing 4\nchannels (0, 1, 2, 3). The channel 0 usually contains the nuclei and the channels 1-3 contains centriolar markers.\n\n```text\n<project_name>/\n└── projections/\n```\n\n1. Run `score` with the arguments source, the index of the nuclei channel (usually 0 or 3), the channel to score and the\n   path to the model. You need to download it from https://figshare.com/articles/software/Cenfind_model_weights/21724421\n\n```shell\ncenfind score /path/to/dataset /path/to/model/ -n 0 -c 1 2 3\n```\n\n```shell\nusage: CENFIND score [-h] --channel_nuclei CHANNEL_NUCLEI [--channel_centrioles CHANNEL_CENTRIOLES [CHANNEL_CENTRIOLES ...]] [--channel_cilia CHANNEL_CILIA] [--vicinity VICINITY] [--cpu] dataset model\n\npositional arguments:\n  dataset               Path to the dataset\n  model                 Absolute path to the model folder\n\noptions:\n  -h, --help            show this help message and exit\n  --channel_nuclei CHANNEL_NUCLEI, -n CHANNEL_NUCLEI\n                        Channel index for nuclei segmentation, e.g., 0 or 3 (default: None)\n  --channel_centrioles CHANNEL_CENTRIOLES [CHANNEL_CENTRIOLES ...], -c CHANNEL_CENTRIOLES [CHANNEL_CENTRIOLES ...]\n                        Channel indices to analyse, e.g., 1 2 3 (default: [])\n  --channel_cilia CHANNEL_CILIA, -l CHANNEL_CILIA\n                        Channel indices to analyse cilium (default: None)\n  --vicinity VICINITY, -v VICINITY\n                        Distance threshold in pixel (default: 50 px) (default: 50)\n  --cpu                 Only use the cpu (default: False)\n```\n\n2. Check that the predictions are satisfactory by looking at the folders `visualisations/` and `statistics/`\n\n## The outputs in version 0.13.x\n\nIn version 0.13, we operated a shift in what cenfind-score outputs. Now, there are modular outputs that can be linked together depending on the applications. In the following section, each output is explained.\n\n### Assignment\n\nCenfind saves the assignment matrix in the assignment folder.\n\nThis matrix is NxC where the row indices correspond to nucleus ID and the column indices to the centriole ID. It describes which centrioles are assigned to which nucleus. One can compute the number of centrioles by cell by summing over the columns and to retrieve the nucleus ID of every centriole assigned by looking up the row number of the entry for a given centriole.\n\n### Centriole predictions\nCenfind saves a TSV file for each field of view with the detected centrioles and the channel used as well as the maximum intensity at the position.\n\n### Nuclei predictions\n\nCenfind saves a JSON file for each field of view with the detected nuclei. Each nucleus contour is saved as an entry in the JSON together with the channel index, the position (row, col) the summed intensity, the surface area, whether the nucleus is fully in the field of view.\n\n### Cilia\nIf specified by the user at the command line prompt, the cilia can be analysed in the given channel. In such cases, the folder called cilia will contain TSV files similar in structure to the one from centrioles.\n\n### Summary statistics\nThe statistics folder contains precomputed information about the distribution of centriole number (statistics.tsv), TSV files for pairs of assigned centrioles their nucleus if possible. If the cilia are analysed, a TSV file containing the fraction of ciliated cells is saved as well.\n\n## Running `cenfind score` in the background\n\nWhen you exit the shell, running programs receive the SIGHUP, which aborts them. This is undesirable if you need to\nclose your shell for some reason. Fortunately, you can make your program ignore this signal by prepending the program\nwith the `nohup` command. Moreover, if you want to run your program in the background, you can append the ampersand `&`.\nIn practice, run `nohup cenfind score ... &` instead of `cenfind score ...`.\n\nThe output will be written to the file `nohup.out` and you can peek the progress by running `tail -F nohup.out`, the\nflag `-F` will refresh the screen as the file is being written. Enter Ctrl-C to exit the tail program.\n\nIf you want to kill the program score, run  `jobs` and then run `kill <jobid>`. If you see no jobs, check the\nlog `nohup.out`; it can be done or the program may have crashed, and you can check the error there.\n\n## Evaluating the quality of the model on a new dataset\n\nThe initial model M is fitted using a set of five representative datasets, hereafter referred to as the standard\ndatasets (DS1-5).\nIf your type of data deviates too much from the standard dataset, M may perform less well.\n\nSpecifically, when setting out to score a new dataset, you may be faced with one of three situations, as reflected by\nthe corresponding F1 score (i.e., 2TP/2TP+FN+FP, TP: true positive, FP: false positive; FN: false negative):\n(1) the initial model (M) performs well on the new dataset (0.9 ≤ F1 ≤ 1); in this case, model M is used;\n(2) model M performs significantly worse on the new dataset (0.5 ≤ F1 < 0.9); in this case, you may want to consider\nretraining the model (see below);\n(3) the model does not work at all (0 ≤ F1 < 0.5); such a low F1-value probably means that the features of the data set\nare too distant from the original representative data set to warrant retraining starting from M.\n\nBefore retraining a model (2), verify once more the quality of the data, which needs to be sufficiently good in terms of\nsignal over noise to enable efficient learning.\nIf this is not the case, it is evident that the model will not be able to learn well.\nIf you, as a human being, cannot tell the difference between a real focus and a stray spot using a single channel at\nhand (i.e., not looking at other channels), the same will hold for the model.\n\nTo retrain the model, you first must annotate the dataset, divide it randomly into training and test sets (90 % versus 10 % of the data, respectively).\nNext, the model is trained with the 90 % set, thus generating a new model, M*.\nLast, you will evaluate the gain of performance on the new dataset, as well as the potential loss of performance on the standard datasets.\n\n### Detailed training procedure:\n\n1. Split the dataset into training (90%) and test (10%) sets, each containing one field of view and the channel to use.\n   This helps trace back issues during the training and renders the model fitting reproducible.\n\n2. Label all the images present in training and test sets using Labelbox. To upload the images, please create the vignettes first and then upload them once you have a project set up.\n3. Save all foci coordinates (x, y), origin at top-left, present in one field of view as one text file under\n   /path/to/dataset/annotation/centrioles/ with the naming scheme <dataset_name>_max_C<channel_index>.txt.\n4. Evaluate the newly annotated dataset using the model M by computing the F1 score.\n5. If the performance is poor (i.e., F1 score < 0.9), fit a new model instance, M*, with the standard dataset plus the\n   new dataset (90% in each case).\n6. Test performance of model M* on the new data set; hopefully the F1 score will now be ≥ 0.9 (if not: consider\n   increasing size of annotated data).\n7. Test performance of model M* on the standard datasets; if performance of F1* ≥ F1, then save M* as the new M (\n   otherwise keep M* as a separate model for the new type of data set).\n',
    'author': 'Leo Burgy',
    'author_email': 'leo.burgy@epfl.ch',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/UPGON/cenfind',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
