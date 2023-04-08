from msvcrt import getch
from sys import stdout


def secure_password_input(prompt=''):
    p_s = ''
    proxy_string = [' ']
    while True:
        stdout.write('\x0D' + prompt + ''.join(proxy_string) + "\b")
        c = getch()
        if c == b'\r':
            break
        elif c == b'\x08':
            if p_s:
                p_s = p_s[:-1]
                proxy_string[len(p_s)] = " "
                proxy_string = proxy_string[:-1] if len(proxy_string) > 1 else proxy_string
        elif c == b'\x03':  # Ctrl+C
            raise KeyboardInterrupt
        else:
            if c.decode('cp1252', 'ignore') in 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNMñÑ1234567890´¨~!@#$%^&*()_+-={}[]|\\:;"\'<>,.?/¡¿':
                proxy_string[len(p_s)] = "\u2217"
                proxy_string.append(' ')
                p_s += c.decode('cp1252', 'ignore')

    stdout.write('\n')
    return p_s

