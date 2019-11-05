from typing import Union
from os import PathLike
from pathlib import Path
from identifier import Identifier
import numpy
import numpy.lib.recfunctions


class Realignment:
    def __init__(self, output_dir: Union[str, PathLike]):
        self._output_dir = output_dir
        self._column_names = ['trans_x',
                              'trans_y',
                              'trans_z',
                              'rot_x',
                              'rot_y',
                              'rot_z']
        # Create root output directory if missing
        Path(self._output_dir).mkdir(parents=True, exist_ok=True)

    def write(self, identifier: Identifier, no_euclidean: bool, data: numpy.ndarray, artifact: numpy.ndarray):
        """
        Write realignment parameters
        :param identifier: The subject, task, run identifier
        :param no_euclidean: If True, write raw translation and rotation.
        If False, write out the L2 norms of translation and rotation.
        :param data: confounds data
        :param artifact: Array indicating if there is a motion artifact or not
        :return: None
        """
        if not set(self._column_names).issubset(set(data.dtype.names)):
            raise ValueError('data does not contain required columns')

        # Create output directory if missing
        path = Path(self._output_dir / f'sub-{identifier.subject_id}' / f'ses-wave{identifier.wave}' / 'func')
        path.mkdir(parents=True, exist_ok=True)

        file_name = f'sub-{identifier.subject_id}_ses-wave{identifier.wave}_' \
                    f'task-{identifier.task}_acq-{identifier.run}-realignment_parameters.txt'

        if not no_euclidean:
            translation_components = numpy.lib.recfunctions.structured_to_unstructured(data[self._column_names[0:3]])
            translation = numpy.linalg.norm(translation_components, axis=1)
            diff_translation = numpy.diff(translation, prepend=0)
            rotation_components = numpy.lib.recfunctions.structured_to_unstructured(data[self._column_names[3:6]])
            # Multiply the radian output of the realignment parameters by the average
            # head radius of 50mm to get a rotational displacement from the origin at the
            # outside of an average skull.
            rotation = 50.0 * numpy.linalg.norm(rotation_components, axis=1)
            diff_rotation = numpy.diff(rotation, prepend=0)
            data_to_write = numpy.stack((translation, rotation, diff_translation, diff_rotation, artifact), axis=1)
        else:
            data_to_write = numpy.lib.recfunctions.append_fields(data[self._column_names], 'artifact', artifact)

        fmt = ['%.7f'] * (len(data_to_write[0]) - 1) + ['%d']
        numpy.savetxt(path / file_name, data_to_write,
                      fmt=fmt, delimiter='   ')
