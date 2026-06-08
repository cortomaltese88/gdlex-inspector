# TODO — GD LEX Inspector

## Scanner

- [ ] Aggiungere test per permessi negati (directory non accessibile)
- [x] Aggiungere supporto CSV come formato di export
- [ ] Ottimizzare performance su directory con milioni di file
- [ ] Aggiungere filtraggio per data modifica (`--newer-than`, `--older-than`)

## Report

- [ ] Progettare export PDF (richiede dipendenza esterna, es. weasyprint)
- [ ] Progettare export DOCX/Word (richiede python-docx)
- [ ] Progettare stampa report diretta
- [ ] Aggiungere grafico donut categorie (HTML inline SVG)
- [ ] Aggiungere grafico barre top cartelle (HTML inline SVG)
- [ ] Aggiungere privacy mode (oscura percorsi utente nel report)

## GUI

- [ ] Preparare GUI Matrix PySide6
- [ ] Definire layout principale: barra laterale + pannello risultati
- [ ] Integrare selezione percorso con dialogo
- [ ] Integrare grafico donut categorie
- [ ] Integrare grafico barre top cartelle
- [ ] Aggiungere doppio clic / apri percorso
- [ ] Aggiungere menu contestuale copia percorso
- [ ] Aggiungere status bar e barra progresso
- [ ] Eseguire scansione in thread separato

## Outlook / PST

- [ ] Progettare backup PST verso destinazione scelta
- [ ] Aggiungere verifica spazio disponibile prima del backup
- [ ] Aggiungere hash SHA-256 opzionale per verifica copia
- [ ] Report backup HTML/JSON separato
- [ ] Aggiungere avviso "Chiudere Outlook prima del backup"

## Remoto

- [ ] Progettare connessione SSH remota
- [ ] Aggiungere profili remoti con UI
- [ ] Progettare scansione remota via SSH
- [ ] Aggiungere Wake-on-LAN GUI
- [ ] Report multi-PC aggregato

## Backend esterni

- [ ] Integrare backend gdu (opzionale, richiede gdu installato)
- [ ] Integrare backend dust (opzionale, richiede dust installato)
- [ ] Integrare backend duf per riepilogo dischi/partizioni
- [ ] Normalizzare output gdu/dust/duf in ScanResult
- [ ] Benchmark locale tra backend

## Packaging

- [ ] Preparare pacchetto Debian
- [ ] Preparare eventuale AppImage Linux
- [ ] Preparare eseguibile Windows portable
- [ ] Valutare installer Windows
- [ ] Aggiungere icone desktop
- [ ] Preparare GitHub Releases
