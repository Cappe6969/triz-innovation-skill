# Coding Case — Coppia di punti più vicina

## Problema originale
Data una lista di N punti 2D, trovare la coppia a distanza minima. N arriva a
~10⁵; la prima idea (doppio loop O(n²)) è troppo lenta.

## Task riformulato (Stadio 1)
Scegliere la strategia algoritmica giusta e implementarla con complessità
dichiarata prima di scrivere codice.

## Funzione primaria (Tool → Action → Object)
Algoritmo (Tool) → trova minima distanza (Action) → coppia di punti (Object).

## Effetti dannosi da evitare
O(n²) su input grandi; complessità implementativa non giustificata su input
piccoli.

## Vincoli reali
N ~10⁵; linguaggio a scelta; correttezza su input degeneri (punti coincidenti).

## Stadio 2 — Ponytail ladder (rung scelto + perché)
**stdlib** — il brute-force O(n²) è corretto e banale: YAGNI su N piccoli. La
complessità serve solo quando N è grande. Prima il baseline, poi il salto.

## Stadio 3 — IFR / almost-IFR
**IFR:** la coppia minima è già disponibile — nessun algoritmo nuovo.
**Almost-IFR:** divide-and-conquer O(n log n) con strip O(n), oppure sort+scan.

## Stadio 4 — Dati + strategia
`points: List[Point]`. Strategia: **divide-and-conquer** (split per x, ricorsione
sui due lati, strip centrale O(n)) — il caso classico del libro di Levitin.
Complessità dichiarata prima di codificare: O(n log n).

## Stadio 5 — Contraddizione + principio
"Velocità (servono tutti i confronti?)" vs "correttezza (la coppia minima può
attraversare lo split)" → [Separation in part]: risolvi i due lati separatamente
(ricorsione), poi combina solo la striscia centrale. La distanza minima
diventa il bound per scartare confronti inutili ([IP-10 Prior action] sort prima).

## Stadio 6 — Il diff minimo sicuro
1. [Brute force] baseline O(n²) come riferimento di verità (test).
2. Test su fixture: random, degeneri (coincidenti, collineari), N=0/1.
3. Implementare divide-and-conquer; verificare che matchi il baseline su ogni
   fixture random (property test: output uguali).

## Stadio 7 — Red flag review
[Nonobvious code]? La condizione della strip (candidati solo entro delta) va
commentata con il perché — la prova è non ovvia. [Vague name]? `closest_pair`,
`strip_candidates` creano immagini. [Leanness]? Solo le due funzioni necessarie.

## Stadio 8 — Test + criterio numerico
- **Candidato:** divide-and-conquer O(n log n) con strip.
- **Test/esperimento:** property test vs brute force su 500 fixture casuali;
  benchmark N=10⁵.
- **Criterio di successo/fallimento:** output identico al brute-force su 500
  fixture (assert esatto); tempo N=10⁵ < 1s (il brute-force è ≥ 60s);
  ~40 righe.
- **Spiegazione ≤3 righe:** dividi per x, risolvi i lati, combina la striscia
  con bound delta; il sort preliminare rende la striscia O(n).
- **Prossimo step se funziona:** generalizzare a k dimensioni se serve.
- **Prossimo step se fallisce:** il baseline brute-force resta il riferimento di
  correttezza; non ottimizzare oltre il necessario.

## Risultati

## Follow-up
