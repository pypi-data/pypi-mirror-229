from logger_local.LoggerComponentEnum import LoggerComponentEnum
from circles_local_database_python.generic_crud.src.generic_crud import GenericCRUD

from dotenv import load_dotenv
load_dotenv()

from circles_local_database_python.connector import Connector   # noqa: E402
from logger_local.Logger import Logger  # noqa: E402

# keep locally for now until package works
from circles_number_generator.src.number_generator import NumberGenerator  # noqa: E402

USER_LOCAL_PYTHON_PACKAGE_COMPONENT_ID = 171
USER_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME = "user_local/src/user.py"


object_to_insert = {
    'component_id': USER_LOCAL_PYTHON_PACKAGE_COMPONENT_ID,
    'component_name': USER_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    'developer_email': 'tal.g@circ.zone'
}

logger = Logger.create_logger(object=object_to_insert)


class User(GenericCRUD):
    def __init__(self):
        INIT_METHOD_NAME = "__init__"
        logger.start(INIT_METHOD_NAME)
        self.connector = Connector.connect("user")
        self.cursor = self.connector.cursor()
        logger.end(INIT_METHOD_NAME)

    def insert(self, profile_id: int, username: str, main_email: str, first_name: str, last_name: str, location_id: int) -> int:
        INSERT_USER_METHOD_NAME = "insert_user"
        logger.start(INSERT_USER_METHOD_NAME,
                     object={"profile_id": profile_id, "username": username, "main_email": main_email,
                             "first_name": first_name, "last_name": last_name, "location_id": location_id})

        number_generator = NumberGenerator("user", "user_table", "user_id")
        number = number_generator.get_random_number()

        query_insert = "INSERT INTO user_table (`number`, username, main_email, first_name, last_name, active_location_id) VALUES (%s, %s, %s, %s, %s, %s)"
        self.cursor.execute(query_insert, (number, username, main_email, first_name, last_name, location_id))

        user_id = self.cursor.lastrowid()

        self.connector.commit()
        logger.end(INSERT_USER_METHOD_NAME, object={"user_id": user_id})
        return user_id

    def update(self, user_id: int, username: str, main_email: str, first_name: str, last_name: str, location_id: int):
        UPDATE_USER_METHOD_NAME = "update_user"
        logger.start(
            UPDATE_USER_METHOD_NAME,
            object={"user_id": user_id, "location_id": location_id, "username": username, "main_email": main_email,
                    "first_name": first_name, "last_name": last_name})

        query_update = "UPDATE user_table SET username = %s, main_email = %s, first_name = %s, last_name = %s, active_location_id = %s WHERE user_id = %s"
        self.cursor.execute(query_update, (username, main_email, first_name, last_name, location_id, user_id))

        self.connector.commit()
        logger.end(UPDATE_USER_METHOD_NAME)

    def read(self, user_id: int) -> (int, int, str, str, str, str, int):
        READ_USER_METHOD_NAME = "read_user"
        logger.start(READ_USER_METHOD_NAME, object={"user_id": user_id})

        query_get = "SELECT `number`, username, main_email, first_name, last_name, active_location_id FROM user_view WHERE user_id = %s"
        self.cursor.execute(query_get, (user_id,))

        rows = self.cursor.fetchall()
        if len(rows) == 0:
            return None
        number, username, main_email, first_name, last_name, active_location_id = rows[0]

        logger.end(
            READ_USER_METHOD_NAME,
            object={"id": user_id, "number": number, "username": username, "main_email": main_email,
                    "first_name": first_name, "last_name": last_name, "active_location_id": active_location_id})
        return number, username, main_email, first_name, last_name, active_location_id

    def delete(self, user_id: int):
        DELETE_USER_METHOD_NAME = "delete_user"
        logger.start(DELETE_USER_METHOD_NAME, object={"user_id": user_id})

        query_update = "UPDATE user_table SET end_timestamp = NOW() WHERE user_id = %s"
        self.cursor.execute(query_update, (user_id,))

        self.connector.commit()
        logger.end(DELETE_USER_METHOD_NAME)
