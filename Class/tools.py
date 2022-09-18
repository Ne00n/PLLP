import subprocess, random, time

class Tools():

    @staticmethod
    def cmd(server,command,runs=4):
        cmd = ['ssh','root@'+server,command]
        for run in range(runs):
            try:
                p = subprocess.run(cmd, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
                if p.returncode != 0:
                    print("Warning got returncode",p.returncode,"on",server)
                    print("Error:",p.stderr.decode('utf-8'))
                if p.returncode != 255: return [p.stdout.decode('utf-8'),p.stderr.decode('utf-8')]
            except Exception as e:
                print("Error:",e)
            print("Retrying",cmd,"on",server)
            time.sleep(random.randint(5, 15))
        exit()

    @staticmethod
    def getAvrg(list):
        result = 0
        for ms in list:
            result += float(ms)
        return round(float(result / len(list)),2)

    @staticmethod
    def genServer(privateKey,publicKey,port):
        template = f'''[Interface]
        Address = 172.16.1.0/31
        ListenPort = {port}
        PrivateKey = {privateKey}
        SaveConfig = false
        Table = off
        [Peer]
        PublicKey = {publicKey}
        AllowedIPs = 0.0.0.0/0'''
        return template

    @staticmethod
    def genClient(privateKey,publicKey,port,ip):
        ip = f"[{ip}]" if ":" in ip else ip
        template = f'''[Interface]
        Address = 172.16.1.1/31
        PrivateKey = {privateKey}
        SaveConfig = false
        Table = off
        [Peer]
        PublicKey = {publicKey}
        AllowedIPs = 0.0.0.0/0
        Endpoint = {ip}:{port}'''
        return template