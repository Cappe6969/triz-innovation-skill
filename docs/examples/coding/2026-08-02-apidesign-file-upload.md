# Coding Case — API file upload con modulo deep

## Problema originale
Serve un modulo di upload file: validazione, virus scan, dedup, storage su S3,
metadati. La prima bozza produce 6 classi esposte e il chiamante deve conoscerle
tutte per fare un upload.

## Task riformulato (Stadio 1)
Progettare l'API di upload con la complessità nascosta: un'interfaccia piccola,
tutta la meccanica dentro.

## Funzione primaria (Tool → Action → Object)
Modulo upload (Tool) → salva in modo sicuro (Action) → file + metadati (Object).

## Effetti dannosi da evitare
Shallow modules (6 classi che il chiamante deve conoscere); pass-through;
information leakage; eccesso di configurazione.

## Vincoli reali
Deve validare (tipo, dimensione), deduplicare, scansionare virus, scrivere su
S3 e restituire l'URL. Il chiamante non deve vedere la pipeline.

## Stadio 2 — Ponytail ladder (rung scelto + perché)
**existing-dep** — S3 SDK, scanner e libreria di hashing esistono già. Il
modulo orchestratore è il solo codice da scrivere.

## Stadio 3 — IFR / almost-IFR
**IFR:** `upload(file)` e basta — lo storage, la validazione e il dedup
accadono da soli dentro. **Almost-IFR:** `upload(bytes, meta) -> Url`
+ errore tipizzato.

## Stadio 4 — Dati + strategia
`FileInput { bytes, name, mime, size }`, `UploadResult { url, is_new }`.
Signature: `upload(input: FileInput) -> UploadResult`. Il modello dati definisce
i confini; nessun parametro di pipeline nel contratto.

## Stadio 5 — Contraddizione + principio
"Configurabilità (dedup on/off, scanner on/off)" vs "interfaccia semplice" →
[IP-6 Universality] un solo punto di estensione: parametri opzionali con
default (common case) e un hook di pipeline interno. [Pull complexity down] —
la meccanica vive nel modulo dove nessuno la vede.

## Stadio 6 — Il diff minimo sicuro
1. [Write comments first] contratto dell'interfaccia prima dell'implementazione:
   se non lo si descrive in 3 righe, il design è sbagliato.
2. Test-first sull'interfaccia pubblica (fake S3, scanner stub).
3. Implementare la pipeline interna: validazione → hashing/dedup → scan →
   upload → metadati. Il chiamante testa solo `upload`.

## Stadio 7 — Red flag review
[Shallow module]? L'interfaccia è 1 metodo — deep. [Information leakage]? Gli
interni (S3, scanner) non compaiono nel contratto. [Pass-through method]?
Nessun parametro threadato: il modulo ha il suo FileInput. [Classitis]? 1
punto di ingresso, non 6.

## Stadio 8 — Test + criterio numerico
- **Candidato:** modulo deep con `upload(FileInput) -> UploadResult`.
- **Test/esperimento:** test sull'interfaccia pubblica per file validi,
  invalidi, duplicati e scan positivo; fake dello storage.
- **Criterio di successo/fallimento:** tutti i casi del contratto passano; il
  consumer usa un solo entry point e non importa classi interne.
- **Spiegazione ≤3 righe:** deep module — l'interfaccia è il costo, la
  funzionalità il beneficio; la pipeline sta dentro, invisibile.
- **Prossimo step se funziona:** aggiungere resumable upload come estensione
  opzionale, senza toccare il contratto.
- **Prossimo step se fallisce:** il contratto non era descrivibile in 3 righe →
  ridisegnare (design it twice).

## Risultati

Design di riferimento soltanto: nessun modulo o test è incluso in questo caso,
quindi non vengono dichiarati esiti o metriche.

## Follow-up

Costruire un fake di storage e uno scanner deterministico, quindi verificare il
contratto pubblico prima di scegliere SDK o provider concreti.
