import os
import csv
from abc import ABC, abstractmethod

class Utility(ABC):
    @abstractmethod
    def getMasterDataFilePath(self):
        pass

    @abstractmethod
    def extractAmountAndCurrency(self, message):
        pass

    def normalize(self, value):
        normalized_value = value
        if not normalized_value:
            normalized_value = ""
        
        normalized_value = str(normalized_value).lower()
        
        return normalized_value 

    def read_file_data(self):
        data_rows = []
        file_path = self.getMasterDataFilePath()

        if not file_path:
            print("Error: Master data file path is not provided.")
        else:
            try:
                if os.path.exists(file_path):
                    with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
                        reader = csv.reader(csvfile)
                        next(reader, None)  # Skip header
                        for row in reader:
                            if row:
                                data_rows.append(row)
                else:
                     print(f"Error: Input file not found at {file_path}")
            except (IOError, csv.Error) as e:
                print(f"Error: Could not read file {file_path}. Reason: {e}")
        
        return data_rows 

    def write_results(self, results):
        if isinstance(results, list):
            fail_cases = 0
            total_cases = len(results)
            write_succeeded = False
            
            failed_rows = []
            
            for result in results:
                if not isinstance(result, (list, tuple)) or len(result) != 5:
                    print(f"Warning: Skipping malformed result item: {result}")
                    total_cases -= 1 
                    continue
                
                msg, ext_amt, exp_amt, ext_curr, exp_curr = result
                
                amt_match = self.normalize(ext_amt) == self.normalize(exp_amt)
                curr_match = self.normalize(ext_curr) == self.normalize(exp_curr)

                if not (amt_match and curr_match):
                    fail_cases += 1
                    failed_rows.append(result)
            
            try:
                file_path = self.getMasterDataFilePath()
                folder_path = os.path.dirname(file_path) if file_path else "."

                output_file_path = os.path.join(folder_path, "output.csv")
                failed_cases_file_path = os.path.join(folder_path, "failedCases.csv")
                
                header = ["Message", "ExtractedAmount", "ExpectedAmount", "ExtractedCurrency", "ExpectedCurrency"]

                with open(output_file_path, mode='w', newline='', encoding='utf-8') as csvfile_out:
                    writer_out = csv.writer(csvfile_out, quoting=csv.QUOTE_ALL, escapechar='\\')
                    writer_out.writerow(header)
                    for row in results:
                        if isinstance(row, (list, tuple)) and len(row) == 5:
                            writer_out.writerow(row)
                
                with open(failed_cases_file_path, mode='w', newline='', encoding='utf-8') as csvfile_fail:
                    writer_fail = csv.writer(csvfile_fail, quoting=csv.QUOTE_ALL, escapechar='\\')
                    writer_fail.writerow(header)
                    for row in failed_rows:
                        writer_fail.writerow(row)
                
                write_succeeded = True
            
            except IOError as e:
                print(f"Error: Could not write output files. Reason: {e}")

            if write_succeeded:
                accuracy = ((total_cases - fail_cases) / total_cases) * 100 if total_cases > 0 else 0
                
                print(f"Total Cases: {total_cases}")
                print(f"Failed Cases: {fail_cases}")
                print(f"Accuracy: {accuracy:.2f}%")
                print(f"CSV writing completed successfully: {output_file_path}")
                print(f"Failed cases saved to: {failed_cases_file_path}")
        else:
            print("Error: Results data must be a list. Aborting write operation.")