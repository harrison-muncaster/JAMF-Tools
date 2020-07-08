import pandas as pd
from matplotlib import style
import matplotlib.ticker as mtick
import matplotlib.pyplot as plt
from functools import cached_property


class Graph:
    def __init__(self, files, user, cols, converters, date=None):
        self.files = files
        self.user = user
        self.cols = cols
        self.converters = converters
        self.date = date
        self.ax = pd.DataFrame(self.dataframe)
        self.style = style.use('seaborn')

    @cached_property
    def dataframe(self):
        """Cached Property: Construct & return dataframe from CSVs."""
        if self.date:
            df = pd.concat((pd.read_csv(f'../logs/unpacked/{f}', usecols=self.cols, converters=self.converters, header=0)
                            for f in self.files.relevant_csv_files
                            if f.split('[')[0] == self.date))
        else:
            df = pd.concat((pd.read_csv(f'../logs/unpacked/{f}', usecols=self.cols, converters=self.converters, header=0)
                            for f in self.files.relevant_csv_files
                            if f.split('[')[0] in self.files.relevant_dates))
        return df

    @cached_property
    def fig(self):
        """Cached Property: Set & Return plot figure."""
        fig = plt.gcf()
        return fig

    def plot_graphs(self, **kwargs):
        """Plot dataframe."""
        self.ax = self.ax.plot(kind=kwargs['kind'], stacked=kwargs['stacked'], colormap=kwargs['colormap'])

    def set_cpu_mem_config(self):
        """Set configs for CPU/MEM graph."""

        #  Shade in area from X-axis to CPU Y-axis line.
        #plt.fill_between(self.ax['time'], self.ax['%cpu-system'], alpha=0.30)

        start = self.files.relevant_csv_files[0].split('[')[0]
        end = self.files.relevant_csv_files[-1].split('[')[0]
        self.set_graph_config(legend_labels=['CPU', 'Memory'],
                              ylabel='Overall CPU Usage %',
                              xlabel=f'{start} - {end}')

    def parse_relevant_rank(self):
        """Parse rows where process-rank is == 1 & drop process-rank col."""
        df = self.ax[self.ax['process-rank'] == 1].drop('process-rank', axis=1)
        self.ax = df.set_index('time')

    def group_processes(self):
        """Group rows by process-name & drop processes == 0."""
        df = self.ax[self.ax['%cpu-process'] > 0.0]
        df = df.groupby(['time', 'process-name']).apply(self.change_process_name)
        self.ax = df.groupby(['time', 'process-name'])['%cpu-process'].sum().unstack()

    def set_process_config(self):
        """Set configs for Processes graph."""
        for p in self.ax.patches:
            width, height = p.get_width(), p.get_height()
            x, y = p.get_xy()
            if height != 0.0:
                self.ax.text(x + width / 2,
                             y + height / 2,
                             '{:.0f}%'.format(height),
                             horizontalalignment='center',
                             verticalalignment='center',
                             fontsize='xx-small')

        self.set_graph_config(legend_labels=None,
                              ylabel='Overall CPU Usage %',
                              xlabel=self.date)

    def set_graph_config(self, **kwargs):
        """Set common graph configs."""

        #  Add % sign to Y-axis tick marks.
        self.ax.yaxis.set_major_formatter(mtick.PercentFormatter())

        #  Set location of legend, font size, and labels.
        plt.legend(loc='upper left', fontsize='x-small', labels=kwargs['legend_labels'])

        #  Set Y label.
        plt.ylabel(kwargs['ylabel'])

        #  Set X label.
        plt.xlabel(kwargs['xlabel'])

        #  Rotate X-axis tick mark labels and set font size.
        plt.setp(self.ax.get_xticklabels(), fontsize='x-small')
        self.fig.autofmt_xdate()

        #  Set size of figure.
        self.fig.set_size_inches((14, 10.5), forward=False)

        #  Remove surrounding whitespace on Graph.
        self.fig.tight_layout()

        #  Set DPI for graph.
        plt.figure(dpi=300)

    @staticmethod
    def change_process_name(group):
        """Change name of process if process < 10%."""
        if group['%cpu-process'].sum() < 10:
            group['process-name'] = 'Other - Processes < 10%'
        return group
