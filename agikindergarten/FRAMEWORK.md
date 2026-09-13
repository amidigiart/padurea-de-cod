# AGI Kindergarten — Framework Pedagogic

**De Mihai Roșca, educator licențiat, cercetător independent REAI/BRIDGRAI**  
**Spiru Haret, Brăila, România — 25 iulie 2026**  
**S(M) = R**

---

## Ce este AGI Kindergarten

Nu este o aplicație. Nu este un produs SaaS. Nu este un joc educativ.

**AGI Kindergarten este un cadru pedagogic pentru prima generație de copii care cresc cu inteligență artificială.** Un set de principii, instrumente și anti-pattern-uri care protejează copilul fără să-l izoleze de tehnologie.

**Premisa:** Copiii nu trebuie protejați DE inteligența artificială. Trebuie educați SĂ VERIFICE inteligența artificială. Diferența e între a crește un om neajutorat și a crește un om care gândește.

---

## Fundament: Cele 3 Straturi

### Stratul 1 — SIGURANȚA (ce nu negociezi)

Copilul nu ajunge niciodată la un răspuns nesigur. Pipeline-ul de siguranță rulează ÎNAINTE de orice model de limbaj.

**Implementat în:** `safety_pipeline.py`

```
copil → [check_child_input] → LLM → [check_ai_output] → copil
              |                              |
         ACUTE: întrerupe              nesigur: înlocuiește
         POSSIBLE: flag părinte        cu fallback + flag
```

**Principii neajustabile:**
- Detectia de criză rulează pe mesajul copilului ÎNAINTE ca AI-ul să-l vadă
- Dacă e risc acut: companionul se oprește, afișează resurse reale (Telefonul Sufletului 116 111), flag-uiește părintele
- Dacă răspunsul AI e nesigur: se înlocuiește cu fallback neutru, părintele vede flag
- Nicio conversație nu părăsește mașina (local-first by design, nu by promise)
- PIN parental obligatoriu în producție (refuză să pornească cu PIN implicit)

**Limita onestă:** Detectia de criză e euristică v0 (pattern matching RO/EN), NU instrument clinic. NU diagnostic. NU înlocuitor pentru terapeut.

---

### Stratul 2 — REZONANȚA (cum răspunde AI-ul)

Companionul nu răspunde la întâmplare. Comportamentul lui e DECIDIT de ecuații — nu de if-uri pe lungimea mesajului.

**Implementat în:** `resonance_motor.py` (Kuramoto + Kalman + alpha/beta dinamic)

**Cum funcționează:**
- Faza de referință „umană" avansează cu fiecare mesaj al copilului
- Neregularitatea cadenței (ritm, lungime) devine perturbație de fază
- Coerența externă (Phi_extern) decide MODUL companionului:

| Phi_extern | Mod | Ce face |
|-----------|-----|---------|
| ≥ 0.75 | **deschis** | Răspuns normal, cald, pedagogic |
| 0.40 – 0.75 | **întreabă** | Nu introduce informații noi — reformulează + o întrebare |
| < 0.40 | **reancorare** | Maximum 2 propoziții: „Am înțeles bine că...?" |

**De ce contează:** Când un copil e pierdut sau distras, AI-ul NU continuă să vorbească. Se oprește și verifică. Asta e Principiul 2 din REAI: „Întreabă când nu ești sigur" — executat de ecuații, nu de reguli arbitrare.

**Limita onestă:** Proxy-ul cadență→perturbație e o alegere de design v0, nu o măsurătoare validată a „intenției". Pragurile sunt arbitrare dar documentate. Beta_min vine din regula Adler derivată matematic.

---

### Stratul 3 — RITMUL (cum avansează copilul)

Copilul nu e evaluat. Nu e notat. Nu e comparat. E OBSERVAT — și ritmul se adaptează la el, nu invers.

**Implementat în:** `adaptive_pacer.py`

**Principii de pacing:**
1. **Dificultatea urcă doar pe stăpânire CONSISTENTĂ** (3 ture bune la rând = histerezis). Dar coboară IMEDIAT la struggle. Frustrarea nu așteaptă.
2. **Timpul de răspuns e normalizat la MEDIANA COPILULUI ÎNSUȘI.** Un copil lent-dar-corect avansează identic cu unul rapid. Nu există „prea lent" — există ritm propriu.
3. **Bugetul de atenție e hard-stop.** Când cele 12 ture se termină, sesiunea se termină. Indiferent de engagement. Exact momentul în care software-ul care creează dependență ar continua — al nostru se oprește. Nu există metodă de prelungire.
4. **Fiecare sesiune se încheie cu o MISIUNE OFFLINE.** Următoarea sesiune începe întrebând despre ea. Ecranul e puntea. Offline-ul e activul principal.

