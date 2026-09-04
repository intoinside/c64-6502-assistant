"""Interfaccia Web locale basata su Streamlit per C64-6502-Assistant."""

import streamlit as st
from c64_assistant.core.cycle_counter import CycleCounter
from c64_assistant.core.validator import HardwareValidator


def run_app():
    st.set_page_config(
        page_title="C64 6502 Assistant",
        page_icon="🕹️",
        layout="wide",
    )

    st.title("🕹️ Commodore 64 & 6502 AI Assistant")
    st.caption("Motore ibrido: AI di Dominio + Validatore Deterministico Hardware (Ispirato a Rizzo AI Academy)")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Codice Assembly 6502")
        default_code = """; Routine raster border color flicker
loop:
    inc $d020
    bne loop
    rts
"""
        code = st.text_area("Inserisci o modifica il codice assembly:", value=default_code, height=300)
        validate_btn = st.button("Analizza & Valida Codice", type="primary")

    with col2:
        st.subheader("Analisi Hardware & Timing")
        if validate_btn or code:
            report = HardwareValidator.validate_code(code)

            if report.is_valid:
                st.success("✅ Codice valido: nessuna istruzione illegale o CMOS rilevata.")
            else:
                st.error(f"❌ Rilevati {report.errors_count} errori nel codice.")

            # Metriche cicli
            t = report.timing_report
            m1, m2, m3 = st.columns(3)
            m1.metric("Cicli Min - Max", f"{t.total_min_cycles} - {t.total_max_cycles}")
            m2.metric("Linee Raster PAL", f"~{t.pal_raster_lines}")
            m3.metric("Dimensione", f"{t.total_bytes} bytes")

            if report.issues:
                st.write("#### Dettaglio Problemi")
                for issue in report.issues:
                    if issue.severity == "ERROR":
                        st.error(f"Riga {issue.line_number}: {issue.message}\n*{issue.suggestion}*")
                    else:
                        st.warning(f"Riga {issue.line_number}: {issue.message}\n*{issue.suggestion}*")


if __name__ == "__main__":
    run_app()
