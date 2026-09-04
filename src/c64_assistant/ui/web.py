"""Interfaccia Web locale basata su Streamlit per C64-6502-Assistant."""

import streamlit as st
from c64_assistant.core.memory import C64MemoryMap
from c64_assistant.core.validator import HardwareValidator


def run_app():
    st.set_page_config(
        page_title="C64 6502 Assistant",
        page_icon="🕹️",
        layout="wide",
    )

    st.title("🕹️ Commodore 64 & 6502 Assistant")
    st.caption("Motore ibrido: AI di Dominio + Validatore Deterministico Hardware (Ispirato a Rizzo AI Academy)")

    tab_code, tab_ai, tab_mem, tab_banking, tab_rag = st.tabs([
        "⚡ Analizzatore & Validatore Assembly",
        "🤖 Assistente AI & Guardrails",
        "🔍 Memory Inspector",
        "🎛️ Banking 6510 ($0001)",
        "📚 Knowledge Base RAG",
    ])

    with tab_code:
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("Codice Assembly 6502")
            default_code = """; Routine raster border color flicker
* = $0801
loop:
    inc $d020
    bne loop
    rts
"""
            code = st.text_area("Inserisci o incolla codice assembly:", value=default_code, height=280)
            validate_btn = st.button("Valida & Calcola Cicli", type="primary")

        with col2:
            st.subheader("Report Hardware Deterministico")
            if validate_btn or code:
                report = HardwareValidator.validate_code(code)

                if report.is_valid:
                    st.success("✅ Codice valido: conforme all'ISA 6502 NMOS standard del C64.")
                else:
                    st.error(f"❌ Rilevati {report.errors_count} errori bloccanti.")

                t = report.timing_report
                m1, m2, m3 = st.columns(3)
                m1.metric("Cicli Min - Max", f"{t.total_min_cycles} - {t.total_max_cycles}")
                m2.metric("Linee Raster PAL (63c)", f"~{t.pal_raster_lines}")
                m3.metric("Dimensione Stimata", f"{t.total_bytes} bytes")

                if report.issues:
                    st.write("#### Problemi e Avvisi")
                    for issue in report.issues:
                        if issue.severity == "ERROR":
                            st.error(f"Riga {issue.line_number} [{issue.code}]: {issue.message}\n💡 *{issue.suggestion}*")
                        else:
                            st.warning(f"Riga {issue.line_number} [{issue.code}]: {issue.message}\n💡 *{issue.suggestion}*")

        if code:
            st.write("### Dettaglio Istruzione per Istruzione")
            table_data = []
            for item in report.timing_report.instructions:
                table_data.append({
                    "Riga": item.line_number,
                    "Etichetta": item.label,
                    "Istruzione": item.mnemonic,
                    "Operando": item.operand,
                    "Modalità Indirizzamento": item.mode.value,
                    "Opcode": f"${item.opcode_hex}" if item.opcode_hex else "-",
                    "Cicli Min": item.base_cycles,
                    "Cicli Max": item.max_cycles,
                    "Byte": item.bytes_count,
                    "Note": item.notes,
                })
            st.dataframe(table_data, use_container_width=True)

    with tab_ai:
        st.subheader("Assistente Intelligente Ibrido (AI + RAG + Guardrails)")
        st.caption("Il codice generato viene sottoposto a verifica hardware deterministica ed eventuale auto-correzione prima di essere mostrato.")

        col_p, col_f = st.columns([2, 1])
        with col_p:
            provider_choice = st.selectbox(
                "Provider Modello:",
                ["offline (Template deterministici locali)", "ollama (Locale 100% via localhost:11434)", "gemini", "openai"],
            )
            provider_clean = provider_choice.split()[0].lower()
        with col_f:
            auto_fix_toggle = st.checkbox("Self-Healing Guardrails (Auto-correzione)", value=True)

        user_prompt = st.text_area(
            "Cosa vuoi realizzare in Assembly 6502?",
            value="Come posso impostare un interrupt raster per cambiare il colore del bordo a riga fissa?",
            height=100,
        )
        ask_btn = st.button("🚀 Chiedi all'Assistente", type="primary")

        if ask_btn and user_prompt:
            from c64_assistant.ai.engine import AssistantEngine

            with st.spinner("Interrogazione RAG e validazione hardware in corso..."):
                engine = AssistantEngine(provider=provider_clean)
                try:
                    ai_response = engine.ask(user_prompt, auto_fix=auto_fix_toggle)

                    st.write("### Spiegazione Tecnica")
                    st.markdown(ai_response.explanation)

                    if ai_response.suggested_code:
                        st.write("### Codice Assembly 6502 Verificato")
                        st.code(ai_response.suggested_code, language="assembly")

                    if ai_response.auto_fix_applied:
                        st.info(f"🛠️ **Auto-correzione applicata:** {ai_response.fix_iterations} iterazione/i.")
                        for h in ai_response.fix_history:
                            st.caption(f"- {h}")

                    if ai_response.validation_report:
                        vrep = ai_response.validation_report
                        vt = vrep.timing_report
                        st.write("### Certificazione Validatore Deterministico")
                        if vrep.is_valid:
                            st.success("✅ Codice conforme al 100% alle specifiche hardware del 6502 NMOS.")
                        else:
                            st.error(f"❌ Codice non conforme: {vrep.errors_count} errori riscontrati.")

                        c1, c2, c3 = st.columns(3)
                        c1.metric("Cicli Min - Max", f"{vt.total_min_cycles} - {vt.total_max_cycles}")
                        c2.metric("Linee Raster PAL (63c)", f"~{vt.pal_raster_lines}")
                        c3.metric("Dimensione", f"{vt.total_bytes} bytes")

                    if ai_response.hardware_context:
                        with st.expander("📚 Riferimenti Manuali C64 Inclusi nel Prompt (RAG)"):
                            for ctx in ai_response.hardware_context:
                                st.markdown(ctx)
                except Exception as e:
                    st.error(f"Errore durante l'esecuzione: {e}")

    with tab_mem:
        st.subheader("Ispezione Aree e Registri Commodore 64")
        address_in = st.text_input("Inserisci indirizzo esadecimale (es. $D020, $01, $0314):", value="$D020")
        if address_in:
            try:
                addr_str = address_in.strip().replace("$", "").replace("0x", "")
                addr = int(addr_str, 16)
                region = C64MemoryMap.get_region_for_address(addr)
                reg_desc = C64MemoryMap.get_register_description(addr)
                zp_info = C64MemoryMap.check_zero_page_safety(addr)

                c1, c2 = st.columns(2)
                with c1:
                    st.info(f"**Indirizzo:** ${addr:04X} ({addr} dec)")
                    st.write(f"**Regione:** {region.name if region else 'RAM generale'}")
                    st.write(f"**Descrizione:** {region.description if region else '-'}")
                    if region and region.notes:
                        st.caption(f"Note: {region.notes}")

                with c2:
                    if reg_desc:
                        st.success(f"**Registro Hardware Conosciuto:**\n{reg_desc}")
                    if zp_info["is_zero_page"]:
                        if zp_info["is_safe"]:
                            st.success(f"**Zero Page Sicura:** {zp_info['details']}")
                        else:
                            st.warning(f"**Zero Page Riservata:** {zp_info['details']}")
            except ValueError:
                st.error("Formato indirizzo non valido.")

    with tab_banking:
        st.subheader("Simulatore di Banking del 6510 ($0001)")
        preset = st.selectbox(
            "Configurazioni Standard:",
            [
                "$37 (55) - Default: BASIC ROM + Kernal ROM + I/O (38 KB RAM)",
                "$36 (54) - 48 KB RAM: RAM a $A000 + Kernal ROM + I/O",
                "$35 (53) - 60 KB RAM: Tutta RAM eccetto I/O $D000-$DFFF",
                "$34 (52) - 64 KB RAM con Character ROM a $D000",
                "$30 (48) - 64 KB RAM pura (ROM e I/O disattivati)",
            ],
        )
        val_hex = int(preset.split()[0].replace("$", ""), 16)
        config = C64MemoryMap.get_banking_config(val_hex)

        st.write(f"**Descrizione:** {config.description}")
        b1, b2, b3, b4 = st.columns(4)
        b1.metric("BASIC ROM ($A000)", "Visibile" if config.basic_rom_visible else "RAM")
        b2.metric("Kernal ROM ($E000)", "Visibile" if config.kernal_rom_visible else "RAM")
        b3.metric("I/O Chips ($D000)", "Attivo" if config.io_visible else "Disattivato")
        b4.metric("Char ROM ($D000)", "Visibile" if config.char_rom_visible else "Nascosta")

    with tab_rag:
        st.subheader("Consultazione Documentazione Tecnica e Manuali C64")
        rag_query = st.text_input(
            "Cerca argomenti hardware o indirizzi esadecimali (es. 'raster interrupt', '$D020', 'SID adsr', '$FFD2'):",
            value="raster interrupt $D012",
        )
        col_chip, col_limit = st.columns([2, 1])
        with col_chip:
            chip_filter = st.selectbox(
                "Filtra per Chip/Sottosistema (opzionale):",
                ["Tutti", "VIC-II", "SID", "CIA", "KERNAL", "ZERO_PAGE", "CPU_6502"],
            )
        with col_limit:
            limit = st.slider("Numero di risultati:", min_value=1, max_value=6, value=3)

        if rag_query:
            from c64_assistant.rag.retriever import C64KnowledgeRetriever

            retriever = C64KnowledgeRetriever()
            if chip_filter != "Tutti":
                raw_results = retriever.find_by_chip(chip_filter)
            else:
                raw_results = retriever.query(rag_query, max_results=limit)

            if raw_results:
                st.write(f"Trovati **{len(raw_results)}** riferimenti tecnici pertinenti:")
                for res in raw_results:
                    with st.expander(
                        f"📖 {res.chunk.source_title} - {res.chunk.section} (Match: {res.match_reason})",
                        expanded=True,
                    ):
                        if res.chunk.chips or res.chunk.memory_addresses:
                            st.caption(
                                f"Chip: {', '.join(res.chunk.chips) or 'Generico'} | "
                                f"Indirizzi: {', '.join(res.chunk.memory_addresses) or '-'}"
                            )
                        st.markdown(res.chunk.content)
                        if res.chunk.code_snippets:
                            st.write("**Snippet di Codice Assembly:**")
                            for snip in res.chunk.code_snippets:
                                st.code(snip, language="assembly")
            else:
                st.info("Nessun frammento di manuale trovato per i criteri specificati.")


if __name__ == "__main__":
    run_app()

