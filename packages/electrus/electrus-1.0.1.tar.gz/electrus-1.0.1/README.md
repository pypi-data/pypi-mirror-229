# Electrus Database

This project provides a reliable database, allowing you to perform CRUD operations and more on collections of documents.

## Features

- Insert single and multiple documents
- Update documents using various operators
- Delete documents based on filters
- Find documents based on filters
- Fetch all documents or with a specified query
- Count documents that match a query
- Retrieve distinct values of a field
- Drop indexes
- Find and update a single document
- Find and replace a single document
- Find and delete a single document
- Perform bulk write operations
- List collections, indexes, and collection names
- Replace documents based on filters
- Rename a collection
- Estimate document count
- Sort documents based on a field
- Aggregate documents using a pipeline
- Create an index on a field
- Drop a collection
- Find or insert a document using upsert
- Retrieve distinct values of a field with a query
- Perform map-reduce operations
- Find documents by email
- Validate data based on a query
- Check if a collection is capped
- Compact the database by removing deleted documents

## Usage

```python

from electrus import Electron

client = Electron(host='localhost', port=37017, username='root', password='root')
db = client['my_database']
collection = db['users']

# Insert one document
insert_result = collection.insert_one({"name": "Alice", "age": 30})
print(insert_result)

# Insert multiple documents
insert_many_result = collection.insert_many([
    {"name": "Bob", "age": 25},
    {"name": "Charlie", "age": 28}
])
print(insert_many_result)

# Update a document
update_result = collection.update_one({"name": "Alice"}, {"$set": {"age": 31}})
print(update_result)

# Update multiple documents
update_many_result = collection.update_many({"age": {"$lt": 30}}, {"$set": {"status": "young"}})
print(update_many_result)

# Delete a document
delete_result = collection.delete_one({"name": "Bob"})
print(delete_result)

# Delete multiple documents
delete_many_result = collection.delete_many({"age": {"$lt": 30}})
print(delete_many_result)

# Find documents using a query
query = {"status": "young"}
found_documents = collection.fetch_all(query)
print(found_documents)

# Count documents matching a query
count = collection.count_documents(query)
print(count)

# Get distinct values for a field
distinct_values = collection.distinct("age", query)
print(distinct_values)

# Create an index
index_result = collection.create_index("age")
print(index_result)

# List collection names
collection_names = collection.list_collection_names()
print(collection_names)

# Drop a collection
drop_result = collection.drop()
print(drop_result)

# Find one document and upsert
upsert_result = collection.find_one_and_upsert({"name": "David"}, {"name": "David", "age": 22})
print(upsert_result)

# Validate data based on a query
validate_query = {"age": 30}
validated_data = collection.validate_data(validate_query)
print(validated_data)

# Check if collection is capped
is_capped = collection.is_capped()
print(is_capped)

# Compact the database
compact_result = collection.compact_database()
print(compact_result)

# List collections in the database
collection_list = collection.list_collections()
print(collection_list)

# List indexes in the collection
index_list = collection.list_indexes()
print(index_list)

# Rename the collection
rename_result = collection.rename_collection("new_collection_name")
print(rename_result)

# Get estimated document count
document_count = collection.estimated_document_count()
print(document_count)

# Sort documents by a field
sorted_documents = collection.sort("age", reverse=True)
print(sorted_documents)

# Aggregate documents using a pipeline
pipeline = [
    {"$sort": {"field": "age", "order": 1}},
    {"$project": ["name", "age"]}
]
aggregated_result = collection.aggregate(pipeline)
print(aggregated_result)

# Find one document and replace
replace_result = collection.find_one_and_replace({"name": "David"}, {"name": "Ella", "age": 27})
print(replace_result)

# Find one document and delete
delete_result = collection.find_one_and_delete({"name": "Ella"})
print(delete_result)

# Perform map-reduce operation
def map_function(item):
    return {"age": item["age"]}

def reduce_function(key, values):
    return sum(values) / len(values)

map_reduce_result = collection.map_reduce(map_function, reduce_function)
print(map_reduce_result)

# Find documents by email
email_search_result = collection.find_by_email("alice@example.com")
print(email_search_result)

# Distinct values with a query
distinct_query_result = collection.distinct_with_query("age", {"status": "young"})
print(distinct_query_result)

# Drop an index
drop_index_result = collection.drop_index("age_1")
print(drop_index_result)

# Define bulk write operations
bulk_operations = [
    {"insert_one": {"name": "Alice", "email": "alice@example.com", "age": 25}},
    {"insert_many": [
        {"name": "Bob", "email": "bob@example.com", "age": 30},
        {"name": "Charlie", "email": "charlie@example.com", "age": 28}
    ]},
    {"update_one": {"filter": {"age": {"$gt": 25}}, "update": {"$set": {"status": "senior"}}}},
    {"update_many": {"filter": {"age": {"$lt": 30}}, "update": {"$set": {"status": "young"}}}},
    {"delete_one": {"age": {"$gt": 25}}},
    {"delete_many": {"age": {"$lt": 30}}}
]

# Use the bulk_write function to perform the defined operations
result = collection.bulk_write(bulk_operations)

```

