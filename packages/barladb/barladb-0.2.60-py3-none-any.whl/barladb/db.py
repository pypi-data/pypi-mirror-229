from barladb.classes import Json
from barladb.log_functions import Log
from barladb import config
from typing import Union, Any
from os import system
from datetime import datetime
import os
import json

RED = "\033[31m"
ORANGE = "\033[33m"
GREEN = "\033[32m"
RESET = "\033[0m"

class BarlaDB:
    def __init__(self):
        self.data = {}

    def get(self, filepath: str) -> dict:
        try:
            data = Json.get(filepath)
            if config.debug:
                print("BarlaDB: " + GREEN + "The data was successfully received! (get)" + RESET)
            if config.log:
                Log.enter_log(f"The data of {filepath}.json successfully received (get)")
            if data == self.data:
                print("BarlaDB: " + ORANGE + "Database is empty. (get)" + RESET)
                if config.log:
                    Log.enter_log(f"Database {filepath}.json is empty! (get)")
                return
            else:
                return data
        except Exception as e:
            #print(e)
            raise FileNotFoundError(f"Database {filepath}.json isn't exists! (get)")
            if config.log:
                Log.enter_log(f"Database {filepath}.json isn't exists! (get)")
            return
    
    def save(self, filepath: str, data: str, CreateBackup=(False, False)) -> str:
        try:
            create, return_name = CreateBackup
            backup_name = None
            if create:
                backupData = Json.get(filepath)
                if not os.path.exists("barladb_backups"):
                    os.makedirs("barladb_backups")
                    current_time = datetime.now()
                    backup_time = current_time.strftime("%d.%m.%y")
                    if not os.path.exists(f"barladb_backups/{backup_time}"):
                        os.makedirs(f"barladb_backups/{backup_time}")
                        current_time = datetime.now()
                        backup_time1 = current_time.strftime("%H-%M.%S, %d.%m.%y")
                        backup_name = f"barladb_backups/{backup_time}/{filepath}_backup_{backup_time1}.json"
                        with open(backup_name, "w") as backup:
                            json.dump(data, backup, ensure_ascii=True, indent=2)
                    else:
                        current_time = datetime.now()
                        backup_time1 = current_time.strftime("%H-%M.%S, %d.%m.%y")
                        backup_name = f"barladb_backups/{backup_time}/{filepath}_backup_{backup_time1}.json"
                        with open(backup_name, "w") as backup:
                            json.dump(data, backup, ensure_ascii=True, indent=2)
                else:
                    current_time = datetime.now()
                    backup_time = current_time.strftime("%d.%m.%y")
                    if not os.path.exists(f"barladb_backups/{backup_time}"):
                        os.makedirs(f"barladb_backups/{backup_time}")
                        current_time = datetime.now()
                        backup_time1 = current_time.strftime("%H-%M.%S, %d.%m.%y")
                        backup_name = f"barladb_backups/{backup_time}/{filepath}_backup_{backup_time1}.json"
                        with open(backup_name, "w") as backup:
                            json.dump(data, backup, ensure_ascii=True, indent=2)
                    else:
                        current_time = datetime.now()
                        backup_time1 = current_time.strftime("%H-%M.%S, %d.%m.%y")
                        backup_name = f"barladb_backups/{backup_time}/{filepath}_backup_{backup_time1}.json"
                        with open(backup_name, "w") as backup:
                            json.dump(data, backup, ensure_ascii=True, indent=2)
                if config.debug:
                    print("BarlaDB: " + GREEN + "Backup successfully created! (save)" + RESET)
                if config.log:
                    Log.enter_log("Backup successfully created. (save)")
                    

            Json.save(filepath, data)
            if data is None:
                if config.debug:
                    print("BarlaDB: " + ORANGE + "Variable with data is empty. (save)" + RESET)
                if config.log:
                    Log.enter_log("Variable with data is empty. (save)")
            else:
                if config.debug:
                    print("BarlaDB: " + GREEN + "The data was successfully received! (save)" + RESET)
                if config.log:
                    Log.enter_log(f"The data of {filepath}.json successfully received! (save)")
            if return_name and create:
                return backup_name
        except:
            raise FileNotFoundError(f"Database {filepath}.json isn't exists! (save)")
            if config.log:
                Log.enter_log(f"Database {filepath}.json isn't exists. (save)")
    
    def create(self, filename: str) -> bool:
        Json.save(filename, self.data)
        if config.debug:
            print("BarlaDB: " + GREEN + f"Database {filename}.json was successfully created! (create)" + RESET)
        if config.log:
            Log.enter_log(f"Database {filename}.json was successfully created. (create)")
        return True
    
    def delete(self, filename: str) -> bool:
        try:
            os.remove(f"{filename}")
            print("BarlaDB: " + GREEN + f"Database {filename}.json was successfully deleted! (delete)" + RESET)
            if config.log:
                Log.enter_log(f"Database {filename}.json was successfully deleted. (delete)")
            return True
        except:
            raise FileExistsError(f"Database {filepath}.json isn't exists! (delete)")
            if config.log:
                Log.enter_log(f"Базы данных {filepath}.json не существует! (delete)")
            return False
    
    def search(self, filepath: str, key: str) -> str:
        try:
            data = Json.get(filepath)
            if data == self.data:
                print("BarlaDB: " + ORANGE + f"Database {filepath}.json is empty. (search)" + RESET)
                if config.log:
                    Log.enter_log(f"Database {filepath}.json is empty. (search)")
                return None
            if key in data:
                print("BarlaDB: " + GREEN + "One match found.\n" + RESET + f'"{key}": {data[key]} (search)')
                if config.log:
                    Log.enter_log(f"One match found. '{key}': {data[key]} (search)")
                return data[key]
            else:
                print("BarlaDB: " + ORANGE + "No matches found. (search)" + RESET)
                if config.log:
                    Log.enter_log("No matches found. (search)")
                return None
        except:
            print("BarlaDB: " + RED + f"Database {filepath}.json isn't exists! (search)" + RESET)
            if config.log:
                Log.enter_log(f"Database {filepath}.json isn't exists. (search)")
            return
    
    def remove_column(self, filepath: str, key: str) -> bool:
        try:
            answer = Json.remove_column(filepath, key)
            if answer:
                print("BarlaDB: " + GREEN + f"The column was successfully deleted: {key}. (remove_column)" + RESET)
                if config.log:
                    Log.enter_log(f"The column was successfully deleted: {key}. (remove_column)")
                return True
            else:
                print("BarlaDB: " + ORANGE + f"No matches found: {key}. (remove_column)" + RESET)
                if config.log:
                    Log.enter_log(f"No matches found: {key}. (remove_column)")
                return False
        except:
            raise FileNotFoundError(f"Database {filepath}.json isn't exists! (remove_column)")
            if config.log:
                Log.enter_log(f"Database {filepath}.json isn't exists. (remove_column)")
            return False
    
    def columns(self, filepath: str) -> int:
        try:
            with open(filepath, "r") as file:
                data = json.load(file)
            int_count = 0
            str_count = 0
            for column in data.values():
                if isinstance(column, (list, tuple, set)):
                    for value in column:
                        if isinstance(value, int):
                            int_count += 1
                        elif isinstance(value, str):
                            str_count += 1
                elif isinstance(column, int):
                    int_count += 1
                elif isinstance(column, str):
                    str_count += 1
            print("BarlaDB: " + GREEN + f"Database {filepath}.json has: {int_count} ints, {str_count} strs. (columns)" + RESET)
            if config.log:
                Log.enter_log(f"Database {filepath}.json has: {int_count} ints, {str_count} strs. (columns)")
            return int_count, str_count
        except:
            raise FileNotFoundError(f"Database {filepath}.json isn't exists! (columns)")
            if config.log:
                Log.enter_log(f"Database {filepath}.json isn't exists. (columns)")
            return None
    
    def restore_backup(self, BackupFilepath: str, DatabaseFilepath: str, RemoveBackupFile=True) -> bool:
            if os.path.exists(BackupFilepath):
                pass
            else:
                raise FileExistsError(f"Backup file doesn't exist. ({BackupFilepath}), (restore_backup)")
                if config.log:
                    Log.enter_log(f"Backup file doesn't exist. ({BackupFilepath}), (restore_backup)")
                return False
            if os.path.exists(DatabaseFilepath):
                pass
            else:
                raise FileExistsError(f"Database file doesn't exist. ({DatabaseFilepath}), (restore_backup)")
                if config.log:
                    Log.enter_log(f"Database file doesn't exist. ({DatabaseFilepath}), (restore_backup)")
                return False
            with open(BackupFilepath, "r") as file:
                BackupData = json.load(file)
            with open(DatabaseFilepath, "w") as file:
                json.dump(BackupData, file, ensure_ascii=True, indent=2)
            print("BarlaDB: " + GREEN + "Successfull return to backup! (restore_backup)" + RESET)
            if config.log:
                Log.enter_log("Successfull return to backup. (restore_backup)")
            if RemoveBackupFile:
                os.remove(BackupFilepath)
                if config.debug:
                    print("BarlaDB: " + GREEN + "Backup file successfully deleted! (restore_backup)" + RESET)
                if config.log:
                    Log.enter_log("Backup file successfully deleted. (restore_backup)")