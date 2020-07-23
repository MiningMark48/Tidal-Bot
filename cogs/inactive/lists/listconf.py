# # import discord
# # from discord.ext import commands
#
# import json
# import os.path as osp
#
# from util.backups import backup_file
#
# usercfg_path = "lists.json"
#
# def_config = {
#     "users": {}
# }
#
#
# def check_and_gen():
#     if not osp.isfile(usercfg_path):
#         with open(usercfg_path, 'w') as file:
#             print("Lists file not found, creating...")
#             json.dump(def_config, file, indent=4, sort_keys=True)
#             print("Lists file created.")
#
#
# def update_users(data):
#     def_config["users"] = data
#
#
# def get_data():
#     global def_config
#     if not def_config["users"]:
#         check_and_gen()
#         with open(usercfg_path, 'r') as file:
#             def_config = json.load(file)
#     return def_config["users"]
#
#
# def save_data():
#     with open(usercfg_path, 'w') as file:
#         json.dump(def_config, file, indent=4, sort_keys=True)
#
#
# def remove_user_data(user_id: str):
#     usercfg = get_data()
#     if user_id in usercfg:
#         del usercfg[user_id]
#     update_users(usercfg)
#     save_data()
#
#
# def set_kv(user_id: str, key_name: str, value):
#     usercfg = get_data()
#
#     if user_id not in usercfg:
#         usercfg[user_id] = {key_name: value}
#         update_users(usercfg)
#         save_data()
#         return
#
#     usercfg[user_id][key_name] = value
#
#     update_users(usercfg)
#     save_data()
#
#
# def get_v(user_id: str, key_name: str):
#     usercfg = get_data()
#
#     try:
#         return usercfg[user_id][key_name]
#     except:
#         return None
#
#
# def del_v(user_id: str, key_name: str):
#     usercfg = get_data()
#     if user_id in usercfg and key_name in usercfg[user_id]:
#         del usercfg[user_id][key_name]
#     update_users(usercfg)
#     save_data()
#
#
# def backup_data():
#     backup_file(usercfg_path)
