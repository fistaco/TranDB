import unittest
from unittest.mock import MagicMock
import sqlite3


class TranDB:
    def __init__(self):
        self.log_file_name = None

    def __repr__(self):
        return "TranDB"

    def __str__(self):
        return "TranDB"

    def create_db(self):
        stripped_log_file_name = self.log_file_name.rsplit(".", 1)[0]
        connection = sqlite3.connect(f"{stripped_log_file_name}.db")
        cursor = connection.cursor()

        header_contents = "Time INT, Command TEXT"
        table_name = f"{stripped_log_file_name}_table"
        create_table_string = f"CREATE TABLE {table_name}({header_contents})"
        cursor.execute(create_table_string)

        log_file_contents = self.get_log_file_contents()

        insert_data_string = f"INSERT INTO {table_name}(Time, Command) VALUES (?, ?);"
        cursor.executemany(insert_data_string, log_file_contents)
        connection.commit()

    def get_log_file_contents(self):
        return []


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.cut = TranDB()
        self.log_file_name = "my_log_file"
        self.log_file_contents = '"Time", "Command"\n"0", "RD"\n"1", "WR"'
        self.cut.log_file_name = f"{self.log_file_name}.csv"
        self.cut.get_log_file_contents = MagicMock(return_value=self.log_file_contents)

    def test_string_overriders_are_overridden(self):
        self.assertEqual("TranDB", repr(TranDB()))
        self.assertEqual("TranDB", str(TranDB()))

    @unittest.mock.patch("TranDB.sqlite3")
    def test_can_create_db_file_from_csv(self, mock_sqlite3):
        mock_sqlite3.connect().return_value = None
        mock_sqlite3.connect().cursor().execute.return_value = None
        mock_sqlite3.connect().cursor().execute_many.return_value = None
        self.cut.create_db()
        self.cut.get_log_file_contents.assert_called_once()


if __name__ == '__main__':
    unittest.main()
