from pathlib import Path
import numpy


def na_converter(s: bytes) -> float:
    """
    Converter to translate :param s: containing 'n/a' to 0.
    :param s: Input string
    :return: float(s) if s represents a floating point number, 0 otherwise
    """
    if s == b'n/a':
        return 0.0
    else:
        return float(s)


def yes_no_converter(s: bytes) -> int:
    """
    Converter to translate :param s: containing "yes" or "no" into 1 or 0.
    :param s:
    :return:
    """
    if s == b'"yes"':
        return 1
    else:
        return 0


class ConfoundsFileReader:
    """Reads confounds file for all subjects"""

    def __init__(self, confounds_path: str, train: bool):
        """
        :param confounds_path: Path root containing data files
        :param train: Is the data training data?
        """
        if train:
            self._files = Path(confounds_path).glob('**/development_sample.csv')
            self._delimiter = ','
            self._converters = {0: yes_no_converter}
            self._data_type = {
                'names': (
                    'artifact',
                    'CSF',
                    'WhiteMatter',
                    'GlobalSignal',
                    'stdDVARS',
                    'non.stdDVARS',
                    'vx.wisestdDVARS',
                    'FramewiseDisplacement',
                    'tCompCor00',
                    'tCompCor01',
                    'tCompCor02',
                    'tCompCor03',
                    'tCompCor04',
                    'tCompCor05',
                    'aCompCor00',
                    'aCompCor01',
                    'aCompCor02',
                    'aCompCor03',
                    'aCompCor04',
                    'aCompCor05',
                    'X',
                    'Y',
                    'Z',
                    'RotX',
                    'RotY',
                    'RotZ'),
                'formats': (
                    'int',
                    'float',
                    'float',
                    'float',
                    'float',
                    'float',
                    'float',
                    'float',
                    'float',
                    'float',
                    'float',
                    'float',
                    'float',
                    'float',
                    'float',
                    'float',
                    'float',
                    'float',
                    'float',
                    'float',
                    'float',
                    'float',
                    'float',
                    'float',
                    'float',
                    'float')}
        else:
            # If not training data, read the confounds.tsv format described here:
            # https://fmriprep.readthedocs.io/en/stable/outputs.html#confounds
            self._files = Path(confounds_path).glob('**/confounds.tsv')
            self._delimiter = '\t'
            self._converters = {3: na_converter, 4: na_converter, 5: na_converter}
            self._data_type = {
                'names': (
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
                    'non_steady_state_outlier00',
                    'trans_x',
                    'trans_y',
                    'trans_z',
                    'rot_x',
                    'rot_y',
                    'rot_z'
                ),
                'formats': (
                    'float',
                    'float',
                    'float',
                    'float',
                    'float',
                    'float',
                    'float',
                    'float',
                    'float',
                    'float',
                    'float',
                    'float',
                    'float',
                    'float',
                    'float',
                    'float',
                    'float',
                    'float',
                    'float',
                    'float',
                    'float',
                    'float',
                    'float',
                    'float',
                    'float'
                )}

    def read_files(self) -> numpy.ndarray:
        n_columns = len(self._data_type['names'])
        output_array = numpy.empty((0, n_columns))

        for f in self._files:
            tmp = numpy.loadtxt(f, delimiter=self._delimiter, skiprows=1, dtype=self._data_type,
                                converters=self._converters)
            output_array = numpy.append(output_array, tmp)

        return output_array
