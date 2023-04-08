# from user_types.Hierarchy import Base
from os.path import isabs, split
from typing import Optional, Union

from .Files import File

PIPE_PREFIX = "│   "
SPACE_PREFIX = "    "
PIPE = "│"
ELBOW = "└──"
TEE = "├──"

SYS_MAIN_STORAGE = None
_folder = None

# # TODO: Just for avoid circular import and be able to use code recommendations
class Base(object):
    def __init__(self):
        self.type = self.__class__.__name__
        self.root : Folder = None
        self.name : str = None
        self.password : str = None
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

class Folder(object):
    def __init__(self, foldername : str, parent : _folder = None):
        self.foldername : str = foldername
        self.subFolders : dict[str, Folder] = {}
        self.files : dict[str, File] = {}
        self.parent : Folder = parent
        if parent!=None:
            parent.subFolders[self.foldername] = self

    def mkfile(self, path : str, user : Base):
        if not user.permissions().get("Make", False):
            return "Permission Denied"

        # Split path into directory and filename components
        directory, filename = split(path)

        # Get the folder object based on the directory path
        if isabs(directory):
            # Absolute path : str, start from root folder
            folder = SYS_MAIN_STORAGE
            directory = directory[1:]  # remove leading "/"
        else:
            # Relative path : str, start from this folder
            folder = self

        # Traverse the folder structure to get to the desired folder
        for folder_name in directory.split('/'):
            if folder_name == '':
                continue
            if folder_name in folder.subFolders:
                folder = folder.subFolders[folder_name]
            else:
                return f"Error: Folder '{folder_name}' not found"

        # Check if file already exists
        if filename in folder.files:
            return f"Error: File '{filename}' already exists"

        # Create the file object and add it to the folder
        file = File(filename, folder)
        folder.files[filename] = file

        return f"File '{file.filename}' created in '{folder.foldername if folder != SYS_MAIN_STORAGE else '/'}'"
    def rmfile(self, path : str, user : Base):
        return (
            self.delete(path, user, File)
            if user.permissions().get("Delete", False)
            else "Permission Denied"
        )

    def mkdir(self, path : str, user : Base):
        if not user.permissions().get("Make", False):
            return "Permission Denied"

        # Split path into directory and folder name components
        directory, folder_name = split(path)

        # Get the starting folder based on the directory path
        if isabs(directory):
            # Absolute path : str, start from root folder
            folder = SYS_MAIN_STORAGE
            directory = directory[1:]  # remove leading "/"
        else:
            # Relative path : str, start from this folder
            folder = self

        # Traverse the folder structure to get to the desired folder
        for dir_name in directory.split('/'):
            if dir_name == '':
                continue
            if dir_name in folder.subFolders:
                folder = folder.subFolders[dir_name]
            else:
                # Folder doesn't exist, create it
                new_folder = Folder(dir_name, folder)
                folder.subFolders[dir_name] = new_folder
                folder = new_folder

        # Check if folder already exists
        if folder_name in folder.subFolders:
            return f"Error: Folder '{folder_name}' already exists"

        # Create the new folder and add it to the parent folder
        new_folder = Folder(folder_name, folder)
        folder.subFolders[folder_name] = new_folder

        return new_folder


    def rmdir(self, path : str, user : Base):
        return (
            self.delete(path, user, Folder)
            if user.permissions().get("Delete", False)
            else "Permission Denied"
        )
        
    def dir(self, path=''):
        if path:
            # Traverse the folder structure to get to the desired folder
            folder = self
            for folder_name in path.split('/'):
                if not folder_name:
                    continue
                if folder_name == '..':
                    folder = folder.parent
                    continue
                if folder_name not in folder.subFolders:
                    return f"Error: Folder '{folder_name}' not found"
                folder = folder.subFolders[folder_name]

            # Call the dir method of the desired folder object
            return folder.dir()

        # No path provided, return the directory listing for this folder
        text = f'{self.foldername if self != SYS_MAIN_STORAGE else "/"}:\n'
        if self.parent is not None:
            text += " + ..\n"
        for folder in self.subFolders.keys():
            text += f" + {folder}" + "\n"
        for file in self.files.keys():
            text += f" - {file}" + "\n"
        return text

    def delete(self, path : str, user : Base, _type  = None):
        # Split path into directory and filename components
        directory, filename = split(path)

        # Check if the folder is in SYS_MAIN_STORAGE and user doesn't have "ADM" perm
        if self == SYS_MAIN_STORAGE and not user.permissions().get('ADM', False) or not user.permissions().get("Delete", False):
            return "Permission Denied"

        #make something here for check if the user is in a subfolder or his user.root

        # Get the folder object based on the directory path
        if isabs(directory):
            # Absolute path : str, start from root folder
            folder = SYS_MAIN_STORAGE
            directory = directory[1:]  # remove leading "/"
        else:
            # Relative path : str, start from this folder
            folder = self

        # Traverse the folder structure to get to the desired folder
        for folder_name in directory.split('/'):
            if folder_name == '':
                continue
            if folder_name in folder.subFolders:
                folder = folder.subFolders[folder_name]
            else:
                return f"Error: Folder '{folder_name}' not found"

        # Delete files or folders that match the wildcard
        deleted_files = []
        deleted_folders = []

        # Create copies of the dictionaries to avoid "dictionary changed size during iteration" error
        files_copy = dict(folder.files)
        subfolders_copy = dict(folder.subFolders)

        if _type is File or not _type:
            for file_name in files_copy:
                if self._match(file_name, filename):
                    del folder.files[file_name]
                    deleted_files.append(file_name)
        if _type is not Folder and _type:
            return f"Invalid type: {type(_type).__class__.__name__}"

        for subfolder_name in subfolders_copy:
            if self._match(subfolder_name, filename):
                del folder.subFolders[subfolder_name]
                deleted_folders.append(subfolder_name)
        if len(deleted_files) == 1 and len(deleted_folders) == 1:
            return f"Deleted file: {deleted_files.pop(0)}. Deleted folder: {deleted_folders.pop(0)}."
        elif len(deleted_files) == 1:
            return f"Deleted file: {deleted_files.pop(0)}."
        elif len(deleted_folders) == 1:
            return f"Deleted folder: {deleted_folders.pop(0)}."
        #//////////////////////////////////////////////
        elif len(deleted_files) > 0 and len(deleted_folders) > 0:
            return f"Deleted files: {', '.join(deleted_files)}. Deleted folders: {', '.join(deleted_folders)}."
        elif len(deleted_files) > 0:
            return f"Deleted files: {', '.join(deleted_files)}."
        elif len(deleted_folders) > 0:
            return f"Deleted folders: {', '.join(deleted_folders)}."
        else:
            return f"No files or folders matching '{filename}' found in '{folder.foldername}'"

    def rename(self, path : str, newname, user : Base):
        if not user.permissions().get("Rename", False):
            return "Permission Denied"

        # Split path into directory and filename components
        directory, filename = split(path)
        # Get the folder object based on the directory path
        if isabs(directory):
            # Absolute path : str, start from root folder
            folder = SYS_MAIN_STORAGE
            directory = directory[1:]  # remove leading "/"
        else:
            # Relative path : str, start from this folder
            folder = self

        # Traverse the folder structure to get to the desired folder
        for folder_name in directory.split('/'):
            if folder_name == '':
                continue
            if folder_name in folder.subFolders:
                folder = folder.subFolders[folder_name]
            else:
                return f"Error: Folder '{folder_name}' not found"

        # Rename the file or folder
        for subfolder_name, subfolder_obj in folder.subFolders.items():
            if subfolder_obj.foldername == filename:
                subfolder_obj.foldername = newname
                folder.subFolders[newname] = subfolder_obj
                del folder.subFolders[filename]
                return f"{filename} renamed to {newname}."

        for file_name, file_obj in folder.files.items():
            if file_obj.filename == filename:
                file_obj.filename = newname
                folder.files[newname] = file_obj
                del folder.files[filename]
                return f"{filename} renamed to {newname}."

        return "Could not rename file or folder. File or folder not found."

        
    def cd(self, path: str):
        if isabs(path):
            # Absolute path
            parts = path.split("/")[1:]
            folder = SYS_MAIN_STORAGE
        else:
            # Relative path
            parts = path.split("/")
            folder = self
            for part in parts:
                if part == "..":
                    if folder.parent is None:
                        break
                    else:
                        folder = folder.parent
                elif part in folder.subFolders:
                    folder = folder.subFolders[part]
                else:
                    return f"Folder {part} not found."
            return folder

        for part in parts:
            if part == "":
                continue
            if part == "..":
                if folder.parent is None:
                    break
                else:
                    folder = folder.parent
            elif part in folder.subFolders:
                folder = folder.subFolders[part]
            else:
                return f"Folder {part} not found."
        return folder

    def to_dict(self, calling_obj=None):
        d = {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
        
        if self.parent != None:
            d["parent"] = self.parent.to_dict(self)
        
        if (childs := self.__dict__.get("subFolders", None)):
            d["subFolders"] = {k:v.to_dict() for k,v in childs.items() if v != calling_obj}

        if (childs := self.__dict__.get("files", None)):
            d["files"] = {k:v.to_dict() for k,v in childs.items() if v != calling_obj}
        return d

    def get_folder_path(self):
        path = self.foldername
        current_folder = self.parent
        while current_folder is not None:
            path = (
                f"{current_folder.foldername}/{path}"
                if current_folder != SYS_MAIN_STORAGE
                else f"/{path}"
            )
            current_folder = current_folder.parent
        return path

    def add_root(self, tree, root_folder):
        tree.append(f"{str(root_folder.foldername)}/")
        tree.append(PIPE)

    def add_body(self, tree, root_folder, prefix=""):
        dir_items = list(root_folder.subFolders.values()) + list(root_folder.files.values())
        dir_items = sorted(dir_items, key=lambda item: isinstance(item, Folder))
        len_diritems = len(dir_items)
        for index, item in enumerate(dir_items):
            connector = ELBOW if index == len_diritems - 1 else TEE
            if isinstance(item, Folder):
                self.generate_directory(
                    tree, item, index, len_diritems, prefix, connector)
            elif isinstance(item, File):
                tree.append(f"{prefix}{connector} {str(item.filename)}")

    def generate_directory(self, tree, folder=None, index=0, len_diritems=0, prefix="", connector=""):
        if not folder:
            folder = self
        tree.append(f"{prefix}{connector} {folder.foldername}/")
        prefix += PIPE_PREFIX if index != len_diritems - 1 else SPACE_PREFIX
        self.add_body(tree, folder, prefix)

    def map(self, path : str = None):
        if not path:
            root_folder = self
        elif path.startswith('/') or path.startswith("C:/"):
            # Absolute path
            path_components = path.split('/')
            root_folder = SYS_MAIN_STORAGE
            for component in path_components[1:]:
                if not component:
                    continue
                if isinstance(root_folder, File):
                    return ("Cannot traverse further, reached a file")
                root_folder = root_folder.subFolders.get(component)
                if not root_folder:
                    return (f"No such folder '{component}'")
        else:
            # Relative path
            path_components = path.split('/')
            root_folder = self
            for component in path_components:
                if not component:
                    continue
                if component == '..':
                    if parent_folder := root_folder.parent:
                        root_folder = parent_folder
                    else:
                        return ("Cannot traverse up, already at root folder")
                else:
                    if isinstance(root_folder, File):
                        return ("Cannot traverse further, reached a file")
                    root_folder = root_folder.subFolders.get(component)
                    if not root_folder:
                        return (f"No such folder '{component}'")

        if not root_folder:
            return ("No such folder")

        tree = []
        self.add_root(tree, root_folder)
        self.add_body(tree, root_folder)
        return "".join(f"{item}\n" for item in tree)
    
    def _match(self, name, pattern):
        if pattern == '*':
            return True
        elif pattern.startswith('*') and pattern.endswith('*'):
            return pattern[1:-1] in name
        elif pattern.startswith('*'):
            return name.endswith(pattern[1:])
        elif pattern.endswith('*'):
            return name.startswith(pattern[:-1])
        else:
            return name == pattern
        
SYS_MAIN_STORAGE : Folder = Folder(foldername="", parent=None)
_folder : Folder = Folder