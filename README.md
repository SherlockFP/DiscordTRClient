# DiscordTRClient

Discord Türkiye'de açılmayınca uğraşmamak için yaptım. Çift tıkla açılıyor, kapatınca her şey normale dönüyor.

## Ne bu

GoodbyeDPI mantığıyla çalışıyor ama öyle ayrı ayrı programla uğraşmıyorsun. Exe'yi açınca bypass arkada kendiliğinden başlıyor, Discord'u önde açıyor. Kapatınca bypass da duruyor.

Başka sitelere dokunmuyor, sadece Discord'luk trafikten geçiyor. O yüzden internet saçmalamıyor.

## Kullanım (kolay yol)

1. [Releases](https://github.com/SherlockFP/DiscordTRClient/releases) kısmından `DiscordTRClient.exe` indir.
2. Çift tıkla, admin izni isteyecek, ver.
3. Discord açılacak, giriş yap kullan.
4. İşin bitince siyah ekrana ENTER bas, kendi kapanıyor.

İlk açılışta antivirüs mırın kırın edebilir, WinDivert yüzünden. Normaldir.

## Kaynaktan çalıştırma

Exe'ye güvenmediysen ya da kendin derlemek istiyorsan:

```bat
run_client.bat
```

`goodbyedpi/` klasörü zaten içinde geliyor (v0.2.2 x64). Python lazım sadece.

Kendin exe yapmak istersen:

```bat
pip install pyinstaller
python -m PyInstaller --onefile --uac-admin --name DiscordTRClient --add-data "goodbyedpi;goodbyedpi" --add-data "discord_blacklist.txt;." desktop_client.py
```

## Dosyalar ne

- `desktop_client.py` - asıl olay burada, bypassı başlatıp Discord'u açıyor
- `discord_blacklist.txt` - sadece Discord adresleri var, o yüzden diğer siteler bozulmuyor
- `run_client.bat` - admin isteyip python ile başlatıyor
- `relay.py` + `index.html` - yedek plan, olur da DPI yetmezse yurtdışı sunucu üzerinden metin client. Şu an lazım değil ama dursun.
- `goodbyedpi/` - GoodbyeDPI dosyaları (ValdikSS'in reposundan, v0.2.2)

## Çalışmazsa

- Admin vermediysen çalışmaz, WinDivert admin istiyor.
- Başka bir goodbyedpi açıksa önce onu kapat.
- `discord.com/app` açılmıyorsa İSS sert kapatmış olabilir, o zaman haber ver relay tarafına bakarız.

## Not

Kişisel kullanım için. GoodbyeDPI ValdikSS'in işi, driver da WinDivert'in. Ben sadece toparlayıp tek tık yaptım.
