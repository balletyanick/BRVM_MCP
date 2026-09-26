# -*- coding: utf-8 -*-
"""
MANSA — interface web locale.

Sert une interface de discussion connectee au meme agent que Claude Code :
  - CLAUDE.md du projet (regles d'investissement, portefeuille, watchlist)
  - memoire persistante ~/.claude/projects/<projet>/memory/
  - serveur MCP brvm-server (cours, RSI, screener temps reel)
  - fichiers locaux du dossier BRVM (lecture et ecriture)
  - recherche et lecture web (Sikafinance, BRVM, Madis Invest)

Lancer :  python server.py      puis ouvrir http://127.0.0.1:8765
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Any, AsyncIterator

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    PermissionResultAllow,
    PermissionResultDeny,
    ResultMessage,
    StreamEvent,
    SystemMessage,
    TextBlock,
    ToolPermissionContext,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROJET = Path(__file__).resolve().parent.parent       # ...\Desktop\BRVM
STATIC = Path(__file__).resolve().parent / "static"
HOTE = os.environ.get("MANSA_HOST", "127.0.0.1")
PORT = int(os.environ.get("MANSA_PORT", "8765"))
MODELE = os.environ.get("MANSA_MODEL", "claude-opus-5")

# Instructions propres a la surface web. Le reste du comportement vient de
# CLAUDE.md et de la memoire, exactement comme dans Claude Code.
APPEND_SYSTEME = """
Tu reponds dans une interface web de discussion, pas dans un terminal.

- Le markdown est rendu : utilise titres, listes et tableaux normalement.
- Pas d'art ASCII ni d'encadres faits de caracteres. Un vrai tableau markdown
  a la place.
- Les blocs de code servent aux chiffres alignes et aux extraits de code,
  pas a encadrer du texte courant.
- Les liens markdown sont cliquables : cite tes sources ainsi.
- Reste concis. L'utilisateur lit sur un ecran, pas dans un rapport imprime.

