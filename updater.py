import json
import os
import socket
import time
import pysftp as sftp

from ssh2.session import Session

# host = ''
# user = ''
# password = ''

with open('servinfo.json', 'r') as file:
    data = json.load(file)
    host = data['host']
    user = data['user']
    password = data['password']


def put_r_portable(sftp, localdir, remotedir, preserve_mtime=False):
    for entry in os.listdir(localdir):
        remotepath = remotedir + "/" + entry
        localpath = os.path.join(localdir, entry)
        if not os.path.isfile(localpath):
            try:
                sftp.mkdir(remotepath)
            except OSError:
                pass
            put_r_portable(sftp, localpath, remotepath, preserve_mtime)
        else:
            sftp.put(localpath, remotepath, preserve_mtime=preserve_mtime)


def upload_files():
    print("Starting upload...")
    directories = ['cogs', 'resources', 'util']
    files = ["bot.py", "extensions.py"]
    cnopts = sftp.CnOpts()
    cnopts.hostkeys = None

    with sftp.Connection(host=host, username=user, password=password, cnopts=cnopts) as s:
        print("Established SFTP connection")
        for dir in directories:
            print(f"Uploading: {dir}")
            remote_path = f'/home/mark/tidalbot_python/{dir}'
            # local_path = 'testdir'
            with s.cd(remote_path):
                put_r_portable(s, dir, remote_path, preserve_mtime=False)
                for f in files:
                    print(f"Uploading: {f}")
                    s.put(f, f"/home/mark/tidalbot_python/{f}", preserve_mtime=False)
                print(f"Upload complete: {dir}")
    print("All uploads complete")
    s.close()
    print("Closed SFTP connection")


def connect_and_start():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, 22))
    print("Connected to socket")

    session = Session()
    session.handshake(sock)
    session.userauth_password(user, password)

    channel = session.open_session()
    print("Session opened")

    channel.shell()

    channel.write('cd tidalbot_python\n')
    # channel.write('ls\n')
    channel.write('nohup /usr/bin/python3.7 bot.py &')

    print("Commands executed")
    time.sleep(1)

    # size, data = channel.read()
    # print(data.decode())

    channel.close()
    print(f'Exit status: {channel.get_exit_status()}')


upload_files()
print("------")
connect_and_start()
