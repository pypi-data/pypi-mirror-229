import newbie

import os

input = newbie.input
print = newbie.print

def client():
    username = input("Insert your Username: ")
    ip = newbie.docker.create_container(username)
    os.system(f"ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i ~/.ssh/newbie newbie@{ip}")