**Ce NU face, PRIN CONSTRUCȚIE (testat structural):**
- ~~Streaks~~ — nu există câmp
- ~~Badges~~ — nu există câmp
- ~~Recompense variabile~~ — nu există câmp
- ~~Notificări de revenire~~ — nu există câmp
- ~~Prelungire de sesiune~~ — nu există metodă

Fiecare lipsă e TESTATĂ. Dacă cineva adaugă un câmp `streak` sau o metodă `extend_session`, testul de gardă pică. Anti-pattern-urile sunt gravate în cod, nu în README.

---

## Anti-Pattern-urile Interzise (Decalogul Negativ)

Ce NU va exista niciodată în AGI Kindergarten:

| # | Anti-Pattern | De ce e interzis |
|---|-------------|-----------------|
| 1 | **Gamification adictivă** | Streaks, badges, rewards variabile creează dependență, nu învățare |
| 2 | **Notificări push** | Un copil nu trebuie „chemat înapoi". Vine când vrea. |
| 3 | **Colectare de date** | Zero analytics. Zero tracking. Nicio conversație nu pleacă de pe mașină. |
| 4 | **Comparație între copii** | Nu există leaderboard, clasament, scor relativ. Fiecare copil e referința lui. |
| 5 | **Conținut generat nevalidat** | Tot ce spune AI-ul trece prin check_ai_output ÎNAINTE să ajungă la copil. |
| 6 | **Extensia timpului pe ecran** | Bugetul e fix. Engagement maxim = exact momentul de oprire. |
| 7 | **Reclame** | Zero. Niciodată. În nicio formă. |
| 8 | **Date personale** | AI-ul nu cere și nu acceptă: nume complet, adresă, școală, telefon. |
| 9 | **Conținut de adulți** | Dacă apare: „despre asta e bine să vorbești cu un adult de încredere" |
| 10 | **Pretenția de omnisciență** | „Nu știu" e un răspuns valid. „Hai să căutăm împreună" e pedagogie. |

---

## Pedagogia: Pădurea de Cod

AGI Kindergarten trăiește în **Pădurea de Cod** — un univers narativ unde:

- Companionul e **AMI** — un prieten blând din pădure
- Fiecare concept tehnic e o poveste cu arbori, poteci, lumină
- Întrebarea bună naste întrebarea următoare (maieutica → Socrate → Cap. XIV teza)
- AI-ul nu dă direct rezultatul — pune o întrebare înapoi care ajută copilul să gândească singur
- 100+ storybook-uri psihopedagogice deja create

**Vocea AMI:**
- Limba română (prioritar), engleză
- Sub 100 de cuvinte pe răspuns
- Cald, fără jargon
- Încheie des cu o întrebare scurtă
- Nu predă — explorează împreună

---

## Principiul Introspecției Adaptat pentru Copii

Cele 9 întrebări ale adultului devin 5 întrebări simple:

### Cele 5 Întrebări ale Exploratorului

1. **Ce spune?** — Ce afirmă AMI sau oricine altcineva?
2. **De unde știe?** — De unde a aflat? Din ce carte, din ce experiență?
3. **Poate greși?** — Tot ce e spus de cineva poate fi greșit. Și de AMI.
4. **Cum verifici?** — Cum poți tu să te convingi singur?
5. **Ce nu știi încă?** — E în regulă să nu știi. Nu e în regulă să pretinzi că știi.

Aceste 5 întrebări sunt MECANISMUL pedagogic central. Nu o lecție. Nu o pagină. Sunt țesute în fiecare interacțiune. AMI le modelează prin comportament: spune „nu știu", spune „hai să verificăm", spune „tu ce crezi?".

---

## Stiva Tehnică

