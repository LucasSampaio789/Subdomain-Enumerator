import sys
import dns.resolver
import json
import concurrent.futures
from datetime import datetime

resolver = dns.resolver.Resolver()

def wordlist_padrao():
    return ["www", "mail", "ftp", "admin", "portal", "api", "blog", "webmail", "dev"]

def resolver_subdominio(subdominio, alvo, resultados):
    try:
        sub_alvo = f"{subdominio}.{alvo}"
        respostas = resolver.resolve(sub_alvo, "A")
        ips = [r.to_text() for r in respostas]
        resultados.append({"subdominio": sub_alvo, "ips": ips})
        print(f"[+] {sub_alvo} -> {', '.join(ips)}")
    except:
        pass

def gerar_relatorio_html(resultados, nome_arquivo="relatorio.html"):
    with open(nome_arquivo, "w") as f:
        f.write("<html><head><title>Relatório DNS Brute Force</title></head><body>")
        f.write("<h1>Relatório DNS Brute Force</h1>")
        f.write(f"<p>Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>")
        f.write("<table border='1'><tr><th>Subdomínio</th><th>IP</th></tr>")
        for resultado in resultados:
            for ip in resultado["ips"]:
                f.write(f"<tr><td>{resultado['subdominio']}</td><td>{ip}</td></tr>")
        f.write("</table></body></html>")
    print(f"[+] Relatório salvo em {nome_arquivo}")

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 dnsbrute.py <dominio> [lista_de_subdominios]")
        sys.exit()
    
    alvo = sys.argv[1]
    wordlist = sys.argv[2] if len(sys.argv) > 2 else None
    
        if wordlist:
        try:
            with open(wordlist, "r") as arq:
                subdominios = arq.read().splitlines()
        except:
            print("Erro ao abrir o arquivo de wordlist")
            sys.exit()
    else:
        subdominios = wordlist_padrao()
        print("[!] Usando wordlist interna")
    
    resultados = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(resolver_subdominio, sub, alvo, resultados) for sub in subdominios]
        concurrent.futures.wait(futures)
    
    with open("resultados.json", "w") as json_file:
        json.dump(resultados, json_file, indent=4)
    print("[+] Resultados salvos em resultados.json")
    
    gerar_relatorio_html(resultados)

if __name__ == "__main__":
    main()
