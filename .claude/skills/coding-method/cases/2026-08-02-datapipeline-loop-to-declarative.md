# Coding Case — Loop annidato → pipeline dichiarativa

## Problema originale
Un worker trasforma una lista di ordini: un `for` annidato con `if` interni
filtra, mappa e accumula in tre passaggi separati, con un contatore a mano.

## Task riformulato (Stadio 1)
Semplificare la trasformazione dati senza cambiare il risultato. Funzione
primaria: ordini → ordini completati e pagati, totale per cliente.

## Funzione primaria (Tool → Action → Object)
Pipeline (Tool) → trasforma (Action) → ordini (Object).

## Effetti dannosi da evitare
Ridondanza (loop manuali), mutazione nascosta, difficoltà di test.

## Vincoli reali
Risultato identico byte-per-byte; nessuna dipendenza nuova; runtime ≤ attuale.

## Stadio 2 — Ponytail ladder (rung scelto + perché)
**one-line** — ogni passaggio collassa in una chiamata idiomatica
`map/filter/reduce`. La platform li fornisce già: [Rewrite ladder] rung finale.

## Stadio 3 — IFR / almost-IFR
**IFR:** la trasformazione è una dichiarazione di intento, non un loop.
**Almost-IFR:** una catena `filter(...).map(...).reduce(...)` con helper puri
con nome.

## Stadio 4 — Dati + strategia
`orders: List[Order]`, `Order { status, customer, total }`. Signature del
pipeline: `completedTotals(orders) -> Dict[customer, Money]`. Strategia:
transform-and-conquer (presort semantic → filter/map/reduce).

## Stadio 5 — Contraddizione + principio
"Leggibilità (dichiarativo)" vs "performance (loop singolo)" → [Separation in
part]: i predicati e le proiezioni sono funzioni pure separate; il loop resta
una sola passata, la lettura diventa dichiarativa. Niente compromesso.

## Stadio 6 — Il diff minimo sicuro
1. Test-first: caso con ordini misti (completati/no, pagati/no).
2. [Rewrite ladder]: rung 1 = codice attuale; rung 2 = helper estratti; rung 3 =
   catena dichiarativa. Test verdi a ogni rung.
3. Eliminare il contatore a mano → `reduce`.

## Stadio 7 — Red flag review
[Repetition]? Eliminata: ogni concetto appare una volta. [Nonobvious code]? I
predicati hanno nomi (`isCompleted`, `isPaid`). [Leanness]? Zero strutture
nuove, solo la catena.

## Stadio 8 — Test + criterio numerico
- **Candidato:** pipeline dichiarativa con helper puri.
- **Test/esperimento:** suite sul caso misto + caso vuoto + caso con ordini
  duplicati (verifica aggiornamento totali).
- **Criterio di successo/fallimento:** output identico al baseline su 3 fixture;
  righe di logica: da ~25 a ~8 (−68%); test verdi.
- **Spiegazione ≤3 righe:** filter/map/reduce dichiarano la trasformazione;
  le funzioni pure separano i concetti; il reduce sostituisce l'accumulo a mano.
- **Prossimo step se funziona:** applicare lo stesso pattern agli altri loop.
- **Prossimo step se fallisce:** tenere i helper puri e mantenere la rung 2.

## Risultati

## Follow-up
