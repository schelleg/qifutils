import pandas as pd

from parse import QIFParser

class QifReport:
    def __init__(self, qifparse):
        """
        Initialize the Report class with a DataFrame.
        :param df: DataFrame containing the QIF data with columns including 'Account' and 'U'.
        """
        self.df = qifparse.df


class AccountBalance(QifReport):
    def __init__(self, qifparse):
        super().__init__(qifparse)

    def generate_report(self, account_name):
        """
        Generate a report for the given account name by summing the 'U' column.
        :param account_name: The account name to filter by (e.g., 'Checking', 'Savings').
        :return: A string report showing the account name and the sum of the 'U' column.
        """
        # Filter the DataFrame by the given Account name
        filtered_df = self.df[self.df['Account'] == account_name]

        # Sum the 'U' column for the filtered rows
        total_u = filtered_df['T'].sum()



        # Prepare the report
        report = f"Report for Account: {account_name}\n"
        report += f"Total sum of 'U' column: {total_u}\n"
        
        # You can add more details to the report if needed
        report += "\nDetailed Transactions:\n"
        report += filtered_df[['D', 'T', 'N', 'P', 'M', 'U']].to_string(index=False)

        return report


# Example usage
if __name__ == "__main__":
    # Sample QIF data for demonstration (including 'U' column)
    sample_qif = """
    !Type:Bank
    D12/01/2024
    T-150.00
    N12345
    PExample Payee
    MExample Memo
    U100
    ^
    !Account:Checking
    !Type:CCard
    D12/01/2024
    T-50.00
    N67890
    PAnother Payee
    MCredit card payment
    U150
    ^
    !Account:Savings
    !Type:Invst
    D12/01/2024
    T+1000.00
    NInvestment Account
    SStock XYZ
    MInvestment transaction
    U200
    ^
    """
    # Save the sample QIF content to a file
    file_path = "schelle_2017a.QIF"
    # with open(file_path, "w") as f:
    #     f.write(sample_qif)

    # Initialize the QIF parser
    parser = QIFParser(file_path)


    # Display the DataFrame with human-readable columns and filled Account field
    print(parser.df)

    # Create the Report object
    report = AccountBalance(parser)

    # Generate a report for the 'Checking' account
    checking_report = report.generate_report("Unnamed Account")
    print("\n" + checking_report)


    # Export the DataFrame to an Excel file
    parser.export_to_excel("report_file.xlsx")