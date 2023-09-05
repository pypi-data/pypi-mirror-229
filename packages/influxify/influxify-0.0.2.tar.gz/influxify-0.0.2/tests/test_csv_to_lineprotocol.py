import unittest
import tempfile
import os
from io import StringIO
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.influxify.main import CsvToInfluxDb
from pandas.testing import assert_frame_equal

class TestCsvToInfluxDb(unittest.TestCase):

    def setUp(self):
        self.csv_data = 'id,name,age,timestamp\n1,John,30,0\n2,Jane,25,0\n3,Bob,40,0\n'
        self.csv_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        self.csv_file.write(self.csv_data)
        self.csv_file.close()
        self.measurement = 'people'
        self.tag_columns = ['id']
        self.field_columns = ['age']
        self.timestamp_col = 'timestamp'
        self.timestamp_format = '%Y-%m-%d %H:%M:%S'
        self.expected_line_protocols = 'people,id=1 age=30 0\npeople,id=2 age=25 0\npeople,id=3 age=40 0\n'

    def tearDown(self):
        os.unlink(self.csv_file.name)

    def test_convert_to_lineprotocol(self):
        csv_to_influxdb = CsvToInfluxDb(self.csv_file.name, self.measurement, self.tag_columns, self.field_columns, self.timestamp_col, self.timestamp_format)
        line_protocols = csv_to_influxdb.convert_to_lineprotocol()
        self.assertEqual(line_protocols, self.expected_line_protocols)

    def test_write_to_lineprotocol(self):
        csv_to_influxdb = CsvToInfluxDb(self.csv_file.name, self.measurement, self.tag_columns, self.field_columns, self.timestamp_col, self.timestamp_format)
        line_protocols = csv_to_influxdb.convert_to_lineprotocol()
        output_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        csv_to_influxdb.write_to_lineprotocol(output_file.name, line_protocols)
        output_file.close()
        with open(output_file.name, 'r') as f:
            self.assertEqual(f.read(), self.expected_line_protocols)

if __name__ == '__main__':
    unittest.main()
