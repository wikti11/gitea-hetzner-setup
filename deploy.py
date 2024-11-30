from hcloud import Client
from hcloud.images.domain import Image
from hcloud.server_types.domain import ServerType
from hcloud.networks.domain import NetworkSubnet
from hcloud.locations.domain import Location
from hcloud.volumes.domain import Volume

# reading cloud-inits
def load_cloud_init(file_name):
    with open(file_name, 'r') as file:
        return file.read()


DB_INIT_FILE = "db-init.yaml"
GITEA_INIT_FILE = "gitea-init.yaml"

cloud_init_db = load_cloud_init(DB_INIT_FILE)
cloud_init_gitea = load_cloud_init(GITEA_INIT_FILE)

# client
client = Client(token="insert_client_api_token_here")
PREFIX = "wikles"

# ssh creation
YOUR_LOCAL_SSH_PUBKEY = "insert_ssh_key_here"
ssh_key_name = f"{PREFIX}-ssh-key"
existing_ssh_key = client.ssh_keys.get_by_name(ssh_key_name)

if existing_ssh_key:
    ssh_key = existing_ssh_key
    print(f"Używany istniejący klucz SSH: {ssh_key.data_model.name}")
else:
    ssh_key = client.ssh_keys.create(name=ssh_key_name, public_key=YOUR_LOCAL_SSH_PUBKEY)
    print(f"Klucz {ssh_key.data_model.name} został dodany: {ssh_key.data_model.public_key}")

# private network
vnet = client.networks.create(
    name=f"{PREFIX}-vnet", 
    ip_range="10.20.0.0/16", 
    subnets=[
        NetworkSubnet(ip_range="10.20.0.0/24", network_zone="eu-central", type="cloud")
    ]
)
print(f"Utworzono sieć wirtualną {vnet.data_model.name} ({vnet.data_model.ip_range})")

# db config
db_server = client.servers.create(
    name=f"{PREFIX}-db",
    server_type=ServerType("cpx11"),
    image=Image(name="ubuntu-22.04"),
    ssh_keys=[ssh_key],
    networks=[vnet],
    location=Location("hel1"),
    user_data=cloud_init_db
)

db_server.action.wait_until_finished()
print(f"Tworzenie serwera bazy danych: {db_server.action.complete}")

db_server = client.servers.get_by_name(f"{PREFIX}-db")
print(f"Serwer db: {db_server.data_model.name}\n\tpubliczne IP: {db_server.data_model.public_net.ipv4.ip}\n\tprywatne IP: {db_server.data_model.private_net[0].ip}")

# wolumen
gitea_volume = client.volumes.create(
    name=f"{PREFIX}-data",
    size=10,
    location=Location("hel1")
).volume

# gitea
gitea_server = client.servers.create(
    name=f"{PREFIX}-gitea",
    server_type=ServerType("cpx11"),
    image=Image(name="ubuntu-22.04"),
    ssh_keys=[ssh_key],
    networks=[vnet],
    location=Location("hel1"),
    volumes=[gitea_volume],
    user_data=cloud_init_gitea
)

gitea_server.action.wait_until_finished()
print(f"Tworzenie serwera Gitea: {gitea_server.action.complete}")

gitea_server = client.servers.get_by_name(f"{PREFIX}-gitea")
print(f"Serwer Gitea: {gitea_server.data_model.name}\n\tpubliczne IP: {gitea_server.data_model.public_net.ipv4.ip}\n\tprywatne IP: {gitea_server.data_model.private_net[0].ip}")
