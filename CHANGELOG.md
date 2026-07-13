# Changelog

Toutes les modifications notables de ce projet sont documentées ici.

Le format suit [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/).

## [1.0.0] - 2026-07-13

### Ajouté
- Interface CLI colorée façon Zenmap, basée sur `rich`
- 8 profils de scan prédéfinis (rapide, découverte, versions, complet, OS, SYN, agressif, personnalisé)
- Détection automatique de l'IP locale, de la passerelle probable et du sous-réseau
- Sauvegarde des résultats de scan dans `~/nmapgui_resultats/`
- Aide intégrée accessible via la touche `H`
- Script d'installation multi-distribution (`apt`, `dnf`, `yum`, `pacman`, `zypper`, `apk`)
- Coloration syntaxique des résultats nmap (ports ouverts/fermés/filtrés, OS détecté, etc.)
