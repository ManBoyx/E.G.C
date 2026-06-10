"""EGC Suite Launcher - Version Windows"""
import sys
import subprocess
from pathlib import Path


APPS = {
    '1': ('antivirus_scanner.py', 'Antivirus Scanner'),
    '2': ('photo_editor.py', 'Photo Editor'),
    '3': ('web_browser.py', 'Web Browser'),
    '4': ('audio_amplifier.py', 'Audio Amplifier'),
}


def main():
    while True:
        print("""
    ============================================
    |        EGC Suite v1.0.0 - Windows        |
    ============================================

    Selectionnez une application:
""")
        for key, (_, name) in APPS.items():
            print(f"    {key}) {name}")
        print("    5) Quitter")
        print()

        choice = input("    Votre choix (1-5): ").strip()

        if choice == '5':
            print("    Au revoir!")
            sys.exit(0)

        if choice in APPS:
            app_file, app_name = APPS[choice]
            print(f"\n    Lancement de {app_name}...")
            script_dir = Path(__file__).resolve().parent
            app_path = script_dir / app_file
            try:
                subprocess.run([sys.executable, str(app_path)], check=True)
            except subprocess.CalledProcessError as e:
                print(f"    Erreur: {e}")
            except KeyboardInterrupt:
                print("\n    Application fermee.")
        else:
            print("    Choix invalide.")


if __name__ == "__main__":
    main()
