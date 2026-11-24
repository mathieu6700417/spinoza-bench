#!/usr/bin/env python3
"""Bench des prompts de l'app-tuteur Spinoza sur OpenRouter.

Usage :
  python3 run.py --scenarios all --roles live            # matrice scénarios live × modèles live
  python3 run.py --scenarios s06,s07 --roles fort
  python3 run.py --scenarios s01 --models openai/gpt-5.6-luna
  python3 run.py --report                                # tableau récapitulatif des runs

Chaque run écrit results/<scenario>/<modele>.md (métriques + sortie brute)
et une ligne dans results/runs.jsonl. Le jugement de qualité est manuel
(voir JUGEMENT.md) : ce script ne mesure que latence, débit et coût.
"""
import argparse, concurrent.futures, json, os, pathlib, re, sys, time

import requests

RACINE = pathlib.Path(__file__).parent
API = "https://openrouter.ai/api/v1/chat/completions"
CLE = os.environ.get("OPENROUTER_API_KEY")

def charger_pricing():
    cache = RACINE / "data" / "pricing.json"
    if cache.exists():
        return json.loads(cache.read_text())
    r = requests.get("https://openrouter.ai/api/v1/models", timeout=30)
    r.raise_for_status()
    prix = {m["id"]: {"in": float(m["pricing"].get("prompt", 0)),
                      "out": float(m["pricing"].get("completion", 0))}
            for m in r.json()["data"]}
    cache.write_text(json.dumps(prix))
    return prix

def rendre_template(nom, variables):
    texte = (RACINE / "prompts" / f"{nom}.md").read_text()
    for cle, val in variables.items():
        if isinstance(val, str) and val.startswith("@"):
            val = (RACINE / val[1:]).read_text()
        texte = texte.replace("{{" + cle + "}}", val or "")
    reste = re.findall(r"\{\{(\w+)\}\}", texte)
    if reste:
        raise ValueError(f"variables non renseignées dans {nom}: {reste}")
    return texte

def message_utilisateur(scenario):
    if scenario["template"] in ("dossier-unite", "ecritures"):
        return scenario.get("reponse") or "Exécute la tâche décrite dans le prompt système."
    morceaux = []
    if scenario.get("transcript"):
        lignes = []
        for tour in scenario["transcript"]:
            (role, texte), = tour.items()
            lignes.append(f"**{'Tuteur' if role == 'tuteur' else 'Élève'}** : {texte}")
        morceaux.append("## TRANSCRIT DU DIALOGUE\n\n" + "\n\n".join(lignes))
    if scenario.get("reponse"):
        etiquette = ("RÉPONSE DE L'ÉLÈVE AU CRITÈRE" if scenario["template"] == "validation-juge"
                     else "RÉPONSE DE L'ÉLÈVE À JUGER")
        morceaux.append(f"## {etiquette}\n\n" + scenario["reponse"])
    if not morceaux or scenario.get("reponse") is None and scenario["template"] == "tuteur-dialogue":
        morceaux.append("(La parole est au tuteur : exécute la TÂCHE du point visé.)")
    return "\n\n".join(morceaux)

def appeler(modele, params, systeme, utilisateur):
    charge = {
        "model": modele,
        "messages": [{"role": "system", "content": systeme},
                     {"role": "user", "content": utilisateur}],
        "stream": True,
        "usage": {"include": True},
        **params,
    }
    entetes = {"Authorization": f"Bearer {CLE}", "Content-Type": "application/json"}
    debut = time.monotonic()
    premier, usage, morceaux = None, {}, []
    with requests.post(API, json=charge, headers=entetes, stream=True, timeout=300) as rep:
        if rep.status_code != 200:
            return {"erreur": f"HTTP {rep.status_code}: {rep.text[:500]}"}
        for ligne in rep.iter_lines():
            if not ligne or not ligne.startswith(b"data: "):
                continue
            brut = ligne[6:]
            if brut == b"[DONE]":
                break
            try:
                bloc = json.loads(brut)
            except json.JSONDecodeError:
                continue
            if bloc.get("usage"):
                usage = bloc["usage"]
            for choix in bloc.get("choices", []):
                delta = choix.get("delta", {}).get("content")
                if delta:
                    if premier is None:
                        premier = time.monotonic()
                    morceaux.append(delta)
    fin = time.monotonic()
    return {
        "sortie": "".join(morceaux),
        "ttft_s": round(premier - debut, 2) if premier else None,
        "total_s": round(fin - debut, 2),
        "tokens_entree": usage.get("prompt_tokens"),
        "tokens_sortie": usage.get("completion_tokens"),
        "tokens_raisonnement": (usage.get("completion_tokens_details") or {}).get("reasoning_tokens"),
    }

