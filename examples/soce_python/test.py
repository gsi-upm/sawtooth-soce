import subprocess


subprocess.call("mkdir /root/.sawtooth", shell=True)
subprocess.call("mkdir /root/.sawtooth/keys/", shell=True)
subprocess.call("echo '68566D5970337336763979244226452948404D635166546A576E5A7234743777' > /root/.sawtooth/keys/root.priv", shell=True)
subprocess.call("soce create 'test1' --url http://rest-api:8008", shell=True)
subprocess.call("python3 setup.py build", shell=True)
subprocess.call("soce-tp-python -vv -C tcp://validator:4004", shell=True)