# Coding Case — Aggiungere tax al checkout legacy

## Problema originale
`checkout(cart)` addebita via `PaymentGateway` hard-coded che fa una chiamata di
rete. Non esistono test. Va aggiunta la tassa prima dell'addebito senza rompere
nulla.

## Task riformulato (Stadio 1)
Aggiungere la funzione "calcola e addebita totale con tassa" a codice non
testato, senza modificare il comportamento già in produzione.

## Funzione primaria (Tool → Action → Object)
Checkout (Tool) → addebita (Action) → carta cliente (Object).

## Effetti dannosi da evitare
Regressione sul totale corrente; chiamata di rete nel test; duplicazione della
logica di calcolo.

## Vincoli reali
Il gateway non deve mai girare nei test; il diff deve restare minimo; la firma
`checkout(cart)` non cambia.

## Stadio 2 — Ponytail ladder (rung scelto + perché)
**minimum-code** — non esiste stdlib/dipendenza per la tassa; ma si riusa tutto
ciò che esiste: la firma, i campi del cart, il gateway reale. Nessun codice
nuovo a parte la funzione pura.

## Stadio 3 — IFR / almost-IFR
**IFR:** il totale con tassa si calcola da solo — nessun modulo nuovo.
**Almost-IFR:** una funzione pura `computeTotal(items)` + una chiamata da
`checkout`.

## Stadio 4 — Dati + strategia
`checkout(cart)` → `cart.items: List[Item]`, ogni `Item` ha `price: Money`.
Signature: `computeTotal(items: List[Item]) -> Money`. Strategia: reduce (O(n)).

## Stadio 5 — Contraddizione + principio
"Devo aggiungere tassa" vs "non devo toccare il codice non testato" →
[Separation in part]: la logica nuova vive in una funzione separata
([Sprout Method]) accanto alla vecchia, non dentro la sua modifica.

## Stadio 6 — Il diff minimo sicuro
1. [Seam] getter virtuale `getGateway()` — una modifica signature-preserving.
2. [Characterization test] `assert checkout(cart(2)).total == 0` → il failure
   stampa il totale reale → lo pinno come baseline.
3. [Sprout Method] `computeTotal(items)` test-first (pura, niente gateway).
4. `checkout` chiama `computeTotal` prima dell'addebito.
Diff: 1 getter + 1 metodo puro + 1 chiamata. Logica vecchia intatta.

## Stadio 7 — Red flag review
[Vague name]? No: `computeTotal` crea un'immagine. [Information leakage]? No:
il gateway resta dietro il seam. [Leanness]? Il getter è l'unica aggiunta
strutturale, e guadagna testabilità — accettato.

## Stadio 8 — Test + criterio numerico
- **Candidato:** sprout + seam + characterization test.
- **Test/esperimento:** suite verde: 1 characterization + 1 behavioral
  (fake che registra `lastAmount`).
- **Criterio di successo/fallimento:** 100% test verdi; `lastAmount` del fake
  == totale con tassa (assert esatto); 0 modifiche a righe pre-esistenti.
- **Spiegazione ≤3 righe:** il seam rende testabile il gateway; lo sprout isola
  la logica nuova; la characterization test pinna il comportamento attuale.
- **Prossimo step se funziona:** rifattorizzare l'addebito dietro un metodo
  estrato.
- **Prossimo step se fallisce:** tornare al getter e verificare che il
  characterization test abbia catturato la divergenza.

## Risultati

## Follow-up
