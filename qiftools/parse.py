import pandas as pd
import re
from datetime import datetime


class QIFParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.current_switch = None # Track the current QIF switch   
        self.current_account = "Unnamed Account"
        self.current_type = "Unset Type"                    
        self.switches = []          # Store all detected switches        
        self.df = self._parse_to_dataframe()

        self.clean_illegal_characters()
        self.clean_column_types()        
        self.translate_fields()


    def _parse_to_dataframe(self):
        # Read the file content
        with open(self.file_path, "r") as file:
            file_content = file.read()
        
        # Split the content into chunks based on '^'
        chunks = file_content.strip().split("^")
        
        rows = []
        for chunk in chunks:
            if not chunk.strip():  # Skip empty chunks
                continue
            
            # Parse each line in the chunk
            row = {}
            for line in chunk.strip().split("\n"):
                if not line:  # Ignore empty lines
                    continue

                line = line.lstrip().rstrip()

                if line.startswith("!"):  # Handle QIF switches
                    self.current_switch = line
                    self._parse_qif_directive(line)
                    continue

                key = line[0]  # Leading character as column
                value = line[1:].strip()  # Rest of the line as value
                row[key] = value

            row["Switch"] = self.current_switch
            row["Account"] = self.current_account  
            row["Type"] = self.current_type



            rows.append(row)
        
        # Convert the list of dictionaries to a DataFrame
        df = pd.DataFrame(rows)

        # Convert the 'D' column to datetime
        if 'D' in df.columns:
            df['D'] = df['D'].apply(QIFParser.to_date)

        return df

    def _parse_qif_directive(self, line):
        """
        Processes a QIF directive and updates the global state.
        
        :param line: A string representing a QIF directive (e.g., '!Account:Checking').
        """
        if line.startswith("!Account:"):
            # Update the current account
            self.current_account = line[len("!Account:"):].strip()
            print(f"Switched to account: {self.current_account}")
        elif  line.startswith("!Type:"):
            # Update the current account
            self.current_type = line[len("!Type:"):].strip()
            print(f"Switched to type: {self.current_type}")

        elif line == "!Option:AutoSwitch":
            # Enable auto-switching for accounts
            self.current_autoswitch = True
            print("Enabled auto-switching for accounts")
        else:
            print(f"Unrecognized directive: {line}")
            # raise ValueError(f"Unrecognized directive: {line}")        

    def translate_fields(self):
        """
        Translate QIF fields to human-readable names based on the current switch.
        :param df: DataFrame containing QIF data.
        :return: DataFrame with translated field names.
        """
        field_translation = {
            '!Type:Bank': {
                'D': 'Date',
                'T': 'Amount',
                'N': 'Transaction Number',  # Check number or reference number
                'P': 'Payee',
                'M': 'Memo'
            },
            '!Type:CCard': {
                'D': 'Date',
                'T': 'Amount',
                'N': 'Transaction Number',  # Credit card transaction number
                'P': 'Payee',
                'M': 'Memo'
            },
            '!Type:Invst': {
                'D': 'Date',
                'T': 'Amount',
                'N': 'Account Name',  # Account associated with the investment
                'S': 'Security',  # Investment security (e.g., stock name)
                'M': 'Memo'
            }
        }

        # Add human-readable columns based on translation map
        for i, row in self.df.iterrows():
            switch = row["Switch"]
            if switch in field_translation:
                translation_map = field_translation[switch]
                for qif_field, readable_name in translation_map.items():
                    if qif_field in row:
                        self.df.loc[i, readable_name] = row[qif_field]  # Assign value to new column
        
        

    def clean_illegal_characters(self):
        """
        Clean the DataFrame by removing illegal characters from each row.
        Illegal characters are defined as anything not alphanumeric or standard punctuation.
        This method removes characters like control characters and other unwanted symbols.
        :param df: DataFrame to be cleaned.
        :return: Cleaned DataFrame.
        """
        # Define a pattern for allowed characters (letters, digits, spaces, common punctuation)
        allowed_pattern = r'[^a-zA-Z0-9\s\.,;:!?()&/-]'
        
        # Iterate over each column and row, cleaning any value that contains illegal characters
        for column in self.df.columns:
            self.df[column] = self.df[column].apply(lambda x: re.sub(allowed_pattern, '', str(x)) if isinstance(x, str) else x)
        print("Illegal characters have been cleaned from the DataFrame.")

    def export_to_excel(self, file_path):
        self.df.to_excel(file_path, index=False)
        print(f"DataFrame has been exported to {file_path}")


    def clean_column_types(self):
        for float_column in ["U", "T"]:
            self.df[float_column] = pd.to_numeric(self.df[float_column], errors="coerce")

    @staticmethod
    def to_date(date_string):
        """
        Convert a date string in formats like '2/ 1'24' or '7/17'24' to a datetime object.
        Example: "2/ 1'24" -> datetime(2024, 2, 1) and "7/17'24" -> datetime(2024, 7, 17)
        """
        if pd.isna(date_string):
            return

        try:
            # Normalize the date string by removing spaces around the slash and fixing the year format
            new_string = date_string.replace("'", "/20")  # Replace `'24` with `2024`
            # Ensure there's no extra space around the month/day
            new_string = new_string.replace("/", "-").replace(" ", "") 
            # Check if the string is in the correct format (e.g., 2-1-2024 or 7-17-2024)
            return datetime.strptime(new_string, "%m-%d-%Y")
        except ValueError as e:
            raise ValueError(f"Invalid date format: {date_string} {new_string}") from e



# Example usage
if __name__ == "__main__":
    # Save a sample QIF content to a file for demonstration
    sample_qif = """
    !Type:Bank
    D2/ 1'24
    T100.00
    PExample Payee
    MExample Memo
    ^
    
    !Account
    NExample Account
    D2/ 2'24
    T200.50
    PAnother Payee
    MAnother Memo
    ^
    """
    # file_path = "sample.qif"
    file_path = r"schelle_2017.QIF"
    # with open(file_path, "w") as f:
    #    f.write(sample_qif)
    
    # Initialize the parser and parse the file
    parser = QIFParser(file_path)

    # Display the DataFrame and tracked switches
    print(parser.df)

    # Export the DataFrame to an Excel file
    parser.export_to_excel("output_file.xlsx")
