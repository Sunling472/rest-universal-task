from dataclasses import dataclass


@dataclass
class ErrorTexts:
    not_allowed_error: str = 'Method is not allowed'
    not_found_error: str = '{name} <{id}> is not found'
    not_found_username_error: str = 'User <{username}> is not found'
    bad_request_invalid_password: str = 'Password is invalid'
    forbidden_token_expired_error: str = 'Token is expired'
    model_not_exist_error: str = '{model_name} with id {item_id} does not exist'
    database_error: str = 'DataBase Error: {details}'
    database_not_params_error: str = 'Not params'

