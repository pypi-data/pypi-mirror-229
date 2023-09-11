from datetime import datetime

class Proxy:
    def __init__(self, collection, security, allowed_methods=None, restricted_fields=None):
        """
        Initialize the Proxy.

        Args:
            collection: The collection to proxy.
            security: The security manager.
            allowed_methods (list, optional): A list of allowed method names.
            restricted_fields (list, optional): A list of restricted field names.

        Usage:
            proxy = Proxy(collection, security, allowed_methods=['find', 'insert_one'], restricted_fields=['password'])
        """
        self.collection = collection
        self.security = security
        self.allowed_methods = allowed_methods or []
        self.restricted_fields = restricted_fields or []

    def __getattr__(self, attr_name):
        """
        Override the behavior of attribute access.

        Args:
            attr_name (str): The name of the attribute being accessed.

        Returns:
            function or attribute: The proxied method or attribute.

        Raises:
            AttributeError: If the attribute does not exist in the collection.
            PermissionError: If access to the attribute is not allowed.

        Usage:
            result = proxy.some_method(arg1, arg2)
        """
        if hasattr(self.collection, attr_name):
            attr = getattr(self.collection, attr_name)
            if callable(attr):
                if attr_name in self.allowed_methods:
                    return lambda *args, **kwargs: self._proxy_method(attr, attr_name, *args, **kwargs)
                else:
                    raise PermissionError(f"Access to '{attr_name}' is not allowed.")
            else:
                return attr
        else:
            raise AttributeError(f"'{type(self.collection).__name__}' object has no attribute '{attr_name}'")

    def _proxy_method(self, method, method_name, *args, **kwargs):
        """
        Proxy a method, applying security checks.

        Args:
            method: The method to proxy.
            method_name (str): The name of the method.
            *args: Positional arguments for the method.
            **kwargs: Keyword arguments for the method.

        Returns:
            Any: The result of the proxied method.

        Raises:
            PermissionError: If authentication, authorization, or security checks fail.

        Usage:
            result = proxy._proxy_method(some_method, 'some_method', arg1, arg2)
        """
        user = self.security.authenticate(kwargs.get('username'), kwargs.get('password'))
        if not user:
            raise PermissionError("Authentication failed.")

        required_roles = self._get_required_roles(method_name)
        if not self.security.authorize(user, required_roles):
            raise PermissionError("Authorization failed.")

        self._check_security(method_name, kwargs, user)
        result = method(*args, **kwargs)
        return result

    def _get_required_roles(self, method_name):
        """
        Get the required roles for a method.

        Args:
            method_name (str): The name of the method.

        Returns:
            list: A list of required roles for the method.

        Usage:
            roles = proxy._get_required_roles('find')
        """
        roles_mapping = {
            "insert_one": ["admin", "editor"],
            "find": ["admin", "editor", "viewer"],
            "aggregate": ["admin", "editor", "viewer"],
            "delete_one": ["admin"],
            "update_one": ["admin", "editor"],
        }
        return roles_mapping.get(method_name, [])

    def _check_security(self, method_name, kwargs, user):
        """
        Check security for a method.

        Args:
            method_name (str): The name of the method.
            kwargs (dict): Keyword arguments for the method.
            user (dict): The user object.

        Raises:
            PermissionError: If security checks fail.

        Usage:
            proxy._check_security('insert_one', {'document': {...}}, user)
        """
        if method_name == "insert_one" and "document" in kwargs:
            document = kwargs["document"]
            for field in self.restricted_fields:
                if field in document:
                    raise PermissionError(f"Field '{field}' is restricted and cannot be modified.")

        if method_name == "update_one" and "query" in kwargs and "new_data" in kwargs:
            query = kwargs["query"]
            if query.get("username") == user.get("username"):
                new_data = kwargs["new_data"]
                if new_data.get("role") and new_data["role"] != user["role"]:
                    raise PermissionError("You cannot change your own role.")

        action = f"Method '{method_name}' executed by user '{user['username']}'"
        self._log_action(action)

    def _log_action(self, action):
        """
        Log an action.

        Args:
            action (str): The action to log.

        Usage:
            proxy._log_action("Method 'find' executed by user 'admin'")
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("audit_log.txt", "a") as log_file:
            log_file.write(f"{timestamp}: {action}\n")
