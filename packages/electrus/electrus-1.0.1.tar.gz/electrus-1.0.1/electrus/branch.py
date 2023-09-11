import os
import re
import json
import platform
import requests
import importlib
from bson import ObjectId
from datetime import datetime, timezone, timedelta

class Electron:
    def __init__(self, host=None, port=None, username=None, password=None, data_dir=None):
        try:
            settings = importlib.import_module('settings')
        except ImportError:
            settings = None

        default_settings = {
            'HOST': 'localhost',
            'PORT': 37017,
            'USER': None,
            'PASSWORD': None
        }

        if settings:
            db_settings = getattr(settings, 'DATABASES', {}).get('default', {})
        else:
            db_settings = default_settings

        self.host = host or db_settings.get('HOST', default_settings['HOST'])
        self.port = port or db_settings.get('PORT', default_settings['PORT'])
        self.username = username or db_settings.get('USER', default_settings['USER'])
        self.password = password or db_settings.get('PASSWORD', default_settings['PASSWORD'])
        self.data_dir = data_dir or self._default_data_dir()

        if self.host == 'localhost' and self.port == 37017:
            if self.username == 'root' and self.password == 'root':
                self._is_local = True
            else:
                self._is_local = False
        else:
            response = self._establish_remote_connection()
            if response and 'token' in response:
                self._is_local = False
                self._token = response['token']
                print(f"Your Connection Token: {self._token}, Note you are connected to a P2P engine")
            else:
                raise ConnectionError("Connection didn't establish")

        self.logger = {
            "enabled": False,
            "path": None,
            "backup": False
        }

    def _default_data_dir(self):
        if platform.system() == 'Windows':
            return os.path.expanduser("~\\.electrus")
        else:
            return os.path.expanduser("~/.electrus")

    def _get_collection_path(self, database, collection):
        return os.path.join(self.data_dir, database, collection, f"{collection}.json")

    def _establish_remote_connection(self):
        url = f"http://{self.host}:8000?port={self.port}"
        payload = {
            "username": self.username,
            "password": self.password
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def __getitem__(self, database):
        return Database(self, database)

    def enable_logger(self, path, backup=False):
        self.logger["enabled"] = True
        self.logger["path"] = path
        self.logger["backup"] = backup

    def log(self, function_name, args, output, error):
        if self.logger["enabled"]:
            log_data = {
                "timestamp": datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime("%Y-%m-%d %H:%M:%S %Z"),
                "function": function_name,
                "args": args,
                "output": output,
                "error": error
            }
            logs = []
            if os.path.exists(self.logger["path"]):
                with open(self.logger["path"], "r") as f:
                    logs = json.load(f)
            logs.append(log_data)
            with open(self.logger["path"], "w") as f:
                json.dump(logs, f, indent=4)

class Database:
    def __init__(self, client, database):
        self.client = client
        self.database = database

    def create_collection(self, collection):
        collection_path = self.client._get_collection_path(self.database, collection)
        os.makedirs(os.path.dirname(collection_path), exist_ok=True)
        with open(collection_path, 'w') as f:
            json.dump([], f, indent=4)

    def list_database_names(self):
        try:
            Collection._log('list_database_names', {}, {'result': "Database names retrieved."})
            return "Database names retrieved."
        except Exception as e:
            Collection._log('list_database_names', {}, {'error': str(e)})
            return f"Error retrieving database names: {str(e)}"

    def delete_collection(self, collection):
        collection_path = self.client._get_collection_path(self.database, collection)
        if os.path.exists(collection_path):
            os.remove(collection_path)

    def __getitem__(self, collection):
        return Collection(self.client, self.database, collection)

class Collection:
    def __init__(self, client, database, collection, enable_logging=False):
        self.client = client
        self.database = database
        self.collection = collection
        self.collection_path = self.client._get_collection_path(database, collection)
        self.logger = None

        if enable_logging:
            self.logger = self._init_logger()

        if not os.path.exists(self.collection_path):
            os.makedirs(os.path.dirname(self.collection_path), exist_ok=True)
            with open(self.collection_path, 'w') as f:
                json.dump([], f, indent=4)

    def _init_logger(self):
        logger = {
            'path': self._get_logs_path(),
            'backup': True
        }
        return logger

    def _get_logs_path(self):
        if platform.system() == 'Windows':
            return os.path.join(self.client.data_dir, '.logs', 'logs.json')
        else:
            return os.path.join(self.client.data_dir, '.logs', 'logs.json')

    def _log(self, function_name, inputs, outputs, error=None):
        if self.logger:
            log_entry = {
                'datetime': str(datetime.now()),
                'function': function_name,
                'inputs': inputs,
                'outputs': outputs,
                'error': str(error) if error else None
            }

            logs = []
            if os.path.exists(self.logger['path']):
                with open(self.logger['path'], 'r') as f:
                    logs = json.load(f)
            logs.append(log_entry)

            with open(self.logger['path'], 'w') as f:
                json.dump(logs, f, indent=4)

    def _read_items(self):
        if os.path.exists(self.collection_path):
            with open(self.collection_path, 'r') as f:
                return json.load(f)
        return []

    def _write_items(self, items):
        with open(self.collection_path, 'w') as f:
            json.dump(items, f, indent=4)

    def _apply_operator_logic(self, item, query):
        for key, value in query.items():
            if isinstance(value, dict):
                for operator, op_value in value.items():
                    if operator == "$eq":
                        if item.get(key) != op_value:
                            return False
                    elif operator == "$ne":
                        if item.get(key) == op_value:
                            return False
                    elif operator == "$lt":
                        if item.get(key) >= op_value:
                            return False
                    elif operator == "$gt":
                        if item.get(key) <= op_value:
                            return False
                    elif operator == "$lte":
                        if item.get(key) > op_value:
                            return False
                    elif operator == "$gte":
                        if item.get(key) < op_value:
                            return False
                    elif operator == "$in":
                        if item.get(key) not in op_value:
                            return False
                    elif operator == "$nin":
                        if item.get(key) in op_value:
                            return False
                    elif operator == "$exists":
                        if op_value and key not in item:
                            return False
                        if not op_value and key in item:
                            return False
                    elif operator == "$unset":
                        if key in item and isinstance(item[key], dict):
                            for unset_field in op_value:
                                if unset_field in item[key]:
                                    return False
                    elif operator == "$push":
                        if key in item and isinstance(item[key], dict):
                            for push_field, push_value in op_value.items():
                                if push_field in item[key] and isinstance(item[key][push_field], list):
                                    if push_value not in item[key][push_field]:
                                        return False
                                else:
                                    return False
                    elif operator == "$pull":
                        if key in item and isinstance(item[key], dict):
                            for pull_field, pull_value in op_value.items():
                                if pull_field in item[key] and isinstance(item[key][pull_field], list):
                                    if pull_value in item[key][pull_field]:
                                        return False
                                else:
                                    return False
                    elif operator == "$rename":
                        if key in item and isinstance(item[key], dict):
                            for rename_field, new_name in op_value.items():
                                if rename_field in item[key]:
                                    return False
            else:
                if item.get(key) != value:
                    return False
        return True

    
    def _update_with_operators(self, item, update_data):
        for operator, op_value in update_data.items():
            if operator == "$set":
                for set_field, set_value in op_value.items():
                    if set_field in item and isinstance(item[set_field], dict):
                        item[set_field].update(set_value)
                    else:
                        item[set_field] = set_value
            elif operator == "$unset":
                for unset_field in op_value:
                    if unset_field in item and isinstance(item[unset_field], dict):
                        for field in unset_field:
                            item[unset_field].pop(field, None)
                    else:
                        item.pop(unset_field, None)
            elif operator == "$push":
                for push_field, push_value in op_value.items():
                    if push_field in item and isinstance(item[push_field], list):
                        item[push_field].append(push_value)
                    else:
                        item[push_field] = [push_value]
            elif operator == "$pull":
                for pull_field, pull_value in op_value.items():
                    if pull_field in item and isinstance(item[pull_field], list):
                        item[pull_field] = [item for item in item[pull_field] if item != pull_value]
            elif operator == "$rename":
                for rename_field, new_name in op_value.items():
                    if rename_field in item and isinstance(item[rename_field], dict):
                        item[new_name] = item.pop(rename_field)
                    else:
                        item[new_name] = item.pop(rename_field, None)
            # Additional operators
            elif operator == "$inc":
                for inc_field, inc_value in op_value.items():
                    if inc_field in item and isinstance(item[inc_field], (int, float)):
                        item[inc_field] += inc_value
                    else:
                        item[inc_field] = inc_value
            elif operator == "$mul":
                for mul_field, mul_value in op_value.items():
                    if mul_field in item and isinstance(item[mul_field], (int, float)):
                        item[mul_field] *= mul_value
            elif operator == "$min":
                for min_field, min_value in op_value.items():
                    if min_field in item and isinstance(item[min_field], (int, float)):
                        item[min_field] = min(item[min_field], min_value)
            elif operator == "$max":
                for max_field, max_value in op_value.items():
                    if max_field in item and isinstance(item[max_field], (int, float)):
                        item[max_field] = max(item[max_field], max_value)
            elif operator == "$currentDate":
                for date_field, date_type in op_value.items():
                    item[date_field] = datetime.utcnow() if date_type == { "$type": "date" } else { "$type": "timestamp" }
            # Additional operators
            elif operator == "$addToSet":
                for add_field, add_value in op_value.items():
                    if add_field in item and isinstance(item[add_field], list):
                        if add_value not in item[add_field]:
                            item[add_field].append(add_value)
                    else:
                        item[add_field] = [add_value]
            elif operator == "$pop":
                for pop_field, pop_value in op_value.items():
                    if pop_field in item and isinstance(item[pop_field], list):
                        if pop_value == 1:
                            item[pop_field].pop()
                        elif pop_value == -1:
                            item[pop_field].pop(0)
            elif operator == "$pullAll":
                for pull_field, pull_values in op_value.items():
                    if pull_field in item and isinstance(item[pull_field], list):
                        item[pull_field] = [value for value in item[pull_field] if value not in pull_values]
            elif operator == "$bit":
                for bit_field, bit_value in op_value.items():
                    if bit_field in item and isinstance(item[bit_field], (int, float)):
                        item[bit_field] = item[bit_field] | bit_value
            elif operator == "$addToSetEach":
                for add_field, add_values in op_value.items():
                    if add_field in item and isinstance(item[add_field], list):
                        for value in add_values:
                            if value not in item[add_field]:
                                item[add_field].append(value)
                    else:
                        item[add_field] = add_values
            elif operator == "$pullEach":
                for pull_field, pull_values in op_value.items():
                    if pull_field in item and isinstance(item[pull_field], list):
                        item[pull_field] = [value for value in item[pull_field] if value not in pull_values]
            elif operator == "$unsetMany":
                for unset_field in op_value:
                    if unset_field in item and isinstance(item[unset_field], dict):
                        for field in unset_field:
                            item[unset_field].pop(field, None)
                    else:
                        item.pop(unset_field, None)
            elif operator == "$pushEach":
                for push_field, push_values in op_value.items():
                    if push_field in item and isinstance(item[push_field], list):
                        item[push_field].extend(push_values)
                    else:
                        item[push_field] = push_values
        return item

    def insert_one(self, data):
        try:
            if self.client._is_local:
                items = self._read_items()
                data['_id'] = str(ObjectId())
                items.append(data)
                self._write_items(items)
                self._log('insert', {'data': data}, {'result': 'Document inserted successfully.'})
                return "Document inserted successfully."
            else:
                self._log('insert', {'data': data}, {'result': 'Data validation failed.'})
                return "connection failed! ^ localhost:37017 is not connected.."
        except Exception as e:
            self._log('insert', {'data': data}, {'error': str(e)})
            return f"Error inserting document: {str(e)}"
    
    def insert_many(self, data_list):
        try:
            if self.client._is_local:
                items = self._read_items()
                for data in data_list:
                    data['_id'] = str(ObjectId())
                    items.append(data)
                self._write_items(items)
                self._log('insert_many', {'data_list': data_list}, {'result': f"{len(data_list)} documents inserted."})
                return f"{len(data_list)} documents inserted."
            else:
                self._log('insert_many', {'data': data_list}, {'result': 'Data validation failed.'})
                return "connection failed! ^ localhost:37017 is not connected.."
        except Exception as e:
            self._log('insert_many', {'data_list': data_list}, {'error': str(e)})
            return f"Error inserting documents: {str(e)}"

    def update_one(self, query, new_data):
        try:
            if self.client._is_local:
                items = self._read_items()
                updated_count = 0
                for item in items:
                    if self._apply_operator_logic(item, query):
                        self._update_with_operators(item, new_data)
                        updated_count += 1
                self._write_items(items)
                self._log('update_one', {'query': query, 'new_data': new_data}, {'result': f"{updated_count} documents updated."})
                return f"{updated_count} documents updated."
            else:
                self._log('upate_one', {'data': query, 'new_data': new_data}, {'result': 'Data validation failed.'})
                return "connection failed! ^ localhost:37017 is not connected.."
        except Exception as e:
            self._log('update_one', {'query': query, 'new_data': new_data}, {'error': str(e)})
            return f"Error updating documents: {str(e)}"

    def update_many(self, query, new_data):
        try:
            if self.client._is_local:  # Add this line
                items = self._read_items()
                updated_count = 0
                for item in items:
                    if self._apply_operator_logic(item, query):
                        self._update_with_operators(item, new_data)
                        updated_count += 1
                self._write_items(items)
                self._log('update_many', {'query': query, 'new_data': new_data}, {'result': f"{updated_count} documents updated."})
                return f"{updated_count} documents updated."
            else:
                self._log('update_many', {'query': query, 'new_data': new_data}, {'result': 'Data validation failed.'})
                return "connection failed! ^ localhost:37017 is not connected.."
        except Exception as e:
            self._log('update_many', {'query': query, 'new_data': new_data}, {'error': str(e)})
            return f"Error updating documents: {str(e)}"

    def delete_one(self, query):
        try:
            if self.client._is_local:  # Add this line
                items = self._read_items()
                before_count = len(items)
                items = [item for item in items if not self._apply_operator_logic(item, query)]
                deleted_count = before_count - len(items)
                self._write_items(items)
                self._log('delete', {'query': query}, {'result': f"{deleted_count} documents deleted."})
                return f"{deleted_count} documents deleted."
            else:
                self._log('delete', {'query': query}, {'result': 'Data validation failed.'})
                return "connection failed! ^ localhost:37017 is not connected.."
        except Exception as e:
            self._log('delete', {'query': query}, {'error': str(e)})
            return f"Error deleting documents: {str(e)}"


    def delete_many(self, query):
        try:
            if self.client._is_local:  # Add this line
                items = self._read_items()
                before_count = len(items)
                items = [item for item in items if not self._apply_operator_logic(item, query)]
                deleted_count = before_count - len(items)
                self._write_items(items)
                self._log('delete_many', {'query': query}, {'result': f"{deleted_count} documents deleted."})
                return f"{deleted_count} documents deleted."
            else:
                self._log('delete_many', {'query': query}, {'result': 'Data validation failed.'})
                return "connection failed! ^ localhost:37017 is not connected.."
        except Exception as e:
            self._log('delete_many', {'query': query}, {'error': str(e)})
            return f"Error deleting documents: {str(e)}"

    
    def find_one(self, query):
        try:
            if self.client._is_local:  # Add this line
                items = self._read_items()
                matching_items = [item for item in items if self._apply_operator_logic(item, query)]

                if matching_items:
                    result = QueryResult(matching_items)
                    self._log('find_one', {'query': query}, {'result': str(result)})
                    return result
                else:
                    error_msg = None
                    self._log('find_one', {'query': query}, {'error': error_msg})
                    return error_msg
            else:
                self._log('find_one', {'query': query}, {'result': 'Data validation failed.'})
                return "connection failed! ^ localhost:37017 is not connected.."
        except Exception as e:
            self._log('find_one', {'query': query}, {'error': str(e)})
            return f"Error finding documents: {str(e)}"

        
    def fetch_all(self, query=None):
        try:
            if self.client._is_local:  # Add this line
                items = self._read_items()
                filtered_items = items
                if query:
                    filtered_items = [item for item in items if self._apply_operator_logic(item, query)]
                self._log('fetch_all', {'query': query}, {'result': filtered_items})
                return filtered_items
            else:
                self._log('fetch_all', {'query': query}, {'result': 'Data validation failed.'})
                return "connection failed! ^ localhost:37017 is not connected.."
        except Exception as e:
            self._log('fetch_all', {'query': query}, {'error': str(e)})
            return f"Error fetching documents: {str(e)}"


    def count_documents(self, query):
        try:
            if self.client._is_local:  # Add this line
                items = self._read_items()
                count = sum(1 for item in items if self._apply_operator_logic(item, query))
                self._log('count_documents', {'query': query}, {'result': f"Count: {count}"})
                return count
            else:
                self._log('count_documents', {'query': query}, {'result': 'Data validation failed.'})
                return "connection failed! ^ localhost:37017 is not connected.."
        except Exception as e:
            self._log('count_documents', {'query': query}, {'error': str(e)})
            return f"Error counting documents: {str(e)}"


    def distinct(self, field, query=None):
        try:
            if self.client._is_local:  # Add this line
                items = self._read_items()
                filtered_items = items
                if query:
                    filtered_items = [item for item in items if self._apply_operator_logic(item, query)]
                distinct_values = set(item.get(field) for item in filtered_items)
                self._log('distinct', {'field': field, 'query': query}, {'result': list(distinct_values)})
                return list(distinct_values)
            else:
                self._log('distinct', {'field': field, 'query': query}, {'result': 'Data validation failed.'})
                return "connection failed! ^ localhost:37017 is not connected.."
        except Exception as e:
            self._log('distinct', {'field': field, 'query': query}, {'error': str(e)})
            return f"Error retrieving distinct values: {str(e)}"


    def drop_index(self, index_name):
        try:
            if self.client._is_local:  # Add this line
                self._log('drop_index', {'index_name': index_name}, {'result': f"Index '{index_name}' dropped."})
                return f"Index '{index_name}' dropped."
            else:
                self._log('drop_index', {'index_name': index_name}, {'result': 'Data validation failed.'})
                return "connection failed! ^ localhost:37017 is not connected.."
        except Exception as e:
            self._log('drop_index', {'index_name': index_name}, {'error': str(e)})
            return f"Error dropping index: {str(e)}"


    def find_one_and_update(self, query, update):
        try:
            if self.client._is_local:  # Add this line
                items = self._read_items()
                for item in items:
                    if self._apply_operator_logic(item, query):
                        original_item = dict(item)
                        item.update(update)
                        self._write_items(items)
                        self._log('find_one_and_update', {'query': query, 'update': update}, {'result': f"Document updated: {original_item} -> {item}"})
                        return f"Document updated: {original_item} -> {item}"
                self._log('find_one_and_update', {'query': query, 'update': update}, {'result': "No matching documents found."})
                return None
            else:
                self._log('find_one_and_update', {'query': query, 'update': update}, {'result': 'Data validation failed.'})
                return "connection failed! ^ localhost:37017 is not connected.."
        except Exception as e:
            self._log('find_one_and_update', {'query': query, 'update': update}, {'error': str(e)})
            return f"Error updating document: {str(e)}"


    def find_one_and_replace(self, query, replacement):
        try:
            if self.client._is_local:  # Add this line
                items = self._read_items()
                for idx, item in enumerate(items):
                    if self._apply_operator_logic(item, query):
                        original_item = dict(item)
                        items[idx] = replacement
                        self._write_items(items)
                        self._log('find_one_and_replace', {'query': query, 'replacement': replacement}, {'result': f"Document replaced: {original_item} -> {replacement}"})
                        return f"Document replaced: {original_item} -> {replacement}"
                self._log('find_one_and_replace', {'query': query, 'replacement': replacement}, {'result': "No matching documents found."})
                return None
            else:
                self._log('find_one_and_replace', {'query': query, 'replacement': replacement}, {'result': 'Data validation failed.'})
                return "connection failed! ^ localhost:37017 is not connected.."
        except Exception as e:
            self._log('find_one_and_replace', {'query': query, 'replacement': replacement}, {'error': str(e)})
            return f"Error replacing document: {str(e)}"


    def find_one_and_delete(self, query):
        try:
            if self.client._is_local:  # Add this line
                items = self._read_items()
                for item in items:
                    if self._apply_operator_logic(item, query):
                        deleted_item = dict(item)
                        items.remove(item)
                        self._write_items(items)
                        self._log('find_one_and_delete', {'query': query}, {'result': f"Document deleted: {deleted_item}"})
                        return f"Document deleted: {deleted_item}"
                self._log('find_one_and_delete', {'query': query}, {'result': "No matching documents found."})
                return None
            else:
                self._log('find_one_and_delete', {'query': query}, {'result': 'Data validation failed.'})
                return "connection failed! ^ localhost:37017 is not connected.."
        except Exception as e:
            self._log('find_one_and_delete', {'query': query}, {'error': str(e)})
            return f"Error deleting document: {str(e)}"

    def bulk_write(self, requests):
        try:
            if self.client._is_local:
                items = self._read_items()
                for request in requests:
                    operation = next(iter(request))
                    if operation == "insert_one":
                        data = request["insert_one"]
                        data['_id'] = str(ObjectId())
                        items.append(data)
                    elif operation == "insert_many":
                        data_list = request["insert_many"]
                        for data in data_list:
                            data['_id'] = str(ObjectId())
                        items.extend(data_list)
                    elif operation == "update_one":
                        filter_query = request["update_one"]["filter"]
                        update_data = request["update_one"]["update"]
                        for item in items:
                            if self._apply_operator_logic(item, filter_query):
                                self._update_with_operators(item, update_data)
                    elif operation == "delete_one":
                        filter_query = request["delete_one"]
                        items = [item for item in items if not self._apply_operator_logic(item, filter_query)]
                    elif operation == "delete_many":
                        filter_query = request["delete_many"]
                        items = [item for item in items if not self._apply_operator_logic(item, filter_query)]
                self._write_items(items)
                self._log('bulk_write', {'requests': requests}, {'result': f"{len(requests)} operations performed."})
                return f"{len(requests)} operations performed."
            else:
                self._log('bulk_write', {'requests': requests}, {'result': 'Data validation failed.'})
                return "connection failed! ^ localhost:37017 is not connected.."
        except Exception as e:
            self._log('bulk_write', {'requests': requests}, {'error': str(e)})
            return f"Error performing bulk write operations: {str(e)}"

    def list_collections(self):
        try:
            if self.client._is_local:  # Add this line
                collections = [name for name in os.listdir(self.client.data_dir) if os.path.isdir(os.path.join(self.client.data_dir, name))]
                self._log('list_collections', {}, {'result': collections})
                return collections
            else:
                self._log('list_collections', {}, {'result': 'Data validation failed.'})
                return "connection failed! ^ localhost:37017 is not connected.."
        except Exception as e:
            self._log('list_collections', {}, {'error': str(e)})
            return f"Error listing collections: {str(e)}"


    def list_indexes(self):
        try:
            if self.client._is_local:  # Add this line
                indexes = self._get_indexes()
                self._log('list_indexes', {}, {'result': indexes})
                return indexes
            else:
                self._log('list_indexes', {}, {'result': 'Data validation failed.'})
                return "connection failed! ^ localhost:37017 is not connected.."
        except Exception as e:
            self._log('list_indexes', {}, {'error': str(e)})
            return f"Error retrieving indexes: {str(e)}"

        
    def list_collection_names(self):
        try:
            if self.client._is_local:  # Add this line
                collection_names = self._get_collection_names()
                self._log('list_collection_names', {}, {'result': collection_names})
                return collection_names
            else:
                self._log('list_collection_names', {}, {'result': 'Data validation failed.'})
                return "connection failed! ^ localhost:37017 is not connected.."
        except Exception as e:
            self._log('list_collection_names', {}, {'error': str(e)})
            return f"Error retrieving collection names: {str(e)}"


    # Helper function to retrieve indexes
    def _get_indexes(self):
        schema_path = self.client._get_collection_path(self.database, f"{self.collection}_indexes.json")
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                return json.load(f)
        return []

    # Helper function to retrieve collection names
    def _get_collection_names(self):
        data_dir = self.client.data_dir
        database_dir = os.path.join(data_dir, self.database)
        collection_names = []
        for root, dirs, files in os.walk(database_dir):
            for file in files:
                if file.endswith('.json') and file != f"{self.collection}_indexes.json":
                    collection_names.append(file.replace('.json', ''))
        return collection_names

    def replace_one(self, query, replacement):
        try:
            if self.client._is_local:  # Add this line
                items = self._read_items()
                for idx, item in enumerate(items):
                    if self._apply_operator_logic(item, query):
                        original_item = dict(item)
                        items[idx] = replacement
                        self._write_items(items)
                        self._log('replace_one', {'query': query, 'replacement': replacement}, {'result': f"Document replaced: {original_item} -> {replacement}"})
                        return f"Document replaced: {original_item} -> {replacement}"
                self._log('replace_one', {'query': query, 'replacement': replacement}, {'result': "No matching documents found."})
                return "No matching documents found."
            else:
                self._log('replace_one', {'query': query, 'replacement': replacement}, {'result': 'Data validation failed.'})
                return "connection failed! ^ localhost:37017 is not connected.."
        except Exception as e:
            self._log('replace_one', {'query': query, 'replacement': replacement}, {'error': str(e)})
            return f"Error replacing document: {str(e)}"


    def rename_collection(self, new_name):
        try:
            if self.client._is_local:  # Add this line
                self.collection = new_name
                self.collection_path = self.client._get_collection_path(self.database, new_name)
                self._log('rename_collection', {'new_name': new_name}, {'result': f"Collection renamed to '{new_name}'."})
                return f"Collection renamed to '{new_name}'."
            else:
                self._log('rename_collection', {'new_name': new_name}, {'result': 'Data validation failed.'})
                return "connection failed! ^ localhost:37017 is not connected.."
        except Exception as e:
            self._log('rename_collection', {'new_name': new_name}, {'error': str(e)})
            return f"Error renaming collection: {str(e)}"


    def estimated_document_count(self):
        try:
            if self.client._is_local:  # Add this line
                count = len(self._read_items())
                self._log('estimated_document_count', {}, {'result': f"Estimated document count: {count}"})
                return f"Estimated document count: {count}"
            else:
                self._log('estimated_document_count', {}, {'result': 'Data validation failed.'})
                return "connection failed! ^ localhost:37017 is not connected.."
        except Exception as e:
            self._log('estimated_document_count', {}, {'error': str(e)})
            return f"Error estimating document count: {str(e)}"


    def sort(self, field, reverse=False):
        try:
            if self.client._is_local:  # Add this line
                items = self._read_items()
                sorted_items = sorted(items, key=lambda item: item.get(field), reverse=reverse)
                result = QueryResult(sorted_items)
                self._log('sort', {'field': field, 'reverse': reverse}, {'result': str(result)})
                return result
            else:
                self._log('sort', {'field': field, 'reverse': reverse}, {'result': 'Data validation failed.'})
                return "connection failed! ^ localhost:37017 is not connected.."
        except Exception as e:
            self._log('sort', {'field': field, 'reverse': reverse}, {'error': str(e)})
            return f"Error sorting documents: {str(e)}"


    def aggregate(self, pipeline):
        try:
            if self.client._is_local:  # Add this line
                items = self._read_items()
                aggregated_items = items

                for stage in pipeline:
                    operator = next(iter(stage))

                    if operator == "$sort":
                        field = stage["$sort"]["field"]
                        order = stage["$sort"]["order"]
                        aggregated_items = sorted(aggregated_items, key=lambda item: item.get(field), reverse=(order == -1))

                    elif operator == "$project":
                        projection_fields = stage["$project"]
                        aggregated_items = [{key: item.get(key) for key in projection_fields} for item in aggregated_items]

                result = QueryResult(aggregated_items)
                self._log('aggregate', {'pipeline': pipeline}, {'result': str(result)})
                return result

            else:
                self._log('aggregate', {'pipeline': pipeline}, {'result': 'Data validation failed.'})
                return "connection failed! ^ localhost:37017 is not connected.."
        except Exception as e:
            self._log('aggregate', {'pipeline': pipeline}, {'error': str(e)})
            return f"Error aggregating documents: {str(e)}"


    def create_index(self, field):
        try:
            if self.client._is_local:  # Add this line
                items = self._read_items()
                indexed_items = sorted(items, key=lambda item: item.get(field))
                self._write_items(indexed_items)
                self._log('create_index', {'field': field}, {'result': f"Index created on field: {field}"})
                return f"Index created on field: {field}"
            else:
                self._log('create_index', {'field': field}, {'result': 'Data validation failed.'})
                return "connection failed! ^ localhost:37017 is not connected.."
        except Exception as e:
            self._log('create_index', {'field': field}, {'error': str(e)})
            return f"Error creating index: {str(e)}"

        
    def drop(self):
        try:
            if self.client._is_local:  # Add this line
                self._delete_data_file()
                self._log('drop', {}, {'result': "Collection dropped."})
                return "Collection dropped."
            else:
                self._log('drop', {}, {'result': 'Data validation failed.'})
                return "connection failed! ^ localhost:37017 is not connected.."
        except Exception as e:
            self._log('drop', {}, {'error': str(e)})
            return f"Error dropping collection: {str(e)}"

        
    def find_one_and_upsert(self, query, update_data):
        try:
            if self.client._is_local:  # Add this line
                items = self._read_items()
                for item in items:
                    if self._apply_operator_logic(item, query):
                        self._update_with_operators(item, update_data)
                        self._write_items(items)
                        self._log('find_one_and_upsert', {'query': query, 'update_data': update_data}, {'result': "Document upserted."})
                        return "Document upserted."
                # If no matching document found, insert the update_data as a new document
                update_data['_id'] = str(ObjectId())
                items.append(update_data)
                self._write_items(items)
                self._log('find_one_and_upsert', {'query': query, 'update_data': update_data}, {'result': "New document inserted."})
                return "New document inserted."
            else:
                self._log('find_one_and_upsert', {'query': query, 'update_data': update_data}, {'result': 'Data validation failed.'})
                return "connection failed! ^ localhost:37017 is not connected.."
        except Exception as e:
            self._log('find_one_and_upsert', {'query': query, 'update_data': update_data}, {'error': str(e)})
            return f"Error upserting document: {str(e)}"

        
    def distinct_with_query(self, field, query):
        try:
            if self.client._is_local:  # Add this line
                items = self._read_items()
                distinct_values = set()
                for item in items:
                    if self._apply_operator_logic(item, query):
                        distinct_values.add(item.get(field))
                self._log('distinct_with_query', {'field': field, 'query': query}, {'result': list(distinct_values)})
                return list(distinct_values)
            else:
                self._log('distinct_with_query', {'field': field, 'query': query}, {'result': 'Data validation failed.'})
                return "connection failed! ^ localhost:37017 is not connected.."
        except Exception as e:
            self._log('distinct_with_query', {'field': field, 'query': query}, {'error': str(e)})
            return f"Error retrieving distinct values: {str(e)}"

        
    def map_reduce(self, map_function, reduce_function):
        try:
            if self.client._is_local:  # Add this line
                items = self._read_items()
                mapped_result = {}
                for item in items:
                    map_result = map_function(item)
                    for key, value in map_result.items():
                        mapped_result.setdefault(key, []).append(value)
                
                reduced_result = {}
                for key, values in mapped_result.items():
                    reduce_result = reduce_function(key, values)
                    reduced_result[key] = reduce_result
                
                self._log('map_reduce', {}, {'result': reduced_result})
                return reduced_result
            else:
                self._log('map_reduce', {}, {'result': 'Data validation failed.'})
                return "connection failed! ^ localhost:37017 is not connected.."
        except Exception as e:
            self._log('map_reduce', {}, {'error': str(e)})
            return f"Error performing map-reduce operation: {str(e)}"

        
    def find_by_email(self, email):
        try:
            if self.client._is_local:
                items = self._read_items()
                result = [item for item in items if item.get("email") == email]
                self._log('find_by_email', {'email': email}, {'result': result})
                return result
            else:
                self._log('find_by_email', {'email': email}, {'result': 'Data validation failed.'})
                return "connection failed! ^ localhost:37017 is not connected.."
        except Exception as e:
            self._log('find_by_email', {'email': email}, {'error': str(e)})
            return f"Error finding documents by email: {str(e)}"
        
    def validate_data(self, query):
        try:
            if self.client._is_local:
                items = self._read_items()
                validated_results = []

                for item in items:
                    if self._apply_operator_logic(item, query):
                        validated_item = {}
                        for key, value in query.items():
                            item_value = item.get(key)
                            if isinstance(value, str) and isinstance(item_value, str):
                                validated_item[key] = item_value
                            elif isinstance(value, int) and isinstance(item_value, int):
                                validated_item[key] = item_value
                            elif isinstance(value, float) and isinstance(item_value, float):
                                validated_item[key] = item_value
                        validated_results.append(validated_item)

                self._log('validate_data', {'query': query}, {'result': validated_results})
                return validated_results
            else:
                self._log('validate_data', {'query': query}, {'result': 'Data validation failed.'})
                return "connection failed! ^ localhost:37017 is not connected.."
        except Exception as e:
            self._log('validate_data', {'query': query}, {'error': str(e)})
            return f"Error validating data: {str(e)}"
        
    def is_capped(self):
        try:
            if self.client._is_local:
                self._log('is_capped', {}, {'result': "Collection is capped."})
                return True if self.capped else False
            else:
                self._log('is_capped', {}, {'result': 'Data validation failed.'})
                return "connection failed! ^ localhost:37017 is not connected.."
        except Exception as e:
            self._log('is_capped', {}, {'error': str(e)})
            return f"Error checking if collection is capped: {str(e)}"
        
    def compact_database(self):
        try:
            if self.client._is_local:
                items = self._read_items()
                compacted_items = [item for item in items if item is not None]
                self._write_items(compacted_items)
                self._log('compact_database', {}, {'result': "Database compacted."})
                return "Database compacted."
            else:
                self._log('compact_database', {}, {'result': 'Data validation failed.'})
                return "connection failed! ^ localhost:37017 is not connected.."
        except Exception as e:
            self._log('compact_database', {}, {'error': str(e)})
            return f"Error compacting database: {str(e)}"
        
    def search_text(self, query):
        try:
            if self.client._is_local:
                items = self._read_items()
                matching_items = [item for item in items if any(value for value in item.values() if re.search(query, str(value)))]
                self._log('search_text', {'query': query}, {'result': matching_items})
                return matching_items
            else:
                self._log('search_text', {'query': query}, {'result': 'Data validation failed.'})
                return "connection failed! ^ localhost:37017 is not connected.."
        except Exception as e:
            self._log('search_text', {'query': query}, {'error': str(e)})
            return f"Error searching documents: {str(e)}"
        
    def export_data(self, file_path):
        try:
            if self.client._is_local:
                items = self._read_items()
                with open(file_path, 'w') as export_file:
                    json.dump(items, export_file, indent=2)
                self._log('export_data', {'file_path': file_path}, {'result': 'Data exported successfully.'})
                return "Data exported successfully."
            else:
                self._log('export_data', {'file_path': file_path}, {'result': 'Data validation failed.'})
                return "connection failed! ^ localhost:37017 is not connected.."
        except Exception as e:
            self._log('export_data', {'file_path': file_path}, {'error': str(e)})
            return f"Error exporting data: {str(e)}"
        
    def import_data(self, file_path):
        try:
            if self.client._is_local:
                with open(file_path, 'r') as import_file:
                    data = json.load(import_file)
                    self._write_items(data)
                self._log('import_data', {'file_path': file_path}, {'result': 'Data imported successfully.'})
                return "Data imported successfully."
            else:
                self._log('import_data', {'file_path': file_path}, {'result': 'Data validation failed.'})
                return "connection failed! ^ localhost:37017 is not connected.."
        except Exception as e:
            self._log('import_data', {'file_path': file_path}, {'error': str(e)})
            return f"Error importing data: {str(e)}"
        
    def expire_data(self, expiration_date):
        try:
            if self.client._is_local:
                items = self._read_items()
                expired_items = [item for item in items if item.get("expiry_date") and item["expiry_date"] < expiration_date]
                for expired_item in expired_items:
                    items.remove(expired_item)
                self._write_items(items)
                self._log('expire_data', {'expiration_date': expiration_date}, {'result': f"{len(expired_items)} documents expired."})
                return f"{len(expired_items)} documents expired."
            else:
                self._log('expire_data', {'expiration_date': expiration_date}, {'result': 'Data validation failed.'})
                return "connection failed! ^ localhost:37017 is not connected.."
        except Exception as e:
            self._log('expire_data', {'expiration_date': expiration_date}, {'error': str(e)})
            return f"Error expiring data: {str(e)}"
        
    def add_version(self, query, new_version):
        try:
            if self.client._is_local:
                items = self._read_items()
                updated_count = 0
                for item in items:
                    if self._apply_operator_logic(item, query):
                        item['versions'].append(new_version)
                        updated_count += 1
                self._write_items(items)
                self._log('add_version', {'query': query, 'new_version': new_version}, {'result': f"{updated_count} documents updated with new version."})
                return f"{updated_count} documents updated with new version."
            else:
                self._log('add_version', {'query': query, 'new_version': new_version}, {'result': 'Data validation failed.'})
                return "connection failed! ^ localhost:37017 is not connected.."
        except Exception as e:
            self._log('add_version', {'query': query, 'new_version': new_version}, {'error': str(e)})
            return f"Error adding version: {str(e)}"

class QueryResult:
    def __init__(self, result):
        self.result = result

    def __str__(self):
        return str([item for item in self.result])

    def __getitem__(self, key):
        values = [item.get(key) for item in self.result]
        if len(values) == 1:
            return values[0]
        return values