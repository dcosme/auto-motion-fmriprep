from src.realignment import Realignment
import numpy


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

        expected_file_name = f'rp_{subject_id}_{wave}_{task}_{run}.txt'
        expected_path = tmp_path / expected_file_name

        assert expected_path.exists()

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

        expected_file_name = f'rp_{subject_id}_{wave}_{task}_{run}.txt'
        expected_path = tmp_path / expected_file_name

        # Assert output has the correct number of columns
        output = numpy.loadtxt(expected_path, delimiter='   ')

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

        expected_file_name = f'rp_{subject_id}_{wave}_{task}_{run}.txt'
        expected_path = tmp_path / expected_file_name

        # Assert output has the correct number of columns
        output = numpy.loadtxt(expected_path, delimiter='   ')

        assert output.shape == (7,)
