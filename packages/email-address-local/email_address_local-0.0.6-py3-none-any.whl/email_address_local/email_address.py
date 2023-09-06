from circles_local_database_python.connector import Connector
from circles_local_database_python.generic_crud import GenericCRUD
from logger_local.Logger import Logger
from logger_local.LoggerComponentEnum import LoggerComponentEnum
from language_local_python_package.src.language_enum_class import LanguageCode
from dotenv import load_dotenv
load_dotenv()
EMAIL_ADDRESS_LOCAL_PYTHON_COMPONENT_ID = 174
EMAIL_ADDRESS_LOCAL_PYTHON_COMPONENT_NAME  = 'email address local'
DEVELOPER_EMAIL = "idan.a@circ.zone"
object1 = {
    'component_id': EMAIL_ADDRESS_LOCAL_PYTHON_COMPONENT_ID,
    'component_name': EMAIL_ADDRESS_LOCAL_PYTHON_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    'developer_email': "idan.a@circ.zone"
}
logger = Logger.create_logger(object=object1)


class EmailAddress(GenericCRUD):

    def __init__(self) -> None:
        pass

    @staticmethod
    def insert(email_address: str, lang_code: LanguageCode, name: str) -> int or None:
        logger.start(object={"email_address": email_address, "lang_code":lang_code.value,"name":name})
        email_id = None
        try:
            connection = Connector.connect("email_address")
            query = "INSERT INTO email_address_table(`email`)" \
                " VALUES ('{}')".format(email_address)
            cursor = connection.cursor()
            cursor.execute(query)
            email_id = cursor.lastrowid()
            query = "INSERT INTO email_address.email_ml_table(email_id,lang_code,name)" \
                " VALUES ({},'{}','{}')".format(email_id, lang_code.value, name)
            cursor.execute(query)
            connection.commit()
        except Exception as e:
            logger.exception(object=e)
            raise
        logger.end(object={'email_id': email_id})
        return email_id

    @staticmethod
    def update(email_address_id: int, new_email: str) -> None:
        try:
            logger.start(
                object={"email_address_id": email_address_id, "new_email": new_email})
            connection = Connector.connect("email_address")
            query = "UPDATE email_address_table SET email = %s WHERE email_address_id = %s;"
            cursor = connection.cursor()
            values = (new_email, email_address_id)
            cursor.execute(query, values)
            connection.commit()
        except Exception as e:
            logger.exception(object=e)
            raise
        logger.end(object={})

    @staticmethod
    def update_name(email_address_id: int, new_name: str) -> None:
        try:
            logger.start(
                object={"email_address_id": email_address_id, "new_name": new_name})
            connection = Connector.connect("email_address")
            query = "UPDATE email_address_table SET email = %s WHERE email_address_id = %s;"
            cursor = connection.cursor()
            values = (new_name, email_address_id)
            cursor.execute(query, values)
            connection.commit()
        except Exception as e:
            logger.exception(object=e)
            raise
        logger.end(object={})

    @staticmethod
    def delete(email_id: int) -> None:
        try:
            logger.start(object={"email_id": email_id})
            connection = Connector.connect("email_address")
            query = "UPDATE email_address_table SET end_timestamp = current_time() WHERE email_address_id = %s;"
            cursor = connection.cursor()
            cursor.execute(query, (email_id,))
            connection.commit()
        except Exception as e:
            logger.exception(object=e)
            raise
        logger.end(object={})

    @staticmethod
    def get_email_address_by_email_address_id(email_address_id: int) -> str:
        email_address = None
        try:
            logger.start(object={"email_address_id":  email_address_id})
            connection = Connector.connect("email_address")
            query = "SELECT email FROM email_address_view WHERE email_address_id=%s"
            cursor = connection.cursor()
            cursor.execute(query, ( email_address_id,))
            result=cursor.fetchone()
            if result is not None:
                email_address = result[0]
        except Exception as e:
            logger.exception(object=e)
            raise
        logger.end(object={'email_address': email_address})
        return email_address

    @staticmethod
    def get_email_address_id_by_email_address(email: str) -> int or None:
        email_address_id = None
        try:
            logger.start(object={"email": email})
            connection = Connector.connect("email_address")
            query = "SELECT email_address_id FROM email_address_view WHERE email=%s"
            cursor = connection.cursor()
            cursor.execute(query, (email,))
            result=cursor.fetchone()
            if result is not None:
                email_address_id = result[0]
        except Exception as e:
            logger.exception(object=e)
            raise
        logger.end(object={'email_address_id': email_address_id})
        return email_address_id