Le reste de ton cadre de travail vient de CLAUDE.md et de ta memoire projet.
Applique-le sans exception, notamment le rafraichissement obligatoire des
donnees MCP et la verification de l'actualite avant toute recommandation.
"""

# Motifs bash refuses. L'agent peut tout lire et ecrire dans le projet, mais
# pas detruire le disque ni pousser du code a l'exterieur sans passer par toi.
BASH_INTERDIT = [
    "rm -rf /", "rm -rf ~", "rm -rf c:", ":(){", "mkfs", "dd if=",
    "format ", "del /s", "rd /s", "rmdir /s", "shutdown", "reg delete",
    "git push --force", "git push -f", "> /dev/sda", "chmod -r 777 /",
]

TOOLS_LECTURE = {
    "Read", "Glob", "Grep", "WebSearch", "WebFetch", "TodoWrite",
    "NotebookRead", "Task", "Agent", "Skill",
}


# ---------------------------------------------------------------------------
# Permissions
# ---------------------------------------------------------------------------

async def autoriser_outil(
    nom: str, entree: dict[str, Any], ctx: ToolPermissionContext
) -> PermissionResultAllow | PermissionResultDeny:
    """Autorise tout sauf les commandes shell destructrices."""
    if nom == "Bash":
        cmd = str(entree.get("command", "")).lower()
        for motif in BASH_INTERDIT:
            if motif in cmd:
                return PermissionResultDeny(
                    behavior="deny",
                    message=(
                        f"Commande bloquee par MANSA (motif « {motif.strip()} »). "
                        "Explique ce que tu voulais faire, Ballet la lancera "
                        "lui-meme s'il est d'accord."
                    ),
                    interrupt=False,
                )
    return PermissionResultAllow(behavior="allow")


def construire_options(reprendre: str | None = None) -> ClaudeAgentOptions:
    return ClaudeAgentOptions(
        # Le prompt Claude Code + une note sur la surface web.
        system_prompt={
            "type": "preset",
            "preset": "claude_code",
            "append": APPEND_SYSTEME,
        },
        # Charge CLAUDE.md, .claude/, les skills et les reglages.
        # La memoire projet et les serveurs MCP de ~/.claude.json sont lus
        # de toute facon, quel que soit ce reglage.
        setting_sources=["user", "project", "local"],
        cwd=str(PROJET),
        model=MODELE,
        permission_mode="acceptEdits",
        can_use_tool=autoriser_outil,
        include_partial_messages=True,      # streaming mot a mot
        # Rend le raisonnement visible dans l'interface, comme dans le terminal.
        thinking={"type": "adaptive", "display": "summarized"},
        skills="all",
        resume=reprendre,
        env={"PYTHONIOENCODING": "utf-8"},
    )


# ---------------------------------------------------------------------------
# Conversations
# ---------------------------------------------------------------------------

class Conversation:
    """Un client Agent SDK vivant, une conversation."""

    def __init__(self, cle: str, reprendre: str | None = None) -> None:
        self.cle = cle
        self.client: ClaudeSDKClient | None = None
        self.session_id: str | None = reprendre
        self.reprendre = reprendre
        self.verrou = asyncio.Lock()
        self.titre = "Nouvelle conversation"
        self.cree = time.time()
        self.cout = 0.0
        self.tours = 0

    async def demarrer(self) -> None:
        if self.client is None:
            self.client = ClaudeSDKClient(options=construire_options(self.reprendre))
            await self.client.connect()

    async def fermer(self) -> None:
        if self.client is not None:
            try:
                await self.client.disconnect()
            except Exception:
                pass
            self.client = None


CONVERSATIONS: dict[str, Conversation] = {}


def obtenir(cle: str | None, reprendre: str | None = None) -> Conversation:
    if not cle or cle not in CONVERSATIONS:
        cle = cle or uuid.uuid4().hex[:12]
        CONVERSATIONS[cle] = Conversation(cle, reprendre)
    return CONVERSATIONS[cle]


# ---------------------------------------------------------------------------
# Mise en forme des evenements outil
# ---------------------------------------------------------------------------

def decrire_outil(nom: str, entree: dict[str, Any]) -> tuple[str, str]:
    """Retourne (libelle lisible, detail court)."""
    if nom.startswith("mcp__brvm-server__"):
        court = nom.split("__")[-1]
        ticker = entree.get("ticker") or ""
        detail = str(ticker)
        if not detail and entree:
            detail = ", ".join(f"{k}={v}" for k, v in list(entree.items())[:3])
        return f"BRVM · {court}", detail
    if nom.startswith("mcp__"):
        bouts = nom.split("__")
        return f"{bouts[1]} · {bouts[-1]}", ""

    simples = {
        "Read": ("Lecture", "file_path"),
        "Write": ("Ecriture", "file_path"),
        "Edit": ("Modification", "file_path"),
        "Glob": ("Recherche fichiers", "pattern"),
        "Grep": ("Recherche texte", "pattern"),
        "Bash": ("Commande", "command"),
        "WebSearch": ("Recherche web", "query"),
        "WebFetch": ("Page web", "url"),
        "TodoWrite": ("Plan", None),
        "Skill": ("Competence", "skill"),
        "Task": ("Sous-agent", "description"),
        "Agent": ("Sous-agent", "description"),
    }
    if nom in simples:
        libelle, cle = simples[nom]
        detail = ""
        if cle:
            brut = str(entree.get(cle, ""))
            if cle == "file_path":
                try:
                    brut = str(Path(brut).relative_to(PROJET))
                except Exception:
                    brut = Path(brut).name
            detail = brut[:160]
        return libelle, detail
    return nom, ""


def sse(evenement: str, donnees: dict[str, Any]) -> str:
    return f"event: {evenement}\ndata: {json.dumps(donnees, ensure_ascii=False)}\n\n"


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

app = FastAPI(title="MANSA")


class Envoi(BaseModel):
    message: str
    conversation: str | None = None
    reprendre: str | None = None


@app.get("/")
async def racine() -> FileResponse:
    return FileResponse(STATIC / "index.html")


@app.get("/api/etat")
async def etat() -> JSONResponse:
    """Ce que l'agent voit reellement : CLAUDE.md, memoire, MCP."""
    claude_md = PROJET / "CLAUDE.md"
    dossier_mem = (
        Path.home() / ".claude" / "projects"
        / "c--Users-Yanick-Desktop-BRVM" / "memory"
    )
    memoires: list[str] = []
    if dossier_mem.is_dir():
        memoires = sorted(p.name for p in dossier_mem.glob("*.md"))

    mcp: list[dict[str, Any]] = []
    try:
        cfg = json.loads((Path.home() / ".claude.json").read_text(encoding="utf-8"))
        for nom, conf in (cfg.get("mcpServers") or {}).items():
            mcp.append({"nom": nom, "type": conf.get("type", "stdio")})
    except Exception:
        pass

    fichiers = []
    for p in sorted(PROJET.iterdir()):
        if p.name.startswith(".") or p.name == "mansa":
            continue
        fichiers.append({"nom": p.name, "dossier": p.is_dir()})

    return JSONResponse({
        "projet": str(PROJET),
        "modele": MODELE,
        "claude_md": claude_md.is_file(),
        "claude_md_taille": claude_md.stat().st_size if claude_md.is_file() else 0,
        "memoires": memoires,
        "mcp": mcp,
        "fichiers": fichiers,
        "conversations": [
            {
                "cle": c.cle, "titre": c.titre, "tours": c.tours,
                "cout": round(c.cout, 4), "cree": c.cree,
            }
            for c in sorted(CONVERSATIONS.values(), key=lambda x: -x.cree)
        ],
    })


