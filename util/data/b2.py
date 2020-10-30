import os.path as osp
import toml
from b2sdk.v1 import *

from util.logger import Logger

config_path = "b2.toml"


def get_data():
    if osp.isfile(config_path):
        with open(config_path, 'r') as file:
            data = toml.load(file)
            Logger.info("Loaded B2 config.")
            return data
    return None


# noinspection PyBroadException
def b2_backup(file_loc, file_name, folder_name):
    data = get_data()

    if not data:
        Logger.warn("Not backing up to B2, config not found.")
        return

    Logger.info("Connecting to B2...")

    try:
        info = InMemoryAccountInfo()
        b2_api = B2Api(info)
        application_key_id = data["AppKey"]["id"]
        application_key = data["AppKey"]["key"]
        b2_api.authorize_account("production", application_key_id, application_key)
        bucket_name = data["bucket"]["name"]
        bucket = b2_api.get_bucket_by_name(bucket_name)
    except Exception as e:
        Logger.fatal(f"Connection to B2 failed : \n\t{e}")
    else:
        Logger.info("Connected to B2")

        Logger.info("Starting backup upload to B2...")
        bucket.upload_local_file(
            local_file=file_loc,
            file_name=f"{data['bucket']['backup_folder_name']}/{folder_name}/{file_name}",
            file_infos={'how': 'automated'},
        )
        Logger.info("Upload to B2 complete.")
