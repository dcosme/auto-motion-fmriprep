import numpy
import matplotlib.pyplot as pyplot
from pathlib import Path
from identifier import Identifier


class Plotter:
    def __init__(self, output_dir: str, identifier: Identifier, data: numpy.ndarray,
                 height: float, width: float, dpi: int, format: str = 'png'):
        self._identifier = identifier
        self._data = data
        self._height = height
        self._width = width
        self._dpi = dpi
        self._format = format

        # Create root output directory if missing
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        # Create output directory if missing
        path = Path(output_dir / f'sub-{identifier.subject_id}' / f'ses-wave{identifier.wave}' / 'func')
        path.mkdir(parents=True, exist_ok=True)

        self._output_dir = path

    def plot(self, column_name: str):
        """
        Plot a single column of data against volume number, labeling volumes with artifacts present.
        :param column_name: Name of column of data to plot
        :return: None
        """
        if column_name not in self._data.dtype.names:
            raise ValueError(f'Invalid data column for plotting: {column_name}')

        # Collect all the volumes where there is an artifact
        artifact_filter = self._data['artifact'] == 1
        artifact_volumes = numpy.where(artifact_filter)[0]
        column_data = self._data[artifact_filter][column_name]

        fig, ax = pyplot.subplots()
        ax.set_frame_on(False)
        ax.set_xlabel('volume')
        ax.set_ylabel(column_name)
        ax.grid(True)

        # Plot all the data for a given output variable
        ax.plot(column_name, data=self._data, linewidth=0.75, color='black')

        # On the same plot, add markers where artifact == 1, labeled with volume number
        ax.plot(artifact_volumes, column_data,
                linewidth=0, marker='o', markersize=16, markerfacecolor='#E4B80E', markeredgewidth=0)
        for i, volume in enumerate(artifact_volumes):
            ax.text(volume, column_data[i], volume,
                    horizontalalignment='center', verticalalignment='center', fontsize=7)

        fig.savefig(self._output_dir / f'{column_name}.{self._format}',
                    dpi=self._dpi, transparent=False, bbox_inches='tight',
                    height=self._height, width=self._width)
