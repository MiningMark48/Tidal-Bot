# import discord
# from discord.ext import commands

import json
import os.path as osp

usrcfg_path = "user_configs.json"

def_config = {
    "users": {}
}

def check_and_gen():
    if not osp.isfile(usrcfg_path):
        with open(usrcfg_path, 'w') as file:
            print("User configs file not found, creating...")
            json.dump(def_config, file, indent=4, sort_keys=True)
            print("User configs file created.")

def update_users(data):
    def_config["users"] = data

def get_data():
    global def_config
    if not def_config["users"]:
        check_and_gen()
        with open(usrcfg_path, 'r') as file:
            def_config = json.load(file)
    return def_config["users"]

def save_data():
    with open(usrcfg_path, 'w') as file:
        json.dump(def_config, file, indent=4, sort_keys=True)

def remove_server_data(user_id: str):
    usrcfg = get_data()
    if user_id in usrcfg:
        del usrcfg[user_id]
    update_users(usrcfg)
    save_data()

def toggle_string_array(user_id: str, emt_name: str, array_name: str):
    usrcfg = get_data()
    result_rem = False

    if user_id not in usrcfg:
        usrcfg[user_id] = {array_name: [emt_name]}
        update_users(usrcfg)
        save_data()
        return

    if array_name not in usrcfg[user_id]:
        usrcfg[user_id][array_name] = []
    
    array_list = usrcfg[user_id][array_name]
    if emt_name in array_list:
        array_list.remove(emt_name)
        result_rem = True
    else:
        array_list.append(emt_name)

    usrcfg[user_id][array_name] = array_list

    update_users(usrcfg)
    save_data()
    return result_rem

def array_contains(user_id: str, emt_name: str, array_name: str):
    usrcfg = get_data()
    try:
        return emt_name in usrcfg[user_id][array_name]
    except:
        return False

def set_kv(user_id: str, key_name: str, value):
    usrcfg = get_data()

    if user_id not in usrcfg:
        usrcfg[user_id] = {key_name: value}
        update_users(usrcfg)
        save_data()
        return

    usrcfg[user_id][key_name] = value

    update_users(usrcfg)
    save_data()

def get_v(user_id: str, key_name: str):
    usrcfg = get_data()

    try:
        return usrcfg[user_id][key_name]
    except: 
        return None

def del_v(user_id: str, key_name: str):
    usrcfg = get_data()
    if user_id in usrcfg and key_name in usrcfg[user_id]:
        del usrcfg[user_id][key_name]
    update_users(usrcfg)
    save_data()

def get_all_if_equals(key_name: str, value):
    usrcfg = get_data()
    users = []
    for user in usrcfg:        
        if usrcfg[user][key_name] == value:
            users.append(user)
    return users
