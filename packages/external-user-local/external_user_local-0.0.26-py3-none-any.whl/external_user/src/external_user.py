from logger_local.LoggerComponentEnum import LoggerComponentEnum
import dotenv
import os
import sys
from logger_local.Logger import Logger
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..')))
from db.external_user_db import ExternalUserDb, EXTERNAL_USER_LOCAL_PYTHON_PACKAGE_COMPONENT_ID,EXTERNAL_USER_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME,DEVELOPER_EMAIL
dotenv.load_dotenv()
object_init = {
    'component_id': EXTERNAL_USER_LOCAL_PYTHON_PACKAGE_COMPONENT_ID,
    'component_name': EXTERNAL_USER_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    'developer_email': DEVELOPER_EMAIL,
}
logger = Logger.create_logger(object=object_init)


class ExternalUser:

    @staticmethod
    def insert_or_update_external_user_access_token( username: str, profile_id: int, system_id: int, access_token: str, expiry=None, refresh_token: str = None) -> None:
        object_start = {
            'username': username,
            'profile_id': profile_id,
            'system_id': system_id,
            'access_token': access_token,
            'expiry': expiry,
            'refresh_token': refresh_token
        }
        current_token=ExternalUserDb.get_access_token(username,profile_id,system_id)
        if current_token is not None:
            ExternalUserDb.delete_access_token(username,system_id,profile_id)
        logger.start(object=object_start)
        ExternalUserDb.insert_or_update_external_user_access_token(
            username, profile_id, system_id, access_token, expiry, refresh_token)
        logger.end(object={})

    @staticmethod
    def get_access_token(username: str, profile_id: int, system_id: int) -> str:
        object_start = {
            'username': username,
            'profile_id': profile_id,
            'system_id': system_id
        }
        logger.start(object=object_start)
        access_token = ExternalUserDb.get_access_token(
            username, profile_id, system_id)
        logger.end(object={'access_token': access_token})
        return access_token

    @staticmethod
    def update_external_user_access_token(username: str, system_id: int, profile_id: int, access_token, expiry=None, refresh_token: str = None) -> None:
        object_start = {
            'username': username,
            'system_id': system_id,
            'profile_id': profile_id,
            'access_token': access_token,
            'expiry': expiry,
            'refresh_token': refresh_token
        }
        logger.start(object=object_start)
        ExternalUserDb.update_access_token(
            username, system_id, profile_id, access_token)
        logger.end(object={})

    @staticmethod
    def get_all_tokens_by_system_id(system_id: int):
        # might be helpfull if we want update users accounts from social media
        object_start = {
            'system_id': system_id
        }
        logger.start(object=object_start)
        access_tokens = ExternalUserDb.get_all_tokens_by_system_id(system_id)
        logger.end(object={'access_tokens': access_tokens})
        return access_tokens

    @staticmethod
    def delete_access_token(username: str, system_id: int, profile_id: int):
        object_start = {
            'username': username,
            'system_id': system_id,
            'profile_id': profile_id,
        }
        logger.start(object=object_start)
        ExternalUserDb.delete_access_token(username, system_id, profile_id)
        logger.end(object={})

    @staticmethod
    def get_access_token_by_system_id_and_profile_id( system_id: int, profile_id: int) -> None:
        object_start = {
            'system_id': system_id,
            'profile_id': profile_id,
        }
        logger.start(object=object_start)
        auth_details = ExternalUserDb.get_auth_details_by_system_id_and_profile_id(
            system_id, profile_id)
        logger.end(object={"auth_details": str(auth_details)})
        return auth_details
