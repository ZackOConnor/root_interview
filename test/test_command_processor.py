import warnings
import unittest
import io
import sys
import os
import subprocess
import src
from mock import patch
from src import command_processor
from src.command_processor import CommandProcessor, report

class TestCommandProcessor(unittest.TestCase):

    def test_process_returns_dict(self):
        return_dict = CommandProcessor('test/test_data.txt').process()
        self.assertIsInstance(return_dict, dict)

    def test_process_returns_correct_values(self):
        return_dict = CommandProcessor('test/test_data.txt').process()
        expec_dict = {'Dan': [50.0, 39.1], 'Alex': [75.0, 42.0], 'Bob': [0, 0]}
        self.assertEqual(return_dict, expec_dict)

    def test_line_parser_return_list(self):
        return_list = CommandProcessor('test/test_data.txt')._line_parser("testing the line parser")
        self.assertIsInstance(return_list, list)

    def test_line_parser_empty(self):
        return_list = CommandProcessor('test/test_data.txt')._line_parser("")
        self.assertIsInstance(return_list, list)

    def test_line_parser_split(self):
        return_list = CommandProcessor('test/test_data.txt')._line_parser("1 2 3")
        expec_list = ["1", "2", "3"]
        assert return_list ==  expec_list

    def test_line_parser_removes_trailing_white_space(self):
        return_list = CommandProcessor('test/test_data.txt')._line_parser("test data\n")
        expec_list = ["test", "data"]
        assert return_list == expec_list
    
    def test_driver_dict(self):
        command_proc = CommandProcessor('test/test_data.txt')
        command_proc._driver(["Empty Data", "Empty Data"], "Test Name")
        expec_dict = {"Test Name": [0,0]}
        assert command_proc.driver_dict == expec_dict

    def test_driver_duplicate_warning(self):
        with warnings.catch_warnings(record=True) as w:
            command_proc = CommandProcessor('test/test_data.txt')
            command_proc.driver_dict = {"Test Name": [0,0]}
            command_proc._driver(["Empty Data", "Empty Data"], "Test Name")
            assert len(w) == 1
            assert issubclass(w[-1].category, RuntimeWarning)
        expec_dict = {"Test Name": [0,0]}
        assert command_proc.driver_dict == expec_dict
     

    def test_trip_dict(self):
        command_proc = CommandProcessor('test/test_data.txt')
        command_proc.driver_dict = {"Test Name": [0,0]}
        command_proc._trip(["trip", "driver", "00:00", "01:00", "60"], "Test Name")
        expec_dict = {"Test Name": [60,60]}
        assert expec_dict ==  command_proc.driver_dict

    def test_trip_driver_does_not_exists(self):
        with self.assertRaises(ValueError):
            command_proc = CommandProcessor('test/test_data.txt')
            command_proc.driver_dict = {}
            command_proc._trip(["trip", "driver", "00:00", "01:00", "60"], "Test Name")

    def test_trip_over_100mph(self):
        command_proc = CommandProcessor('test/test_data.txt')
        command_proc.driver_dict = {"Test Name": [0,0]}
        command_proc._trip(["trip", "driver", "00:00", "01:00", "10000"], "Test Name")
        expec_dict = {"Test Name": [0,0]}
        assert expec_dict ==  command_proc.driver_dict

    def test_trip_under_5mph(self):
        command_proc = CommandProcessor('test/test_data.txt')
        command_proc.driver_dict = {"Test Name": [0,0]}
        command_proc._trip(["trip", "driver", "00:00", "01:00", "1"], "Test Name")
        expec_dict = {"Test Name": [0,0]}
        assert expec_dict ==  command_proc.driver_dict

    def test_run_command_driver(self):
        with patch("src.command_processor.CommandProcessor._driver") as mock_command:
            command_proc = CommandProcessor('test/test_data.txt')
            command_proc._run_command(["Driver", 'Test Name'], "Test Name")
            self.assertTrue(mock_command.called)

    def test_run_command_trip(self):
        with patch("src.command_processor.CommandProcessor._trip") as mock_command:
            command_proc = CommandProcessor('test/test_data.txt')
            command_proc._run_command(["Trip", "driver", "00:00", "01:00", "60"], "Test Name")
            self.assertTrue(mock_command.called)


    def test_run_command_trip_raises_error(self):
        with self.assertRaises(ValueError):
            command_proc = CommandProcessor('test/test_data.txt')
            command_proc._run_command(["in valid command", 'Test Name'], "Test Name")

    def test_report_message(self):
        test_driver_dict = {"test name" : [60,60]}
        captured_output = io.StringIO()
        sys.stdout = captured_output
        report(test_driver_dict)
        sys.stdout = sys.__stdout__
        expec_line = "test name: 60 miles @ 60 mph\n"
        assert expec_line == captured_output.getvalue()


    def test_report_message_edge_case(self):
        test_driver_dict = {"test name" : [0,0]}
        captured_output = io.StringIO()
        sys.stdout = captured_output
        report(test_driver_dict)
        sys.stdout = sys.__stdout__
        expec_line = "test name: 0 miles\n"
        assert expec_line == captured_output.getvalue()

    def test_report_message_sorting(self):
        test_driver_dict = {"test name2" : [60,60], "test name1" : [120,60], "test name3" : [30,60]}
        captured_output = io.StringIO()
        sys.stdout = captured_output
        report(test_driver_dict)
        sys.stdout = sys.__stdout__
        expec_line = "test name3: 60 miles @ 120 mph\ntest name2: 60 miles @ 60 mph\ntest name1: 60 miles @ 30 mph\n"
        assert expec_line == captured_output.getvalue()

    def test_main(self):
        out_put = os.popen("python ./src/command_processor.py ./test/test_data.txt").read()
        expec_line = "Alex: 42 miles @ 34 mph\nDan: 39 miles @ 47 mph\nBob: 0 miles\n"
        assert expec_line == out_put


if __name__ == '__main__':
        unittest.main()