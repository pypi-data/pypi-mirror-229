"""
Configuration module that implements default configuration for Google Cloud
S3 and a remote SSH server, with the possibility to extend to other providers.
"""
# pylint: disable=missing-class-docstring,too-few-public-methods
from dataclasses import dataclass


@dataclass
class RemoteConfig:
    pass


@dataclass
class GoogleCloud(RemoteConfig):
    project_number: str
    service_account_file: str
    object_acl: str
    bucket_acl: str
    location: str
    storage_class: str
    type: str = "google cloud storage"


class S3(RemoteConfig):
    provider: str
    access_key_id: str
    secret_access_key: str
    region: str
    endpoint: str
    type: str = "s3"
    # get access key and secret key from the enviroment
    # variables. Must set `access_key_id`  and `secret_access_key`
    # to empty.
    env_auth = False
    # used only when creating buckets. Must stay empty
    location_constraint: str = ""
    acl = "private"
    server_side_encryption = ""
    storage_class = ""


class SSH(RemoteConfig):
    ...
