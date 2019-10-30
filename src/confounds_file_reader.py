from pathlib import Path
from typing import Tuple
import numpy
import re


def yes_no_converter(s: bytes) -> int:
    """
    Converter to translate :param s: containing "yes" or "no" into 1 or 0.
    :param s:
    :return:
    """
    if s == b'yes':
        return 1
    else:
        return 0


class ConfoundsFileReader:
    """Reads confounds file for all subjects"""

    def __init__(self, confounds_path: str, train: bool = False):
        """
        :param confounds_path: Path root containing data files
        :param train: Is the data training data?
        """
        self._names = [
            'csf',
            'white_matter',
            'global_signal',
            'std_dvars',
            'dvars',
            'framewise_displacement',
            't_comp_cor_00',
            't_comp_cor_01',
            't_comp_cor_02',
            't_comp_cor_03',
            't_comp_cor_04',
            't_comp_cor_05',
            'a_comp_cor_00',
            'a_comp_cor_01',
            'a_comp_cor_02',
            'a_comp_cor_03',
            'a_comp_cor_04',
            'a_comp_cor_05',
            'trans_x',
            'trans_y',
            'trans_z',
            'rot_x',
            'rot_y',
            'rot_z']

        self._delimiter = '\t'
        # Extract the subject ID, wave number, task name, and run number from the file name
        self._pattern = 'sub-(.*)_ses-wave(\\d*)_task-(.*)_\\w*-(\\d*)_.*'

        if train:
            self._files = Path(confounds_path).glob('**/development_sample.tsv')
            # Add a converter and column data name for training / test data
            self._converters = {'artifact': yes_no_converter}
            self._names = ['artifact'] + self._names
        else:
            # If not training data, read the confounds.tsv format described here:
            # https://fmriprep.readthedocs.io/en/stable/outputs.html#confounds
            self._files = Path(confounds_path).glob('**/*confounds_regressors.tsv')
            self._converters = None

    def get_confounds(self) -> Tuple[str, int, str, int, numpy.ndarray]:
        for f in self._files:
            subject_id, task, wave, run = '', '', 0, 0
            match = re.search(self._pattern, str(f))
            if match:
                subject_id, wave, task, run = match.groups()
            tmp = numpy.genfromtxt(f, delimiter=self._delimiter,
                                   names=True,
                                   missing_values='n/a',
                                   filling_values=0,
                                   converters=self._converters)
            # select only the desired columns, because confounds_regressors.tsv file has hundreds of confounds
            yield subject_id, wave, task, run, numpy.copy(tmp[self._names])
