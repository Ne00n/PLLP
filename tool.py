from Class.tools import Tools
import subprocess, sys, re

start = sys.argv[1]
target = sys.argv[2]

start = subprocess.check_output(['dig','ANY','+short',start]).decode("utf-8").strip()
target = subprocess.check_output(['dig','ANY','+short',target]).decode("utf-8").strip()

print(f"Testing from {start} to {target}")
print(f"Generating keys")
keys = Tools.cmd(start,'key=$(wg genkey) && echo $key && echo $key | wg pubkey')[0]
serverPrivate, serverPublic = keys.splitlines()

keys = Tools.cmd(target,'key=$(wg genkey) && echo $key && echo $key | wg pubkey')[0]
clientPrivate, clientPublic = keys.splitlines()

latency = {}
for port in range(1000,55000,1000):
    print(f"Testing on Port {port}")
    #Stopping wireguard
    Tools.cmd(start,f'systemctl stop wg-quick@PLLP')
    Tools.cmd(target,f'systemctl stop wg-quick@PLLP')
    #Generate Server config
    serverConfig = Tools.genServer(serverPrivate.rstrip(),clientPublic.rstrip(),port)
    #Deploying Server config
    Tools.cmd(start,f'echo "{serverConfig}" > /etc/wireguard/PLLP.conf && systemctl start wg-quick@PLLP')
    #Generating Client config
    clientConfig = Tools.genClient(clientPrivate.rstrip(),serverPublic.rstrip(),port,start)
    #Deploying Client config
    Tools.cmd(target,f'echo "{clientConfig}" > /etc/wireguard/PLLP.conf && systemctl start wg-quick@PLLP')
    #Running fping
    fping = Tools.cmd(target,f'fping -c10 172.16.1.0')[0]
    parsed = re.findall("([0-9.]+).*?([0-9]+.[0-9]).*?([0-9])% loss",fping, re.MULTILINE)
    latency =  {}
    for ip,ms,loss in parsed:
        if port not in latency: latency[port] = []
        latency[port].append(ms)
    #drop first ping result
    del latency[port][0]
    latency[port].sort()
    avg = Tools.getAvrg(latency[port])
    print(f"Got {avg}ms")
    #Stopping wireguard
    Tools.cmd(start,f'systemctl stop wg-quick@PLLP')
    Tools.cmd(target,f'systemctl stop wg-quick@PLLP')
#Removing wireguard files
Tools.cmd(start,f'rm /etc/wireguard/PLLP.conf')
Tools.cmd(target,f'rm /etc/wireguard/PLLP.conf')