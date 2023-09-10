import newbie

import os

print = newbie.print

def create_container(username: str) -> None:
    container_name = username
    ip = _create(container_name)
    return ip

def _exists(container_name: str) -> bool:
    if os.system(f"docker ps -a --filter name=newbie_{container_name} --format {{.Names}}") == 0:
        return True
    else:
        return False

def _create(container_name: str) -> str:
    if _exists(container_name):
        print(f"Container {container_name} already exists.")
        return
    
    command = f"docker run -d --name newbie_{container_name} -e NEWBIE_AUTHORIZED_KEYS=\"$NEWBIE_AUTHORIZED_KEYS\" -e NEWBIE_USERNAME={container_name} tklco/sparcs-newbie-2023f-linux"
    os.system(command)

    ip = _get_ip(container_name)
    print(f"Container {container_name} created. IP: {ip}")

    return 

def _get_ip(container_name: str) -> str:
    command = f"docker inspect newbie_{container_name} --format {{.NetworkSettings.IPAddress}}"
    return os.popen(command).read().strip()

def _delete(container_name: str) -> None:
    if not _exists(container_name):
        print(f"Container {container_name} does not exist.")
        return
    
    command = f"docker rm -f newbie_{container_name}"
    os.system(command)