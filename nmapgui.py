#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NmapGUI - Une interface CLI simple et colorée pour nmap, façon "Zenmap" en terminal.
Compatible Linux (Debian/Ubuntu, Fedora, Arch, etc.)

Auteur: Claude (Anthropic) pour Antoine
Licence: MIT
"""

import os
import re
import sys
import shutil
import socket
import subprocess
import datetime

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.prompt import Prompt, Confirm
    from rich.text import Text
    from rich.align import Align
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich import box
except ImportError:
    print("Le module 'rich' n'est pas installé.")
    print("Lance d'abord install.sh, ou tape: pip install rich")
    sys.exit(1)

console = Console()

# ---------------------------------------------------------------------------
# Configuration des scans proposés dans le menu
# ---------------------------------------------------------------------------
SCANS = {
    "1": {
        "nom": "Scan rapide",
        "desc": "Ping + ports les plus courants (rapide, idéal pour débuter)",
        "args": ["-T4", "-F"],
        "root": False,
    },
    "2": {
        "nom": "Découverte du réseau (ping scan)",
        "desc": "Trouve juste les appareils allumés sur le réseau, sans scanner les ports",
        "args": ["-sn"],
        "root": False,
    },
    "3": {
        "nom": "Scan de services (versions)",
        "desc": "Détecte les logiciels/versions qui tournent sur les ports ouverts",
        "args": ["-sV", "--top-ports", "100", "-T4"],
        "root": False,
    },
    "4": {
        "nom": "Scan complet (tous les ports)",
        "desc": "Scanne les 65535 ports. Beaucoup plus long !",
        "args": ["-p-", "-T4"],
        "root": False,
    },
    "5": {
        "nom": "Détection du système d'exploitation",
        "desc": "Essaie de deviner l'OS de la cible (nécessite souvent root)",
        "args": ["-O"],
        "root": True,
    },
    "6": {
        "nom": "Scan furtif SYN",
        "desc": "Scan discret, plus difficile à détecter (nécessite root)",
        "args": ["-sS"],
        "root": True,
    },
    "7": {
        "nom": "Scan agressif complet",
        "desc": "OS + versions + scripts + traceroute. Très complet, plus lent",
        "args": ["-A", "-T4"],
        "root": True,
    },
    "8": {
        "nom": "Scan personnalisé",
        "desc": "Tu écris toi-même les options nmap",
        "args": None,
        "root": False,
    },
}

BANNER = r"""
[bold cyan]
 ███╗   ██╗███╗   ███╗ █████╗ ██████╗      ██████╗ ██╗   ██╗██╗
 ████╗  ██║████╗ ████║██╔══██╗██╔══██╗    ██╔════╝ ██║   ██║██║
 ██╔██╗ ██║██╔████╔██║███████║██████╔╝    ██║  ███╗██║   ██║██║
 ██║╚██╗██║██║╚██╔╝██║██╔══██║██╔═══╝     ██║   ██║██║   ██║██║
 ██║ ╚████║██║ ╚═╝ ██║██║  ██║██║         ╚██████╔╝╚██████╔╝██║
 ╚═╝  ╚═══╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝          ╚═════╝  ╚═════╝ ╚═╝
[/bold cyan]
[dim]       l'interface simple pour scanner un réseau, comme Zenmap mais en CLI[/dim]
"""

IP_REGEX = re.compile(
    r"^(25[0-5]|2[0-4]\d|1?\d?\d)(\.(25[0-5]|2[0-4]\d|1?\d?\d)){3}(/\d{1,2})?$"
)


def clear():
    os.system("clear" if os.name != "nt" else "cls")


def obtenir_ip_locale() -> str:
    """Récupère la vraie IP locale de l'appareil (celle du réseau WiFi/mobile), sans root."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        # Astuce: pas besoin que 8.8.8.8 soit joignable, connect() en UDP
        # ne fait pas de vrai échange réseau, ça choisit juste l'interface de sortie
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return ""


