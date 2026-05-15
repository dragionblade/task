from Child import Child

def main():
    obj = Child()

    csv_data = obj.read_file_data()

    processed_results = []
    for row in csv_data:
        if len(row) >= 3:
            message = row[0]
            expected_amount = row[1]
            expected_currency = row[2]
            
            extracted_amount, extracted_currency = obj.extractAmountAndCurrency(message)
            
            processed_results.append(
                (message, extracted_amount, expected_amount, extracted_currency, expected_currency)
            )
        else:
            print(f"Warning: Skipping malformed row: {row}")
            
    obj.write_results(processed_results)
    print("Process finished.")

if __name__ == "__main__":
    main()