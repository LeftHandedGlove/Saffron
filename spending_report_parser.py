import csv
import os
from enum import Enum, auto
import pprint
import datetime

class ReportSource(Enum):
    UNKNOWN = auto()
    SAFFRON = auto()
    DISCOVER = auto()
    WELLS_FARGO = auto()

class CardType(Enum):
    UNKNOWN = auto()
    CREDIT = auto()
    CHECKING = auto()

class Sorters(Enum):
    TRANSACTION_DATE = auto()


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
            f"{self.posted_date}, {self.description}, {self.amount}, {self.source_category}, "
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

    def save_report(self, report_dir):
        now_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        report_path = os.path.join(report_dir, f"Saffron_Spending_Report_{now_str}.csv")
        with open(report_path, 'w+', newline='') as report_csv_file:
            csv_writer = csv.writer(report_csv_file)
            csv_writer.writerow([
                'Source', 'CardType', 'TransDate', 'PostDate', 'Description', 'Amount', 
                'SourceCategory', 'Category', 'SubCategory', 'SubSubCategory'
            ])
            for entry in self.get_entires(sorted_by=Sorters.TRANSACTION_DATE):
                if entry.transaction_date is None:
                    trans_date_str = ""
                else:
                    trans_date_str = entry.transaction_date.strftime('%Y-%m-%d')
                if entry.posted_date is None:
                    post_date_str = ""
                else:
                    post_date_str = entry.posted_date.strftime('%Y-%m-%d')
                csv_writer.writerow([
                    entry.source.name, 
                    entry.card_type.name, 
                    trans_date_str,
                    post_date_str,
                    entry.description,
                    entry.amount,
                    entry.source_category,
                    entry.category,
                    entry.subcategory,
                    entry.subsubcategory
                ])

    def add_entry(self, entry):
        if not self.check_for_repeat_entry(entry):
            self.entries.append(entry)

    def check_for_repeat_entry(self, entry_to_check):
        # TODO: There is a bug where if there are legitimate repeats then 
        #       those will be removed. That could probably be fixed by 
        #       adding a source file with timestamp attribute to each entry
        #       and checking against that. This is so rare that I won't bother
        #       with it now.
        for entry in self.entries:
            trans_date_same = entry.transaction_date == entry_to_check.transaction_date
            amount_same = entry.amount == entry_to_check.amount
            description_same = entry.description == entry_to_check.description
            if trans_date_same and amount_same and description_same:
                return True
        return False

    def get_entires(self, filters=None, sorted_by=None):
        copied_entries = self.entries.copy()
        # Apply Filters
        if filters is None:
            pass
        else:
            raise NotImplementedError(f"Unsupported Filters Found")
        # Sort filtered list
        if sorted_by == Sorters.TRANSACTION_DATE:
            copied_entries.sort(key=lambda x: x.transaction_date)
        elif sorted_by is None:
            pass
        else:
            raise NotImplementedError(f"Unsupported Sorter: {sorted_by.name}")
        return copied_entries
        

class FinanceFolderParser:
    def __init__(self):
        self.spending_report = SpendingReport()

    def parse_report(self, report_path):
        # Determine the type of report
        with open(report_path, 'r') as report_csv_file:
            line_0 = report_csv_file.readlines()[0]
            if 'Saffron_Spending_Report' in os.path.basename(report_path):
                report_source = ReportSource.SAFFRON
            elif 'Trans. Date,Post Date,Description,Amount,Category' in line_0:
                report_source = ReportSource.DISCOVER
            elif '"*"' in line_0:
                report_source = ReportSource.WELLS_FARGO
            else:
                report_source = ReportSource.UNKNOWN
        # Parse the report
        source_to_parser_map = {
            ReportSource.SAFFRON: self.parse_saffron_csv_report,
            ReportSource.DISCOVER: self.parse_discover_csv_report,
            ReportSource.WELLS_FARGO: self.parse_wells_fargo_csv_report
        }
        try:
            source_to_parser_map[report_source](report_path)
        except KeyError as err:
            pass

    def parse_saffron_csv_report(self, csv_file_path):
        with open(csv_file_path, 'r') as report_csv_file:
            csv_reader = csv.reader(report_csv_file)
            for row_idx, row in enumerate(csv_reader):
                if row_idx == 0:
                    continue
                entry = ReportEntry()
                entry.source = ReportSource[row[0]]
                entry.card_type = CardType[row[1]]
                entry.transaction_date = datetime.datetime.strptime(row[2], "%Y-%m-%d").date()
                try:
                    entry.posted_date = datetime.datetime.strptime(row[3], "%Y-%m-%d").date()
                except ValueError as err:
                    pass
                entry.description = row[4]
                entry.amount = float(row[5])
                entry.source_category = row[6]
                entry.category = row[7]
                entry.subcategory = row[8]
                entry.subsubcategory = row[9]
                self.spending_report.add_entry(entry)
            
    def parse_discover_csv_report(self, csv_file_path):
        with open(csv_file_path, 'r') as report_csv_file:
            csv_reader = csv.reader(report_csv_file)
            for row_idx, row in enumerate(csv_reader):
                if row_idx == 0:
                    continue
                entry = ReportEntry()
                entry.source = ReportSource.DISCOVER
                entry.card_type = CardType.CREDIT
                entry.transaction_date = datetime.datetime.strptime(row[0], "%m/%d/%Y").date()
                entry.posted_date = datetime.datetime.strptime(row[1], "%m/%d/%Y").date()
                entry.description = row[2]
                entry.amount = float(row[3])
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
                entry.transaction_date = datetime.datetime.strptime(row[0], "%m/%d/%Y").date()
                entry.description = row[4]
                entry.amount = float(row[1])
                self.spending_report.add_entry(entry)
            

    def parse_folder(self, folder_path):
        self.spending_report.clear_report()
        for filename in os.listdir(folder_path):
            full_path = os.path.join(folder_path, filename)
            if os.path.isfile(full_path):
                if os.path.splitext(filename)[1] == '.csv':
                    self.parse_report(full_path)
        self.spending_report.save_report(folder_path)
        return self.spending_report



