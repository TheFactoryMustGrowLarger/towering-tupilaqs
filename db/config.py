from configparser import ConfigParser


def config(filename='database.ini', section='postgresql') -> dict:
    """**Makes a dict out of string.**

    Taking info from database.ini to use for the database connection
    :param filename: A ini file containing info for connection
    :type filename: str
    :param section: Where in the ini file it should look
    :type section: str
    :return: A dictionary with connection info
    :rtype: dict
    """
    parser = ConfigParser()
    parser.read(filename)

    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file.'.format(section, filename))

    return db
