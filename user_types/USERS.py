import typing

import file_system
import user_types.Hierarchy as Hierarchy

from .Hierarchy import SYSTEM

Users: dict[str, Hierarchy.Base] = {SYSTEM.name: SYSTEM}
hierarchy_priority = {1: SYSTEM, 2: Hierarchy.Admin, 3:  Hierarchy.User, 4: Hierarchy.Invited}

perms : dict[str, bool] = {
            "Rename": bool,
            "ADM": bool,
            "Delete": bool,
            "Write": bool,
            "Read": bool,
            "Make": bool,
            "SYS-CONTROL": bool
        }

def new_root(user : typing.Union[Hierarchy.User, Hierarchy.Admin, Hierarchy.Invited]):
    """
    Creates a new root
    """
    return file_system.SYS_MAIN_STORAGE.mkdir(path=user.name, user=SYSTEM)

def new(name : str, password : str = "", type : str = "UsEr"):
    """
    Creates a new user or admin
    """

    if name in Users:
        return "The user already exists"

    type = type.lower()

    if type == "admin":
        Admin = Hierarchy.Admin(name=name, password=password, root=None)
        return _extracted_from_new_20(Admin, name)
    elif type == "invited":
        Invited = Hierarchy.Invited(name=name, root=None)
        return _extracted_from_new_20(Invited, name)
    elif type == "user":
        User = Hierarchy.User(name=name, password=password, root=None)
        return _extracted_from_new_20(User, name)
    else:
        return "The type is not valid"


# TODO Rename this here and in `new`
def _extracted_from_new_20(user, name):
    user.root = new_root(user=user)
    Users[name] = user
    return user

def set_permissions(user : typing.Union[Hierarchy.User, Hierarchy.Admin, Hierarchy.Invited], new_permissions : perms):
    """
    Sets the permissions of a user
    """
    if user.name not in Users:
        return "The user does not exist"

    if user.name == "SYSTEM":
        return "You cannot change the permissions of the system"

    if user.permissions() == new_permissions: 
        return "The permissions are already set"

    user.perms = new_permissions
    return "The permissions have been set"

def Users_list():
    """
    Returns a list of all the users
    """
    return sorted(list(Users.keys()))
    