from logger_local.LoggerComponentEnum import LoggerComponentEnum
import random 
import sys
from dotenv import load_dotenv
load_dotenv()
from circles_local_database_python.connector import Connector # noqa: E402
from logger_local.Logger import Logger  # noqa: E402


INIT_METHOD_NAME = "__init__"
GET_CONNECTION_METHOD_NAME = "get_connection"
GET_RANDOM_NUMBER_METHOD_NAME = "get_random_number"

CIRCLES_NUMBER_GENERATOR_COMPONENT_ID = 177
CIRCLES_NUMBER_GENERATOR_COMPONENT_NAME = "circles_number_generator/src/number_generator.py"

object_to_insert = {
    'component_id': CIRCLES_NUMBER_GENERATOR_COMPONENT_ID,
    'component_name': CIRCLES_NUMBER_GENERATOR_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    'developer_email': 'tal.g@circ.zone'
}

logger = Logger.create_logger(object=object_to_insert)

class NumberGenerator:

    @staticmethod
    def get_random_number(schema: str, table: str, id_column_name: str, number_column_name: str = "`number`"):
        logger.start(GET_RANDOM_NUMBER_METHOD_NAME)
        connector = Connector.connect(schema)
        cursor = connector.cursor()

        successful = False

        while not successful:
            number = random.randint(1, sys.maxsize)
            logger.info(object = {"Random number generated": str(number)})
            
            query_get = "SELECT %s FROM %s.%s WHERE %s = %s"
            cursor.execute(query_get % (id_column_name, schema, table, number_column_name, number))
            if cursor.fetchone() == None:
                successful = True
                logger.info("Number does not already exist in database")

        logger.end(GET_RANDOM_NUMBER_METHOD_NAME, object = {"number" : number})
        return number 