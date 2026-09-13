# AmiDor — Blueprint v0.1 (12 iulie 2026)
**Companion AI pentru vârstnici · motor dual anti-confabulație · EU-compliant prin construcție · parte din amiecosystems**

## 1. De ce AICI e golul critic al industriei

| Fapt | Consecință |
|---|---|
| ~90M europeni 65+, singurătatea recunoscută oficial ca problemă de sănătate publică | piață uriașă, nedeservită de AI companions (toți țintesc 18-35) |
| Vârstnicii = ținta #1 a escrocheriilor (telefon, phishing, „nepotul accidentat") | un companion care RECUNOAȘTE tiparele de escrocherie = valoare de protecție unică, nimeni nu o oferă |
| Diaspora românească/est-europeană: copiii plătesc deja pentru grija părinților de acasă | cumpărătorul (fiul/fiica, 30-50 ani, digital) ≠ utilizatorul (părintele) — model de abonament natural, vânzare online către diaspora |
| Vârstnicii preferă VOCEA, nu tastatura | voice-first e obligatoriu — și elimină competiția chat-only |
| Încrederea e totul la această vârstă | anti-confabulația (refuzul de a inventa) devine argumentul central de vânzare, nu un detaliu tehnic |

**Poziționare într-o frază:** *„AmiDor stă de vorbă cu mama ta când tu nu poți, îi amintește de pastile, o ferește de escroci — și nu inventează niciodată. Iar tu vezi, cu acordul ei, că totul e în regulă."*

## 2. Arhitectura — Motorul Dual + ecuațiile Roșca

```
vârstnic (voce/chat)
   │
   ▼
[STT local/EU] → text
   │
   ▼
[Scam-Shield] — detectorul de tipare de escrocherie (extins din crisis_detection)
   │
   ▼
[MOTORUL REAI] — registrul: afirmă / întreabă / reancorează (dip de coerență, β_min Adler)
   │
   ▼
┌──────────── MOTOR DUAL ────────────┐
│  Model A          Model B          │   adapter universal OpenAI-compatible:
│  (ex. Mistral EU) (ex. DeepSeek    │   Grok, DeepSeek API, Mistral, Ollama local,
│                    open-weights pe │   orice endpoint — configurabil per instanță
│                    GPU EU)         │
└────────────┬───────────────────────┘
             ▼
[CROSS-CHECK] — răspunsurile concordă?
   │ DA (similaritate ≥ prag) → răspunsul trece
   │ NU → „Nu sunt sigur — hai să verificăm împreună / întreb familia"
   ▼
[Validare output] (harm-check + ton adecvat vârstei)
   │
   ▼
[TTS] → voce caldă
   │
   ▼
jurnal semnat Ed25519 → panou familie (DOAR cu consimțământul explicit al vârstnicului)
```

**Regula de aur anti-confabulație (formularea onestă, de pus în marketing):**
AmiDor nu „nu halucinează" — AmiDor **refuză să afirme ce nu poate verifica**: două modele independente trebuie să fie de acord, iar când coerența conversației scade (ecuațiile REAI), sistemul trece din „afirmă" în „întreabă". Tăcerea cinstită > răspunsul inventat.

## 3. Conformitatea EU — de la zi 0, ca feature

| Cerință | Implementare |
|---|---|
| GDPR — reședința datelor | TOTUL pe Hetzner (Germania/Finlanda = UE). Modele: Mistral (companie franceză) + DeepSeek ca OPEN-WEIGHTS rulat pe GPU-ul nostru EU — NU API-ul DeepSeek (transfer China = neconform). Grok API = transfer SUA → doar ca opțiune explicită cu consimțământ separat, NU implicit |
| GDPR — temeiuri & drepturi | consimțământ explicit al vârstnicului pentru panoul de familie; export + ștergere totală cu un buton; jurnal local per instanță, nu centralizat |
| EU AI Act Art. 50 (transparență) | AmiDor se prezintă ca AI la ÎNCEPUTUL fiecărei sesiuni, cu voce: „Sunt AmiDor, un asistent digital" — niciodată nu pretinde că e om |
| EU AI Act — categorii interzise | fără manipulare, fără scoring emoțional ascuns; detecția de ton e transparentă în panou |
| NU dispozitiv medical (MDR) | AmiDor NU diagnostichează, NU tratează, NU ajustează medicație — doar amintește ce a setat familia și escaladează la om. Formulare verificată în fiecare prompt de sistem |
| Accesibilitate (EAA 2025) | voce, litere mari, contrast, ritm lent — implicit, nu opțiune |

