# ROADMAP — GD LEX Inspector

## Fase 0 — Bootstrap progetto ✅

- [x] Inizializzazione repository git
- [x] Struttura Python (`gdlex_inspector/`)
- [x] Licenza GPL-3.0-or-later
- [x] README, TODO, ROADMAP
- [x] Icona SVG Matrix
- [x] Smoke test (`scripts/smoke_test.sh`)
- [x] CLI minima (`version`, `scan`)

---

## Fase 1 — Scanner locale read-only

- [ ] Scansione file e cartelle
- [ ] Top file per dimensione
- [x] Top directory per dimensione (albero completo)
- [ ] Riepilogo per estensione
- [ ] Riepilogo per categoria euristica
- [ ] Classificazione prudenziale (rischio)
- [ ] Export JSON
- [ ] Export HTML con tema Matrix
- [ ] Gestione permessi negati (non bloccante)
- [ ] Supporto Linux, Windows, WSL
- [ ] Filtraggio per data modifica
- [x] Export CSV

---

## Fase 2 — GUI Matrix

> GUI funzionale con tema Matrix; restano gli ampliamenti elencati sotto.

- [x] GUI PySide6 con tema scuro Matrix coerente con GD LEX *(Step 2A)*
- [x] Selezione percorso con dialogo *(Step 2A)*
- [ ] Profili scansione rapida
- [x] Tabelle risultati interattive (Top file, Top cartelle, Categorie) *(Step 2A)*
- [x] Doppio clic / apri percorso *(Step 2A)*
- [ ] Menu contestuale copia percorso
- [x] Status bar *(Step 2A)*
- [ ] Barra progresso (indicatore testuale attivo in Step 2A)
- [x] Scansione in thread separato (non blocca UI) *(Step 2A)*
- [ ] Dialog informazioni
- [x] Icona applicazione SVG *(Step 2A)*
- [x] Export HTML/JSON/CSV dalla GUI *(Step 2A)*

---

## Fase 3 — Grafici e report avanzati

- [x] Grafico torta/donut per categorie (report HTML statico; GUI esclusa)
- [x] Grafico barre top cartelle (report HTML statico; GUI esclusa)
- [ ] Export PDF (weasyprint o equivalente)
- [ ] Export DOCX/Word (python-docx)
- [ ] Stampa report diretta
- [ ] Report con note manuali
- [ ] Stati manuali per risultato
- [ ] Colonna rischio/prudenza
- [ ] Privacy mode (oscura percorsi utente)
- [ ] Salvataggio e confronto scansioni

---

## Fase 4 — Backup Outlook PST

- [ ] Ricerca PST/OST nel percorso analizzato
- [ ] Backup **solo PST** come funzione separata e consapevole
- [ ] OST: solo avviso, mai copia automatica
- [ ] Destinazione NAS/cartella selezionata dall'utente
- [ ] Verifica spazio disponibile prima della copia
- [ ] Copia senza sovrascrittura (no clobber)
- [ ] Verifica dimensione dopo copia
- [ ] Hash SHA-256 opzionale
- [ ] Report backup HTML/JSON
- [ ] Apertura cartella destinazione dopo backup
- [ ] Nessuna modifica agli originali

---

## Fase 5 — Controllo remoto

- [x] Rilevamento SMB/CIFS e warning per share o cartelle parziali *(Step 4C)*
- [ ] Helper Windows remoto per raccolta diagnostica
- [ ] Supporto WinRM/SSH per diagnosi Windows
- [ ] Profilo `remote-smb-diagnostic`
- [ ] Profili PC remoti (nome, host, porta, utente, chiave SSH)
- [ ] Connessione SSH tramite comando di sistema
- [ ] Remote check (ping/stato)
- [ ] Remote scan (scansione remota via SSH)
- [ ] Ricerca Outlook remota
- [ ] Wake-on-LAN (GUI + invio packet)
- [ ] Report multi-PC aggregato
- [ ] Nessuna cancellazione remota
- [ ] Nessun salvataggio password in chiaro

---

## Fase 6 — Backend esterni maturi

Ispirazione: [gdu](https://github.com/dundee/gdu), [dust](https://github.com/bootandy/dust),
[duf](https://github.com/muesli/duf).

- [ ] Integrazione opzionale `gdu` (backend veloce multipiattaforma)
- [ ] Integrazione opzionale `dust` (output CLI leggibile)
- [ ] Integrazione opzionale `duf` per riepilogo dischi e partizioni
- [ ] Backend Python interno sempre disponibile come fallback
- [ ] Normalizzazione output in `ScanResult` (modello unificato)
- [ ] Benchmark locale tra backend
- [ ] Nessuna dipendenza obbligatoria: tutti i backend esterni sono opzionali

**Note:** nessun fork, nessuna copia di codice.
Uso esclusivamente come processo esterno tramite subprocess, con output normalizzato.

---

## Fase 7 — Packaging

- [x] Pacchetto Debian (`dpkg`)
- [ ] Eventuale AppImage Linux
- [ ] Eseguibile Windows portable (PyInstaller o Nuitka)
- [ ] Eventuale installer Windows
- [x] Icona e voce desktop Linux (`.svg`, `.desktop`)
- [ ] Icona desktop Windows (`.ico`)
- [ ] GitHub Releases
- [ ] Valutare APT repo solo se progetto pubblico

---

## Fase 8 — Funzioni avanzate

- [ ] Confronto tra scansioni (delta occupazione disco nel tempo)
- [ ] Duplicati probabili (nome + dimensione)
- [ ] Duplicati certi (hash SHA-256 opzionale)
- [ ] Profili di scansione rapida evoluti
- [ ] Dashboard studio/multi-PC
