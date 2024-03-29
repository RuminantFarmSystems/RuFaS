class UserInput(Exception):
    """Raised when the user enters an invalid input at the prompt"""

    def __init__(self, msg):
        self.msg = "USER INPUT ERROR: " + str(msg)


class InvalidJSONfile(Exception):
    """Raised when the json file fed to the program has problems"""

    def __init__(self, file_name):
        self.msg = "Skipping simulation for {}\n".format(file_name)


class JSONfileData(Exception):
    """Raised when specific parts of the json file has problems"""

    def __init__(self, section, msg):
        self.section = section
        self.msg = msg
