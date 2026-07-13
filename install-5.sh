#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# install.sh - Installe NmapGUI sur Linux (Debian/Ubuntu, Fedora/RHEL, Arch, openSUSE)
# ---------------------------------------------------------------------------

set -e

CYAN="\033[1;36m"
GREEN="\033[1;32m"
YELLOW="\033[1;33m"
RED="\033[1;31m"
RESET="\033[0m"

echo -e "${CYAN}"
cat << "EOF"
  _   _                       ____ _   _ ___
 | \ | |_ __ ___   __ _ _ __ / ___| | | |_ _|
 |  \| | '_ ` _ \ / _` | '_ \| |  _| | | || |
 | |\  | | | | | | (_| | |_) | |_| | |_| || |
 |_| \_|_| |_| |_|\__,_| .__/ \____|\___/|___|
                       |_|
EOF
echo -e "${RESET}"
echo -e "${CYAN}Installation de NmapGUI pour Linux...${RESET}"
echo ""

SUDO=""
if [ "$(id -u)" -ne 0 ]; then
    if command -v sudo >/dev/null 2>&1; then
        SUDO="sudo"
    else
        echo -e "${RED}✗ Ce script a besoin des droits root (ou de sudo) pour installer les paquets système.${RESET}"
        exit 1
    fi
fi

# 1. Détection du gestionnaire de paquets et installation de nmap + python3 + pip
echo -e "${CYAN}[1/3] Détection de la distribution et installation de nmap / python3...${RESET}"

if command -v apt-get >/dev/null 2>&1; then
    $SUDO apt-get update -y
    $SUDO apt-get install -y nmap python3 python3-pip
elif command -v dnf >/dev/null 2>&1; then
    $SUDO dnf install -y nmap python3 python3-pip
elif command -v yum >/dev/null 2>&1; then
    $SUDO yum install -y nmap python3 python3-pip
elif command -v pacman >/dev/null 2>&1; then
    $SUDO pacman -Sy --noconfirm nmap python python-pip
elif command -v zypper >/dev/null 2>&1; then
    $SUDO zypper install -y nmap python3 python3-pip
elif command -v apk >/dev/null 2>&1; then
    $SUDO apk add --no-cache nmap python3 py3-pip
else
    echo -e "${YELLOW}⚠ Gestionnaire de paquets non reconnu.${RESET}"
    echo -e "${YELLOW}  Installe manuellement : nmap, python3, python3-pip, puis relance ce script.${RESET}"
    exit 1
fi

# 2. Installation de rich via pip
echo -e "${CYAN}[2/3] Installation de la bibliothèque Python 'rich'...${RESET}"
if [ -f "$(dirname "${BASH_SOURCE[0]}")/requirements.txt" ]; then
    python3 -m pip install --user --break-system-packages -r "$(dirname "${BASH_SOURCE[0]}")/requirements.txt" 2>/dev/null \
        || python3 -m pip install --user -r "$(dirname "${BASH_SOURCE[0]}")/requirements.txt"
else
    python3 -m pip install --user --break-system-packages rich 2>/dev/null \
        || python3 -m pip install --user rich
fi

# 3. Rendre le script exécutable et créer un raccourci pratique
echo -e "${CYAN}[3/3] Configuration du raccourci 'nmapgui'...${RESET}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
chmod +x "$SCRIPT_DIR/nmapgui.py"

LOCAL_BIN="$HOME/.local/bin"
mkdir -p "$LOCAL_BIN"

cat > "$LOCAL_BIN/nmapgui" << EOF
#!/usr/bin/env bash
python3 "$SCRIPT_DIR/nmapgui.py" "\$@"
EOF
chmod +x "$LOCAL_BIN/nmapgui"

echo ""
echo -e "${GREEN}✓ Installation terminée avec succès !${RESET}"
echo ""

if echo "$PATH" | grep -q "$HOME/.local/bin"; then
    echo -e "Pour lancer l'application, tape :"
    echo -e "  ${CYAN}nmapgui${RESET}"
else
    echo -e "${YELLOW}⚠ $HOME/.local/bin n'est pas dans ton PATH.${RESET}"
    echo -e "Ajoute cette ligne à ton ~/.bashrc ou ~/.zshrc :"
    echo -e "  ${CYAN}export PATH=\"\$HOME/.local/bin:\$PATH\"${RESET}"
    echo -e "Puis relance ton terminal, ou tape directement :"
    echo -e "  ${CYAN}python3 $SCRIPT_DIR/nmapgui.py${RESET}"
fi

echo ""
echo -e "Pour les scans nécessitant les droits root (OS detection, SYN scan...) :"
echo -e "  ${CYAN}sudo nmapgui${RESET}"
echo ""
echo -e "${YELLOW}Rappel : ne scanne que ton propre réseau ou des cibles autorisées.${RESET}"
echo ""
