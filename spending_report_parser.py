import csv
import os
from enum import Enum, auto
import pprint
import datetime

class ReportSource(Enum):
    UNKNOWN = auto()
    DISCOVER = auto()
    WELLS_FARGO = auto()

class CardType(Enum):
    UNKNOWN = auto()
    CREDIT = auto()
    CHECKING = auto()


class ReportEntry:
    def __init__(self):
        # Defined by report
        self.source = ReportSource.UNKNOWN
        self.card_type = CardType.UNKNOWN
        self.transaction_date = None
        self.posted_date = None
        self.description = ""
        self.amount = 0.0
        self.source_category = ""
        # Defined by user
        self.category = ""
        self.subcategory = ""
        self.subsubcategory = ""

    def __str__(self):
        return (
            f"{self.source.name}, {self.card_type.name}, {self.transaction_date}, "
            f"{self.posted_date}, {self.description}, {self.source_category}, "
            f"{self.category}, {self.subcategory}, {self.subsubcategory}"
        )


class SpendingReport:
    def __init__(self):
        self.entries = []

    def __repr__(self):
        return "SpendingReport()"
    
    def __str__(self):
        entries_str = ""
        for entry in self.entries:
            entries_str += f"{entry}\n"
        return entries_str

    def clear_report(self):
        self.entries = []

    def add_entry(self, entry):
        self.entries.append(entry)
        

class FinanceFolderParser:
    def __init__(self):
        self.spending_report = SpendingReport()

    def parse_report(self, report_path):
        # Determine the type of report
        with open(report_path, 'r') as report_csv_file:
            line_0 = report_csv_file.readlines()[0]
            if 'Trans. Date,Post Date,Description,Amount,Category' in line_0:
                report_source = ReportSource.DISCOVER
            elif '"*"' in line_0:
                report_source = ReportSource.WELLS_FARGO
            else:
                report_source = ReportSource.UNKNOWN
        # Parse the report
        source_to_parser_map = {
            ReportSource.DISCOVER: self.parse_discover_csv_report,
            ReportSource.WELLS_FARGO: self.parse_wells_fargo_csv_report
        }
        try:
            source_to_parser_map[report_source](report_path)
        except KeyError as err:
            pass
            
    def parse_discover_csv_report(self, csv_file_path):
        with open(csv_file_path, 'r') as report_csv_file:
            csv_reader = csv.reader(report_csv_file)
            for row_idx, row in enumerate(csv_reader):
                if row_idx == 0:
                    continue
                entry = ReportEntry()
                entry.source = ReportSource.DISCOVER
                entry.card_type = CardType.CREDIT
                entry.transaction_date = row[0]
                entry.posted_date = row[1]
                entry.description = row[2]
                entry.amount = row[3]
                entry.source_category = row[4]
                self.spending_report.add_entry(entry)

    def parse_wells_fargo_csv_report(self, csv_file_path):
        # Get the card type from the file name
        if 'Checking' in os.path.basename(csv_file_path):
            card_type = CardType.CHECKING
        elif 'CreditCard' in os.path.basename(csv_file_path):
            card_type = CardType.CREDIT
        else:
            card_type = CardType.UNKNOWN
        with open(csv_file_path, 'r') as report_csv_file:
            csv_reader = csv.reader(report_csv_file)
            for row in csv_reader:
                entry = ReportEntry()
                entry.source = ReportSource.WELLS_FARGO
                entry.card_type = card_type
                entry.transaction_date = row[0]
                entry.description = row[4]
                entry.amount = row[1]
                self.spending_report.add_entry(entry)
            

    def parse_folder(self, folder_path):
        self.spending_report.clear_report()
        for filename in os.listdir(folder_path):
            full_path = os.path.join(folder_path, filename)
            if os.path.isfile(full_path):
                if os.path.splitext(filename)[1] == '.csv':
                    self.parse_report(full_path)
        print(self.spending_report)
        return self.spending_report



