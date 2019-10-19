import unittest
from unittest import mock
from unittest.mock import MagicMock
import csv
import re
import sqlite3


class TranDB:
    def __init__(self):
        self.log_file_name = "log_file_name.csv"

    def __repr__(self):
        return "TranDB"

    def __str__(self):
        return self.__repr__()

    def add_to_db(self):
        stripped_log_file_name = self.log_file_name.rsplit(".", 1)[0]
        connection = self._try_create_db(f"{stripped_log_file_name}.db")
        cursor = connection.cursor()

        log_file_headers, log_file_contents = self._get_log_file_data()
        log_file_header_as_sql = self._get_log_file_header_as_sql_header(log_file_headers)

        table_name = f"{stripped_log_file_name}_table"
        create_table_string = f"CREATE TABLE IF NOT EXISTS {table_name}({log_file_header_as_sql})"
        cursor.execute(create_table_string)

        header_count = self._get_number_of_headers(log_file_headers)
        values_string = f"VALUES ({self._get_insert_data_values_question_mark_string(header_count)})"
        insert_data_string = f"INSERT INTO {table_name}({log_file_headers}) {values_string};"
        cursor.executemany(insert_data_string, log_file_contents)
        connection.commit()

    @staticmethod
    def _try_create_db(db_name):
        return sqlite3.connect(db_name)

    def _get_log_file_data(self):
        with open(self.log_file_name, 'rb') as file:
            csv_file_as_list = csv.reader(file).strip().split("\n")
            header = csv_file_as_list[0]
            contents = csv_file_as_list[1:]
            return header, contents

    @staticmethod
    def _get_log_file_header_as_sql_header(header=""):
        header = header.replace('"', '').replace(',', '')
        return re.sub(r'([^\s]+)', r'\1 TEXT,',  header).strip(",")

    @staticmethod
    def _get_number_of_headers(header_string):
        return len(header_string.split(","))

    @staticmethod
    def _get_insert_data_values_question_mark_string(num_headers):
        return ("?, " * num_headers).strip(", ")


class TranDBTestCases(unittest.TestCase):
    def setUp(self):
        self.cut = TranDB()

    def set_log_file_variables(self, name="my_log_file", contents='"0", "RD"\n"1", "WR"',
                               headers='"Time", "Command"'):
        self.cut.log_file_name = f"{name}.csv"
        self.cut._get_log_file_data = MagicMock(return_value=(headers, contents))
        self.cut._get_log_file_header_as_sql_header = MagicMock(return_value=headers)

    def test_string_overriders_are_overridden(self):
        self.assertEqual("TranDB", repr(TranDB()))
        self.assertEqual(repr(TranDB()), str(TranDB()))

    def test_can_convert_header_to_sql_header(self):
        headers = '"Time", "Command"'
        self.assertEqual("Time TEXT, Command TEXT", self.cut._get_log_file_header_as_sql_header(headers))

    def test_can_get_number_of_headers(self):
        header_string = "Time, Command, Address"
        exp_number_of_headers = 3
        self.assertEqual(exp_number_of_headers, self.cut._get_number_of_headers(header_string))

        header_string = "Time, Command"
        exp_number_of_headers = 2
        self.assertEqual(exp_number_of_headers, self.cut._get_number_of_headers(header_string))

    def test_can_get_insert_data_values_question_mark_string(self):
        num_headers = 3
        exp_return_val = "?, ?, ?"
        self.assertEqual(exp_return_val, self.cut._get_insert_data_values_question_mark_string(num_headers))

        num_headers = 2
        exp_return_val = "?, ?"
        self.assertEqual(exp_return_val, self.cut._get_insert_data_values_question_mark_string(num_headers))

    @mock.patch("TranDB.sqlite3")
    def test_can_create_db_file_from_csv(self, mock_sqlite3):
        self.set_log_file_variables()
        mock_sqlite3.connect().return_value = None
        mock_sqlite3.connect().cursor().execute.return_value = None
        mock_sqlite3.connect().cursor().execute_many.return_value = None
        self.cut.add_to_db()
        self.cut._get_log_file_data.assert_called_once()


class FileIOTestCases(unittest.TestCase):
    def setUp(self):
        self.cut = TranDB()
        self.file_contents = "TIME, CMD, ADDRESS\n0, RD, 0xbaadbeefdeadbeef\n10, WR, 0xbaadbeefdeadbeef\n"

    @staticmethod
    def get_builtin_open_patch(file_contents=None):
        return mock.patch("builtins.open", mock.mock_open(read_data=file_contents))

    def test_can_get_log_file_contents_without_headers(self):
        csv.reader = MagicMock(return_value=self.file_contents)
        exp_return_val = ['0, RD, 0xbaadbeefdeadbeef', '10, WR, 0xbaadbeefdeadbeef']
        with self.get_builtin_open_patch(self.file_contents):
            header, contents = self.cut._get_log_file_data()
            self.assertEqual(exp_return_val, contents)

    def test_invalid_file_throws_exception(self):
        self.cut.log_file_name = "INVALID_FILE_NAME"
        self.assertRaises(FileNotFoundError, self.cut._get_log_file_data)


if __name__ == '__main__':
    unittest.main()