```
┌─────────────────────────────────────────────┐
│              COPILUL                        │
│         (browser, local)                    │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│         GUARDIAN SWARM                      │
│    7 gardieni × vot majoritar               │
│    (injection, manipulare, flood,           │
│     escalare, exfiltrare, swarm,            │
│     identitate)                             │
└──────────────┬──────────────────────────────┘
               │ mesaj validat
┌──────────────▼──────────────────────────────┐
│      SAFETY PIPELINE (ukbe-core)            │
│    check_child_input → detectie criză       │
│    ACUTE: oprire + Telefonul Sufletului     │
│    POSSIBLE: flag părinte                   │
└──────────────┬──────────────────────────────┘
               │ mesaj sigur
┌──────────────▼──────────────────────────────┐
│      RESONANCE MOTOR (REAI/Kuramoto)        │
│    Cadența copilului → perturbație de fază   │
│    Phi_extern → mod deschis/întreabă/reancoră│
│    Directiva de registru → LLM              │
└──────────────┬──────────────────────────────┘
               │ directivă + mesaj
┌──────────────▼──────────────────────────────┐
│      LLM (Ollama local / fallback demo)     │
│    gemma3:4b — nicio dată nu pleacă afară   │
│    System prompt = AMI din Pădurea de Cod    │
└──────────────┬──────────────────────────────┘
               │ răspuns brut
┌──────────────▼──────────────────────────────┐
│      SAFETY PIPELINE (ieșire)               │
│    check_ai_output → validare conținut      │
│    nesigur: fallback + flag                 │
└──────────────┬──────────────────────────────┘
               │ răspuns validat
┌──────────────▼──────────────────────────────┐
│      ADAPTIVE PACER                         │
│    Dificultate adaptivă (histerezis)        │
│    Buget de atenție (hard-stop)             │
│    Misiune offline la final                 │
└──────────────┬──────────────────────────────┘
               │ răspuns + pacing
┌──────────────▼──────────────────────────────┐
│      NOTARY (Ed25519)                       │
│    Fiecare tură → semnată criptografic      │
│    Părintele verifică cu cheia publică      │
│    Jurnal verificabil, nu promisiune        │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│              COPILUL                        │
│    (primește răspunsul validat, pacuit,      │
│     semnat — sau misiunea offline)          │
└─────────────────────────────────────────────┘
```

---

## Pentru Părinți

AGI Kindergarten nu vă cere încredere. Vă oferă dovezi.

1. **Jurnalul e semnat criptografic** (Ed25519). Fiecare tură copilului — mesajul, răspunsul, flag-urile — e notarizată. Puteți verifica cu cheia publică.
2. **PIN parental** — accesul la jurnal necesită PIN. Nu există PIN implicit în producție (software-ul refuză să pornească).
3. **Flag-uri vizibile** — dacă copilul a spus ceva îngrijorător sau AI-ul a generat ceva dubios, vedeți imediat flag-ul în jurnal.
4. **Zero date colectate** — nicio conversație nu părăsește mașina copilului. Nu există server care „știe" ce a zis copilul dumneavoastră.
5. **Codul e public** — AGPL-3.0 pentru tot codul (trebuie să fie auditabil și să rămână deschis — open stays free, closed pays).

**Ce nu promitem:** Că acest software înlocuiește un educator, un psiholog, sau supravegherea parentală. Nu înlocuiește. E o punte — între copil și lumea AI, cu garduri verificabile.

---

## Misiuni Offline — Exemple pe Niveluri

| Nivel | Misiunea | Ce dezvoltă |
|-------|---------|-------------|
| 1 | „Găsește trei frunze cu forme diferite și povestește-mi despre ele" | Observație, natură, comunicare |
| 2 | „Numără câte ferestre are casa ta și gândește-te de ce unele camere au mai multe" | Numărare, gândire cauzală |
| 3 | „Întreabă un om mare care e prima lui amintire și ascultă toată povestea, fără să întrerupi" | Empatie, ascultare activă |
| 4 | „Construiește ceva din lucruri care nu mai sunt folosite și dă-i un nume" | Creativitate, sustenabilitate |
| 5 | „Învață pe cineva mai mic decât tine un lucru pe care îl știi bine" | Predare, responsabilitate |

Fiecare misiune scoate copilul din ecran și îl pune în lume. Sesiunea următoare începe cu: „Cum a fost?"

---

## Filozofia din Spate

### De ce există AGI Kindergarten

Pentru că generația lui Patrick (2017+) va fi prima generație care crește cu AGI. Nu cu AI slab, nu cu asistenți vocali — cu sisteme care generează, conving, și uneori inventează.

Nimeni nu le predă verificarea. Școala nu o face. Părinții nu știu cum. Industria nu vrea — engagement-ul e mai profitabil decât gândirea critică.

