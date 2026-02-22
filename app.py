import json
import streamlit as st
from pathlib import Path
import pandas as pd

import db
import ai
from pdf_export import export_readiness_map

APP_TITLE = "Ownership Entry Lab (MVP)"

CONTENT_PATH = Path("content.json")
EXPORT_DIR = Path("exports")

def load_content():
    return {int(k): v for k,v in json.loads(CONTENT_PATH.read_text(encoding="utf-8")).items()}

def page_header():
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    st.title(APP_TITLE)
    st.caption("Prototyp: 8 týdnů práce s rolí vlastníka (Founder + NextGen). Data v SQLite. AI shrnutí je heuristické.")

def login_box():
    st.subheader("Přihlášení")
    family_code = st.text_input("Kód rodiny (Family Code)", value=st.session_state.get("family_code",""))
    access_code = st.text_input("Přístupový kód (Access Code)", type="password", value=st.session_state.get("access_code",""))
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Přihlásit"):
            fam = db.get_family_by_code(family_code.strip())
            if not fam:
                st.error("Rodina nenalezena.")
                return
            user = db.auth_user(fam["id"], access_code.strip())
            if not user:
                st.error("Neplatný přístupový kód.")
                return
            st.session_state["family_code"] = family_code.strip()
            st.session_state["access_code"] = access_code.strip()
            st.session_state["family"] = dict(fam)
            st.session_state["user"] = dict(user)
            st.success(f"Přihlášen(a): {user['display_name']} ({user['role']})")
            st.rerun()
    with col2:
        if st.button("Odhlásit"):
            for k in ["family_code","access_code","family","user"]:
                st.session_state.pop(k, None)
            st.rerun()

def admin_panel(content):
    st.subheader("Admin panel")
    tabs = st.tabs(["Rodiny", "Uživatelé", "Dashboard & Export"])
    # Families
    with tabs[0]:
        st.markdown("### Vytvořit rodinu")
        name = st.text_input("Název rodiny", key="new_family_name")
        code = st.text_input("Kód rodiny (unikátní)", key="new_family_code")
        if st.button("Vytvořit rodinu"):
            if not name.strip() or not code.strip():
                st.error("Vyplň název i kód.")
            else:
                try:
                    db.create_family(name.strip(), code.strip())
                    st.success("Rodina vytvořena.")
                except Exception as e:
                    st.error(f"Chyba: {e}")
        st.markdown("### Existující rodiny")
        fams = db.list_families()
        if fams:
            st.dataframe(pd.DataFrame([dict(r) for r in fams]), use_container_width=True)
        else:
            st.info("Zatím žádné rodiny.")
    # Users
    with tabs[1]:
        st.markdown("### Přidat uživatele do rodiny")
        fams = db.list_families()
        if not fams:
            st.info("Nejdřív vytvoř rodinu.")
        else:
            fam_map = {f"{r['name']} ({r['family_code']})": r for r in fams}
            fam_label = st.selectbox("Rodina", list(fam_map.keys()))
            fam = fam_map[fam_label]
            display = st.text_input("Jméno", key="new_user_name")
            role = st.selectbox("Role", ["admin","founder","nextgen"], index=2)
            access = st.text_input("Přístupový kód", type="password", key="new_user_access")
            if st.button("Vytvořit uživatele"):
                if not display.strip() or not access.strip():
                    st.error("Vyplň jméno i kód.")
                else:
                    db.create_user(fam["id"], display.strip(), role, access.strip())
                    st.success("Uživatel vytvořen.")
            st.markdown("### Uživatelé v rodině")
            users = db.list_users(fam["id"])
            if users:
                st.dataframe(pd.DataFrame([dict(r) for r in users]), use_container_width=True)
            else:
                st.info("Zatím žádní uživatelé.")
    # Dashboard & Export
    with tabs[2]:
        st.markdown("### Facilitátorský dashboard")
        fam = st.session_state.get("family")
        if not fam:
            st.info("Přihlas se jako admin do konkrétní rodiny pro dashboard (nebo použij export pro vybranou rodinu).")
        fams = db.list_families()
        if not fams:
            st.info("Zatím žádné rodiny.")
            return
        fam_map = {f"{r['name']} ({r['family_code']})": r for r in fams}
        fam_label = st.selectbox("Rodina pro dashboard", list(fam_map.keys()), key="dash_fam")
        fam = fam_map[fam_label]
        all_ans = db.get_all_answers(fam["id"])
        if not all_ans:
            st.info("Zatím nejsou žádné odpovědi.")
            return
        df = pd.DataFrame([dict(r) for r in all_ans])
        st.dataframe(df[["week","display_name","role","question_index","question_text","answer_text","updated_at"]], use_container_width=True, height=320)

        st.markdown("### AI poznámky (heuristika)")
        notes = ai.draft_facilitator_notes(all_ans)
        st.code(notes, language="text")

        st.markdown("### Export")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Export JSON (vše)"):
                EXPORT_DIR.mkdir(parents=True, exist_ok=True)
                out = EXPORT_DIR / f"{fam['family_code']}_answers.json"
                df.to_json(out, orient="records", force_ascii=False, indent=2)
                st.success(f"Uloženo: {out}")
        with col2:
            if st.button("Export PDF (Ownership Readiness Map – draft)"):
                EXPORT_DIR.mkdir(parents=True, exist_ok=True)
                pdf_path = str(EXPORT_DIR / f"{fam['family_code']}_readiness_map_draft.pdf")
                # create simple sections
                sections = [
                    ("1. Klíčové postoje (náhled)", "Tento draft je určen pro facilitátora. Doporučení: doplňte kontext a rozhodněte, co sdílet."),
                    ("2. Opakující se motivy (z odpovědí)", "—"),
                    ("3. Potenciální napětí a rozdíly (hypotézy)", "—"),
                    ("4. Doporučení témat na další setkání", "—"),
                ]
                export_readiness_map(pdf_path, fam["name"], notes, sections)
                st.success(f"Uloženo: {pdf_path}")

