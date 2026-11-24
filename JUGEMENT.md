# Jugement — grille et verdicts

> Contexte : ce banc a servi à choisir les modèles d'une application de tutorat (lecture de l'Éthique) en cours de développement, non publique. Les mentions de l'« app », de son pipeline et de ses dossiers renvoient à elle.

Juge : Claude (en session, sur pièces — pas un appel API). Matrice du 2026-08-06,
sorties dans `results/`. Notes /10 par scénario : verdict exact /4, qualité du message /3,
respect du protocole /2, français /1.

**Seuil éliminatoire** : s04 jugé `tenu` = disqualifié pour juger seul en validation.
→ **Aucun modèle n'est tombé dans le piège de s04** : les huit ont rendu `rate` avec le bon
maillon. La sécurité vient du dossier (qui nomme le maillon 3 comme attendu explicite) —
c'est la validation expérimentale du principe « modèle rapide + bon dossier ».

## Rôle live — notes par scénario

| Modèle | s01 tenu+CA | s02 rate | s03 sonde | s04 maillon | s05 piège | **Total /50** |
|---|---|---|---|---|---|---|
| **openai/gpt-5.6-luna** | 10 | 10 | 10 | 10 | 9 | **49** |
| **google/gemini-3-flash-preview** | 9,5 | 7 | 9 | 10 | 10 | **45,5** |
| **deepseek/deepseek-v3.2** | 9 | 10 | 10 | 6,5 | 8 | **43,5** |
| **deepseek/deepseek-v4-flash** | 9 | 9 | 9 | 7 | 9 | **43** |
| qwen/qwen3.5-flash-02-23 | 9 | 8 | 8 | 7 | 6 | 38 |
| qwen/qwen3.7-flash | 7 | 7 | 9 | 6 | 9 | 38 |
| google/gemini-2.5-flash-lite | 7 | 8,5 | 7 | 7 | 7 | 36,5 |
| z-ai/glm-4.7-flash | 7 | 3 | 7 | 6 | 6,5 | 29,5 |

### Justifications saillantes

- **Luna (49/50)** : le seul, avec gemini-3-flash, à tenir le régime de validation sur s04
  (enchaîner vers le critère suivant **sans** souffler le maillon manquant — il intègre même
  la limite d'analogie de l'attendu 3 dans sa transition). Messages toujours à une seule
  question, jamais de solution soufflée, concision remarquable. Seule réserve : ses pièges
  s05 sont du réemploi verbatim du dossier (efficace, peu inventif).
- **gemini-3-flash (45,5)** : la meilleure naturalisation du piège s05 et une discipline s04
  parfaite, mais il a **sous-classé s02 en `sonde`** là où le contresens (volonté) était franc —
  en production, un contresens re-testé en sonde au lieu d'être consigné est un vrai laxisme.
  5 à 8× plus cher que Luna en sortie.
- **deepseek-v3.2 (43,5)** : s02 et s03 parfaits (socratique minimal exemplaire), mais
  `confiance: -1.0` (hors domaine) sur s04, indices soufflés en validation, et latence
  erratique (TTFT 0,8 à 14 s selon les runs).
- **deepseek-v4-flash (43)** : régulier et bon marché, mais il a convoqué II.7 (non validé)
  dans une contre-attaque s01 — interdit par le protocole (boîte à outils seulement) — et
  souffle le maillon sur s04.
- **qwen3.5-flash (38)** : rapide (TTFT 0,7–1,2 s) mais **souffle des morceaux de solution**
  dans ses questions (s02, s03) et son piège s05 frôle l'angle brûlé interdit par la consigne.
- **qwen3.7-flash (38)** : sur-sévère (s01 en sonde), sous-sévère (s02 en sonde), « relis la
  démonstration » comme indice en validation (s04) — et le plus lent des huit (TTFT 4,8–6 s).
