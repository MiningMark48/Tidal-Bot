# import discord
# from discord.ext import commands

import json
import os.path as osp

servcfg_path = "server_configs.json"

def_config = {
    "servers": {}
}


def check_and_gen():
    if not osp.isfile(servcfg_path):
        with open(servcfg_path, 'w') as file:
            print("Server configs file not found, creating...")
            json.dump(def_config, file, indent=4, sort_keys=True)
            print("Server configs file created.")


def update_servers(data):
    def_config["servers"] = data


def get_data():
    global def_config
    if not def_config["servers"]:
        check_and_gen()
        with open(servcfg_path, 'r') as file:
            def_config = json.load(file)
    return def_config["servers"]


def save_data():
    with open(servcfg_path, 'w') as file:
        json.dump(def_config, file, indent=4, sort_keys=True)


def remove_server_data(guild_id: str):
    servcfg = get_data()
    if guild_id in servcfg:
        del servcfg[guild_id]
    update_servers(servcfg)
    save_data()


def toggle_string_array(guild_id: str, emt_name: str, array_name: str):
    servcfg = get_data()
    result_rem = False

    if guild_id not in servcfg:
        servcfg[guild_id] = {array_name: [emt_name]}
        update_servers(servcfg)
        save_data()
        return

    if array_name not in servcfg[guild_id]:
        servcfg[guild_id][array_name] = []

    array_list = servcfg[guild_id][array_name]
    if emt_name in array_list:
        array_list.remove(emt_name)
        result_rem = True
    else:
        array_list.append(emt_name)

    servcfg[guild_id][array_name] = array_list

    update_servers(servcfg)
    save_data()
    return result_rem


def array_contains(guild_id: str, emt_name: str, array_name: str):
    servcfg = get_data()
    try:
        return emt_name in servcfg[guild_id][array_name]
    except:
        return False


def set_kv(guild_id: str, key_name: str, value):
    servcfg = get_data()

    if guild_id not in servcfg:
        servcfg[guild_id] = {key_name: value}
        update_servers(servcfg)
        save_data()
        return

    servcfg[guild_id][key_name] = value

    update_servers(servcfg)
    save_data()


def get_v(guild_id: str, key_name: str):
    servcfg = get_data()

    try:
        return servcfg[guild_id][key_name]
    except:
        return None


def del_v(guild_id: str, key_name: str):
    servcfg = get_data()
    if guild_id in servcfg and key_name in servcfg[guild_id]:
        del servcfg[guild_id][key_name]
    update_servers(servcfg)
    save_data()
