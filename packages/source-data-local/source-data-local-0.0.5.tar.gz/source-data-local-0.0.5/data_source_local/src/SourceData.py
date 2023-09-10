from dotenv import load_dotenv
from logger_local.LoggerLocal import logger_local
from circles_local_database_python.database import database
load_dotenv()
obj = {
    'component_id': 117
}
logger_local.init(object=obj)
db = database()
connection = db.connect_to_database()


class SourceData():
    @staticmethod
    def insert_source_data(source_name):
        object1 = {
            'source_name': source_name,
        }
        logger_local.start(object=object1)
        try:
            cursor = connection.cursor()
            query_importer_source = "INSERT INTO source.source_table(`created_user_id`,`updated_user_id`)" \
                " VALUES (1, 1)"
            cursor.execute(query_importer_source)
            connection.commit()
            last_inserted_id = cursor.lastrowid
            query_importer_source_ml = "INSERT INTO source.source_ml_table(`source_name`,`source_id`,`created_user_id`,`updated_user_id`)" \
                " VALUES (%s, %s, 1, 1)"
            cursor.execute(query_importer_source_ml,
                           (source_name, last_inserted_id))
            connection.commit()
            logger_local.end(object={})
            connection.close()
        except Exception as e:
            logger_local.exception(object=e)

    @staticmethod
    def get_source_data_id(source_name):
        source_id = None
        try:
            object1 = {
                'source_name': source_name,
            }
            logger_local.start(object=object1)
            cursor = connection.cursor()
            cursor.execute("SELECT source_id FROM source.source_ml_en_view WHERE source_name = '{}'".format(
                source_name))
            if cursor:
                source_id = cursor.fetchone()[0]
            else:
                source_id = None
        except Exception as e:
            logger_local.exception(object=e)
        object1 = {
            'source_id': source_id,
        }
        logger_local.end(object=object1)
        return source_id
