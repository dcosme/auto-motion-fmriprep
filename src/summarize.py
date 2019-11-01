import numpy
import csv
from os import PathLike
from pathlib import Path
from typing import Union


class Summarize:
    def __init__(self, summary_dir: Union[str, PathLike], study: str = ''):
        self._summary_dir = Path(summary_dir)
        self._study = study
        self._by_run = []
        self._by_task = []
        self._all_artifacts = []

    def add(self, subject_id: str, wave: str, task: str, run: str, artifact: numpy.ndarray):
        """
        Add data to summaries
        :param subject_id: Subject identifier
        :param wave: Wave number
        :param task: Task name
        :param run: Run number
        :param artifact: Array indicating if there is a motion artifact or not
        :return: None
        """
        # Create summaries
        artifact_filter = (artifact == 1)
        artifact_volumes = numpy.where(artifact_filter)[0]
        num_artifact_volumes = numpy.sum(artifact)
        percent = num_artifact_volumes / artifact.size * 100.0

        self._by_run.append((subject_id, wave, task, run, num_artifact_volumes, percent))
        self._by_task.append((subject_id, wave, task, num_artifact_volumes, percent))

        for v in artifact_volumes:
            self._all_artifacts.append((subject_id, wave, task, v, 1))

    def write(self):
        """
        Write summaries to summary files
        :return: None
        """
        Path(self._summary_dir).mkdir(parents=True, exist_ok=True)

        with open(self._summary_dir / (self._study + '_summaryRun.csv'), 'w') as csv_file:
            bb = csv.writer(csv_file, quoting=csv.QUOTE_NONNUMERIC)
            bb.writerow(["subjectID", "wave", "task", "run", "nVols", "percent"])
            bb.writerows(self._by_run)

        with open(self._summary_dir / (self._study + '_summaryTask.csv'), 'w') as csv_file:
            bb = csv.writer(csv_file, quoting=csv.QUOTE_NONNUMERIC)
            bb.writerow(["subjectID", "wave", "task", "nVols", "percent"])
            bb.writerows(self._by_task)

        with open(self._summary_dir / (self._study + '_trashVols.csv'), 'w') as csv_file:
            bb = csv.writer(csv_file, quoting=csv.QUOTE_NONNUMERIC)
            bb.writerow(["subjectID", "wave", "task", "run", "volume", "trash"])
            bb.writerows(self._all_artifacts)
