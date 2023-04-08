class Base(object):
    def __init__(self, name : str, password : str = None, root = None):
        self.type = self.__class__.__name__
        self.root = root
        self.name = name
        self.password = password
        self.perms = {
            "Rename": bool,
            "ADM": bool,
            "Delete": bool,
            "Write": bool,
            "Make": bool,
            "Read": bool,
            "SYS-CONTROL": bool
        }
        
    def permissions(self):
        return self.perms
    
class User(Base):
    def __init__(self, name, password, root):
        self.type = self.__class__.__name__
        self.root = root
        self.name = name
        self.password = password
        self.perms = {
            "Rename": True,
            "ADM": False,
            "Delete": True,
            "Write": True,
            "Make": True,
            "Read": True,
            "SYS-CONTROL": False
        }

        #super(User, self).__init__(self.type, self.name, self.password, self.root)
        
    def permissions(self):
        return self.perms

    def to_dict(self):
        return {
            "type": self.type,
            "name": self.name,
            "password": self.password,
            "permissions": self.perms,
            'root': self.root.to_dict()
        }

class Admin(Base):
    def __init__(self, name, password, root):
        self.type = self.__class__.__name__
        self.root = root
        self.name = name
        self.password = password
        self.perms = {
            "Rename": True,
            "ADM": True,
            "Delete": True,
            "Write": True,
            "Make": True,
            "Read": True,
            "SYS-CONTROL": False
        }

        #super(Admin, self).__init__(self.type, self.name, self.password, self.root)

    def permissions(self):
        return self.perms

    def to_dict(self):
        return {
            'type': self.type,
            'name': self.name,
            'password': self.password,
            'perms': self.perms,
            'root': self.root.to_dict()
        }

class Invited(Base):
    def __init__(self, name, root):
        self.type = self.__class__.__name__
        self.root = root
        self.name = name
        self.perms = {
            "Rename": False,
            "ADM": False,
            "Delete": False,
            "Write": False,
            "Make": False,
            "Read": True,
            "SYS-CONTROL": False
        }

        #super(Invited, self).__init__(self.type, self.name, self.root)

    def permissions(self):
        return self.perms

    def to_dict(self):
        return {
            'type': self.type,
            'name': self.name,
            'perms': self.perms,
            'root': self.root.to_dict()
        }
        
class System(object):
    def __init__(self):
        from file_system.Folders import SYS_MAIN_STORAGE
        self.name = "SYSTEM"
        self.PERMS = {
            "Rename": True,
            "ADM": True,
            "Delete": True,
            "Write": True,
            "Read": True,
            "Make": True,
            "SYS-CONTROL": True
        }
        self.password = "SYS"
        self.root = SYS_MAIN_STORAGE
        self.type = self.__class__.__name__

    def permissions(self):
        return self.PERMS

    def to_dict(self):
        return {
            'type': self.type,
            'name': self.name,
            'password': self.password,
            'perms': self.perms,
            'root': self.root.to_dict()
        }

SYSTEM = System()
del System