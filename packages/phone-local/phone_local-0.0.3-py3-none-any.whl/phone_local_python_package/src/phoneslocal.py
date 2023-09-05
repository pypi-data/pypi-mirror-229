from circles_local_database_python.connector import Connector
from circles_local_database_python.generic_crud.src.generic_crud import GenericCRUD
from logger_local.LoggerComponentEnum import LoggerComponentEnum
from logger_local.Logger import Logger


PHONE_LOCAL_PYTHON_COMPONENT_ID = 200
PHONE_LOCAL_PYTHON_COMPONENT_NAME = 'phone-local'

object_init = {
    'component_id': PHONE_LOCAL_PYTHON_COMPONENT_ID,
    'component_name': PHONE_LOCAL_PYTHON_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    "developer_email": "jenya.b@circ.zone"
}
logger = Logger.create_logger(object=object_init)


class PhonesLocal(GenericCRUD):
    def __init__(self) -> None:
        pass

    def get_phone_number_by_profile_id(profile_id: int) -> list:
        logger.start("Return Phone Number by profile id",
                     object={"profile_id": profile_id})
        phone_id = profile_id
        try:
            data = GenericCRUD.get_records_by_id(
                "phone", "phone_view", "phone_id", phone_id)
            phone_number = data[0][3]

            logger.end("Return Phone Numbers of a specific id", object={
                       'phone_id': phone_id, 'phone_number': phone_number})
            return phone_number
        except Exception as e:
            logger.exception(
                "Couldn't get phone number for phone_id=" + phone_id, object=e)
            logger.end()
            raise Exception
