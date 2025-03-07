# Configuração Automática de Switches Cisco via SSH/Telnet

Este script automatiza a configuração de switches Cisco utilizando conexões SSH e Telnet. Ele lê uma lista de IPs a partir de um arquivo Excel, tenta conectar-se aos dispositivos utilizando credenciais predefinidas e executa um conjunto de comandos para configurar os switches.

## Funcionalidades
- Conexão via **SSH** (preferencialmente) ou **Telnet** (caso SSH falhe).
- Execução automática de comandos em cada switch.
- Geração de logs individuais para cada IP na pasta `Logs_ip`.
- Suporte para múltiplas credenciais de acesso.

## Requisitos

Antes de executar o script, certifique-se de ter os seguintes itens instalados:

- **Python 3.x**
- Bibliotecas necessárias (instale com o comando abaixo):

```sh
pip install paramiko pandas openpyxl
```

## Como Usar

1. **Prepare o arquivo de IPs**
   - O script lê os IPs dos switches a partir de um arquivo **Excel** localizado em `Arquivo_IP/ips_switch_cisco.xlsx`.
   - O arquivo deve ter uma estrutura simples, com uma coluna chamada `IP`, contendo os endereços dos switches.

2. **Configuração das Credenciais**
   - Dentro do script, as credenciais para login nos switches estão definidas na lista `credentials`.
   - Modifique os valores conforme suas credenciais de acesso aos switches.

3. **Executando o Script**
   - No terminal, execute:

   ```sh
   python script.py
   ```

4. **Verificando os Logs**
   - Cada switch terá um arquivo de log gerado na pasta `Logs_ip`, nomeado como `log_<IP>.txt`.
   - Se um switch falhar na conexão, seu IP será listado no final da execução.

## Estrutura do Projeto
```
/
|-- script.py  # Script principal
|-- Arquivo_IP/
|   |-- ips_switch_cisco.xlsx  # Lista de IPs
|-- Logs_ip/  # Pasta onde os logs serão armazenados
```

## Observações
- O script primeiro tenta SSH e, se falhar, usa Telnet.
- Caso um IP falhe em ambas as conexões, ele será registrado na lista de falhas.
- Modifique os comandos na lista `commands` dentro do script para personalizar a configuração aplicada.

---
Feito para facilitar a automação de configuração em redes Cisco! 🚀


