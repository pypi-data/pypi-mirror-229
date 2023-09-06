import sys
import os
script_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_directory, '..'))
from circles_importer.importer import Importer
from logger_local.Logger import Logger
from logger_local.LoggerComponentEnum import LoggerComponentEnum
from circles_local_database_python.connector import Connector
import datetime

LOCATION_ID = 17241
ENTITY_TYPE_ID = 1
ENTITY_ID = 2
USER_ID = 1
IMPORTER_LOCAL_PYTHON_COMPONENT_ID = 114
IMPORTER_LOCAL_PYTHON_COMPONENT_NAME = 'importer-local-python-package'
URL = "https://example.com"

object_init = {
    'component_id': IMPORTER_LOCAL_PYTHON_COMPONENT_ID,
    'component_name': IMPORTER_LOCAL_PYTHON_COMPONENT_NAME,
    'component_category':LoggerComponentEnum.ComponentCategory.Unit_Test.value,
    'testing_framework':LoggerComponentEnum.testingFramework.Python_Unittest.value,
    'developer_email': 'idan.a@circlez.ai'
}
logger = Logger.create_logger(object=object_init)

class TestImporter():
    importer=Importer()
    def test_insert(self):
        logger.start("test insert and after get it", object={})
        database_conn = Connector.connect('importer')
        data_source_id = TestImporter.get_minutes_digit()
        cursor = database_conn.cursor()    
        self.importer.insert(
            url=URL,user_id=USER_ID,data_source_id=data_source_id,location_id=LOCATION_ID,entity_type_id=ENTITY_TYPE_ID,entity_id=ENTITY_ID)
        sql_query="SELECT source_id,entity_type_id,entity_id,url FROM importer.importer_table WHERE created_user_id={} ORDER BY created_timestamp desc limit 1".format(USER_ID)
        cursor.execute(sql_query)
        token=cursor.fetchone()
        assert token[0]==data_source_id
        assert token[1]==ENTITY_TYPE_ID
        assert token[2]==ENTITY_ID
        assert token[3]==URL
        logger.end("Test succeeded", object={'token':token})
        return

    @staticmethod
    def get_minutes_digit():
        current_time = datetime.datetime.now()
        minutes = current_time.minute
        minutes_digit = minutes % 10
        return minutes_digit