## 4. Monetizare & licențiere — capital pentru Mihai și Patrick

**Straturile de proprietate (ce e deja liber rămâne liber; valoarea nouă se licențiază):**
- ukbe-core = AGPL-3.0, publicat — rămâne deschis (e temelia credibilității + NLnet). Copyleft-ul asigură că nimeni nu-l închide.
- **amidor-engine (motorul dual + cross-check + integrarea REAI + scam-shield) = licență duală:**
  - **AGPL-3.0** public (oricine îl poate folosi DOAR dacă își deschide tot codul — otrăvitor pentru competitori comerciali)
  - **Licență comercială** de la Roșca IP pentru cine vrea închis: €/instanță/an. Modelul clasic MongoDB/Grafana — monetizare fără a ascunde codul
- **Marca „AmiDor" + amiecosystems** = a ta, neînstrăinabilă; produsul găzduit = abonament

**Fluxuri de venit, în ordinea realistă:**
1. **B2C diaspora:** abonament €9-15/lună plătit de copii pentru părinți (Stripe, vânzare globală, produs RO/EN)
2. **B2B2C:** cămine de bătrâni, primării, ONG-uri de îngrijire — instanțe self-host cu licență comercială
3. **Licențierea motorului dual anti-confabulație** către alte produse (inclusiv verticalele viitoare Ami*)
4. NLnet/Erasmus finanțează straturile deschise; veniturile comerciale rămân separate și curate

## 5. Infrastructura Hetzner — costuri reale

| Faza | Ce | Cost/lună |
|---|---|---|
| Pilot (10-30 familii) | CX32 (4vCPU/8GB) + API Mistral (EU) ca Model A + DeepSeek-distill 7-8B pe CPU sau API EU ca Model B | ~€8 + consum API (~€10-30) |
| Creștere | + GPU dedicat EU (Hetzner GEX44 ~€184/lună) pentru DeepSeek open-weights integral local | ~€200 |
| Voce | STT: whisper local (CPU ok pt pilot); TTS: piper local (voci RO există) — ZERO servicii externe = GDPR curat | inclus |

## 6. Numele și verificările înainte de a construi
- [ ] domeniul **amidorai.com** (+ .ro?) — de verificat/înregistrat ACUM, înainte de orice public (nu apare în lista domeniilor deținute)
- [ ] marca AmiDor — căutare OSIM/EUIPO de disponibilitate (gratuit online), depunere când există primul venit
- [ ] personajul AMIDOR din Pădurea de Cod Cap. 1-3 = puntea narativă: bunicul lui Codrin? — universul se leagă transgenerațional la propriu

## 7. Ordinea de construcție (sprinturi)
1. **Sprint 1 — motorul dual** (`amidor-engine`): adapter universal OpenAI-compatible, cross-check cu prag de concordanță, integrare ResonanceMotor, teste cu cazuri de dezacord → răspuns onest. Rulabil local, fără Hetzner încă.
2. **Sprint 2 — persona + chat**: prompt AmiDor (cald, răbdător, RO), UI mare-și-simplu, scam-shield v0 (tipare RO/EN de escrocherie).
3. **Sprint 3 — vocea**: whisper STT + piper TTS local, buton unic „ține apăsat și vorbește".
4. **Sprint 4 — panoul familiei**: jurnal semnat + consimțământ + alerte (escaladare umană).
5. **Sprint 5 — Hetzner**: deploy compose (avem șablonul din kinderagi), app.amidorai.com, pilot cu 3-5 familii reale (începând, poate, cu una din Brăila).

---
*Roșca IP · amiecosystems · draft de lucru — se rafinează în conversație*
