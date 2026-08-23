# 🐍 Snake Arcade Game in Python

Un'edizione moderna, fluida ed elegante del classico gioco **Snake**, sviluppata in **Python**.
Il progetto include una versione grafica completa in stile arcade neon con effetti sonori ed effetti particellari, e una versione standalone leggera senza dipendenze esterne.

---

## 🌟 Caratteristiche Principali

- 🎮 **Doppia Versione di Gioco**:
  - **Edizione Arcade Moderna (`main.py`)**: Realizzata con Pygame, include grafica curata a tema Dark Neon, animazioni, occhi dinamici del serpente, particelle e suoni sintetizzati a 16-bit.
  - **Edizione Standalone Tkinter (`snake_tkinter.py`)**: Zero dipendenze esterne (utilizza solo la libreria standard di Python), ideale per giocare subito su qualsiasi computer.
- 🍏 **Frutti Speciali e Bonus**:
  - **Mela Rossa Classica**: +10 Punti e allungamento del serpente.
  - **Mela Stella Dorata (Bonus a tempo)**: +50 Punti con timer di scadenza visualizzato nell'HUD.
- ⚙️ **Difficoltà e Modalità di Gioco**:
  - **3 Livelli di Difficoltà**: *Facile*, *Medio*, *Difficile* (velocità dinamica).
  - **2 Modalità Bordi**: *Muri Mortali* (classico) oppure *Teletrasporto* (il serpente attraversa i bordi e ricompare dal lato opposto).
- 🏆 **Salvataggio Record**: Il punteggio massimo viene salvato in locale nel file `scores.json`.
- 🔊 **Effetti Sonori Integrati**: File audio WAV a 16-bit generati direttamente in Python (mangiata, bonus, game over e click menu).
- 🖱️ **Doppio Sistema di Controllo**: Supporta sia i tasti **Freccia** sia i tasti **W, A, S, D**.

---

## 📂 Struttura del Progetto

```
SnakeGame/
├── main.py                # Avvio principale del gioco (Edizione Arcade Pygame)
├── snake_tkinter.py       # Versione standalone Tkinter (Zero dipendenze)
├── game_engine.py         # Motore logico (serpente, collisioni, particelle, punteggio)
├── constants.py           # Configurazione grafica, velocità, dimensioni e palette colori
├── sound_generator.py     # Generatore procedurale di effetti sonori WAV a 44.1 kHz
├── assets/
│   └── sounds/            # Effetti sonori WAV (eat, bonus, game_over, click)
├── scores.json            # File di memorizzazione del record punteggio
├── requirements.txt       # Librerie Python richieste (pygame)
├── avvia_gioco.bat        # Script di avvio con 1 doppio-click su Windows
├── avvia_tkinter.bat      # Script per avvio immediato della versione Tkinter
├── .gitignore             # File di esclusione per Git
└── README.md              # Documentazione del progetto
```

---

## 🚀 Come Avviare il Gioco

### Opzione 1: Con Doppio Click (Consigliato su Windows)
Fai doppio click sul file:
- **`avvia_gioco.bat`**: Controlla l'ambiente, installa automaticamente `pygame` se necessario e avvia il gioco.
- **`avvia_tkinter.bat`**: Avvia direttamente la versione leggera senza installare nulla.

---

### Opzione 2: Da Terminale (PowerShell o CMD)

1. Apri il terminale nella cartella del progetto:
   ```bash
   cd C:\Users\Utente\Desktop\SnakeGame
   ```

2. *(Opzionale per la versione Pygame)* Installa le dipendenze:
   ```bash
   pip install -r requirements.txt
   ```

3. Avvia la versione preferita:
   - **Versione Arcade Completa**:
     ```bash
     python main.py
     ```
   - **Versione Leggera Standalone**:
     ```bash
     python snake_tkinter.py
     ```

---

## 🕹️ Comandi di Gioco

| Azione | Tasti da Tastiera |
| :--- | :--- |
| **Muovi Serpente** | <kbd>⬆️</kbd> <kbd>⬇️</kbd> <kbd>⬅️</kbd> <kbd>➡️</kbd> oppure <kbd>W</kbd> <kbd>A</kbd> <kbd>S</kbd> <kbd>D</kbd> |
| **Pausa / Riprendi** | <kbd>P</kbd> oppure <kbd>SPAZIO</kbd> |
| **Attiva/Disattiva Audio** | <kbd>M</kbd> |
| **Rigioca (dopo Game Over)** | <kbd>SPAZIO</kbd> oppure <kbd>INVIO</kbd> |
| **Torna al Menu** | <kbd>ESC</kbd> |

---

## 🛠️ Personalizzazione

Puoi personalizzare facilmente i parametri di gioco modificando il file `constants.py`:
- **Velocità**: Modifica il dizionario `SPEED_CONFIG` per regolare la velocità per ciascuna difficoltà.
- **Dimensioni Griglia**: Modifica `GRID_SIZE`, `GRID_WIDTH` e `GRID_HEIGHT`.
- **Colori e Tema**: Personalizza le costanti `COLOR_SNAKE_HEAD`, `COLOR_GRID_BG`, `COLOR_FOOD_RED`, ecc.

---

Buon divertimento con **Snake Game**! 🐍✨
