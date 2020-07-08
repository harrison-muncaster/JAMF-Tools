import glob
import os
import shutil
import tarfile
from datetime import timedelta


class Files:
    def __init__(self, num_days, today):
        #  Collect all tar files
        self.all_tars = glob.iglob('../logs/*.tar.gz')

        #  Sort tar files by most recent creation time
        self.sorted_tars = sorted(self.all_tars, key=os.path.getctime, reverse=True)

        #  Collect all CSV files
        self.recent_csv_files = glob.glob("../logs/*.csv")

        self.num_days = int(num_days)
        self.today = today

        #  Extract TAR files to unpacked directory
        self.extract_tar_files()

        #  Copy CSV files to unpacked directory
        self.copy_csv_files()

        #  Collect all CSV files in unpacked directory
        self.all_csv_files = glob.glob("../logs/unpacked/*.csv")

        #  Collect date relevant CSV files from unpacked directory
        self.relevant_csv_files = sorted([file.split('../logs/unpacked/')[1] for file in self.all_csv_files])

        #  Determine relevant dates
        self.relevant_dates = {(self.today - timedelta(days=x)).isoformat() for x in range(self.num_days)}

    def extract_tar_files(self):
        """Extract TAR files to new temp directory."""
        os.mkdir('../logs/unpacked')
        try:
            if self.num_days == 30:
                relevant_tars = [self.sorted_tars[0]]
            elif self.num_days == 60:
                relevant_tars = self.sorted_tars[:2]
            elif self.num_days == 90:
                relevant_tars = self.sorted_tars[:3]
            elif self.num_days == 180:
                relevant_tars = self.sorted_tars[:6]

            for tar in relevant_tars:
                tar_reader = tarfile.open(tar)
                tar_reader.extractall('../logs/unpacked')
                tar_reader.close()
        except IndexError as e:
            pass

    def copy_csv_files(self):
        """Copy CSV files to new temp directory."""
        for file in self.recent_csv_files:
            shutil.copy2(file, '../logs/unpacked')