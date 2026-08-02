# Coding Case — Trade-off architetturale: cache + invalidation

## Problema originale
Un servizio di lettura profile fa 1 chiamata di rete per ogni richiesta. Serve
una cache, ma i dati cambiano spesso e l'invalidation è il vero problema: se la
cache è stale, il cliente legge dati vecchi.

## Task riformulato (Stadio 1)
Ridurre la latenza media senza violare il requisito di freschezza, scegliendo
tra le strategie architetturali disponibili prima di scrivere codice.

## Funzione primaria (Tool → Action → Object)
Servizio di lettura (Tool) → serve il profile (Action) → dati cliente (Object).

## Effetti dannosi da evitare
Stale read; cache stamp (ogni istanza con copie incoerenti); complessità di
invalidation nascosta nel codice di business.

## Vincoli reali
Il dato cambia < 5 volte/minuto; la lettura deve riflettere le scritture entro
30s; nessuna dependency nuova se non strettamente necessaria.

## Stadio 2 — Ponytail ladder (rung scelto + perché)
**stdlib** — una cache in-process `map + ttl` risolve il caso d'uso medio senza
Redis; l'invalidation si fa con TTL corto + versionamento. La dependency nuova
(Redis) è un salto che si valuta solo se il TTL corto non basta.

## Stadio 3 — IFR / almost-IFR
**IFR:** ogni lettura restituisce il dato giusto senza rete — come se non
esistesse cache né invalidation. **Almost-IFR:** cache locale con TTL ≤ 30s
quando il contratto ammette letture stale entro quella finestra. Il TTL limita
la staleness; non la elimina. Se serve read-after-write, occorre invalidazione
o write-through.

## Stadio 4 — Dati + strategia
`profile(userId) -> Profile`. Strategia: **cache-aside** con TTL corto e
versionamento del payload. Il TTL è la policy di freschezza; il version tag
serve a scartare chunk stale prodotti da deploy.

## Stadio 5 — Contraddizione + principio
"Freschezza (dato sempre aggiornato)" vs "velocità (niente rete)" → [Separation
in time]: il dato è fresco **quando** serve — il TTL rende il compromesso
esplicito e misurabile, invece che implicito. [IP-10 Prior action]: la cache si
riempie alla prima lettura; il cold start è accettato per costruzione.

## Stadio 6 — Il diff minimo sicuro
1. Test con clock controllato: hit entro TTL, refresh dopo TTL e write/read. In
   caso di backend non disponibile, la policy sceglie esplicitamente tra errore
   e valore stale; non promette insieme freschezza e disponibilità.
2. Aggiungere la cache come wrapper del client esistente, non dentro il business
   logic ([Seam] sull'interfaccia del client dati).
3. Se il TTL non basta: misuro stale-rate prima di introdurre Redis — mai prima.

## Stadio 7 — Red flag review
[Information leakage]? La politica di freschezza (TTL) è un parametro, non una
costante sparsa. [Nonobvious code]? Il version tag ha un commento col perché.
[Leanness]? Wrapper + parametro: nessuna classe nuova. [Reinventing the wheel]?
`map + ttl` è stdlib, non un cache engine fatto in casa.

## Stadio 8 — Test + criterio numerico
- **Candidato:** cache-aside in-process con TTL 30s + version tag.
- **Test/esperimento:** test con clock controllato per TTL, write/read,
  backend-down e version mismatch; benchmark separato con/senza cache.
- **Criterio di successo/fallimento:** nessun valore supera la finestra di
  staleness dichiarata; read-after-write passa solo se richiesto dal contratto;
  nessuna dipendenza nuova per la variante locale.
- **Spiegazione ≤3 righe:** il TTL trasforma "sempre fresco" in "fresco quando
  serve" — separazione nel tempo; la cache è un wrapper, il business logic non
  cambia; Redis è rimandato finché la misura non lo giustifica.
- **Prossimo step se funziona:** estendere a più istanze con TTL scalato, poi
  valutare Redis solo se lo stale-rate misurato lo richiede.
- **Prossimo step se fallisce:** il vincolo era "le scritture visibili entro 30s
  ma nessuna stale read" → la contraddizione è reale, non apparente → tornare a
  Stadio 5 e applicare [Separation in part] (cache per-partition, write-through).

## Risultati

Analisi non eseguita contro un servizio reale. Un TTL di 30 secondi consente
letture stale fino a 30 secondi e quindi non giustifica l'assenza di letture
stale. Latenza e hit-rate restano da misurare nel sistema target.

## Follow-up

Definire prima il contratto di consistenza. Provare TTL locale con clock fake;
passare a invalidazione/write-through soltanto se read-after-write è richiesto.