def user_week_view(content, role):
    family = st.session_state["family"]
    user = st.session_state["user"]

    st.subheader("Týdenní modul")
    week = st.selectbox("Vyber týden", list(range(1,9)), index=0)
    w = content[week]
    st.markdown(f"## Týden {week}: {w['title']}")
    st.write(w["intro"])
    st.info("Odpovědi vidíte pouze vy (admin vidí vše).")

    questions = w["founder_questions"] if role == "founder" else w["nextgen_questions"]
    existing = {r["question_index"]: r for r in db.get_answers_for_user(family["id"], user["id"], week)}
    for i, q in enumerate(questions, start=1):
        st.markdown(f"**{i}. {q}**")
        default = existing.get(i, {}).get("answer_text","")
        ans = st.text_area("Vaše odpověď", value=default, key=f"ans_{week}_{i}", height=120)
        if st.button("Uložit odpověď", key=f"save_{week}_{i}"):
            db.upsert_answer(family["id"], user["id"], week, i, q, ans)
            st.success("Uloženo.")
    st.markdown("### Mini-úkol týdne")
    st.write(w["mini_task"])

def main():
    db.init_db()
    content = load_content()
    page_header()

    if "user" not in st.session_state:
        login_box()
        st.divider()
        st.subheader("Rychlý start (Admin)")
        st.write("1) Vytvoř rodinu → 2) Vytvoř uživatele (admin/founder/nextgen) → 3) Přihlas se jako účastník a vyplň odpovědi.")
        return

    user = st.session_state["user"]
    role = user["role"]

    # Sidebar info
    st.sidebar.header("Session")
    st.sidebar.write(f"Rodina: **{st.session_state['family']['name']}**")
    st.sidebar.write(f"Uživatel: **{user['display_name']}**")
    st.sidebar.write(f"Role: `{role}`")
    if st.sidebar.button("Odhlásit"):
        for k in ["family_code","access_code","family","user"]:
            st.session_state.pop(k, None)
        st.rerun()

    if role == "admin":
        admin_panel(content)
    else:
        user_week_view(content, role)

if __name__ == "__main__":
    main()
