import itertools
from asyncio import run
from hashlib import sha512
from sys import stderr
from time import sleep
from typing import Any

import file_system
import user_types
import utils

manager : utils.AsyncManager = utils.AsyncManager()

running : bool = True

blue = utils.Convertors(59, 120, 255).terminal_rgb_format
red = utils.Convertors(231, 72, 86).terminal_rgb_format
green = utils.text_formatting.get('colors').get("green1").terminal_rgb_format
white = utils.text_formatting.get('colors').get("white").terminal_rgb_format
default = u"\033[0m"

class Exit(BaseException):
    pass

class _main():
    def __init__(self, *args : list[Any], **kwargs : dict[Any, Any]):
        self.current_user : user_types.Base = None
        self.current_dir : file_system.Folder = None
        self.logged : bool = False
        
    def login(self):
        global blue, red, green, white
        attempts = 0
        while not self.logged:
            
            if attempts > 10:
                print("Too many attempts")
                raise Exit()
            
            username : str = str(input(f"{green}Username {white}> "))
            password : str = str(utils.secure_password_input(f"{red}Password {white}> "))
            password = sha512(password.encode()).hexdigest()

            if username not in user_types.Users:
                attempts += 1
                continue

            if user_types.Users.get(username).permissions() == user_types.Invited(None, None).permissions():
                return self._extracted_from_login_13(username)
            if user_types.Users.get(username).password == password:
                return self._extracted_from_login_13(username)
            attempts += 1

    # TODO Rename this here and in `login`
    def _extracted_from_login_13(self, username):
        self.logged = True
        _user = user_types.Users.get(username)
        self.current_user = _user
        self.current_dir = _user.root
        del _user
        return
            
            
        
    def __call__(self, *args, **kwds):
        global blue, red, green, white
        while running:
            if not self.logged:
                self.login()
            print()
            # Use user variables in the prompt string
            prompt = f"{blue}┌──({red}root💀{self.current_user.name}{blue})-[{white}~{self.current_dir.get_folder_path() if self.current_dir != file_system.SYS_MAIN_STORAGE and not isinstance(self.current_dir, str) else str()}{blue}]\n└─{red}# {white}"

            command : str = str(input(prompt)) 
            self.ProcessCommands(command=command)
            
    def ProcessCommands(self, command: str):
        parts = command.split()
        cmd = parts[0].lower()
        args = parts[1:]

        if cmd == "exit":
            raise Exit()

        elif cmd == "cd":
            path = self.current_dir.cd(self.List2Str(args))
            if isinstance(path, str):
                print(path)
            else:
                self.current_dir = path

        elif cmd == "dir":
            if isinstance(self.current_dir, str):
                print(self.current_dir)
            print(self.current_dir.dir(self.List2Str(args)))

        elif cmd == "mkdir":
            if not args:
                print("Invalid args")
            else:
                result = self.current_dir.mkdir(self.List2Str(args), self.current_user)
                if isinstance(result, str):
                    print(result)
                else:
                    print(f"Folder '{result.foldername}' created in '{result.parent.foldername if result.parent != file_system.SYS_MAIN_STORAGE else '/'}'")

        elif cmd == "rmdir":
            if not args:
                print("Invalid args")
            else:
                result = self.current_dir.rmdir(self.List2Str(args), self.current_user)
                print(result)

        elif cmd == "mkfile":
            if not args:
                print("Invalid args")
            else:
                result = self.current_dir.mkfile(self.List2Str(args), self.current_user)
                print(result)

        elif cmd == "rmfile":
            if not args:
                print("Invalid args")
            else:
                result = self.current_dir.rmfile(self.List2Str(args), self.current_user)
                print(result)

        elif cmd == "rename":
            if not args or len(args) < 2:
                print("Invalid args")
            else:
                result = self.current_dir.rename(args[0], self.List2Str(args[1:]), self.current_user)
                if isinstance(result, str):
                    print(result)

        elif cmd in ["delete", "del"]:
            if not args:
                print("Invalid args")
            else:
                result = self.current_dir.delete(self.List2Str(args), self.current_user, None)
                print(result)

        elif cmd == "open":
            if not args or len(args) <= 1:
                print("Invalid args")
            else:
                mode = args[0]
                filename = args[1]
                data = self.List2Str(args[2:])
                if filename in self.current_dir.files:
                    file = self.current_dir.files.get(filename)
                    print(file.open(mode=mode, data=data, user=self.current_user))
                else:
                    print(f"{filename} was not found.")

        elif cmd == "map":
            path = self.List2Str(args).strip()
            out = self.current_dir.map(path or None)
            print(out)

        elif cmd == "mkuser":
            if not self.current_user.permissions().get("SYS-CONTROL", False):
                print("Permissions denied")
            elif not args or len(args) <= 2:
                print("Invalid args")
            else:
                _type, username, password = args[0], args[1], self.List2Str(args[2:])
                user = user_types.new(name=username, password=password, type=_type)
                if isinstance(user, str):
                    print(user)
                else:
                    print(f"Successfully created {username} as {user.__class__.__name__}")

        elif cmd == "logout":
            while self.logged:
                self.logged = False
            return self.login()

        elif cmd in ["cls", "clear"]:
            print("\033[H\033[J", end="")

        elif cmd == "rainbow":
            try:
                text = self.List2Str(args)
                text = text if text != "" else "Hi! Mr.White"
                while True:
                    for r, g, b in itertools.product(range(256), repeat=3):
                        color = utils.Convertors(r, g, b)
                        print(f"{color.terminal_rgb_format} {text}{utils.text_formatting.get('colors').get('white').terminal_rgb_format} // Color: {color.terminal_rgb_format}rgb{(r, g, b)}      {utils.text_formatting.get('colors').get('white').terminal_rgb_format}", end="\r", flush=True)
            except KeyboardInterrupt:
                print("\n")
                return
            
    def List2Str(self, List: list[str]):
        return "" if not List or all(x.isspace() for x in List) else " ".join(List)

    
    def close(self):
        global running
        running = False
        print("Closing threads, tasks and processes.")
        print(default)
        exit(0)
        
main = _main()  
            
async def main_wrapper():
    global main
    try:
        # create and run main program instance
        manager.new_thread(func=main(), args=None, kwargs=None).run()
    except KeyboardInterrupt or Exit as e:
        pass
    except Exception as e:
        print(f"Exception occurred: {e.args}", file=stderr)
    finally:
        #https://www.twitch.tv/ferxwe
        # always call close function when program terminates
        main.close()

manager.new_thread(func=run, args=run(main_wrapper()), kwargs=None).run()