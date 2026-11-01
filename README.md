# layn-signage

Offentlig TV-visning av Layn-bruk, vist på Yodeck: https://bekvern.github.io/layn-signage/

**Denne siden er offentlig. Den skal aldri inneholde kundenavn, domenenavn eller partnernavn.** Bare summer, andeler og anonyme etiketter som «Ny kunde 1».

| Fil | Hva |
|---|---|
| `index.html` | Selve visningen. Bytter side hvert 15. sekund |
| `data.js` | Tallene. Byttes ut én gang i måneden |
| `gen_signage.py` | Lager `data.js` fra dashboardet «Layn Flow Statistikk» |

## Oppdatere
```
python3 gen_signage.py layn-flow.html data.js
```
`layn-flow.html` er dashboardets HTML. Skriptet leser konstantene `D`, `SMS` og `PYF`, regner ut summene og skriver `data.js`.

Skriptet har en **sikkerhetssjekk**: det samler alle kunde-, domene- og partnernavn fra dashboardet og nekter å skrive filen hvis noen av dem dukker opp som eget ord i utdata. Ikke fjern den sjekken.

Reglene og datagrunnlaget er dokumentert i mappen `Fakturagrunnlag/LAYN STATISTIKK` på Bents PC.