def lancer_run(scenario, entree_modele, role, pricing):
    modele = entree_modele["id"]
    defauts = json.loads((RACINE / "models.json").read_text())["params_defaut"].get(role, {})
    params = {**defauts, **entree_modele.get("params", {})}
    systeme = rendre_template(scenario["template"], scenario.get("vars", {}))
    utilisateur = message_utilisateur(scenario)
    print(f"→ {scenario['id']} × {modele}", flush=True)
    for essai in range(3):
        res = appeler(modele, params, systeme, utilisateur)
        if "erreur" not in res or "429" not in res.get("erreur", ""):
            break
        time.sleep(5 * (essai + 1))
    prix = pricing.get(modele, {"in": 0, "out": 0})
    if res.get("tokens_entree") is not None:
        res["cout_usd"] = round(res["tokens_entree"] * prix["in"]
                                + (res["tokens_sortie"] or 0) * prix["out"], 6)
    res |= {"scenario": scenario["id"], "modele": modele, "role": role,
            "horodatage": time.strftime("%Y-%m-%d %H:%M:%S")}
    dossier = RACINE / "results" / scenario["id"]
    dossier.mkdir(parents=True, exist_ok=True)
    lisible = modele.replace("/", "__")
    corps = res.pop("sortie", "")
    (dossier / f"{lisible}.md").write_text(
        "```json\n" + json.dumps(res, ensure_ascii=False, indent=2) + "\n```\n\n"
        "## SORTIE BRUTE\n\n" + (corps or f"(vide — {res.get('erreur', '?')})") + "\n")
    with open(RACINE / "results" / "runs.jsonl", "a") as flux:
        flux.write(json.dumps(res, ensure_ascii=False) + "\n")
    return res

def rapport():
    lignes = [json.loads(l) for l in open(RACINE / "results" / "runs.jsonl")]
    derniers = {}
    for l in lignes:
        derniers[(l["scenario"], l["modele"])] = l
    print(f"{'scén.':<6}{'modèle':<42}{'TTFT':>6}{'total':>7}{'t.out':>7}{'coût $':>10}  err")
    for (s, m), l in sorted(derniers.items()):
        print(f"{s:<6}{m:<42}{l.get('ttft_s') or '—':>6}{l.get('total_s') or '—':>7}"
              f"{l.get('tokens_sortie') or '—':>7}{l.get('cout_usd', '—'):>10}  "
              f"{(l.get('erreur') or '')[:40]}")

def principal():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenarios", default="all")
    ap.add_argument("--roles", default=None, help="live, fort, live_temoin (défaut : ceux du scénario)")
    ap.add_argument("--models", default=None, help="ids explicites, séparés par des virgules")
    ap.add_argument("--concurrency", type=int, default=6)
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()
    if args.report:
        rapport(); return
    if not CLE:
        sys.exit("OPENROUTER_API_KEY absente de l'environnement")
    pricing = charger_pricing()
    catalogue = json.loads((RACINE / "models.json").read_text())
    scenarios = []
    for f in sorted((RACINE / "scenarios").glob("*.json")):
        sc = json.loads(f.read_text())
        if args.scenarios == "all" or sc["id"] in args.scenarios.split(","):
            scenarios.append(sc)
    travaux = []
    for sc in scenarios:
        roles = args.roles.split(",") if args.roles else sc["roles"]
        for role in roles:
            if role not in sc["roles"]:
                continue
            if args.models:
                entrees = [{"id": m} for m in args.models.split(",")]
            else:
                entrees = catalogue.get(role, [])
            for entree in entrees:
                travaux.append((sc, entree, role))
    print(f"{len(travaux)} runs à lancer")
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        avenirs = [pool.submit(lancer_run, sc, e, r, pricing) for sc, e, r in travaux]
        for a in concurrent.futures.as_completed(avenirs):
            res = a.result()
            etat = res.get("erreur", f"ok {res.get('total_s')}s")
            print(f"✓ {res['scenario']} × {res['modele']} — {etat}", flush=True)

if __name__ == "__main__":
    principal()
