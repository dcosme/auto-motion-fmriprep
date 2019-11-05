from src.confounds_file_reader import ConfoundsFileReader
import shutil


class TestConfoundsFileReader:
    def test_regex_train(self, tmp_path, shared_datadir):
        # Create a badly-named data file in test-controlled path
        shutil.copyfile((shared_datadir / 'test_development.tsv'), tmp_path / 'development_sample.tsv')

        c = ConfoundsFileReader(tmp_path)

        # Assert that get_confounds should not return any subject ID, wave number, task name or run number
        # when the file name is not in the expected format.
        for i, _ in c.get_confounds():
            assert i.subject_id == ''
            assert i.task == ''
            assert i.wave == ''
            assert i.run == ''

    def test_regex(self, tmp_path, shared_datadir):
        # Verify that the regex extracts subject ID, wave number, task name or run number from files named in the
        # expected form for actual data. file_name = sub-DEV001_ses-wave1_task-WTP_acq-4_desc-confounds_regressors
        # Create a training data file in test-controlled path
        subject_id = 'DEV001'
        wave = '1'
        task = 'WTP'
        run = '4'
        file_name = f'sub-{subject_id}_ses-wave{wave}_task-{task}_acq-{run}_desc-confounds_regressors.tsv'
        confounds_path = tmp_path / "confounds"
        confounds_path.mkdir()
        data_file = confounds_path / file_name
        shutil.copyfile((shared_datadir / 'test_confounds.tsv'), data_file)

        c = ConfoundsFileReader(confounds_path)

        # Assert that data has a subject ID, wave number, task name and run number
        for i, _ in c.get_confounds():
            assert i.subject_id == subject_id
            assert i.task == task
            assert i.wave == wave
            assert i.run == run

    def test_multiple_files(self, tmp_path, shared_datadir):
        # Create several files with data
        # The test data file has extra columns, to verify column filtering,
        # and missing data in the form of 'n/a' entries, to verify na_converter.
        subject_id = 'DEV001'
        wave = "1"
        task = 'WTP'

        confounds_path = tmp_path / "confounds"
        confounds_path.mkdir()

        num_files = 4
        for run in range(num_files):
            file_name = f'sub-{subject_id}_ses-wave{wave}_task-{task}_acq-{run}_desc-confounds_regressors.tsv'
            data_file = confounds_path / file_name
            shutil.copyfile((shared_datadir / 'test_confounds.tsv'), data_file)

        c = ConfoundsFileReader(confounds_path)

        # Assert that several files were read, and that the data has the "right" shape
        count = 0
        for _, data in c.get_confounds():
            assert data.shape == (2,)
            assert len(data[0]) == c.get_size()
            count += 1

        assert count == num_files

    def test_training_data(self, tmp_path, shared_datadir):
        # Create a badly-named data file in test-controlled path
        shutil.copyfile((shared_datadir / 'test_development.tsv'), tmp_path / 'development_sample.tsv')

        c = ConfoundsFileReader(tmp_path)

        data = c.get_training_data()

        # There are two lines of input data.
        # Length of data should be length of _names + 1, for the additional 'artifact' column in training data.
        assert data.shape == (2,)
        assert len(data[0]) == c.get_size() + 1

    def test_v1_1_file_format(self, tmp_path, shared_datadir):
        # Verify that ConfoundsFileReader can read data in the V1.1 fmriprep format.
        # The primary differences are that the files are named differently:
        # "sub-<sub_id>/func/sub-<sub_id>_task-<task_id>_run-<run_id>_confounds.tsv",
        # that the column names are represented differently: WhiteMatter compared with white_matter,
        # and that there are many many fewer confounds in the older format.
        subject_id = 'DEV001'
        wave = '1'
        task = 'WTP'
        run = '1'

        file_name = f'sub-{subject_id}_ses-wave{wave}_task-{task}_run-{run}_confounds.tsv'
        confounds_path = tmp_path / "confounds"
        confounds_path.mkdir()
        data_file = confounds_path / file_name
        shutil.copyfile((shared_datadir / 'test_v1_1_confounds.tsv'), data_file)

        c = ConfoundsFileReader(confounds_path, is_v1_1_format=True)

        # Assert that several files were read, and that the data has the "right" shape
        for _, data in c.get_confounds():
            assert data.shape == (2,)
            assert len(data[0]) == c.get_size()
            assert 'csf' in data.dtype.names
