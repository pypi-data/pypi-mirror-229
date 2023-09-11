from circles_local_database_python.connector import Connector
from circles_local_database_python.generic_crud import GenericCRUD
from logger_local.LoggerComponentEnum import LoggerComponentEnum
from logger_local.Logger import Logger

PHONE_LOCAL_PYTHON_COMPONENT_ID = 200
PHONE_LOCAL_PYTHON_COMPONENT_NAME = "phone_local_python_package/src/phoneslocal.py"
DEVELOPER_EMAIL = 'jenya.b@circ.zone'

object_init = {
    'component_id': PHONE_LOCAL_PYTHON_COMPONENT_ID,
    'component_name': PHONE_LOCAL_PYTHON_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    "developer_email": DEVELOPER_EMAIL
}
logger = Logger.create_logger(object=object_init)


class PhonesLocal(GenericCRUD):
    def __init__(self) -> None:
        pass

    def get_phone_number_normalized_by_phone_id( phone_id: int) -> int:
        logger.start("Return Phone Number by phone id",
                     object={"phone_id": phone_id})
        try:
            #TODO: change to fetch_one_by_column()
            #data = GenericCRUD.fetchall_by_where_condition(schema_name="phone",table_name="phone_view",
            #                                               select_clause="number_normalized",where_condition=f'phone_id={phone_id}')
            data = GenericCRUD(schema_name="phone").select(table_name="phone_view",select_clause_value="number_normalized",
                                                          id_column_name="phone_id",id_column_value=phone_id)
            phone_number = int(data[0][0])
            logger.end("Return Phone Number of a specific phone id", object={
                       'phone_id': phone_id, 'phone_number': phone_number})
            return phone_number
        except Exception as e:
            logger.exception(
                f"Couldn't get phone number for phone_id={phone_id}", object=e)
            logger.end()
            raise Exception
