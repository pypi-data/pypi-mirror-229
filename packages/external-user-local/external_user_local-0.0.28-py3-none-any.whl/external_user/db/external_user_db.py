from datetime import datetime
from logger_local.Logger import Logger
from logger_local.LoggerComponentEnum import LoggerComponentEnum
from dotenv import load_dotenv
from circles_local_database_python.connector import Connector
import sys
import os
script_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_directory, '..', 'db'))

load_dotenv()
EXTERNAL_USER_LOCAL_PYTHON_PACKAGE_COMPONENT_ID = 115
EXTERNAL_USER_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME = 'external_user_local_python'
DEVELOPER_EMAIL = "idan.a@circ.zone"
object_init = {
    'component_id': EXTERNAL_USER_LOCAL_PYTHON_PACKAGE_COMPONENT_ID,
    'component_name': EXTERNAL_USER_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    'developer_email': DEVELOPER_EMAIL,
}
logger = Logger.create_logger(object=object_init)


class ExternalUserDb:

    # TODO: Where do we do "USE external_user"? Shall we add it to __init__
    def __init__(self):
        pass

    @staticmethod
    def insert_or_update_external_user_access_token(username: str, profile_id: int, system_id: int, access_token: str, expiry=None, refresh_token: str = None) -> None:
        try:
            object_start = {
                'username': username,
                'profile_id': profile_id,
                'system_id': system_id,
                'access_token': access_token,
                'expiry': expiry,
                'refresh_token': refresh_token
            }
            logger.start(object=object_start)
            connection = Connector.connect('external_user')
            if (expiry is None):
                expiry = ""
            if (refresh_token is None):
                refresh_token = ""
            query_insert_external = "INSERT INTO external_user_table (system_id,username,access_token,expiry,refresh_token) VALUES (%s,%s,%s,%s,%s)"
            values = (system_id, username, access_token, expiry, refresh_token)
            cursor = connection.cursor()
            cursor.execute(query_insert_external, values)
            id_new = cursor.lastrowid()
            values = (id_new, profile_id)
            connection.commit()
            connection_profile = Connector.connect('external_user_profile')
            query_insert_external_user_profile = "INSERT INTO external_user_profile_table (external_user_id,profile_id) VALUES (%s,%s)"
            cursor = connection_profile.cursor()
            cursor.execute(query_insert_external_user_profile, values)
            connection_profile.commit()
            object_info = {
                'username': username,
                'system_id': system_id,
                'profile_id': profile_id,
                'access_token': access_token,
            }
            logger.info("external user inserted", object=object_info)
        except Exception as error:
            logger.exception(object=error)
            raise
        logger.end(object={})

    @staticmethod
    def get_access_token(username: str, profile_id: int, system_id: int) -> str:
        access_token = None
        try:
            object_start = {
                'username': username,
                'profile_id': profile_id,
                'system_id': system_id
            }
            logger.start(object=object_start)
            connection = Connector.connect('external_user')
            query_get = "SELECT access_token FROM external_user.external_user_view as eu join external_user_profile.external_user_profile_table as eup on eu.external_user_id=eup.external_user_id WHERE eu.username=%s AND eu.system_id=%s And eup.profile_id=%s"
            cursor = connection.cursor()
            cursor.execute(query_get, (username, system_id, profile_id))
            access_token = cursor.fetchone()
        except Exception as error:
            logger.exception(object=error)
            raise
        logger.end(object={'access_token': access_token})
        return access_token

    @staticmethod
    def get_all_tokens_by_system_id(system_id: int) -> any:
        # good for update users details by system
        access_tokens = None
        try:
            object_start = {
                'system_id': system_id
            }
            logger.start(object=object_start)
            connection = Connector.connect('external_user')
            query_get_all = "SELECT access_token FROM external_user.external_user_view WHERE system_id=%s"
            cursor = connection.cursor()
            cursor.execute(query_get_all, (system_id))
            access_tokens = cursor.fetchall()
        except Exception as error:
            logger.exception(object=error)
            raise
        logger.end(object={'access_tokens': access_tokens})
        return access_tokens

    @staticmethod
    def update_access_token(username: str, system_id: int, profile_id: int, access_token: str) -> None:
        try:
            object_start = {
                'username': username,
                'system_id': system_id,
                'profile_id': profile_id,
                'access_token': access_token,
            }
            logger.start(object=object_start)
            connection = Connector.connect('external_user')
            update_query = "UPDATE external_user.external_user_table AS eu JOIN external_user_profile.external_user_profile_table AS eup ON eu.external_user_id = eup.external_user_id SET eu.access_token = %s WHERE eu.username = %s AND eu.system_id = %s AND eup.profile_id = %s;"
            values = (access_token, username, system_id, profile_id)
            cursor = connection.cursor()
            cursor.execute(update_query, values)
            connection.commit()
            object_info = {
                'username': username,
                'system_id': system_id,
                'profile_id': profile_id,
                'access_token': access_token,
            }
            logger.info("external user updated", object=object_info)
        except Exception as error:
            logger.exception(object=error)
            raise
        logger.end(object={})

    @staticmethod
    def delete_access_token(username: str, system_id: int, profile_id: int) -> None:
        try:
            object_start = {
                'username': username,
                'system_id': system_id,
                'profile_id': profile_id,
            }
            logger.start(object=object_start)
            connection = Connector.connect('external_user')
            cursor = connection.cursor()
            update_query = "UPDATE external_user.external_user_table AS eu JOIN external_user_profile.external_user_profile_table AS eup ON eu.external_user_id = eup.external_user_id SET eu.end_timestamp = %s WHERE eu.username = %s AND eu.system_id = %s AND eup.profile_id = %s;"
            current_datetime = datetime.now()
            current_date = current_datetime.date()
            values = (current_date, username, system_id, profile_id)
            cursor.execute(update_query, values)
            connection.commit()
            object_info = {
                'username': username,
                'system_id': system_id,
                'profile_id': profile_id,
            }
            logger.info("external user updated", object=object_info)
        except Exception as error:
            logger.exception(object=error)
            raise
        logger.end(object={})

    @staticmethod
    def get_auth_details_by_system_id_and_profile_id(system_id: int, profile_id: int) -> any:
        auth_details = None
        try:
            object_start = {
                'system_id': system_id,
                "profile_id": profile_id
            }
            logger.start(object=object_start)
            connection = Connector.connect('external_user')
            query_get_all = "SELECT access_token,refresh_token,expiry FROM external_user.external_user_view as eu join external_user_profile.external_user_profile_table as eup on eu.external_user_id=eup.external_user_id WHERE eu.system_id=%s And eup.profile_id=%s order by eu.start_timestamp desc limit 1"
            cursor = connection.cursor()
            cursor.execute(query_get_all, (system_id, profile_id))
            auth_details = cursor.fetchall()[0]
        except Exception as error:
            logger.exception(object=error)
            raise
        logger.end(object={'auth_details': auth_details})
        return auth_details

    @staticmethod
    def get_auth_details(username: str, system_id: int, profile_id: int) -> any:
        auth_details = None
        try:
            object_start = {
                "username": username,
                'system_id': system_id,
                "profile_id": profile_id,
            }
            logger.start(object=object_start)
            connection = Connector.connect('external_user')
            query_get_all = "SELECT access_token,refresh_token,expiry FROM external_user.external_user_view as eu join external_user_profile.external_user_profile_table as eup on eu.external_user_id=eup.external_user_id WHERE eu.username=%s AND eu.system_id=%s And eup.profile_id=%s order by eu.start_timestamp desc limit 1"
            cursor = connection.cursor()
            cursor.execute(query_get_all, (username, system_id, profile_id))
            auth_details = cursor.fetchall()[0]
        except Exception as error:
            logger.exception(object=error)
            raise
        logger.end(object={'auth_details': auth_details})
        return auth_details
