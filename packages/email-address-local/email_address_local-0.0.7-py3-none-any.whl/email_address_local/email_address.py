from circles_local_database_python.connector import Connector
from circles_local_database_python.generic_crud.src.generic_crud import GenericCRUD
from logger_local.Logger import Logger
from logger_local.LoggerComponentEnum import LoggerComponentEnum
from language_local_python_package.src.language_enum_class import LanguageCode
from dotenv import load_dotenv
load_dotenv()
EMAIL_ADDRESS_LOCAL_PYTHON_COMPONENT_ID = 174
EMAIL_ADDRESS_LOCAL_PYTHON_COMPONENT_NAME = 'email address local'
DEVELOPER_EMAIL = "idan.a@circ.zone"
EMAIL_ADDRESS_SCHEMA_NAME = "email_address"
EMAIL_ADRESS_ML_TABLE_NAME = "email_ml_table"
EMAIL_ADDRESS_TABLE_NAME = "email_address_table"
EMAIL_ADDRESS_VIEW = "email_address_view"
EMAIL_ADDRESS_ID_COLLUMN_NAME = "email_address_id"
EMAIL_COLLUMN_NAME = "email"
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
        logger.start(object={"email_address": email_address,
                     "lang_code": lang_code.value, "name": name})
        data = {
            EMAIL_COLLUMN_NAME: f"'{email_address}'",
        }
        email_address_id = None
        result = GenericCRUD.insert(
            schema_name=EMAIL_ADDRESS_SCHEMA_NAME, table_name=EMAIL_ADDRESS_TABLE_NAME, json_data=data)
        email_address_id = result["contacts ids"][0]
        data = {
            "email_id": email_address_id,
            "lang_code": f"'{lang_code.value}'",
            "name": f"'{name}'"
        }
        GenericCRUD.insert(schema_name=EMAIL_ADDRESS_SCHEMA_NAME,
                           table_name=EMAIL_ADRESS_ML_TABLE_NAME, json_data=data)
        logger.end(object={'email_address_id': email_address_id})
        return email_address_id

    @staticmethod
    def update(email_address_id: int, new_email: str) -> None:
        logger.start(
            object={"email_address_id": email_address_id, "new_email": new_email})
        data = {"email": new_email}
        GenericCRUD.update_by_where_condition(schema_name=EMAIL_ADDRESS_SCHEMA_NAME, table_name=EMAIL_ADDRESS_TABLE_NAME,
                                              data_json=data, where_condition=f"{EMAIL_ADDRESS_ID_COLLUMN_NAME}={email_address_id}")
        logger.end(object={})

    @staticmethod
    def delete(email_address_id: int) -> None:
        logger.start(object={"email_id": email_address_id})
        GenericCRUD.delete_by_where_condition(schema_name=EMAIL_ADDRESS_SCHEMA_NAME, table_name=EMAIL_ADDRESS_TABLE_NAME,
                                              where_condition=f"{EMAIL_ADDRESS_ID_COLLUMN_NAME}={email_address_id}")
        logger.end(object={})

    @staticmethod
    def get_email_address_by_email_address_id(email_address_id: int) -> str or None:
        logger.start(object={"email_address_id":  email_address_id})
        email_address = None
        result = GenericCRUD.fetchall_by_id(schema_name=EMAIL_ADDRESS_SCHEMA_NAME, table_name=EMAIL_ADDRESS_VIEW, select_clause=[
                                            EMAIL_COLLUMN_NAME], id_column_name=EMAIL_ADDRESS_ID_COLLUMN_NAME, id_column_value=email_address_id)
        if result:
            email_address = result[0][0]
        logger.end(object={'email_address': email_address})
        return email_address

    @staticmethod
    def get_email_address_id_by_email_address(email: str) -> int or None:
        email_address_id = None
        logger.start(object={"email": email})
        result = GenericCRUD.fetchall_by_where_condition(schema_name=EMAIL_ADDRESS_SCHEMA_NAME, table_name=EMAIL_ADDRESS_VIEW, select_clause=[
                                                         EMAIL_ADDRESS_ID_COLLUMN_NAME], where_condition=f"{EMAIL_COLLUMN_NAME}='{email}'")
        if result:
            email_address_id = result[0][0]
        logger.end(object={'email_address_id': email_address_id})
        return email_address_id
