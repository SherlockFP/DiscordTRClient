# discord client - acinca bypass basliyor, kapatinca duruyor
# siteye gomulmuyor bu is, driver lazim o yuzden exe olarak yaptim
import ctypes
import os
import shutil
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from shutil import which

if getattr(sys, "frozen", False):
    BASE = Path(sys.executable).parent
    MEIPASS = Path(getattr(sys, "_MEIPASS"))
else:
    BASE = Path(__file__).parent
    MEIPASS = BASE

def gb_klasoru():
    # exe yapinca dosyalar gecici yere aciliyor, driver orda sorun cikariyor
    # o yuzden appdata altina kopyalayip ordan calistiriyorum
    if getattr(sys, "frozen", False):
        d = Path(os.environ.get("LOCALAPPDATA", str(BASE))) / "DiscordTRClient" / "goodbyedpi"
        d.mkdir(parents=True, exist_ok=True)
        for f in ["goodbyedpi.exe", "WinDivert.dll", "WinDivert64.sys"]:
            src = MEIPASS / "goodbyedpi" / f
            dst = d / f
            if src.exists():
                if not dst.exists() or src.stat().st_size != dst.stat().st_size:
                    shutil.copy2(src, dst)
        bl = MEIPASS / "discord_blacklist.txt"
        if bl.exists():
            shutil.copy2(bl, d.parent / "discord_blacklist.txt")
        return d
    return BASE / "goodbyedpi"

GB_DIR = gb_klasoru()
GB_EXE = GB_DIR / "goodbyedpi.exe"
if getattr(sys, "frozen", False):
    BLACKLIST = GB_DIR.parent / "discord_blacklist.txt"
else:
    BLACKLIST = BASE / "discord_blacklist.txt"

# sadece discord listesine dokunuyor, gerisine karismiyor
GB_ARGS = ["-p", "-r", "-s", "-m", "--blacklist", str(BLACKLIST),
    "--dns-addr", "77.88.8.8", "--dns-port", "1253"]

def admin_mi():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def browser_bul():
    for n in ["msedge.exe", "chrome.exe", "firefox.exe"]:
        p = which(n)
        if p:
            return p
    return None

def main():
    if sys.platform != "win32":
        print("windows lazim kanka")
        return
    if not admin_mi():
        print("yonetici olarak acman lazim, yoksa driver calismiyor")
        input("kapatmak icin enter...")
        return
    if not GB_EXE.exists():
        print("goodbyedpi.exe yok, goodbyedpi klasorune bak")
        print("https://github.com/ValdikSS/GoodbyeDPI/releases")
        input("kapatmak icin enter...")
        return

    print("aciliyor, bekle...")
    proc = subprocess.Popen([str(GB_EXE)] + GB_ARGS, cwd=str(GB_DIR))
    time.sleep(1.5)
    if proc.poll() is not None:
        print("goodbyedpi hemen kapandi, baska biri acik kalmis olabilir")
        input("kapatmak icin enter...")
        return

    print("tamam discord geliyor")
    url = "https://discord.com/app"
    b = browser_bul()
    try:
        if b and "firefox" not in b.lower():
            subprocess.Popen([b, "--app=" + url])
        else:
            webbrowser.open(url)
    except Exception as e:
        print("browser acilmadi:", e)
        print("sunla gir:", url)

    print("cikmak icin enter'a bas, arkadaki de kapaniyor")
    try:
        input()
    except:
        pass
    print("kapaniyor...")
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except:
        proc.kill()
    print("kapandi, internet normale dondu")

if __name__ == "__main__":
    main()
