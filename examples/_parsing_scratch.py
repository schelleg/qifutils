import pandas as pd

def parse_qif(file_content):
    # Split the content into chunks based on '^'
    chunks = file_content.strip().split("^")
    
    rows = []
    for chunk in chunks:
        if not chunk.strip():  # Skip empty chunks
            continue
        
        # Parse each line in the chunk
        row = {}
        for line in chunk.strip().split("\n"):
            if line:  # Ignore empty lines
                key = line[0]  # Leading character as column
                value = line[1:].strip()  # Rest of the line as value
                row[key] = value
        rows.append(row)
    
    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(rows)
    return df

# Example QIF content
qif_content = """
D2023-12-31
T100.00
PExample Payee
MExample Memo
^

D2024-01-01
T200.50
PAnother Payee
MAnother Memo
^
"""

# Parse the QIF content into a DataFrame
df = parse_qif(qif_content)

# Display the DataFrame
print(df)