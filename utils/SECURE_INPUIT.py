from msvcrt import getwche
from sys import stdout


def secure_password_input(prompt=''):
    p_s = ''
    proxy_string = [' ']
    while True:
        stdout.write('\x0D' + prompt + ''.join(proxy_string) + "\b")
        c = getwche()
        if c == '\r':
            break
        elif c == '\x08':
            if p_s:
                p_s = p_s[:-1]
                proxy_string[len(p_s)] = " "
                proxy_string = proxy_string[:-1] if len(proxy_string) > 1 else proxy_string
        elif c == '\x03':  # Ctrl+C
            raise KeyboardInterrupt
        else:
            proxy_string[len(p_s)] = "\u2217"
            proxy_string.append(' ')
            #p_s += c.decode('cp1252', 'ignore')
            p_s += c.decode('utf-8', 'ignore')

    stdout.write('\n')
    print(p_s)
    return p_s

