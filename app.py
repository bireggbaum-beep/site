# app.py - Ihre neue Streamlit Webanwendung

import streamlit as st
import base64
import json
from github import Github, Auth
from github.GithubException import UnknownObjectException

# --- Rekursive Suchfunktion (bleibt unverändert) ---
def find_and_update_images_recursive(data_structure, target_folder, found_images_set):
    if isinstance(data_structure, dict):
        for key, value in data_structure.items():
            if key == "image" and isinstance(value, str) and value:
                base_image_name = value.split('/')[-1]
                found_images_set.add(base_image_name)
                data_structure[key] = f"{target_folder}/{base_image_name}"
            else:
                find_and_update_images_recursive(value, target_folder, found_images_set)
    elif isinstance(data_structure, list):
        for item in data_structure:
            find_and_update_images_recursive(item, target_folder, found_images_set)

# --- Streamlit Benutzeroberfläche ---
st.set_page_config(page_title="GitHub Bild-Verwaltung", layout="centered")
st.title("🖼️ GitHub Bild-Verwaltung")
st.write("Dieses Werkzeug hilft Ihnen, Bilder in Ihrem GitHub-Repository zu organisieren und die zugehörige JSON-Datei automatisch zu aktualisieren.")

# --- Eingabefelder in der Seitenleiste für eine saubere Optik ---
with st.sidebar:
    st.header("Einstellungen")
    github_user = st.text_input("GitHub-Benutzer/Organisation", value="bireggbaum-beep")
    repo_name = st.text_input("Repository-Name", value="site")
    target_folder = st.text_input("Neuer Ziel-Ordner für Bilder", placeholder="z.B. assets/images")
    github_token = st.text_input("GitHub-Token", type="password", help="Ihr Token wird nicht gespeichert und nur für diese Sitzung verwendet.")
    
    uploaded_json = st.file_uploader("JSON-Produktdaten hochladen", type=["json"])
    
    delete_originals = st.checkbox("Originalbilder nach dem Kopieren löschen")

# --- Start-Button und Logik ---
if st.button("▶️ Prozess starten", type="primary", use_container_width=True):
    # --- Validierung der Eingaben ---
    if not all([github_user, repo_name, target_folder, github_token, uploaded_json]):
        st.error("❌ Bitte füllen Sie alle Felder in der Seitenleiste aus und laden Sie eine JSON-Datei hoch.")
    else:
        try:
            # --- HAUPTSKRIPT (angepasst für Streamlit) ---
            st.info("▶️ Starte den Prozess...")

            # JSON-Datei einlesen
            json_filename = uploaded_json.name
            json_content_bytes = uploaded_json.getvalue()
            products_data = json.loads(json_content_bytes)
            st.write(f"✅ Datei '{json_filename}' erfolgreich eingelesen.")

            # Mit GitHub verbinden
            try:
                auth = Auth.Token(github_token)
                g = Github(auth=auth)
                repo = g.get_repo(f"{github_user}/{repo_name}")
                st.write(f"✅ Erfolgreich mit dem Repository '{repo.full_name}' verbunden.")
            except Exception as e:
                st.error(f"❌ Fehler bei der Verbindung zu GitHub: {e}")
                st.stop() # Prozess anhalten

            # Bilder finden und JSON anpassen
            images_to_copy = set()
            updated_products_data = products_data.copy()
            find_and_update_images_recursive(updated_products_data, target_folder.strip('/'), images_to_copy)

            if not images_to_copy:
                st.warning("ℹ️ Keine Bilder im Feld 'image' in der JSON-Datei gefunden.")
                st.stop()
            st.write(f"🔎 {len(images_to_copy)} einzigartige Bilder zur Verarbeitung gefunden.")

            # Platzhalter für Fortschrittsanzeige
            progress_bar = st.progress(0, text="Verarbeite Bilder...")
            successfully_copied = {}
            
            # Bilder auf GitHub verarbeiten
            for i, image_name in enumerate(images_to_copy):
                try:
                    file_content = repo.get_contents(image_name)
                    new_path = f"{target_folder.strip('/')}/{image_name}"
                    commit_message = f"Kopiere Bild {image_name} nach {target_folder}"
                    
                    try:
                        existing_file = repo.get_contents(new_path)
                        repo.update_file(new_path, commit_message, file_content.decoded_content, existing_file.sha)
                    except UnknownObjectException:
                        repo.create_file(new_path, commit_message, file_content.decoded_content)
                    
                    successfully_copied[image_name] = file_content.sha
                except UnknownObjectException:
                    st.warning(f"⚠️ Bild '{image_name}' wurde nicht im Hauptverzeichnis gefunden.")
                except Exception as e:
                    st.error(f"❌ Fehler beim Kopieren von '{image_name}': {e}")
                
                # Fortschrittsbalken aktualisieren
                progress_bar.progress((i + 1) / len(images_to_copy), text=f"Verarbeite: {image_name}")
            
            progress_bar.empty() # Fortschrittsbalken ausblenden
            st.write(f"--- Kopiervorgang abgeschlossen: {len(successfully_copied)} Bilder verarbeitet. ---")

            # Originalbilder löschen
            if delete_originals and successfully_copied:
                st.write("--- Beginne mit dem Löschen der Originalbilder... ---")
                for image_name, sha in successfully_copied.items():
                    try:
                        repo.delete_file(image_name, f"Lösche Originalbild {image_name}", sha)
                    except Exception as e:
                        st.error(f"❌ Fehler beim Löschen von '{image_name}': {e}")
                st.write(f"--- Löschvorgang abgeschlossen: {len(successfully_copied)} Bilder gelöscht. ---")

            # Aktualisierte JSON-Datei hochladen
            try:
                updated_json_string = json.dumps(updated_products_data, indent=2, ensure_ascii=False)
                commit_message = f"Aktualisiere Bildpfade in {json_filename}"
                try:
                    json_file_on_repo = repo.get_contents(json_filename)
                    repo.update_file(json_filename, commit_message, updated_json_string, json_file_on_repo.sha)
                    st.write(f"🔄 '{json_filename}' erfolgreich aktualisiert.")
                except UnknownObjectException:
                    repo.create_file(json_filename, commit_message, updated_json_string)
                    st.write(f"✅ '{json_filename}' wurde neu im Repository erstellt.")
                
                st.success("🎉 Prozess erfolgreich abgeschlossen!")
                st.balloons()
            except Exception as e:
                st.error(f"❌ Kritischer Fehler beim Hochladen der '{json_filename}': {e}")

        except Exception as e:
            st.error(f"Ein unerwarteter Fehler ist aufgetreten: {e}")