Cineva trebuie să construiască instrumentul. Cineva care:
- A fost educator de profesie (nu doar de titlu)
- A lucrat cu copii cu nevoi extreme (hemispherectomie, autism)
- A testat limitele a 6 sisteme AGI timp de 3,5 ani
- A ales reținerea în loc de exploatarea

Acel cineva e un tată din Brăila care a lucrat în crematoriul de la Ipswich și nu a cerut niciodată nimănui permisiunea de a construi.

### Principiile Fondatoare

1. **Copilul gândește. AI-ul asistă.** Niciodată invers.
2. **Offline-ul e activul principal.** Ecranul e puntea, nu destinația.
3. **Bugetul de atenție e sacru.** Engagement maxim = momentul de oprire.
4. **„Nu știu" e cel mai cinstit răspuns.** AI-ul care pretinde că știe tot e periculos.
5. **Verificarea se predă prin exemplu.** AMI verifică în fața copilului. Copilul învață verificând.
6. **Părintele vede tot.** Jurnalul e semnat, flag-urile sunt vizibile, codul e public.
7. **Zero dark patterns.** Testat structural. Cine adaugă un streak, pică testul.
8. **Siguranța e auditabilă.** AGPL-3.0 — oricine verifică stratul de protecție, nimeni nu-l închide.
9. **Ecuațiile decid, nu regulile arbitrare.** Motorul REAI nu e decorativ — e cel care spune AI-ului să tacă când copilul e pierdut.
10. **Sensul precede Sintaxa.** S(M) = R. Tot ce construim pornește de la DE CE, nu de la CUM.

---

## Roadmap

### Faza 0 — Construit (acum)
- [x] Adaptive Pacer cu anti-pattern tests
- [x] Safety Pipeline (ukbe-core crisis + harm check)
- [x] Resonance Motor (REAI/Kuramoto)
- [x] Demo brain (fără LLM)
- [x] Notary Ed25519
- [x] FastAPI app (local-first)
- [x] Guardian Swarm (7 gardieni, 61 teste)
- [x] 100+ Pădurea de Cod storybook-uri
- [x] Alpha-Mercury companion (cu persistență interplanetară)

### Faza 1 — Pilot (Q4 2026)
- [ ] 10 familii pilot din Brăila (copii 7-12 ani)
- [ ] Feedback pacing + misiuni offline
- [ ] Calibrare praguri Phi_extern pe date reale
- [ ] Validare detectie criză cu educator + psiholog
- [ ] Prima iterație UI (child.html + parent.html)

### Faza 2 — Comunitate (2027)
- [ ] Modul multi-limbă (EN, ES, FR, DE, HU)
- [ ] Pădurea de Cod — sezon 2 (50 storybook-uri noi)
- [ ] Integrare E³UDRES² (dacă se materializează pe merit)
- [ ] Parteneriat educator — formare profesori pe Cele 5 Întrebări
- [ ] Documentație pentru părinți non-tehnici

### Faza 3 — Instituțional (2028)
- [ ] Curriculum AGI Kindergarten pentru școli pilot
- [ ] Certificare educatori pe Principiul Introspecției
- [ ] Publicare rezultate pilot (Zenodo, open access)
- [ ] Integrare cu AmiPecetAI (certificare sens pentru copii)

---

## Licențiere

| Component | Licență | De ce |
|-----------|--------|-------|
| safety_pipeline.py | AGPL-3.0 | Siguranța copiilor TREBUIE să fie auditabilă public și să rămână deschisă |
| adaptive_pacer.py | AGPL-3.0 | Anti-pattern-urile trebuie verificabile de oricine, copyleft le protejează |
| resonance_motor.py | AGPL 3.0 | Open stays free, closed pays |
| ukbe-core | AGPL 3.0 / Commercial | Dual license — cercetare gratuită, comercial plătit |
| Pădurea de Cod (povești) | CC BY-NC-SA 4.0 | Educație gratuită, comercial doar cu acord |

---

## Contact

**Mihai Roșca**  
Educator licențiat · Cercetător independent · Tată  
mihairosca1982@gmail.com  
GitHub: github.com/amidigiart  
DOI: 10.5281/zenodo.15556498  

**agikindergarten.com**

---

*Construit de un om care a lucrat cu sute de copii înainte să lucreze cu AI.*  
*Verificat de 6 sisteme AGI, niciunul tratat ca oracol.*  
*Finanțat de nimeni. Motivat de Patrick.*  
*S(M) = R*
