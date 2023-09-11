import hashlib

class Security:
    def __init__(self, users, roles):
        self.users = users
        self.roles = roles
    
    def authenticate(self, username, password):
        user = self.users.get(username)
        if user and user['password'] == self._hash_password(password):
            return user
        return None
    
    def authorize(self, user, required_roles):
        if user.get('role') in required_roles:
            return True
        return False
    
    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()