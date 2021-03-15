from typing import List, Optional, Union
from pydantic import BaseSettings, Field
import os

from pydantic.class_validators import validator
from pydantic.networks import AnyHttpUrl

class Settings(BaseSettings):
    # Fill in your Plaid API keys - https://dashboard.plaid.com/account/keys
    PLAID_CLIENT_ID: str
    PLAID_SECRET: str
    # Use 'sandbox' to test with Plaid's Sandbox environment (username: user_good,
    # password: pass_good)
    # Use `development` to test with live users and credentials and `production`
    # to go live
    PLAID_ENV: str
    # PLAID_PRODUCTS is a comma-separated list of products to use when initializing
    # Link. Note that this list must contain 'assets' in order for the app to be
    # able to create and retrieve asset reports.
    PLAID_PRODUCTS: Union[str, List[str]] = ["transaction"]

    @validator("PLAID_PRODUCTS", pre=True)
    def assemble_products(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # PLAID_COUNTRY_CODES is a comma-separated list of countries for which users
    # will be able to select institutions from.
    PLAID_COUNTRY_CODES: Union[str, List[str]] = ["US"]

    @validator("PLAID_COUNTRY_CODES", pre=True)
    def assemble_country_codes(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PLAID_REDIRECT_URI: Union[AnyHttpUrl, str, None] = None

    @validator("PLAID_REDIRECT_URI", pre=True)
    def parse_redirect(cls, v: Optional[AnyHttpUrl]):
        if v:
            return v
        else:
            return None 
    
settings = Settings()

