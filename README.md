# 🛡️ NmapGUI

Une interface **CLI simple, colorée et intuitive** pour [nmap](https://nmap.org/), inspirée de Zenmap — mais 100% terminal, ultra légère, et pensée pour que même un débutant complet puisse scanner un réseau en quelques secondes.

![Python](https://img.shields.io/badge/python-3.7%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Linux-lightgrey)

```
  _   _                       ____ _   _ ___
 | \ | |_ __ ___   __ _ _ __ / ___| | | |_ _|
 |  \| | '_ ` _ \ / _` | '_ \| |  _| | | || |
 | |\  | | | | | | (_| | |_) | |_| | |_| || |
 |_| \_|_| |_| |_|\__,_| .__/ \____|\___/|___|
                       |_|
```

## ✨ Fonctionnalités

- **Menu numéroté** : 8 types de scans prêts à l'emploi (rapide, découverte réseau, versions, tous les ports, OS, SYN furtif, agressif, personnalisé)
- **Détection automatique de ton réseau** : l'app affiche ta vraie IP locale, ta passerelle probable et ton sous-réseau, et te propose de scanner directement ton réseau en appuyant sur Entrée
- **Résultats colorés en direct** : ports ouverts en vert, fermés en rouge, filtrés en jaune
- **Sauvegarde des résultats** dans `~/nmapgui_resultats/`
- **Aide intégrée** (touche `H`) qui explique les scans, les couleurs, et root vs sans-root
- **Zéro configuration** : un seul script Python + un script d'installation

## 📦 Installation

```bash
git clone https://github.com/<ton-pseudo>/nmapgui.git
cd nmapgui
chmod +x install.sh
./install.sh
```

Le script détecte automatiquement ta distribution (Debian/Ubuntu, Fedora/RHEL, Arch, openSUSE, Alpine) et installe `nmap`, `python3` et la bibliothèque `rich`.

Une fois installé, lance simplement :

```bash
nmapgui
```

Pour les scans nécessitant les droits root (détection d'OS, scan SYN furtif) :

```bash
sudo nmapgui
```

### Installation manuelle

Si tu préfères ne pas utiliser `install.sh` :

```bash
pip install -r requirements.txt
python3 nmapgui.py
```

(assure-toi que `nmap` est installé sur ton système au préalable)

## 🖥️ Aperçu du menu

| N° | Type de scan | Root requis |
|----|---------------|:---:|
| 1 | Scan rapide | non |
| 2 | Découverte du réseau (ping scan) | non |
| 3 | Scan de services (versions) | non |
| 4 | Scan complet (tous les ports) | non |
| 5 | Détection du système d'exploitation | oui |
| 6 | Scan furtif SYN | oui |
| 7 | Scan agressif complet | oui |
| 8 | Scan personnalisé (tes propres options nmap) | selon options |

## ⚠️ Avertissement légal

Cet outil est une interface pour `nmap`. **Scanner un réseau ou un système sans autorisation explicite du propriétaire est illégal dans la grande majorité des pays.**

Utilise NmapGUI uniquement sur :
- ton propre réseau,
- des machines que tu possèdes,
- des cibles pour lesquelles tu as une autorisation écrite,
- ou des cibles de test publiques et autorisées comme `scanme.nmap.org`.

Les auteurs déclinent toute responsabilité en cas d'usage abusif.

## 🧰 Prérequis

- Linux (Debian/Ubuntu, Fedora/RHEL, Arch, openSUSE, Alpine)
- Python 3.7+
- nmap (installé automatiquement par `install.sh`)

## 📁 Structure du dépôt

```
nmapgui/
├── nmapgui.py        # Application principale
├── install.sh         # Script d'installation multi-distribution
├── requirements.txt    # Dépendances Python
├── README.md
├── LICENSE
└── CHANGELOG.md
```

## 🤝 Contribuer

Les issues et pull requests sont les bienvenues ! Idées d'améliorations futures :
- Export des résultats en JSON/HTML
- Historique des scans consultable dans l'app
- Détection automatique du système d'exploitation local pour adapter les conseils

## 📄 Licence

Distribué sous licence MIT. Voir [LICENSE](LICENSE) pour plus de détails.
