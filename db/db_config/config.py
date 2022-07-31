import os
from configparser import ConfigParser

# https://stackoverflow.com/a/5137509
dir_path = os.path.dirname(os.path.realpath(__file__))


def config(filename='database.ini', section="postgresql") -> dict:
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
    if os.path.exists(full_filename):
        parser.read(full_filename)
    else:
        dir_content = os.listdir(dir_path)
        raise OSError('No {} found, copy one of the database_*.ini files to database.ini in {}. '
                      'found {}'.format(full_filename,
                                        dir_path,
                                        dir_content))

    db = {}

    if parser.has_section(section):
        params = parser.items(section)
        for key, value in params:
            # translate boolean true/false
            if value.lower() == 'true':
                value = True
            elif value.lower() == 'false':
                value = False

            db[key] = value
    else:
        raise Exception('Section {} not found in the {} file.'.format(section, full_filename))

    return db


if __name__ == '__main__':
    c = config('database_remote.ini')
    for key, value in c.items():
        print(key, type(value), value)