# Recovery

```python

from electrus import Recovery, Electron

client = Electron(host='localhost', port=37017, username='root', password='root')
db = client['my_database']
collection = db['users']
# Create a recovery instance
recovery = Recovery(client)

# Backup a database
backup_result = recovery.backup('my_database', format='zip')
print(backup_result)  # Backup of 'my_database' created at '/path/to/backup/my_database.zip'.

# Restore a database
restore_result = recovery.restore('/path/to/backup/my_database.zip', format='zip')
print(restore_result)  # Database restored from 'zip' backup.


```

# Proxy with Firewall

```python
# Example usage
class Database:
    def insert(self, data):
        print(f"Inserted data: {data}")
    
    def update(self, query, update_data):
        print(f"Updated data matching query: {query} with {update_data}")

# Security setup
users = {
    "admin": {"password": "admin_pass", "role": "admin"},
    "editor": {"password": "editor_pass", "role": "editor"},
    "viewer": {"password": "viewer_pass", "role": "viewer"},
}
roles = ["admin", "editor", "viewer"]

security = Security(users, roles)

# Proxy setup
allowed_methods = ["insert_one", "update_one", "find", "aggregate", "delete_one"]
restricted_fields = ["restricted_field"]

collection = Database()
proxy = Proxy(collection, security, allowed_methods, restricted_fields)

# Firewall setup
allowed_functions = ["insert_one", "update_one", "find", "aggregate", "delete_one"]
roles_permissions = {
    "admin": allowed_functions,
    "editor": ["insert_one", "update_one"],
    "viewer": ["find", "aggregate"],
}
firewall = Firewall(allowed_functions, roles_permissions)

# Secure proxy methods
secure_insert_one = firewall.secure_function(proxy.insert_one)
secure_update_one = firewall.secure_function(proxy.update_one)
secure_find = firewall.secure_function(proxy.find)
secure_aggregate = firewall.secure_function(proxy.aggregate)
secure_delete_one = firewall.secure_function(proxy.delete_one)

user_role = "admin"
user_ip = "192.168.1.10"

# Usage
try:
    # Authentication
    user = security.authenticate("admin", "admin_pass")
    if user:
        print(f"Authentication successful: {user}")
    else:
        print("Authentication failed.")

    # Authorization
    if security.authorize(user, ["admin", "editor"]):
        print("Authorization successful.")
    else:
        print("Authorization failed.")

    # Insert document
    secure_insert_one(user_role, user_ip, document={"name": "John", "age": 30})
    
    # Update document
    secure_update_one(user_role, user_ip, query={"name": "John"}, new_data={"age": 31})
    
    # Find documents
    secure_find(user_role, user_ip, query={"age": {"$gte": 30}})
    
    # Aggregate documents
    secure_aggregate(user_role, user_ip, pipeline=[{"$match": {"age": {"$gte": 30}}}, {"$group": {"_id": "$name"}}])
    
    # Delete document
    secure_delete_one(user_role, user_ip, query={"name": "John"})
    
except PermissionError as e:
    print(f"Permission Error: {str(e)}")
```