def obtenir_reseau_local():
    """Déduit l'IP locale, la passerelle probable (.1) et le sous-réseau /24 associé."""
    ip = obtenir_ip_locale()
    if not ip or ip.startswith("127."):
        return None
    morceaux = ip.split(".")
    if len(morceaux) != 4:
        return None
    sous_reseau = f"{morceaux[0]}.{morceaux[1]}.{morceaux[2]}.0/24"
    passerelle_probable = f"{morceaux[0]}.{morceaux[1]}.{morceaux[2]}.1"
    return {
        "ip_locale": ip,
        "sous_reseau": sous_reseau,
        "passerelle": passerelle_probable,
    }


def check_nmap_installed() -> bool:
    return shutil.which("nmap") is not None


def is_root() -> bool:
    try:
        return os.geteuid() == 0
    except AttributeError:
        return False


def afficher_banniere():
    clear()
    console.print(Align.center(Text.from_markup(BANNER)))


def afficher_menu():
    table = Table(
        show_header=True,
        header_style="bold white on dark_green",
        box=box.ROUNDED,
        border_style="green",
        expand=True,
    )
    table.add_column("N°", justify="center", style="bold yellow", width=4)
    table.add_column("Type de scan", style="bold cyan")
    table.add_column("Description", style="white")
    table.add_column("Root", justify="center", width=6)

    for cle, scan in SCANS.items():
        root_tag = "[red]oui[/red]" if scan["root"] else "[green]non[/green]"
        table.add_row(cle, scan["nom"], scan["desc"], root_tag)

    console.print(table)
    console.print(
        Panel(
            "[bold]0[/bold] : Quitter    |    [bold]H[/bold] : Aide",
            style="dim",
            box=box.MINIMAL,
        )
    )


def valider_cible(cible: str) -> bool:
    """Validation très permissive : accepte IP, plage CIDR, ou nom d'hôte/domaine."""
    cible = cible.strip()
    if not cible:
        return False
    if IP_REGEX.match(cible):
        return True
    # nom de domaine ou hostname simple (lettres, chiffres, points, tirets)
    hostname_regex = re.compile(r"^[a-zA-Z0-9](?:[a-zA-Z0-9\-\.]{0,253})[a-zA-Z0-9]$")
    return bool(hostname_regex.match(cible))


def choisir_cible() -> str:
    console.print()
    reseau = obtenir_reseau_local()

    if reseau:
        console.print(
            Panel(
                f"[bold]Ton téléphone est actuellement sur ce réseau :[/bold]\n"
                f"  📱 Ton IP           : [bold green]{reseau['ip_locale']}[/bold green]\n"
                f"  📡 Passerelle probable (box/routeur) : [bold cyan]{reseau['passerelle']}[/bold cyan]\n"
                f"  🌐 Tout le réseau local          : [bold magenta]{reseau['sous_reseau']}[/bold magenta]\n\n"
                "[yellow]Astuce :[/yellow] entre directement l'une de ces valeurs pour scanner "
                "ta box ou tout ton réseau local !\n\n"
                "Autres exemples valides :\n"
                "  • [cyan]scanme.nmap.org[/cyan]  (cible de test officielle de nmap, autorisée publiquement)",
                title="[bold]Quelle cible scanner ?[/bold]",
                border_style="blue",
            )
        )
    else:
        console.print(
            Panel(
                "Exemples valides :\n"
                "  • [cyan]192.168.1.1[/cyan]           (une seule machine)\n"
                "  • [cyan]192.168.1.0/24[/cyan]        (tout le réseau local)\n"
                "  • [cyan]scanme.nmap.org[/cyan]       (un nom de domaine)\n\n"
                "[dim](Impossible de détecter ton IP locale automatiquement, "
                "vérifie que le WiFi/données sont activés)[/dim]",
                title="[bold]Quelle cible scanner ?[/bold]",
                border_style="blue",
            )
        )

    while True:
        if reseau:
            cible = Prompt.ask(
                "[bold cyan]➤ Entre une adresse IP, un réseau ou un nom d'hôte[/bold cyan]",
                default=reseau["sous_reseau"],
            )
        else:
            cible = Prompt.ask("[bold cyan]➤ Entre une adresse IP, un réseau ou un nom d'hôte[/bold cyan]")
        if valider_cible(cible):
            return cible.strip()
        console.print("[bold red]✗ Format invalide, réessaie (ex: 192.168.1.1)[/bold red]")


