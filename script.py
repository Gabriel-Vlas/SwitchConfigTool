import paramiko
import telnetlib
import time
import pandas as pd
import os

# Ativar logs do Paramiko para debug
paramiko.util.log_to_file("paramiko_debug.log")

# Caminho do arquivo Excel
xlsx_path = "Arquivo_IP/ips_switch_cisco.xlsx"

# Criar pasta para logs se não existir
log_dir = "Logs_ip"
os.makedirs(log_dir, exist_ok=True)

# Ler IPs do arquivo Excel
try:
    df = pd.read_excel(xlsx_path)
    switches = [{"ip": ip} for ip in df["IP"].dropna().astype(str)]
except Exception as e:
    print(f"❌ Erro ao ler o arquivo Excel: {e}")
    exit()

# Possíveis logins e senhas
credentials = [
    {"username": "admin", "password": "SenhaPrincipal", "enable_password": None},
    {"username": "rhp", "password": "SenhaPrincipal", "enable_password": "@RHOTestSenha"}
]

# Comandos a serem executados
commands = [
    "enable",
    "configure terminal",
    "vtp mode transparent",
    "exit",
    "copy running-config startup-config"
]

# Lista para armazenar IPs com falha na conexão
falhas = []

def connect_ssh(ip, credentials):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    for cred in credentials:
        try:
            client.connect(ip, username=cred["username"], password=cred["password"], timeout=5)
            print(f"✅ Conectado via SSH: {ip}")
            return client, cred["enable_password"]
        except paramiko.AuthenticationException:
            continue
        except Exception as e:
            print(f"❌ Erro SSH em {ip}: {e}")
            return None, None
    print(f"❌ Falha na autenticação SSH: {ip}")
    return None, None

def execute_commands_ssh(client, commands, enable_password, log_file):
    shell = client.invoke_shell()
    time.sleep(1)  
    shell.recv(65535)  
    log_file.write(" Log SSH:\n")
    for cmd in commands:
        shell.send(cmd + "\n")
        time.sleep(2)  
        if cmd.lower() == "enable" and enable_password:
            shell.send(enable_password + "\n")
            time.sleep(2)
    shell.send("\n")
    time.sleep(2)
    output = shell.recv(65535).decode()
    log_file.write(output + "\n")
    print(output)
    client.close()

def connect_telnet(ip, credentials):
    for cred in credentials:
        try:
            tn = telnetlib.Telnet(ip, timeout=5)
            tn.read_until(b"Username:")
            tn.write(cred["username"].encode('ascii') + b"\n")
            tn.read_until(b"Password:")
            tn.write(cred["password"].encode('ascii') + b"\n")
            print(f"✅ Conectado via Telnet: {ip}")
            return tn, cred["enable_password"]
        except Exception as e:
            print(f"❌ Erro Telnet em {ip}: {e}")
            return None, None
    print(f"❌ Falha na autenticação Telnet: {ip}")
    return None, None

def execute_commands_telnet(tn, commands, enable_password, log_file):
    log_file.write(" Log Telnet:\n")
    for cmd in commands:
        tn.write(cmd.encode('ascii') + b"\n")
        time.sleep(2)
        if cmd.lower() == "enable" and enable_password:
            tn.write(enable_password.encode('ascii') + b"\n")
            time.sleep(2)
    tn.write(b"\n")
    time.sleep(2)
    output = tn.read_very_eager().decode()
    log_file.write(output + "\n")
    print(output)
    tn.close()

# Loop pelos switches
for switch in switches:
    ip = switch["ip"]
    log_filename = os.path.join(log_dir, f"log_{ip}.txt")
    with open(log_filename, "w") as log_file:
        client, enable_password = connect_ssh(ip, credentials)
        if client:
            execute_commands_ssh(client, commands, enable_password, log_file)
        else:
            tn, enable_password = connect_telnet(ip, credentials)
            if tn:
                execute_commands_telnet(tn, commands, enable_password, log_file)
            else:
                falhas.append(ip)

# Exibir os IPs que falharam
if falhas:
    print("\n❌ IPs com falha na conexão:")
    for ip in falhas:
        print(f"- {ip}")
else:
    print("\n✅ Todos os switches foram configurados com sucesso!")
