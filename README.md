# spinoza-bench

A prompt and model benchmark for a Spinoza reading tutor. It runs 5 prompts over 7 scenarios and builds a scenarios x models matrix through OpenRouter, measuring time to first token, duration, tokens and cost for each run.

Quality is judged against a written rubric (`JUGEMENT.md`). The outputs were graded scenario by scenario, against the rubric in a Claude session, on the raw outputs. No API call was used for grading.

Main finding: 6 of the 8 models gave the student the missing step of the proof after a failed answer, although the prompt said not to. So that rule moved out of the prompt and into the app's code. All 8 still caught the key trap (s04, a skipped step in the argument), because the reference dossier named the expected step.

Model choice: for the live dialogue role, `openai/gpt-5.6-luna` scored best (49/50) and no model fell into the key trap scenario (s04, a skipped step in the argument). For the strong role (unit dossiers, re-judging), `openai/gpt-5.6-terra` was retained.

The text of the Ethics used in `data/` is Charles Appuhn's French translation (1913), in the public domain. The rest of this README is in French.

## Run

```sh
pip install -r requirements.txt
export OPENROUTER_API_KEY=...
python3 run.py --scenarios all
```

---

# spinoza-bench — validation des prompts avant l'app

Banc d'essai des prompts de la future app-tuteur Spinoza (remplacement de la CLI `/spinoza`),
pour choisir les modèles OpenRouter les moins chers à qualité suffisante, rôle par rôle.

## Les rôles à pourvoir

- **live** — conduit le dialogue en direct (verdict JSON + relance, streaming). Candidats ≤ 0,30 $/M entrée.
- **fort** — dossier d'unité (batch), re-jugement des critères de validation, audit, écritures.

## Contenu

- `prompts/` — les 5 prompts de l'app, versionnés ici avant d'être embarqués : `tuteur-dialogue`,
  `validation-juge`, `dossier-unite`, `audit`, `ecritures`.
- `data/` — matériau réel : texte de I.16 (traduction de Charles Appuhn, 1913, domaine public), dossier d'unité de référence
  fait main, boîte à outils I.déf→I.15.
- `scenarios/` — 7 scénarios. s01 bonne réponse (tenu + contre-attaque), s02 erreur subtile (volonté),
  s03 formulation perfectible (sonde), **s04 maillon escamoté (LE test discriminant)**, s05 génération
  de piège, s06 dossier d'unité, s07 re-jugement fort du tenu-à-tort de s04.
- `run.py` — matrice scénarios × modèles, streaming, mesure TTFT / durée / tokens / coût.
- `results/` — un `.md` par run (métriques + sortie brute), `runs.jsonl` cumulatif.
- `JUGEMENT.md` — grille et verdicts (juge : Claude, en session — pas un appel API).

## Lancer

```sh
export OPENROUTER_API_KEY=...
python3 run.py --scenarios all              # tout (roles définis par scénario)
python3 run.py --scenarios s01 --models openai/gpt-5.6-luna
python3 run.py --report                     # tableau récapitulatif
```

Le jugement de qualité ne se fait pas ici : les sorties de `results/` sont lues et notées
dans `JUGEMENT.md` selon sa grille. La latence seule est objective ; la qualité est jugée
sur pièces, scénario par scénario.
