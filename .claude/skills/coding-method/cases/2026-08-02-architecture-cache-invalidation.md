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
esistesse cache né invalidation. **Almost-IFR:** cache locale con TTL ≤ 30s:
il dato è al massimo 30s vecchio, quindi il vincolo di freschezza è rispettato
senza alcuna logica di invalidation.

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
1. Test sul comportamento: scritto → letto (fresco), scritto → letto dopo TTL
   (aggiornato), fallimento del backend → si serve l'ultimo valore buono.
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
- **Test/esperimento:** 8 test (freschezza, TTL expiry, backend-down, version
  mismatch, hit rate); benchmark latenza con/senza cache su 10⁴ letture.
- **Criterio di successo/fallimento:** 8/8 verdi; latenza p50 da ~150ms a
  <5ms; stale-rate misurato 0% sui test con scritture ogni 10s; 0 dependency
  nuove.
- **Spiegazione ≤3 righe:** il TTL trasforma "sempre fresco" in "fresco quando
  serve" — separazione nel tempo; la cache è un wrapper, il business logic non
  cambia; Redis è rimandato finché la misura non lo giustifica.
- **Prossimo step se funziona:** estendere a più istanze con TTL scalato, poi
  valutare Redis solo se lo stale-rate misurato lo richiede.
- **Prossimo step se fallisce:** il vincolo era "le scritture visibili entro 30s
  ma nessuna stale read" → la contraddizione è reale, non apparente → tornare a
  Stadio 5 e applicare [Separation in part] (cache per-partition, write-through).

## Risultati

## Follow-up
