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

# Entrambi
python -m gdlex_inspector scan . --json report.json --html report.html
```

---

## Opzioni disponibili

| Opzione | Descrizione |
|---|---|
| `--top N` | Numero di file/cartelle in cima (default: 10) |
| `--min-size SIZE` | Soglia minima (es. `100K`, `500M`, `2G`) |
| `--max-depth N` | Profondità massima di ricorsione |
| `--json PATH` | Esporta report JSON |
| `--html PATH` | Esporta report HTML |
| `--exclude PATTERN` | Escludi pattern glob (ripetibile) |
| `--follow-symlinks` | Segui symlink (default: disabilitato) |

---

## Limiti della prima versione (v0.1.0)

- Solo scanner Python interno (nessun backend esterno gdu/dust/duf).
- Nessuna GUI (prevista in Fase 2 — PySide6/Matrix).
- Nessuna copia backup PST reale (predisposta, non implementata — Fase 4).
- Nessuna connessione SSH reale (predisposta, non implementata — Fase 5).
- Nessun Wake-on-LAN GUI (solo funzioni utility — Fase 5).
- Nessun export PDF/DOCX (previsto in Fase 3).
- Nessun grafico interattivo (previsto in Fase 3).
- Calcolo dimensione cartelle: somma ricorsiva file diretti (senza subtree per directory intermedie nella top list — miglioramento previsto).

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
