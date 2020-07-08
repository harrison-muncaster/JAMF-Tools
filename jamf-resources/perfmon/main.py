#!/usr/bin/env python3

import os
import shutil
from datetime import date
from matplotlib.backends.backend_pdf import PdfPages

from files import Files
from graph import Graph


NUM_DAYS = os.environ['NUM_DAYS']
USER_NAME = os.environ['USER_NAME']
TODAY = date.today()
PROCESS_COLS = ['time', 'process-name', '%cpu-process']
CPU_MEM_COLS = ['time', '%cpu-system', '%memory-system', 'process-rank']
PROCESS_CONVERT = {'%cpu-process': lambda x: float(x.strip('%')),
                   'time': lambda x: x.split('_')[1],
                   'process-name': lambda x: x.split('/')[-1]}
CPU_MEM_CONVERT = {'%cpu-system': lambda x: float(x.strip('%')),
                   '%memory-system': lambda x: float(x.strip('%'))}


def main():
    graphs = []

    #  Create a FILES object that parses the relevant files for graphs.
    files = Files(NUM_DAYS, TODAY)

    #  Create CPU/MEM graph instance and configure settings.
    cpu_mem = Graph(files, USER_NAME, CPU_MEM_COLS, CPU_MEM_CONVERT)
    cpu_mem.parse_relevant_rank()
    cpu_mem.plot_graphs(kind='line', stacked=False, colormap='cool')
    cpu_mem.set_cpu_mem_config()
    graphs.append(cpu_mem)

    #  Create PROCESS graph instance for each relevant day and configure settings.
    for file in sorted(files.relevant_csv_files, reverse=True):
        date = file.split('[')[0]
        if date in files.relevant_dates:
            processes = Graph(files, USER_NAME, PROCESS_COLS, PROCESS_CONVERT, date)
            processes.group_processes()
            processes.plot_graphs(kind='bar', stacked='True', colormap='cool')
            processes.set_process_config()
            graphs.append(processes)

    #  Iterate over each graph object and print to single PDF file.
    with PdfPages(f'../logs/{USER_NAME}-{NUM_DAYS}DayReport.pdf') as pdf:
        for graph in graphs:
            pdf.savefig(graph.fig)

    #  Remove temp directory for CSV files.
    shutil.rmtree('../logs/unpacked/')


if __name__ == '__main__':
    main()
