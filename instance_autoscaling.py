from cpu_utilization import get_cpu_usage
import requests
import time

# -----------------------------
# Keystone Authentication
# -----------------------------
def get_token():
    url = "http://10.224.76.78/identity/v3/auth/tokens"
    payload = {
        "auth": {
            "identity": {
                "methods": ["password"],
                "password": {
                    "user": {
                        "name": "admin",
                        "domain": {"id": "default"},
                        "password": "pranav"
                    }
                }
            },
            "scope": {
                "project": {
                    "name": "admin",
                    "domain": {"id": "default"}
                }
            }
        }
    }

    r = requests.post(url, json=payload)
    return r.headers["X-Subject-Token"]


# -----------------------------
# Nova API – Create Instance
# -----------------------------
def create_instance(token):
    nova_url = "http://10.224.76.78/compute/v2.1/servers"

    server_data = {
        "server": {
            "name": "autoscale-vm",
            "imageRef": "2caa938d-243a-42e8-a454-6e8b894af38a",
            "flavorRef": "84",
            "networks": [{"uuid": "38cf01ad-82d7-477c-b115-b5a8231c7354"}]
        }
    }

    headers = {
        "X-Auth-Token": token,
        "Content-Type": "application/json"
    }

    r = requests.post(nova_url, json=server_data, headers=headers)
    print("Nova API response:", r.json())


def get_instance_count(token):
    url = "http://10.224.76.78/compute/v2.1/servers/detail"
    headers = {"X-Auth-Token": token}

    r = requests.get(url, headers=headers)
    data = r.json()

    # Count ACTIVE instances only
    active = [s for s in data["servers"] if s["status"] == "ACTIVE"]
    return len(active)



# -----------------------------
# Autoscaling Loop
# -----------------------------
MAX_SIZE = 4
INCREMENT = 1
EVALUATION_PERIOD = 40
THRESHOLD = 20

host = "172.24.4.205"
username = "cirros"
password = "pranav@123"

while True:
    usage = get_cpu_usage(host, username, password=password)
    print(f"CPU: {usage:.2f}%")

    if usage >= THRESHOLD:
        print("High utilization detected")

        token = get_token()
        current = get_instance_count(token)

        print(f"Current instance count: {current}")

        if current < MAX_SIZE:
            print("Scaling out by 1 instance...")
            create_instance(token)
        else:
            print("Max scaling size reached — no new instances created")
    else:
        print("CPU normal")

    time.sleep(EVALUATION_PERIOD)

