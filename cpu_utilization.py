import paramiko
import time
import requests

def get_cpu_usage(host, username, key_file=None, password=None):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    client.connect(
        hostname=host,
        username=username,
        key_filename=key_file,
        password=password,
        look_for_keys=False
    )

    def read_proc_stat():
        stdin, stdout, stderr = client.exec_command("cat /proc/stat | head -1")
        line = stdout.read().decode().strip()
        parts = line.split()[1:]
        return list(map(int, parts))

    stat1 = read_proc_stat()
    time.sleep(1)
    stat2 = read_proc_stat()

    deltas = [s2 - s1 for s1, s2 in zip(stat1, stat2)]
    idle = deltas[3]
    total = sum(deltas)

    cpu_usage = 100 * (1 - idle / total)

    client.close()
    return cpu_usage


if __name__ == "__main__":
    host = "172.24.4.205"
    username = "cirros"
    password = "pranav@123"

    while True:
        usage = get_cpu_usage(host, username, password=password)
        print(f"CPU: {usage:.2f}%")

        if usage >= 20:
            print("high util")
        else:
            print("low util")

        time.sleep(10)