def colorer_ligne(ligne: str) -> str:
    """Colore intelligemment une ligne de sortie nmap pour la rendre plus lisible."""
    l = ligne

    if re.search(r"\bopen\b", l):
        return f"[bold green]{l}[/bold green]"
    if re.search(r"\bclosed\b", l):
        return f"[dim red]{l}[/dim red]"
    if re.search(r"\bfiltered\b", l):
        return f"[yellow]{l}[/yellow]"
    if l.strip().startswith("PORT"):
        return f"[bold white on blue]{l}[/bold white on blue]"
    if "Nmap scan report" in l:
        return f"[bold magenta]{l}[/bold magenta]"
    if "Host is up" in l:
        return f"[bold green]{l}[/bold green]"
    if "MAC Address" in l:
        return f"[cyan]{l}[/cyan]"
    if "OS details" in l or "Running:" in l or "OS CPE" in l:
        return f"[bold blue]{l}[/bold blue]"
    if "Service Info" in l:
        return f"[cyan]{l}[/cyan]"
    if l.strip().startswith("Nmap done"):
        return f"[bold white on dark_green]{l}[/bold white on dark_green]"
    if "Starting Nmap" in l:
        return f"[dim]{l}[/dim]"
    return l


def lancer_scan(args: list, cible: str):
    cmd = ["nmap"] + args + [cible]
    cmd_str = " ".join(cmd)

    console.print()
    console.print(Panel(f"[bold]{cmd_str}[/bold]", title="Commande exécutée", border_style="magenta"))
    console.print()

    lignes_resultat = []

    try:
        with console.status("[bold green]Scan en cours... (ça peut prendre un moment)[/bold green]", spinner="dots"):
            processus = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
            )
            # On lit en direct pour ne pas rester bloqué sans retour visuel
            sortie_brute = []
            for ligne in processus.stdout:
                sortie_brute.append(ligne.rstrip("\n"))
            processus.wait()

        for ligne in sortie_brute:
            lignes_resultat.append(ligne)
            console.print(colorer_ligne(ligne))

        if processus.returncode != 0:
            console.print()
            console.print(
                Panel(
                    "[bold red]Le scan a rencontré un problème.[/bold red]\n"
                    "Vérifie que la cible est joignable, ou que nmap est bien installé.\n"
                    "Si tu utilises une option qui demande 'root' (comme -sS ou -O) "
                    "et que ton téléphone n'est pas rooté, utilise plutôt un scan "
                    "sans root (options 1, 2, 3, 4).",
                    border_style="red",
                )
            )
    except FileNotFoundError:
        console.print("[bold red]✗ nmap n'est pas installé ! Lance install.sh d'abord.[/bold red]")
        return
    except KeyboardInterrupt:
        console.print("\n[yellow]Scan interrompu par l'utilisateur.[/yellow]")
        return

    proposer_sauvegarde(lignes_resultat, cible)


def proposer_sauvegarde(lignes: list, cible: str):
    if not lignes:
        return
    console.print()
    if Confirm.ask("[bold]Veux-tu sauvegarder ce résultat dans un fichier ?[/bold]", default=False):
        dossier = os.path.expanduser("~/nmapgui_resultats")
        os.makedirs(dossier, exist_ok=True)
        horodatage = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        cible_propre = re.sub(r"[^a-zA-Z0-9]", "_", cible)
        chemin = os.path.join(dossier, f"scan_{cible_propre}_{horodatage}.txt")
        with open(chemin, "w") as f:
            f.write("\n".join(lignes))
        console.print(f"[bold green]✓ Résultat sauvegardé dans :[/bold green] {chemin}")


