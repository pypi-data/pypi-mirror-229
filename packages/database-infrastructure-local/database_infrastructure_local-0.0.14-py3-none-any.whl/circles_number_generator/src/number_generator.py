import random 
import sys
try:
    # Works when importing this module from another package
    from circles_number_generator.src.constants import *
except Exception as e:
    # Works when running the tests from this package
    from constants import *
from dotenv import load_dotenv
load_dotenv()
from circles_local_database_python.connector import Connector # noqa: E402
from logger_local.Logger import Logger  # noqa: E402


INIT_METHOD_NAME = "__init__"
GET_CONNECTION_METHOD_NAME = "get_connection"
GET_RANDOM_NUMBER_METHOD_NAME = "get_random_number"

logger = Logger.create_logger(object=OBJECT_TO_INSERT_CODE)

class NumberGenerator:

    @staticmethod
    def get_random_number(schema: str, table: str, number_column_name: str = "`number`"):
        logger.start(GET_RANDOM_NUMBER_METHOD_NAME)
        connector = Connector.connect(schema)
        cursor = connector.cursor()

        successful = False

        while not successful:
            random_number = random.randint(1, sys.maxsize)
            logger.info(object = {"Random number generated": str(random_number)})
            
            query_get = "SELECT COUNT(*) FROM %s.%s WHERE %s = %s LIMIT 1"
            cursor.execute(query_get % (schema, table, number_column_name, random_number))
            rows_count, = cursor.fetchone()
            if rows_count == 0:
                successful = True
                logger.info("Number does not already exist in database")
            else:
                logger.info("Number already exists in database")

        logger.end(GET_RANDOM_NUMBER_METHOD_NAME, object = {"number" : random_number})
        return random_number 