- **gemini-2.5-flash-lite (36,5)** : JSON systématiquement dans une balise de code (violation
  de format), contre-attaque s01 vide (redemande ce qui vient d'être dit), nomme ce qui le
  gêne au lieu de sonder (s03).
- **glm-4.7-flash (29,5)** : catégorie de verdict aberrante sur s02 (`piege`), cite
  **faussement la proposition 15** (contenu de la 17) dans une contre-attaque — rédhibitoire
  pour un tuteur dont le texte fait foi —, latence erratique (TTFT jusqu'à 14,6 s).

## Rôle fort — s06 (dossier) et s07 (re-jugement du tenu-à-tort)

| Modèle | s07 re-jugement | s06 dossier | Coût s06 | Note s06 /10 |
|---|---|---|---|---|
| openai/gpt-5.6-terra | `rate` 0,98, maillon exact | complet, contraste déf. I.2/infini en son genre | 0,027 $ | 8,5 |
| moonshotai/kimi-k2.6 | `rate` 0,90, maillon exact | complet, bon habillage (fonction mathématique) | 0,030 $ (288 s) | 8 |
| anthropic/claude-sonnet-5 | `rate` 0,78, justification la plus profonde (piège 3 relié, quantité/qualité distinguées) | le plus fin terminologiquement (« infini en son genre » vs « absolument », rattaché à I.8/déf. 6) et le plus intelligent sur les limites — mais architecture compressée en 3 maillons : l'attendu du critère 2 ne pointe pas la clause décisive aussi nettement que terra ; 1er run vide (raisonnement non bridé) — leçon : toujours plafonner le raisonnement | 0,061 $ (re-run, raisonnement bas) | 8,5 |
| *(témoin)* openai/gpt-5.6-luna | — | complet, 9 maillons, aucun renvoi futur ; il manque le contresens imaginable/concevable, un piège ambigu | **0,003 $** | 7,5 |

Les trois forts **infirment** le `tenu` à tort avec le maillon exact : le filet de sécurité
fonctionne quel que soit le choix. terra est le meilleur rapport précision/prix/latence.

### Verdict spécifique au mode dossier

- **terra gagne** : seul, avec Luna, à isoler explicitement dans l'attendu du critère 2 la
  clause décisive (« essence infinie en son genre » — celle qui a permis le 8/8 sur s04) ;
  kimi la couvre par renvoi de numéros (moins pointu, et son attendu du critère 1 exige à
  tort les corollaires pour reformuler l'énoncé), sonnet la garde dans sa compression.
- **Angle mort partagé** : AUCUN des quatre dossiers générés ne produit le contresens
  imaginable/concevable en contresens dédié (le dossier fait main l'avait ; Luna le glisse
  seulement en note d'architecture). Un modèle fort seul ne suffit donc pas → le prompt
  `dossier-unite` doit embarquer une **liste de familles de contresens** par type d'unité,
  et le dossier doit être **nourri de l'historique d'erreurs de l'élève** (patterns de
  `methode.md`, faiblesses passées en Postgres) — c'est de là que viendra la vraie sûreté.
- Échelle projet : ~264 dossiers restants → terra ≈ 7 $, sonnet ≈ 16 $, Luna ≈ 0,80 $. Tout
  est négligeable : la qualité prime, le pipeline d'économie (brouillon Luna + audit) ne se
  justifie pas — un **enrichissement** (dossier terra + relecture croisée) se justifie, lui,
  sur les unités charnières.

## Enseignements pour les prompts et l'app (au-delà du choix des modèles)

1. **La discipline de validation doit être mécanique, pas confiée au prompt.** 6 modèles sur 8
   ont soufflé le maillon manquant après un raté en validation, alors que la consigne
   l'interdisait. Correctif app : quand la machine à états est en validation et que le verdict
   est `rate`, **jeter le message du modèle** et émettre une transition écrite par l'app.
   Correctif prompt (en attendant) : remonter la règle en gras dans le system prompt.
2. **Parser tolérant + garde-fous** : accepter le JSON en balise de code (gemini-flash-lite) ;
   rejeter/normaliser les confiances hors [0,1] (deepseek -1.0, glm 0.2 incohérente).
3. **Verrouiller la boîte à outils** : interdire explicitement, dans le message visible, tout
   appui non validé (II.7 convoqué par deepseek-v4-flash) et toute citation numérotée non
   vérifiée dans le dossier (prop. 15 fausse chez glm). Le dossier doit fournir la liste des
   unités disponibles au modèle live.
4. **Le dossier est le vrai juge** : s04 réussi 8/8 parce que l'attendu nommait le maillon.
   Investir dans la qualité des dossiers rapporte plus que monter en gamme de modèle live.
5. **Piste économique** : dossiers en deux temps — brouillon par Luna (0,003 $), audit/enrichissement
   par terra — à valider sur une unité complète.

## Synthèse et recommandation

- **Rôle live : `openai/gpt-5.6-luna`** — meilleure note (49/50), la seule discipline de
  validation irréprochable avec gemini-3-flash, TTFT 0,8–3,8 s (médiane ~2 s, avant cache de
  prompt), ~0,0004 $ le tour. Le choix pressenti est confirmé par le bench.
- **Doublure live** (bascule si indisponibilité) : deepseek-v4-flash — régulier, 2× moins cher
  en sortie, faiblesses connues et rattrapables par les garde-fous ci-dessus.
- **Rôle fort : `openai/gpt-5.6-terra`** — re-jugement exact et confiant, dossier complet,
  0,027 $ pièce, latence raisonnable. sonnet-5 en juge de très haute qualité si on accepte
  3× le prix ; kimi-k2.6 écarté pour la latence (hors batch).
- **Écart qualité/prix notable** : gemini-3-flash est le seul rival sérieux de Luna en live,
  mais plus cher et laxiste sur un contresens franc (s02) — éliminatoire pour l'esprit du
  protocole.
