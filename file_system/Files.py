from io import BytesIO

# # TODO: Just for avoid circular import and be able to use code recommendations
class Base(object):
    def __init__(self):
        self.type = self.__class__.__name__
        self.root = None
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

class File(object):
    def __init__(self, filename : str, parent):
        self.filename : str = filename
        self.parent = parent
        self.file : BytesIO = BytesIO(bytes("", encoding="utf-8"))

    def open(self, mode : str,  user : Base, data = None) -> str or int:
        """
        mode:
          -r: read
          -w: write
          -c: clear

        data is only used when mode is w
        open(mode : str, data : str, user : User) -> str
        """
        def read():
            if not user.permissions().get('Read', False):
                return "Permission denied"
            try:
                self.file.seek(0)
                return str(self.file.read().decode("utf-8"))
            except Exception:
                return "Error reading file"

        def write(data : str) -> str:
            if not data:
                return "Invalid data"
            if user.permissions().get('Write', False):
                self.file.seek(0, 2)
                self.file.write(f"{data}\n".encode("utf-8"))
                self.file.flush()
                return "Success"
            else: 
                return "Permission Denied"

        def clear():
            if user.permissions().get('Delete', False) == True:
                self.file = BytesIO(bytes("", encoding="utf-8"))
                return "Success"
            else: return "Permission Denied"

        if mode.upper() in {"R", "-R"}: return read()
        elif mode.upper() in {"W", "-W"}: return write(data=data)
        elif mode.upper() in {"C", "-C"}: return clear()
        else: return (f"Invalid mode:{mode}")


    def to_dict(self):
        return {
            "filename": self.filename,
            "file": self.file.decode("utf-8"),
            "parent": self.parent.to_dict()
        }

