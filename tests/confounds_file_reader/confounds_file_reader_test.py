from src.confounds_file_reader import ConfoundsFileReader
from pathlib import Path
import shutil


class TestConfoundsFileReader:
    def test_regex_train(self, tmp_path, shared_datadir):
        # Create a training data file in test-controlled path
        shutil.copyfile((shared_datadir / 'test_development.tsv'), tmp_path / 'development_sample.tsv')

        c = ConfoundsFileReader(tmp_path, train=True)

        # Assert that training data should not have any subject ID, wave number, task name or run number
        for subject_id, wave, task, run, _ in c.get_confounds():
            assert subject_id == ''
            assert task == ''
            assert wave == ''
            assert run == ''

    def test_regex(self, tmp_path, shared_datadir):
        # Verify that the regex extracts subject ID, wave number, task name or run number from files named in the
        # expected form for actual data. file_name = sub-DEV001_ses-wave1_task-WTP_acq-4_desc-confounds_regressors
        # Create a training data file in test-controlled path
        subject_id = 'DEV001'
        wave = '1'
        task = 'WTP'
        run = '4'
        file_name = f'sub-{subject_id}_ses-wave{wave}_task-{task}_acq-{run}_desc-confounds_regressors.tsv'
        data_file = tmp_path.joinpath(file_name)
        shutil.copyfile((shared_datadir / 'test_confounds.tsv'), data_file)

        c = ConfoundsFileReader(tmp_path)

        # Assert that data has a subject ID, wave number, task name and run number
        for a_subject_id, a_wave, a_task, a_run, _ in c.get_confounds():
            assert a_subject_id == subject_id
            assert a_task == task
            assert a_wave == wave
            assert a_run == run

    def test_multiple_files(self, tmp_path, shared_datadir):
        # Create several files with data
        # The test data file has extra columns, to verify column filtering,
        # and missing data in the form of 'n/a' entries, to verify na_converter.
        subject_id = 'DEV001'
        wave = "1"
        task = 'WTP'

        num_files = 4
        for run in range(num_files):
            file_name = f'sub-{subject_id}_ses-wave{wave}_task-{task}_acq-{run}_desc-confounds_regressors.tsv'
            data_file = tmp_path.joinpath(file_name)
            shutil.copyfile((shared_datadir / 'test_confounds.tsv'), data_file)

        c = ConfoundsFileReader(tmp_path)

        # Assert that several files were read, and that the data has the "right" shape
        count = 0
        for a_subject_id, a_wave, a_task, a_run, data in c.get_confounds():
            assert data.shape == (2,)
            assert len(data[0]) == len(c._names)
            count += 1

        assert count == num_files
