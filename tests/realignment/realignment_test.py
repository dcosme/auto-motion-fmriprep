from src.realignment import Realignment
import numpy
import pytest


class TestRealignment:
    def test_write_file_created(self, tmp_path):
        rp = Realignment(tmp_path)
        subject_id = 'SUBJECT_ID'
        wave = '1'
        run = '1'
        task = 'TASK'
        data = numpy.array([(1.0, 2.0, 3.0, 4.0, 5.0, 6.0)],
                           dtype=[('trans_x', 'f8'),
                                  ('trans_y', 'f8'),
                                  ('trans_z', 'f8'),
                                  ('rot_x', 'f8'),
                                  ('rot_y', 'f8'),
                                  ('rot_z', 'f8')])
        artifact = numpy.array([0.0])

        rp.write(subject_id=subject_id, wave=wave, task=task, run=run, no_euclidean=False, data=data, artifact=artifact)

        expected_file_name = f'sub-{subject_id}_ses-wave{wave}_task-{task}_acq-{run}-realignment_parameters.txt'
        expected_path = tmp_path / f'sub-{subject_id}' / f'ses-wave{wave}' / 'func'

        assert expected_path.exists()
        assert (expected_path / expected_file_name).exists()

    def test_invalid_columns(self, tmp_path):
        # Verify that invalid input data raises a ValueError
        rp = Realignment(tmp_path)
        subject_id = 'SUBJECT_ID'
        wave = '1'
        run = '1'
        task = 'TASK'
        data = numpy.array([(1.0, 2.0, 3.0)],
                           dtype=[('invalid_column_1', 'f8'),
                                  ('invalid_column_2', 'f8'),
                                  ('invalid_column_3', 'f8')])
        artifact = numpy.array([0.0])

        with pytest.raises(ValueError):
            rp.write(subject_id=subject_id,
                     wave=wave,
                     task=task,
                     run=run,
                     no_euclidean=False,
                     data=data,
                     artifact=artifact)

    def test_no_euclidean_false(self, tmp_path):
        rp = Realignment(tmp_path)
        subject_id = 'SUBJECT_ID'
        wave = '1'
        run = '1'
        task = 'TASK'
        data = numpy.array([(1.0, 2.0, 3.0, 4.0, 5.0, 6.0)],
                           dtype=[('trans_x', 'f8'),
                                  ('trans_y', 'f8'),
                                  ('trans_z', 'f8'),
                                  ('rot_x', 'f8'),
                                  ('rot_y', 'f8'),
                                  ('rot_z', 'f8')])
        artifact = numpy.array([0.0])

        rp.write(subject_id=subject_id, wave=wave, task=task, run=run, no_euclidean=False, data=data, artifact=artifact)

        expected_file_name = f'sub-{subject_id}_ses-wave{wave}_task-{task}_acq-{run}-realignment_parameters.txt'
        expected_path = tmp_path / f'sub-{subject_id}' / f'ses-wave{wave}' / 'func'

        # Assert output has the correct number of columns
        output = numpy.loadtxt(expected_path / expected_file_name, delimiter='   ')

        assert output.shape == (5,)

    def test_no_euclidean_true(self, tmp_path):
        rp = Realignment(tmp_path)
        subject_id = 'SUBJECT_ID'
        wave = '1'
        run = '1'
        task = 'TASK'
        data = numpy.array([(1.0, 2.0, 3.0, 4.0, 5.0, 6.0)],
                           dtype=[('trans_x', 'f8'),
                                  ('trans_y', 'f8'),
                                  ('trans_z', 'f8'),
                                  ('rot_x', 'f8'),
                                  ('rot_y', 'f8'),
                                  ('rot_z', 'f8')])
        artifact = numpy.array([0.0])

        rp.write(subject_id=subject_id, wave=wave, task=task, run=run, no_euclidean=True, data=data, artifact=artifact)

        expected_file_name = f'sub-{subject_id}_ses-wave{wave}_task-{task}_acq-{run}-realignment_parameters.txt'
        expected_path = tmp_path / f'sub-{subject_id}' / f'ses-wave{wave}' / 'func'

        # Assert output has the correct number of columns
        output = numpy.loadtxt(expected_path / expected_file_name, delimiter='   ')

        assert output.shape == (7,)
