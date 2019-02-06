import sys
import warnings
import pandas as pd
from datetime import datetime

class CommandProcessor:
    """Collects driver and trip data from a .txt file in order to aggregate data by driver
    Parameters: 
        file_path - path to the .txt to be processed 
    """  

    def __init__(self, file_path):
        self.file_path = file_path
        self.file = open(self.file_path)
        self.driver_dict = dict()
        # add any new commands to this list
        self.valid_command_list = ['Driver','Trip']

    def _line_parser(self, line):
        """removes trailing whitespace specifically \\n and parses the line to return a list
        Parameters:
            line - a single line from the .txt file
        returns the line parsed on spaces as a list 
        """
        line = (line.rstrip()).split(' ')
        return line

    def _run_command(self, parsed_line, driver):
        """pulls out the command from the parsed_line list and runs the appropriate function
        Parameters:
            parsed_line - a single list returned from _line_parser
            driver - name of the driver, str
        """
        # gets the command from the parsed line
        command = parsed_line[0]
        if command not in self.valid_command_list:
            raise ValueError("{} is not a vaild command. Vaild commands are {}".format(command, self.valid_command_list))
        command = command.lower()
        # runs the appropriate method of the CommandProcessor class based on the command parameter
        run_command = getattr(CommandProcessor, '_' + command)
        run_command(self, parsed_line, driver)

    def process(self):
        """runs each line of the file through the parser and command runner 
        returns 
            self.driver_dict - a dictionary of {driver_name: [total_minutes, total_miles]}
        """
        for line in self.file:
            parsed_line = self._line_parser(line)
            driver = parsed_line[1]
            self._run_command(parsed_line, driver)
        return self.driver_dict

    def _driver(self, parsed_line, driver):
        """takes in a driver command and creates a new key, value pair in driver_dict set to {driver name: [0,0]}"""
        # gives a warning if the driver already exists in driver_dict
        if driver in self.driver_dict.keys():  
            warnings.warn('Driver {} already exists'.format(driver), RuntimeWarning)
        else:
            self.driver_dict[driver] = [0, 0]

    def _trip(self, parsed_line, driver):
        """Calculates the elapsed time in minutes and miles driven and adds them to driver_dict based on driver name
        if the average MPH for the trip is between 5 and 100 MPH
        """
        if driver not in self.driver_dict.keys():
            raise ValueError("{} does not exists as a driver".format(driver))
        frmt = '%H:%M'  # time format
        start_time = datetime.strptime(parsed_line[2], frmt)
        end_time = datetime.strptime(parsed_line[3], frmt)
        elapsed_time = end_time - start_time
        elapsed_minutes = elapsed_time.total_seconds() / 60
        miles_driven = float(parsed_line[4])

        # checks that the MPH is between 5 and 100
        if 5 < miles_driven / elapsed_minutes * 60 < 100:
            self.driver_dict[driver][0] = self.driver_dict[driver][0] + elapsed_minutes
            self.driver_dict[driver][1] = self.driver_dict[driver][1] + miles_driven

def report(driver_dict):
    """Calculates MPH and sorts based on total miles traveled, then prints to command prompt"""
    driver_df = pd.DataFrame.from_dict(driver_dict, orient='index')
    driver_df.columns = ['Minutes', 'Miles']
    driver_df['MPH'] = driver_df.Miles / driver_df.Minutes * 60 
    driver_df = driver_df.round()
    driver_df = driver_df.fillna(0)
    driver_df = driver_df.astype(int)
    driver_df = driver_df.sort_values(by=['Miles', 'MPH'], ascending=False)

    def create_msg(driver_info):
        """returns formatted driver information"""
        created_msg = "{driver}: {miles} miles".format(driver=driver_info.name, miles=driver_info[1])
        if driver_info[1] != 0:
            created_msg += " @ {} mph".format(driver_info[2])
        print(created_msg)
    # applies the msg function to every row
    formatted_driver_dict = driver_df.apply(create_msg, axis=1)
    return formatted_driver_dict


def main():
    # takes the file path given from the command prompt
    file_path = sys.argv[1]
    # processes and aggregate by driver the .txt file
    commands = CommandProcessor(file_path).process()
    # sorts and prints driver data to the command prompt 
    report(commands)

if __name__ == "__main__":
    main()