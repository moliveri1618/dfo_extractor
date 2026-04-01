from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError



async def go_in_nuovo_progetto_page(page: Page) -> None:
    # wait for list to update after "NUOVO PROGETTO"
    await page.wait_for_timeout(1000)

    # wait until at least one "configurazione" edit link exists
    edit_link = page.locator("a[href*='/configurazione/']").first
    await edit_link.wait_for(state="visible", timeout=10000)

    # click it (pencil icon link)
    await edit_link.click()

    await page.wait_for_timeout(1500)



async def compila_dati_cliente(
    page: Page,
    riferimento_cliente: str,
    email_cliente: str,
    indirizzo_cliente: str,
    note_generali: str,
) -> None:
    
    # Small helper to be resilient to slightly different markup/labels
    async def fill_by_label_or_fallback(label_text: str, value: str, fallback_css: str | None = None):
        if value is None:
            return

        loc = page.get_by_label(label_text, exact=False)
        if await loc.count() > 0:
            await loc.first.fill(value)
            return

        # Fallback if the label isn't properly bound (common in custom UIs)
        if fallback_css:
            fb = page.locator(fallback_css)
            if await fb.count() > 0:
                await fb.first.fill(value)
                return

        raise Exception(f"Could not find field for label '{label_text}'")

    # Inputs
    await fill_by_label_or_fallback(
        "RIFERIMENTO CLIENTE",
        riferimento_cliente,
        fallback_css="input[name*='riferimento' i], input[id*='riferimento' i]"
    )

    await fill_by_label_or_fallback(
        "EMAIL CLIENTE",
        email_cliente,
        fallback_css="input[type='email'], input[name*='email' i], input[id*='email' i]"
    )

    await fill_by_label_or_fallback(
        "INDIRIZZO CLIENTE",
        indirizzo_cliente,
        fallback_css="input[name*='indirizzo' i], input[id*='indirizzo' i]"
    )

    # Notes is likely a textarea
    notes_loc = page.get_by_label("NOTE GENERALI", exact=False)
    if await notes_loc.count() > 0:
        await notes_loc.first.fill(note_generali)
    else:
        notes_fb = page.locator("textarea, textarea[name*='note' i], textarea[id*='note' i]").first
        if await notes_fb.count() > 0:
            await notes_fb.fill(note_generali)
        else:
            raise Exception("Could not find NOTE GENERALI textarea")
        


async def aggiungi_prodotto_categoria(
    page: Page,
    categoria: str,
    codice_prodotto: str,   # e.g. "M2001.3"
    sottocategoria: int 
) -> None:
    
    # 1) Click "+ AGGIUNGI PRODOTTO"
    btn = page.get_by_role("button", name="AGGIUNGI PRODOTTO")
    if await btn.count() == 0:
        btn = page.get_by_text("AGGIUNGI PRODOTTO", exact=False)
    await btn.first.click()

    # 2) Wait for modal
    modal_title = page.get_by_text("SELEZIONA IL MODELLO CHE PREFERISCI", exact=False)
    await modal_title.wait_for(state="visible", timeout=10000)

    modal = page.locator("#modelli")
    await modal.wait_for(state="visible", timeout=10000)

    # 3) Click category tab inside modal
    tab = modal.get_by_role("tab", name=categoria)
    await tab.wait_for(state="visible", timeout=10000)
    await tab.click()
    await page.wait_for_timeout(400)

    # 4) Pagination indicators (the little squares)
    indicators = modal.locator(".carousel-indicators li, .carousel-indicators button")
    pages = max(await indicators.count(), 1)
    # print("👉 total indicators (dots):", await indicators.count())

    # Helper: decide the "search scope"
    async def get_scope():
        
        # find ANY section containing "SPAZZOLINO"
        # print("\n🔍 Searching SPAZZOLINO section...")
        section_title = modal.locator("div:has-text('SPAZZOLINO')").first
        # print("👉 matches count:", await modal.locator("div:has-text('SPAZZOLINO')").count())

        # 👀 highlight what was selected
        # await section_title.highlight()
        # await page.wait_for_timeout(800)

        await section_title.wait_for(state="visible", timeout=10000)
        txt = await section_title.inner_text()
        # print("👉 selected text:", txt[:100])

        section = section_title.locator(
            "xpath=ancestor::div[contains(@class,'row') or contains(@class,'container') or contains(@class,'col')][1]"
        )
        # print("👉 container selected")

        # 👀 highlight container
        # await section.highlight()
        # await page.wait_for_timeout(800)

        return section

    scope = await get_scope()

    # 5) Try each page until we find the correct code inside the correct section
    header = None
    for i in range(sottocategoria, pages):

        # show which dot we are clicking / currently checking
        # print(f"\n🟦 Page iteration i={i}/{pages-1}")
        # try:
        #     dot = indicators.nth(i)
        #     cls = await dot.get_attribute("class")
        #     print(f"👉 dot[{i}] class={cls}")
        #     await dot.highlight()
        #     await page.wait_for_timeout(300)
        # except Exception as e:
        #     print("⚠️ could not highlight dot:", e)


        header = scope.locator("div.card-header", has_text=codice_prodotto)
        # cnt = await header.count()
        # print(f"👉 headers found on this page: {cnt}")

        if await header.count() > 0:
            try:
                await header.wait_for(state="visible", timeout=1500)
                # print("✅ FOUND product header, stopping loop")
                # await header.first.highlight()
                # await page.wait_for_timeout(600)
                break
            except PlaywrightTimeoutError:
                pass

        if i < pages - 1:
            await indicators.nth(i + 1).click()
            await page.wait_for_timeout(600)

    if header is None or await header.count() == 0:
        raise Exception(f"Product {codice_prodotto} not found")

    # 6) Click the correct card's SELEZIONA
    card = header.locator("xpath=ancestor::div[contains(@class,'card')][1]")
    await card.locator("a.text-center", has_text="SELEZIONA").click()
    await page.wait_for_timeout(800)



