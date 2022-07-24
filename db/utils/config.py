import os
from configparser import ConfigParser

# https://stackoverflow.com/a/5137509
dir_path = os.path.dirname(os.path.realpath(__file__))


def config(filename='database.ini', section='local') -> dict:
    """**Makes a dict out of string.**

    Taking info from database.ini to use for the database connection
    :param filename: A ini file containing info for connection in the same folder as this file
    :type filename: str
    :param section: Where in the ini file it should look
    :type section: str
    :return: A dictionary with connection info
    :rtype: dict
    """
    full_filename = os.path.join(dir_path, filename)
    parser = ConfigParser()
    parser.read(full_filename)

    db = {}
    section = "postgresql "+section
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file.'.format(section, full_filename))

    return db