def afficher_aide():
    clear()
    console.print(
        Panel(
            "[bold]Qu'est-ce que c'est ?[/bold]\n"
            "NmapGUI est une interface simple pour piloter [cyan]nmap[/cyan], "
            "l'outil de référence pour scanner les réseaux et découvrir "
            "quels appareils/ports/services sont accessibles.\n\n"
            "[bold]Règle d'or :[/bold] scanne uniquement [underline]ton propre réseau[/underline] "
            "ou des cibles pour lesquelles tu as une autorisation explicite. "
            "Scanner un réseau qui ne t'appartient pas sans permission est illégal "
            "dans la plupart des pays.\n\n"
            "[bold]Root ou pas root ?[/bold]\n"
            "Sans privilèges root, tu peux quand même faire des scans TCP "
            "classiques (options 1, 2, 3, 4). Les options marquées "
            "[red]'root: oui'[/red] demandent des privilèges élevés : relance "
            "l'app avec [bold cyan]sudo nmapgui[/bold cyan] pour les utiliser "
            "pleinement, sinon nmap basculera automatiquement sur un mode "
            "compatible.\n\n"
            "[bold]Comprendre les couleurs des résultats :[/bold]\n"
            "  [bold green]vert[/bold green]  = port ouvert / hôte actif\n"
            "  [dim red]rouge terne[/dim red] = port fermé\n"
            "  [yellow]jaune[/yellow] = port filtré (pare-feu probable)\n",
            title="[bold]Aide[/bold]",
            border_style="blue",
        )
    )
    Prompt.ask("\n[dim]Appuie sur Entrée pour revenir au menu[/dim]", default="", show_default=False)


def main():
    if not check_nmap_installed():
        console.print(
            Panel(
                "[bold red]nmap n'est pas installé sur ce système.[/bold red]\n"
                "Lance d'abord : [bold cyan]bash install.sh[/bold cyan]",
                border_style="red",
            )
        )
        sys.exit(1)

    while True:
        afficher_banniere()
        afficher_menu()
        choix = Prompt.ask("\n[bold cyan]➤ Ton choix[/bold cyan]", default="0")
        choix = choix.strip().lower()

        if choix in ("0", "q", "quit", "exit"):
            console.print("\n[bold cyan]À bientôt ! 👋[/bold cyan]\n")
            break

        if choix in ("h", "help", "aide"):
            afficher_aide()
            continue

        if choix not in SCANS:
            console.print("[bold red]✗ Choix inconnu.[/bold red]")
            continue

        scan = SCANS[choix]

        if scan["root"] and not is_root():
            console.print(
                Panel(
                    f"[yellow]⚠ '{scan['nom']}' fonctionne mieux avec les droits root.[/yellow]\n"
                    "Tu peux relancer l'app avec [bold cyan]sudo nmapgui[/bold cyan] pour l'avoir, "
                    "ou continuer : nmap basculera automatiquement vers une méthode "
                    "compatible sans root si besoin.",
                    border_style="yellow",
                )
            )
            if not Confirm.ask("Continuer quand même ?", default=True):
                continue

        cible = choisir_cible()

        if choix == "8":
            console.print()
            args_perso = Prompt.ask(
                "[bold cyan]➤ Options nmap[/bold cyan] (ex: -p 80,443 -sV)",
                default="-T4 -F",
            )
            args = args_perso.split()
        else:
            args = scan["args"]

        lancer_scan(args, cible)
        console.print()
        Prompt.ask("[dim]Appuie sur Entrée pour revenir au menu[/dim]", default="", show_default=False)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n[bold cyan]Interrompu. À bientôt ! 👋[/bold cyan]\n")
        sys.exit(0)
