# GD LEX Inspector

**Multiplatform disk inspection and prudential reporting tool for GD LEX workflows.**

> **Stato: Prototipo iniziale — v0.1.0**
> Tool diagnostico e prudenziale. Nessuna cancellazione automatica. Nessuna modifica ai file analizzati.

---

## Cos'è

`gdlex-inspector` è uno strumento da riga di comando per l'ispezione dell'occupazione disco,
la reportistica e il supporto ai workflow GD LEX.
Pensato per ambienti Linux, Windows e WSL.

Nella prima versione esegue **solo operazioni read-only**:
- scansione directory e file;
- classificazione per categoria ed estensione;
- classificazione prudenziale (PST Outlook, cache browser, node_modules, ecc.);
- esportazione report in formato JSON e HTML con tema Matrix scuro.

---

## Ispirazione tecnica

Il progetto si ispira a tool maturi come
[gdu](https://github.com/dundee/gdu),
[dust](https://github.com/bootandy/dust),
[ncdu](https://dev.yorhel.nl/ncdu),
[WinDirStat](https://github.com/windirstat/windirstat) e
[QDirStat](https://github.com/shundhammer/qdirstat),
ma nasce come **wrapper/report prudenziale GD LEX**, con focus su:
- sicurezza e assenza di cancellazioni automatiche;
- reportistica Outlook PST e workflow Windows/Linux/WSL;
- classificazione prudenziale per categorie di rischio.

Nessun codice è stato copiato o derivato da tali progetti.

---

## Natura prudenziale

- **Nessun file viene modificato, spostato o cancellato.**
- Il tool non richiede privilegi amministrativi per l'uso ordinario.
- Non segue i symlink per default (prevenzione loop).
- Gli accessi negati vengono registrati ma non bloccano la scansione.

---

## Installazione locale

```bash
cd /home/marco/progetti/gdlex-inspector
pip install -e .
```

Oppure senza installazione:

```bash
python -m gdlex_inspector --help
```

---

## Uso CLI

### Comandi principali

```bash
# Versione
python -m gdlex_inspector version

# Aiuto
python -m gdlex_inspector --help

# Scansione base
python -m gdlex_inspector scan /percorso

# Top 20 file più grandi
python -m gdlex_inspector scan /percorso --top 20

# Con soglia minima e profondità massima
python -m gdlex_inspector scan /percorso --top 50 --min-size 100M --max-depth 3

# Esporta JSON e HTML
python -m gdlex_inspector scan /percorso --json report.json --html report.html

# Esporta CSV
python -m gdlex_inspector scan /percorso --csv report.csv

# Escludi pattern
python -m gdlex_inspector scan /percorso --exclude node_modules --exclude .git
```

---

## Esempi Linux

```bash
# Scansione home
python -m gdlex_inspector scan ~ --top 20

# Scansione con export
python -m gdlex_inspector scan ~ --json ~/report.json --html ~/report.html

# Solo file grandi
python -m gdlex_inspector scan /var --top 10 --min-size 500M
```

## Esempi WSL

```bash
# Scansione percorso Windows montato
python -m gdlex_inspector scan /mnt/c/Users/Utente --top 50 --min-size 500M

# Export su disco Windows
python -m gdlex_inspector scan . --json /mnt/c/Users/Utente/Desktop/report.json --html /mnt/c/Users/Utente/Desktop/report.html
```

## Esempi Windows nativo

```bash
# Uso futuro / se installato come entry point
gdlex-inspector scan C:\Users\Utente --top 50

# Con Python esplicito
python -m gdlex_inspector scan C:\Users\Utente --top 20 --min-size 1G
```

---

## Esportazione report

```bash
# JSON strutturato
python -m gdlex_inspector scan . --json report.json

# HTML con tema scuro Matrix
python -m gdlex_inspector scan . --html report.html

# CSV multi-sezione (top_files, top_dirs, extensions, categories, issues)
python -m gdlex_inspector scan . --csv report.csv

# Tutti i formati insieme
python -m gdlex_inspector scan . --json report.json --html report.html --csv report.csv
```

Il report HTML include grafici statici inline (donut per categorie e barre per le
top cartelle), senza JavaScript obbligatorio né dipendenze esterne.

---

## Opzioni disponibili

| Opzione | Descrizione |
|---|---|
| `--top N` | Numero di file/cartelle in cima (default: 10) |
| `--min-size SIZE` | Soglia minima (es. `100K`, `500M`, `2G`) |
| `--max-depth N` | Profondità massima di ricorsione |
| `--json PATH` | Esporta report JSON |
| `--html PATH` | Esporta report HTML |
| `--csv PATH` | Esporta report CSV (sezioni: top_files, top_dirs, extensions, categories, issues) |
| `--exclude PATTERN` | Escludi pattern glob (ripetibile) |
| `--follow-symlinks` | Segui symlink (default: disabilitato) |

---

## GUI (sperimentale — Step 2A)

> **Stato: sperimentale.** La GUI è funzionale ma in fase di sviluppo attivo.
> Richiede un ambiente grafico (X11/Wayland). Non funziona in ambienti headless.

### Installazione dipendenza GUI

```bash
pip install PySide6
# oppure tramite extra opzionale:
pip install 'gdlex-inspector[gui]'
```

### Avvio GUI

```bash
python3 -m gdlex_inspector gui

# Con percorso pre-compilato:
python3 -m gdlex_inspector gui --path /percorso/da/analizzare
```

### Funzionalità GUI

- Tema scuro Matrix (coerente con i report HTML)
- Selezione percorso tramite dialogo cartella
- Opzioni: Top N, Min size, Max depth
- Scansione in thread separato (UI non bloccata durante la scansione)
- Tabelle interattive: Top file, Top cartelle, Categorie
- Doppio clic su riga per aprire nel file manager
- Pulsante "Apri percorso" per la riga selezionata
- Esportazione report: HTML, JSON, CSV
- Area log con messaggi di stato in tempo reale
- Icona SVG dell'applicazione

Se PySide6 non è installato e si tenta di avviare la GUI, viene mostrato un
messaggio di errore chiaro. La CLI continua a funzionare normalmente senza PySide6.

---

## Integrazione desktop Linux/KDE

> Permette di avviare GD LEX Inspector dal menu applicazioni KDE/GNOME senza
> usare il terminale. Non richiede privilegi di root.

### Prerequisiti

```bash
# Installare PySide6 (necessario per la GUI)
pip install PySide6
# oppure via extra opzionale:
pip install 'gdlex-inspector[gui]'
```

### Installazione editable (necessaria per il comando `gdlex-inspector`)

Se si usa direttamente il repository sorgente (senza pacchetto .deb), installare
il progetto in modalità editable per rendere disponibile il comando `gdlex-inspector`:

```bash
cd /home/marco/progetti/gdlex-inspector
python3 -m pip install -e ".[gui]"
```

Verificare che il comando sia disponibile:

```bash
gdlex-inspector --help
gdlex-inspector gui
```

In alternativa, senza installazione:

```bash
python3 -m gdlex_inspector gui
```

### Installare la voce menu

```bash
./scripts/install_desktop_entry.sh
```

Lo script:

- non richiede sudo;
- copia il desktop file in `~/.local/share/applications/`;
- copia l'icona SVG in `~/.local/share/icons/hicolor/scalable/apps/`;
- aggiorna le cache KDE/GTK se i comandi sono disponibili;
- è idempotente (rieseguibile senza problemi).

### Rimuovere la voce menu

```bash
./scripts/uninstall_desktop_entry.sh
```

### Avvio

Dopo l'installazione, GD LEX Inspector compare nel menu applicazioni sotto
le categorie **Utility / System / FileTools**.

Dalla riga di comando:

```bash
gdlex-inspector gui
# oppure
python3 -m gdlex_inspector gui
```

---

## Limiti della prima versione (v0.1.0)

- Solo scanner Python interno (nessun backend esterno gdu/dust/duf).
- GUI sperimentale disponibile (Fase 2 Step 2A — PySide6/Matrix).
- Nessuna copia backup PST reale (predisposta, non implementata — Fase 4).
- Nessuna connessione SSH reale (predisposta, non implementata — Fase 5).
- Nessun Wake-on-LAN GUI (solo funzioni utility — Fase 5).
- Nessun export PDF/DOCX (previsto in Fase 3).
- Nessun grafico interattivo; il report HTML include grafici statici.

---

## Roadmap sintetica

| Fase | Contenuto |
|---|---|
| 0 | Bootstrap, struttura, CLI, smoke test ✅ |
| 1 | Scanner read-only completo, categorie, JSON/HTML |
| 2 | GUI Matrix PySide6 |
| 3 | Grafici, PDF, DOCX, stampa |
| 4 | Backup Outlook PST prudenziale |
| 5 | Controllo remoto SSH, Wake-on-LAN |
| 6 | Backend esterni gdu/dust/duf |
| 7 | Packaging Debian, Windows portable |
| 8 | Duplicati, confronto scansioni, dashboard |

---

## Licenza

GPL-3.0-or-later — STUDIO GD LEX. Vedere `LICENSE`.
