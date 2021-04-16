from subprocess import Popen
import time


class Mpc:
    def __init__(self, length=None):
        self.ids = []
        self.ips = []
        self.ports = []
        self.ip_provider = []
        self.port_provider = []
        if length is None:
            self.length = 4096
        else:
            self.length = length

    def add_player(self, name, ip, port):
        if name != 'provider':
            self.ids.append(len(self.ids))
            self.ips.append(ip)
            self.ports.append(port)
        else:
            self.ip_provider.append(ip)
            self.port_provider.append(port)

    def start(self):
        Popen(['python', '-c', f'import charlie; charlie.main({self.length}, {self.ip_provider}, {self.port_provider},'
                               f' {len(self.ids)})'])
        for i in range(len(self.ids)):
            Popen(['python', '-c', f'import player; player.main({self.ids[i]}, {self.length}, {self.ip_provider},'
                                   f' {self.port_provider}, {self.ips}, {self.ports})'])

        time.sleep(2)
        Popen(['python', '-c', f'import client; client.main({self.ips}, {self.ports})'])






