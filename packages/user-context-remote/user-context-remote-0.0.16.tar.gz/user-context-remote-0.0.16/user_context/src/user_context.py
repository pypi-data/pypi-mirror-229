import os
from our_url.src.index import UrlCirclez
import json
from typing import Any
import jwt
from our_url.src.action_name_enum import ActionName
from our_url.src.entity_name_enum import EntityName
from our_url.src.component_name_enum import ComponentName
from language_local_python_package.src.language_enum_class import LanguageCode
from dotenv import load_dotenv
import requests
from httpstatus import HTTPStatus
load_dotenv()
BRAND_NAME = os.getenv('BRAND_NAME')
ENVIORNMENT_NAME = os.getenv('ENVIRONMENT_NAME')
AUTHENTICATION_API_VERSION = 1


class UserContext:
    _instance = None

    def __new__(cls, email: str = None, password: str = None):
        if cls._instance is None:
            cls._instance = super(UserContext, cls).__new__(cls)
            cls._instance._initialize(email, password)
        return cls._instance

    def _initialize(self, email: str, password: str):
        self.user_id = None
        self.profile_id = None
        self.language = None
        self.first_name = None
        self.last_name = None
        self.name=None
        self._authenticate(email, password)

    @staticmethod
    def login(email: str = None, password: str = None):
        #logger.start(object={"email": email, "passowrd": password})
        if UserContext._instance is None:
            if email is None:
                email=os.getenv("PRODUCT_USERNAME")
            if password is None:
                password=os.getenv("PRODUCT_PASSWORD")
            if email is None or password is None or email == "" or password == "":
                raise Exception(
                    "please insert in your .env PRODUCT_USERNAME and PRODUCT_PASSWORD")
            UserContext._instance = UserContext(email=email, password=password)
        user=UserContext._instance
        #logger.end(object={"user": str(user)})
        return user

    def _set_real_user_id(self, user_id: int) -> None:
        #logger.start(object={"user_id": user_id})
        self.user_id = user_id
        #logger.end()

    def _set_real_profile_id(self, profile_id: int) -> None:
        #logger.start(object={"profile_id": profile_id})
        self.profile_id = profile_id
        #logger.end()

    def get_real_user_id(self) -> int:
        #logger.start()
        #logger.end(object={"user_id": self.user_id})
        return self.user_id

    def get_real_profile_id(self) -> int:
        #logger.start()
        #logger.end(object={"user_id": self.profile_id})
        return self.profile_id

    def get_curent_lang_code(self) -> str:
        #logger.start()
        #logger.end(object={"language": self.language})
        return self.language

    def _set_current_lang_code(self, language: LanguageCode) -> None:
        #logger.start(object={"language": language.value})
        self.language = language.value
        #logger.end()

    def _set_real_first_name(self, first_name: str) -> None:
        #logger.start(object={"first_name": first_name})
        self.first_name = first_name
        #logger.end()

    def _set_real_last_name(self, last_name: str) -> None:
        #logger.start(object={"first_name": last_name})
        self.last_name = last_name
        #logger.end()

    def get_real_first_name(self) -> str:
        #logger.start()
        #logger.end(object={"first_name": self.first_name})
        return self.first_name

    def get_real_last_name(self) -> str:
        #logger.start()
        #logger.end(object={"last_name": self.last_name})
        return self.last_name
    def _set_real_name(self, name: str) -> None:
        #logger.start(object={"first_name": last_name})
        self.name = name
        #logger.end()

    def get_real_name(self) -> str:
        #logger.start()
        #logger.end(object={"first_name": self.first_name})
        return self.name

    # def get_user_json_by_user_jwt_token(self, jwt_token: str) -> None:
    #     if jwt_token is None or jwt_token == "":
    #         raise Exception(
    #             "Your .env PRODUCT_NAME or PRODUCT_PASSWORD is wrong")
    #     #logger.start(object={"jwt_token": jwt_token})
    #     try:
    #         secret_key = os.getenv("JWT_SECRET_KEY")
    #         if secret_key is not None:
    #             decoded_payload = jwt.decode(jwt_token, secret_key, algorithms=[
    #                                          "HS256"], options={"verify_signature": False})
    #             self.profile_id = int(decoded_payload.get('profileId'))
    #             self.user_id = int(decoded_payload.get('userId'))
    #             self.language = decoded_payload.get('language')
    #             #logger.end()
    #     except jwt.ExpiredSignatureError as e:
    #         # Handle token expiration
    #         #logger.exception(object=e)
    #         print("Error:JWT token has expired.", sys.stderr)
    #         #logger.end()
    #         raise
    #     except jwt.InvalidTokenError as e:
    #         # Handle invalid token
    #         #logger.exception(object=e)
    #         print("Error:Invalid JWT token.", sys.stderr)
    #         #logger.end()
    #         raise

    def _authenticate(self, email: str, password: str) -> None:
        #logger.start(object={"email": email, "password": password})
        try:
            url_circlez = UrlCirclez()
            url_jwt = url_circlez.endpoint_url(
                brand_name=BRAND_NAME,
                environment_name=ENVIORNMENT_NAME,
                component=ComponentName.AUTHENTICATION.value,
                entity=EntityName.AUTH_LOGIN.value,
                version=AUTHENTICATION_API_VERSION,
                action=ActionName.LOGIN.value
            )
            data = {"email": email, "password": password}
            headers = {"Content-Type": "application/json"}
            output = requests.post(
                url=url_jwt, data=json.dumps(data, separators=(",", ":")), headers=headers
            )
            if output.status_code !=HTTPStatus.OK :
                raise Exception(output.text)
            user_jwt_token = output.json()["data"]["token"]
            if "userDetails" in output.json()["data"]:
                if "profileId" in output.json()["data"]["userDetails"]:
                    profile_id = output.json(
                    )["data"]["userDetails"]["profileId"]
                    self._set_real_profile_id(int(profile_id))
                if "userId" in output.json()["data"]["userDetails"]:
                    user_id = output.json()["data"]["userDetails"]["userId"]
                    self._set_real_user_id(int(user_id))
                if "lang_code" in output.json()["data"]["userDetails"]:
                    lang_code = output.json(
                    )["data"]["userDetails"]["lang_code"]
                    self._set_current_lang_code(lang_code)
                if "firstName" in output.json()["data"]["userDetails"]:
                    first_name = output.json(
                    )["data"]["userDetails"]["firstName"]
                    self._set_real_first_name(first_name)
                if "lastName" in output.json()["data"]["userDetails"]:
                    last_name = output.json(
                    )["data"]["userDetails"]["lastName"]
                    self._set_real_last_name(last_name)
                if self.first_name is not None and self.last_name is not None:
                    name=first_name+" "+last_name
                    self._set_real_name(name)
            #logger.end(object={"user_jwt_token": user_jwt_token })
            return user_jwt_token 
        except Exception as e:
            print(e)
            #logger.exception(object=e)
            #logger.end()
            raise

# from #logger_local.#loggerComponentEnum import #loggerComponentEnum
# from #logger_local.#logger import #logger

# USER_CONTEXT_LOCAL_PYTHON_COMPONENT_ID = 197
# USER_CONTEXT_LOCAL_PYTHON_COMPONENT_NAME = "User Context python package"
# DEVELOPER_EMAIL = "idan.a@circ.zone"
# obj = {
#     'component_id': USER_CONTEXT_LOCAL_PYTHON_COMPONENT_ID,
#     'component_name': USER_CONTEXT_LOCAL_PYTHON_COMPONENT_NAME,
#     'component_category': #loggerComponentEnum.ComponentCategory.Code.value,
#     'developer_email': DEVELOPER_EMAIL
# }
# #logger = #logger.create_#logger(object=obj)
