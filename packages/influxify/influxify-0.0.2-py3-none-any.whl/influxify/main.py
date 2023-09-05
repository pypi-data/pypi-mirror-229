import pandas as pd

class CsvToInfluxDb:
    """A class that converts a CSV file to InfluxDB Line Protocol format.

    Attributes:
        csv_file_path (str): The file path of the CSV file.
        measurement (str): The name of the InfluxDB measurement to use.
        tag_columns (list[str]): A list of column names to use as tags in the Line Protocol.
        field_columns (list[str]): A list of column names to use as fields in the Line Protocol.
        timestamp_col (str): The name of the column to use as the timestamp in the Line Protocol.
        timestamp_format (str): The format string of the timestamp column, e.g. '%Y-%m-%d %H:%M:%S'.

    """
    def __init__(self, csv_file_path, measurement, tag_columns, field_columns, timestamp_col, timestamp_format=None):
        self.csv_file_path = csv_file_path
        self.measurement = measurement
        self.tag_columns = tag_columns
        self.field_columns = field_columns
        self.timestamp_format = timestamp_format
        self.timestamp_col = timestamp_col

    def convert_to_lineprotocol(self):
        """Convert the CSV file to InfluxDB Line Protocol format.

        Returns:
            str: A string containing the Line Protocol.

        """

        df = pd.read_csv(self.csv_file_path)
        
        df = df.replace(float('nan'), '')
        
        df[self.timestamp_col] = pd.to_datetime(df[self.timestamp_col], format='mixed').astype('int64') // 10**9 * 10**9


        df[self.tag_columns] = df[self.tag_columns].replace(' ', '\ ', regex=True)
        
        line_protocols = ''
        
        for i, row in df.iterrows():
            tags = ",".join([f"{tag}={row[tag]}" for tag in self.tag_columns])
            fields = ",".join([f"{field}={row[field]}" if isinstance(row[field], (int, float)) else f'{field}="{row[field]}"' for field in self.field_columns])
            line_protocols += (f"{self.measurement},{tags} {fields} {row[self.timestamp_col]}\n")
        
        return  line_protocols
    
    def write_to_lineprotocol(self, filepath, line_protocols):
        """Write the Line Protocol to a file.

        Args:
            filepath (str): The file path of the output file.
            line_protocols (str): The Line Protocol to write.

        """
        with open(filepath, 'w+') as f:
                f.write(line_protocols)

    