async def imposta_qta_prodotto(
        page: Page, 
        codice_prodotto: str, 
        rigo: int = 1,
        qta: int = 1,
        misura: str = "L",
        l_cm: int = 100,
        h_cm: int = 200,
        colore: str = "RAL 9010",
        tipo_rete: str = "ANTI BATTERICA",
        riferimento_etichetta: int = 12,
    ) -> None:


    # Scope to the specific product table (based on your HTML: id="modello:M2001.3")
    table = page.locator(f'table[id="modello:{codice_prodotto}"]')
    await table.wait_for(state="visible", timeout=20000)
    row = table.locator(f"tbody tr:has-text('R:{rigo}')").first
    await row.wait_for(state="visible", timeout=10000)

    # --- MISURA (native <select>) ---
    misura_select = row.locator("select[name*='MISULFI' i], select").first
    await misura_select.wait_for(state="visible", timeout=10000)
    await misura_select.select_option(label=misura)
    await misura_select.dispatch_event("change")
    await misura_select.dispatch_event("blur")

    # --- QTA ---
    qta_input = row.locator(
        "input[name*='qta' i], input[id*='qta' i], input[placeholder*='qta' i]"
    ).first
    if await qta_input.count() == 0:
        qta_input = row.locator("tbody input[type='number'], tbody input").first
    await qta_input.wait_for(state="visible", timeout=10000)
    await qta_input.fill(str(qta))

    # --- L cm ---
    l_input = row.locator("input[id*=':L:']").first
    await l_input.wait_for(state="visible", timeout=10000)
    await l_input.fill(str(l_cm))

    # --- H cm ---
    h_input = row.locator("input[id*=':H:']").first
    await h_input.wait_for(state="visible", timeout=10000)
    await h_input.fill(str(h_cm))

    # --- COLORE (row-safe) ---
    # 1) click the COLORE modal trigger cell in THIS row
    colore_input = row.locator(
        "input[tipo_oggetto='MODAL'][colonna*='COL' i], input[id*=':COL' i]"
    ).first
    await colore_input.wait_for(state="attached", timeout=10000)
    colore_cell = colore_input.locator("xpath=ancestor::td[1]")
    await colore_cell.click(force=True)

    # 2) wait for color cards
    cards = page.locator(".card[onclick*='segna_colore']")
    await cards.first.wait_for(state="visible", timeout=10000)

    # 3) pick specific color
    await page.locator(".card[onclick*='segna_colore']", has_text=colore).first.click()

    await page.wait_for_timeout(300)

    # --- RIFERIMENTO ETICHETTA ---
    rif_input = row.locator(
        "textarea[colonna='RIFERIMENTO'], textarea[id*=':RIFERIMENTO:']"
    ).first
    await rif_input.wait_for(state="visible", timeout=10000)
    await rif_input.fill(str(riferimento_etichetta))

    # 👉 IMPORTANT: trigger save (blur event)
    await qta_input.press("Tab")
    await page.wait_for_timeout(1000)