from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
import asyncio


BASE = Path(__file__).resolve().parent

app = FastAPI(title="Bot Yuyu - Quotex")

app.mount(
    "/static",
    StaticFiles(directory=BASE / "static"),
    name="static"
)


# =========================================================
# ESTADO DEL BOT
# =========================================================

class AccountState:

    def __init__(self):

        self.connected = False

        self.account_type = "DEMO"

        self.email = None

        # Saldo de prueba
        self.balance = 115722.81

        self.profit = 0.0

        self.wins = 0

        self.losses = 0

        self.auto = False

        self.amount_pct = 6

        self.win_limit = 10

        self.loss_limit = 10


state = AccountState()


# =========================================================
# MODELO LOGIN
# =========================================================

class LoginRequest(BaseModel):

    email: str

    password: str

    account_type: str = "DEMO"


# =========================================================
# PAGINA PRINCIPAL
# =========================================================

@app.get("/")
async def index():

    return FileResponse(
        BASE / "static" / "index.html"
    )


# =========================================================
# LOGIN
# =========================================================

@app.post("/api/login")
async def login(req: LoginRequest):

    # IMPORTANTE:
    # No guardamos ni mostramos la contraseña.

    state.connected = True

    state.email = req.email

    state.account_type = req.account_type.upper()

    return {

        "ok": True,

        "connected": True,

        "account_type": state.account_type,

        "message":
        "Sesión de interfaz iniciada. "
        "Conector Quotex autorizado pendiente."

    }


# =========================================================
# CERRAR SESION
# =========================================================

@app.post("/api/logout")
async def logout():

    state.connected = False

    state.email = None

    state.auto = False

    return {

        "ok": True

    }


# =========================================================
# ESTADO ACTUAL
# =========================================================

@app.get("/api/state")
async def get_state():

    return {

        "connected":
        state.connected,

        "account_type":
        state.account_type,

        "email":
        state.email,

        "balance":
        state.balance,

        "wins":
        state.wins,

        "losses":
        state.losses,

        "profit":
        state.profit,

        "auto":
        state.auto,

        "amount_pct":
        state.amount_pct,

        "win_limit":
        state.win_limit,

        "loss_limit":
        state.loss_limit

    }


# =========================================================
# AUTOMATICO
# =========================================================

@app.post("/api/auto")
async def set_auto(enabled: bool):

    state.auto = (
        bool(enabled)
        and state.connected
    )

    return {

        "ok": True,

        "auto": state.auto

    }


# =========================================================
# WEBSOCKET
# ACTUALIZACION EN TIEMPO REAL
# =========================================================

@app.websocket("/ws")
async def websocket_endpoint(
    ws: WebSocket
):

    await ws.accept()

    try:

        while True:

            await ws.send_json({

                "connected":
                state.connected,

                "account_type":
                state.account_type,

                "balance":
                state.balance,

                "wins":
                state.wins,

                "losses":
                state.losses,

                "profit":
                state.profit,

                "auto":
                state.auto

            })

            await asyncio.sleep(1)

    except WebSocketDisconnect:

        pass