@app.get("/api/sessions")
async def sessions() -> JSONResponse:
    """Sessions Claude Code passees sur ce projet, reprenables."""
    try:
        from claude_agent_sdk import list_sessions
        trouvees = list(list_sessions(directory=str(PROJET), limit=25))
        return JSONResponse([
            {
                "session_id": s.session_id,
                "resume": (s.summary or "sans titre")[:110],
                "modifie": getattr(s, "last_modified", 0),
            }
            for s in trouvees
        ])
    except Exception as exc:
        return JSONResponse({"erreur": str(exc)}, status_code=200)


@app.post("/api/interrompre")
async def interrompre(envoi: Envoi) -> JSONResponse:
    conv = CONVERSATIONS.get(envoi.conversation or "")
    if conv and conv.client:
        try:
            await conv.client.interrupt()
            return JSONResponse({"ok": True})
        except Exception as exc:
            return JSONResponse({"ok": False, "erreur": str(exc)})
    return JSONResponse({"ok": False, "erreur": "conversation inconnue"})


@app.post("/api/effacer")
async def effacer(envoi: Envoi) -> JSONResponse:
    conv = CONVERSATIONS.pop(envoi.conversation or "", None)
    if conv:
        await conv.fermer()
    return JSONResponse({"ok": True})


@app.post("/api/chat")
async def chat(envoi: Envoi, requete: Request) -> StreamingResponse:
    conv = obtenir(envoi.conversation, envoi.reprendre)
    if conv.titre == "Nouvelle conversation":
        conv.titre = envoi.message.strip()[:60] or "Sans titre"

    async def flux() -> AsyncIterator[str]:
        yield sse("debut", {"conversation": conv.cle})

        if conv.verrou.locked():
            yield sse("erreur", {"message": "Une reponse est deja en cours."})
            return

        async with conv.verrou:
            try:
                await conv.demarrer()
            except Exception as exc:
                yield sse("erreur", {
                    "message": f"Impossible de demarrer l'agent : {exc}"
                })
                return

            assert conv.client is not None
            recu_du_texte = False

            try:
                await conv.client.query(envoi.message)

                async for msg in conv.client.receive_response():
                    if await requete.is_disconnected():
                        break

                    # --- streaming mot a mot -------------------------------
                    if isinstance(msg, StreamEvent):
                        ev = msg.event or {}
                        if ev.get("type") == "content_block_delta":
                            d = ev.get("delta") or {}
                            if d.get("type") == "text_delta":
                                recu_du_texte = True
                                yield sse("texte", {"t": d.get("text", "")})
                            elif d.get("type") == "thinking_delta":
                                yield sse("reflexion", {"t": d.get("thinking", "")})
                        elif ev.get("type") == "content_block_start":
                            bloc = ev.get("content_block") or {}
                            if bloc.get("type") == "text":
                                yield sse("bloc", {"genre": "texte"})
                            elif bloc.get("type") == "thinking":
                                yield sse("bloc", {"genre": "reflexion"})
                        continue

                    # --- appels d'outils -----------------------------------
                    if isinstance(msg, AssistantMessage):
                        for bloc in msg.content:
                            if isinstance(bloc, ToolUseBlock):
                                libelle, detail = decrire_outil(bloc.name, bloc.input)
                                yield sse("outil", {
                                    "id": bloc.id, "nom": bloc.name,
                                    "libelle": libelle, "detail": detail,
                                })
                            elif isinstance(bloc, TextBlock) and not recu_du_texte:
                                # Repli si le streaming partiel n'a rien donne.
                                yield sse("texte", {"t": bloc.text})
                        continue

                    # --- resultats d'outils --------------------------------
                    if isinstance(msg, UserMessage):
                        if isinstance(msg.content, list):
                            for bloc in msg.content:
                                if isinstance(bloc, ToolResultBlock):
                                    yield sse("resultat", {
                                        "id": bloc.tool_use_id,
                                        "erreur": bool(bloc.is_error),
                                    })
                        continue

                    if isinstance(msg, SystemMessage):
                        if msg.subtype == "init":
                            conv.session_id = msg.data.get("session_id")
                            yield sse("init", {
                                "session_id": conv.session_id,
                                "outils": len(msg.data.get("tools") or []),
                                "mcp": msg.data.get("mcp_servers") or [],
                            })
                        continue

                    # --- fin de tour ---------------------------------------
                    if isinstance(msg, ResultMessage):
                        conv.tours += 1
                        if msg.total_cost_usd:
                            conv.cout += msg.total_cost_usd
                        if msg.session_id:
                            conv.session_id = msg.session_id
                        yield sse("fin", {
                            "cout": round(msg.total_cost_usd or 0.0, 4),
                            "cout_total": round(conv.cout, 4),
                            "duree_ms": msg.duration_ms,
                            "tours": msg.num_turns,
                            "erreur": msg.is_error,
                            "session_id": msg.session_id,
                        })

            except Exception as exc:
                yield sse("erreur", {"message": f"{type(exc).__name__}: {exc}"})

    return StreamingResponse(
        flux(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# static apres les routes pour ne pas masquer /api
from fastapi.staticfiles import StaticFiles  # noqa: E402

app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")


def principal() -> None:
    import uvicorn

    if not (PROJET / "CLAUDE.md").is_file():
        print(f"  Attention : aucun CLAUDE.md dans {PROJET}", file=sys.stderr)

    print()
    print("  MANSA — interface locale")
    print(f"  Projet  : {PROJET}")
    print(f"  Modele  : {MODELE}")
    print(f"  Adresse : http://{HOTE}:{PORT}")
    print()
    print("  Ctrl+C pour arreter.")
    print()

    uvicorn.run(app, host=HOTE, port=PORT, log_level="warning")


if __name__ == "__main__":
    principal()