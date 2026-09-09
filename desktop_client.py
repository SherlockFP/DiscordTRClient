"""
Direkt client + gomulu GoodbyeDPI mantigi (Windows)
===================================================
Evet, demek istedigini anladim: ayri bir program acip dugmeye basmak yerine,
Discord client'ini acinca bypass otomatik baslasin, kapatinca dursun ve
sadece Discord etkilensin.

Neden boyle yaptik (kisa teknik not):
- Tarayici/sitenin icine GoodbyeDPI gomulemez. GoodbyeDPI WinDivert driver ile
  paket parcaliyor, bu ham soket/driver isi. JS'nin boyle yetkisi yok.
- O yuzden "gomulu" dedigin sey gercekte sunucu degil: client exe'sinin
  yaninda duran goodbyedpi.exe'yi client acilirken otomatik baslatip,
  sadece discord_blacklist.txt'deki domainlere uygulamak.
  Baska siteye dokunmaz -> internet bozulmaz.

Kullanim:
1. https://github.com/ValdikSS/GoodbyeDPI/releases adresinden x86_64 bit
   surumu indir, icindeki goodbyedpi.exe + WinDivert64.sys + WinDivert.dll
   dosyalarini bu klasorun altindaki goodbyedpi/ klasorune koy.
   (Otomatik indirme yapmiyorum: driver oldugu icin senin indirmen guvenli.)
2. Bu dosyayi yonetici olarak calistir:
   run_client.bat'a cift tikla (admin ister).
3. Client Discord'u app modunda acar, cikista bypass'i oldurur.

Not: ilk acilista antivir us uyarabilir (WinDivert normaldir).
Sesli sohbet dahil Discord'un kendisi acilir, relay'deki gibi text-only degil.
"""
import ctypes
import os
import shutil
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from shutil import which

BASE = Path(__file__).parent if not getattr(sys, "frozen", False) else Path(sys.executable).parent


def resource_path(rel: str) -> Path:
    # PyInstaller onefile: dosyalar _MEIPASS'ta, normalde BASE'de.
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        return Path(meipass) / rel
    return BASE / rel


def runtime_dir() -> Path:
    # Driver'in stabil calismasi icin bundle ise kalici klasore cikar.
    if getattr(sys, "frozen", False):
        d = Path(os.environ.get("LOCALAPPDATA", str(BASE))) / "DiscordTRClient" / "goodbyedpi"
        d.mkdir(parents=True, exist_ok=True)
        for name in ("goodbyedpi.exe", "WinDivert.dll", "WinDivert64.sys"):
            src = resource_path(f"goodbyedpi/{name}")
            dst = d / name
            if src.exists() and (not dst.exists() or src.stat().st_size != dst.stat().st_size):
                shutil.copy2(src, dst)
        bl_src = resource_path("discord_blacklist.txt")
        bl_dst = d.parent / "discord_blacklist.txt"
        if bl_src.exists():
            shutil.copy2(bl_src, bl_dst)
        return d
    return BASE / "goodbyedpi"


GB_DIR = runtime_dir()
GB_EXE = GB_DIR / "goodbyedpi.exe"
BLACKLIST = GB_DIR.parent / "discord_blacklist.txt" if getattr(sys, "frozen", False) else BASE / "discord_blacklist.txt"

# Turkiye icin genelde stabil olan, sadece blacklist'e uygulanan profil.
# -p -r -s -m: parcala + SNI degistir + ... (GoodbyeDPI klasigi)
# --blacklist: SADECE bu listedekilere dokun -> diger internet bozulmaz.
GB_ARGS = ["-p", "-r", "-s", "-m",
           "--blacklist", str(BLACKLIST),
           "--dns-addr", "77.88.8.8", "--dns-port", "1253"]


def is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def find_browser_app():
    for name in ("msedge.exe", "chrome.exe", "firefox.exe"):
        p = which(name)
        if p:
            return p
    return None


def main():
    if sys.platform != "win32":
        print("Bu launcher su an sadece Windows icin.")
        sys.exit(1)
    if not is_admin():
        print("HATA: Yonetici olarak calistir (run_client.bat zaten bunu ister).")
        print("WinDivert driver admins iz olmadan paketlere dokunamaz.")
        sys.exit(1)
    if not GB_EXE.exists():
        print(f"HATA: {GB_EXE} bulunamadi.")
        print("GoodbyeDPI release indirip goodbyedpi/ klasorune koy:")
        print("  https://github.com/ValdikSS/GoodbyeDPI/releases")
        print("Gerekli dosyalar: goodbyedpi.exe, WinDivert64.sys, WinDivert.dll")
        sys.exit(1)
    if not BLACKLIST.exists():
        print(f"HATA: {BLACKLIST} yok.")
        sys.exit(1)

    print("Bypass baslatiliyor (sadece Discord listesi)...")
    proc = subprocess.Popen([str(GB_EXE), *GB_ARGS], cwd=str(GB_DIR))
    time.sleep(1.5)
    if proc.poll() is not None:
        print(f"HATA: goodbyedpi hemen kapandi (kod {proc.returncode}).")
        print("Baska bir goodbyedpi calisiyor olabilir, once onu kapat.")
        sys.exit(1)
    print("Bypass calisiyor. Discord aciliyor...")

    url = "https://discord.com/app"
    browser = find_browser_app()
    try:
        if browser and "firefox" not in browser.lower():
            # App modu: sade pencere, direkt client hissi.
            subprocess.Popen([browser, "--app=" + url])
        else:
            webbrowser.open(url)
    except Exception as e:
        print(f"Tarayici acilamadi: {e}, linki elle ac: {url}")

    print("\nCikmak icin bu pencereye ENTER bas. Bypass otomatik duracak.")
    try:
        input()
    except KeyboardInterrupt:
        pass
    finally:
        print("Bypass durduruluyor...")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        print("Temiz kapatildi. Internet normale dondu.")


if __name__ == "__main__":
    main()
