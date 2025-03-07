import paramiko
import networkx as nx
import matplotlib.pyplot as plt

# Lista de switches com IPs e múltiplas credenciais
switches = [
    {"ip": "10.5.255.1", "credentials": [{"username": "rhpadmin", "password": "Pxp#@!SrwR1U3g"}, {"username": "rhp", "password": "rhpcpd2014"}]}
    # Adicione mais switches aqui
]
def get_cdp_neighbors(ip, credentials):
    """Obtém vizinhos CDP do switch Cisco tentando múltiplas credenciais, incluindo portas de conexão."""
    for creds in credentials:
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(ip, username=creds["username"], password=creds["password"], timeout=5)
            
            stdin, stdout, stderr = client.exec_command("show cdp neighbors detail")
            output = stdout.read().decode()
            client.close()
            
            neighbors = []
            neighbor = {}
            for line in output.split("\n"):
                if "Device ID:" in line:
                    if neighbor:
                        neighbors.append(neighbor)  # Adiciona o vizinho anterior antes de criar o novo
                    neighbor = {"device": line.split(": ")[1], "local_interface": "", "remote_interface": "", "remote_ip": ""}
                if "IP address:" in line:
                    neighbor["remote_ip"] = line.split(": ")[1]
                if "Interface:" in line and "Port ID (outgoing port):" in line:
                    neighbor["local_interface"] = line.split(": ")[1].strip()
                    neighbor["remote_interface"] = line.split(": ")[2].strip()
            
            if neighbor:
                neighbors.append(neighbor)  # Adiciona o último vizinho
            return neighbors
        except Exception as e:
            print(f"Erro ao conectar em {ip} com {creds['username']}: {e}")
    
    print(f"Falha em todas as tentativas de conexão com {ip}")
    return []

# Criando a topologia da rede
topology = nx.Graph()

to_scan = set(switch["ip"] for switch in switches)  # Lista de IPs a escanear
scanned = set()  # Lista de IPs já escaneados

while to_scan:
    current_ip = to_scan.pop()
    if current_ip in scanned:
        continue  # Pula se já foi escaneado

    switch_info = next((s for s in switches if s["ip"] == current_ip), None)
    if switch_info:
        neighbors = get_cdp_neighbors(switch_info["ip"], switch_info["credentials"])
        for neighbor in neighbors:
            if neighbor["remote_ip"]:
                topology.add_edge(
                    current_ip, neighbor["remote_ip"], 
                    label=f"{neighbor['local_interface']} -> {neighbor['remote_interface']}"
                )
                
                # Se ainda não escaneamos este switch, adicionamos para futura varredura
                if neighbor["remote_ip"] not in scanned and neighbor["remote_ip"] not in to_scan:
                    to_scan.add(neighbor["remote_ip"])
                    # Adicionamos o novo switch à lista, assumindo mesmas credenciais iniciais
                    switches.append({"ip": neighbor["remote_ip"], "credentials": switch_info["credentials"]})

    scanned.add(current_ip)

# Desenhando a topologia com as portas
plt.figure(figsize=(12, 10))
pos = nx.spring_layout(topology)  # Layout da topologia
nx.draw(topology, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=3000, font_size=10)
labels = nx.get_edge_attributes(topology, 'label')
nx.draw_networkx_edge_labels(topology, pos, edge_labels=labels, font_size=8)

plt.title("Topologia da Rede com Portas de Conexão")
plt.show()