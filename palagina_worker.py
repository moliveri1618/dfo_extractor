import os
from fastapi import HTTPException
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

from schemas import LoginPayload, NuovoProgettoPayload
from utils import (
    go_in_nuovo_progetto_page,
    compila_dati_cliente,
    aggiungi_prodotto_categoria,
    imposta_qta_prodotto,
)
from config import LOGIN_URL, LISTA_CONFIG_URL, STATE_PATH


# For now keep credentials here if you want minimum changes.
# Better later: move to env vars / secret manager / DB.
PALAGINA_USERNAME = os.getenv("PALAGINA_USERNAME")
PALAGINA_PASSWORD = os.getenv("PALAGINA_PASSWORD")
PALAGINA_REMEMBER = True


async def do_login(
    page: Page,
    username: str,
    password: str,
    remember: bool = False,
) -> None:
    await page.goto(LOGIN_URL, wait_until="domcontentloaded")
    await page.fill("#user_login", username)
    await page.fill("#user_pass", password)

    if remember:
        await page.check("#rememberme")

    await page.click("#wp-submit")
    await page.wait_for_timeout(2000)

    if await page.locator("#login_error").count() > 0:
        err = (await page.locator("#login_error").inner_text()).strip()
        raise HTTPException(status_code=401, detail=f"Palagina login failed: {err}")


async def is_logged_in(page: Page) -> bool:
    try:
        await page.goto(LISTA_CONFIG_URL, wait_until="domcontentloaded")
        await page.wait_for_timeout(1000)

        # If login form is visible, session is not valid
        if await page.locator("#user_login").count() > 0:
            return False

        # If "NUOVO PROGETTO" exists, we are likely authenticated
        if await page.get_by_text("NUOVO PROGETTO", exact=False).count() > 0:
            return True

        return False
    except Exception:
        return False


async def get_authenticated_context(browser: Browser) -> tuple[BrowserContext, bool]:
    """
    Returns:
        context,
        session_reused
    """
    # Try cached state first
    if os.path.exists(STATE_PATH):
        try:
            context = await browser.new_context(storage_state=STATE_PATH)
            page = await context.new_page()

            if await is_logged_in(page):
                return context, True

            await context.close()
        except Exception:
            # Broken state file or invalid browser state -> ignore and relogin
            pass

    # Fallback to fresh login
    if not PALAGINA_USERNAME or not PALAGINA_PASSWORD:
        raise HTTPException(
            status_code=500,
            detail="Missing PALAGINA_USERNAME / PALAGINA_PASSWORD for automatic login fallback.",
        )

    context = await browser.new_context()
    page = await context.new_page()

    await do_login(
        page=page,
        username=PALAGINA_USERNAME,
        password=PALAGINA_PASSWORD,
        remember=PALAGINA_REMEMBER,
    )

    await context.storage_state(path=STATE_PATH)
    return context, False


async def palagina_login_worker(payload: LoginPayload, headless: bool = False):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context()
        page = await context.new_page()

        await do_login(
            page=page,
            username=payload.username,
            password=payload.password,
            remember=payload.remember,
        )

        await context.storage_state(path=STATE_PATH)
        final_url = page.url
        await browser.close()

    return {
        "success": True,
        "headless": headless,
        "final_url": final_url,
        "state_file": STATE_PATH,
    }


async def palagina_nuovo_progetto_worker(
    payload: NuovoProgettoPayload,
    headless: bool = True,
):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)

        try:
            context, session_reused = await get_authenticated_context(browser)
            page = await context.new_page()

            await page.goto(LISTA_CONFIG_URL, wait_until="domcontentloaded")
            await page.get_by_text("NUOVO PROGETTO", exact=False).click()
            await page.wait_for_timeout(1500)

            await go_in_nuovo_progetto_page(page)
            await page.wait_for_timeout(1500)

            await compila_dati_cliente(
                page,
                riferimento_cliente=payload.testata.committente,
                email_cliente=payload.testata.email,
                indirizzo_cliente=f"{payload.testata.indirizzo}, {payload.testata.citta} {payload.testata.cap}",
                note_generali=payload.cantiere.consegna,
            )
            await page.wait_for_timeout(1500)

            for idx, z in enumerate(payload.zanzariere, start=1):
                codice_prodotto = z.contratto.modello + " CRICCHETTO"

                await aggiungi_prodotto_categoria(
                    page,
                    categoria="LUCE",
                    codice_prodotto="RV 40 GOLD CRICCHETTO",
                    sottocategoria=7,
                )

                await imposta_qta_prodotto(
                    page,
                    codice_prodotto="RV 40 GOLD CRICCHETTO",
                    rigo=idx,
                    qta=1,
                    misura="L",
                    l_cm=z.rilievo.larghezza,
                    h_cm=z.rilievo.altezza,
                    colore="RAL 9010",
                    tipo_rete=z.contratto.rete,
                    riferimento_etichetta=idx,
                )

            final_url = page.url
            await page.wait_for_timeout(4000)
            await context.close()
            await browser.close()

            return {
                "success": True,
                "headless": headless,
                "final_url": final_url,
                "session_reused": session_reused,
            }

        finally:
            await browser.close()
