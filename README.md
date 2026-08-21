<div align="center">

# persian-reel

**ویدیوی سلفی خام گوشیت رو به یک ریلز آمادهٔ اینستاگرام تبدیل می‌کنه.**

یک اسکیل برای [کلاد](https://claude.ai) که فوتیج خام رو با پنل موشن‌گرافیک،
زیرنویس فارسی سینک‌شده با گفتار، اسکچ‌های دست‌کشیده، ساند افکت و موزیک زمینه
بسته‌بندی می‌کنه و به MP4 رندر می‌گیره.

![خروجی persian-reel](docs/img/hero.png)

<sub>ساخته‌شده با کیت اسکچ و آیکون خود اسکیل. گوینده به‌صورت نمادین نشون داده شده.</sub>

</div>

---

<div dir="rtl">

## چیکار می‌کنه

یک فایل `.mov` از گوشیت به کلاد می‌دی، یک ریلز ۹:۱۶ تحویل می‌گیری:

- **سکوت‌ها رو کات می‌کنه** — مکث‌ها کوتاه می‌شن و همهٔ نشانه‌های زمانی خودکار جابه‌جا می‌شن
- **فارسی رو ترنسکرایب می‌کنه** با Whisper large-v3 و زیرنویس‌ها رو روی مکث‌های طبیعی می‌شکنه
- **پنل گرافیکی می‌سازه** بالای کادر، که هر ۳ تا ۵ ثانیه عوض می‌شه
- **اسکچ می‌کشه** به‌صورت SVG واقعی که خط‌به‌خط جلوی چشم کشیده می‌شه
- **صدا می‌ذاره** — افکت روی ضرب‌های انیمیشن، موزیک زیر صدای گوینده
- **رندر می‌گیره** فریم‌به‌فریم و قطعی، با [HyperFrames](https://github.com/heygen-com/hyperframes)

همه‌چیز لوکال اجرا می‌شه. Whisper، ffmpeg، کیت اسکچ و بیش از ۵۴۰۰ آیکون هیچ حسابی
نمی‌خوان. فقط کاتالوگ موزیک — که اختیاریه — به حساب کاربری نیاز داره.

## نصب

**در Claude Code** — داخل پوشهٔ اسکیل‌هات کلون کن:

</div>

<div dir="ltr">

```bash
git clone https://github.com/aradazr/persian-reel ~/.claude/skills/persian-reel
```

</div>

<div dir="rtl">

**در Claude Desktop یا claude.ai** — فایل بسته‌بندی‌شده رو از
[Releases](../../releases) بگیر و در Settings ← Capabilities ← Skills آپلود کن.

بعدش فقط عادی با کلاد حرف بزن:

> «این ویدیو رو برام ادیت کن»

اسکیل روی هر درخواست ویدیوی کوتاه فارسی خودش فعال می‌شه؛ لازم نیست اسمش رو تایپ کنی.

## پیش‌نیازها

| | |
|---|---|
| Node 22+ و Python 3.10+ | اجرا |
| `ffmpeg` و `ffprobe` | کار صدا و تصویر |
| Google Chrome | HyperFrames از طریقش رندر می‌گیره |
| `npm i lucide-static simple-icons` | ۲۰۰۰ آیکون + ۳۴۰۰ لوگوی برند، آفلاین |
| یک فونت فارسی | پیدا، وزیرمتن، یا مال خودت — **داخل ریپو نیست**، پایین توضیح دادم |

با `npx hyperframes doctor` بررسی کن.

## چیدمان

بوم ۱۰۸۰×۱۹۲۰، تقسیم‌شده طوری که هیچ نیمه‌ای اون یکی رو خفه نکنه:

| ناحیه | هندسه |
|---|---|
| پنل گرافیک | `0,0 1080×920` — کرم `#F7EEE7` |
| گوینده | `0,920 1080×1000` — `object-fit: cover` |
| پیل زیرنویس | وسط‌چین در `top: 886` — روی درز دو نیمه می‌شینه |

پالت: مرکب `#20242F`، اکسنت `#E07B53` برای پرکردن، `#B7502A` برای هر چیزی که متن
داره، پیل `#3C4454`.

## بازهٔ تمام‌قاب

![بازهٔ تمام‌قاب](docs/img/fullframe.png)

برداشتن پنل و پر کردن کادر با گوینده، همون چیزیه که نمی‌ذاره ریلز حس «قالب آماده»
بده. سه چیز باید با هم عوض بشن:

**کات بزن، نه فید.** فید، پنل نیمه‌شفاف رو روی فوتیج متحرک می‌کشه و شبیه باگ می‌شه.

**حدود ۲ برابر zoom کن.** صورت از ۰.۱۶ ارتفاع قاب به ۰.۳۲ می‌ره. بدون این، گوینده
فقط توی قاب خالی‌تری می‌شینه و اون لحظه حس «جای خالی» می‌ده نه تأکید.

**زیرنویس رو بیار پایین**، وگرنه می‌افته روی صورتش.

## چی داخلشه

| اسکریپت | کارش |
|---|---|
| `cutsilence.py` | مکث‌ها رو کوتاه می‌کنه و نگاشت زمانی می‌ده تا نشانه‌های موجود جابه‌جا شن |
| `transcribe.py` | Whisper large-v3 ← تایم‌کد کلمه‌ای ← خطوط اندازهٔ زیرنویس |
| `sketch.py` | SVG دست‌کشیدهٔ قطعی — لرزش seed-دار، هیچ‌وقت `Math.random()` |
| `icon.py` | آیکون Lucide رو با ضخامت مناسب ویدیو inline می‌کنه |
| `brand.py` | لوگوی رسمی برندها رو می‌گیره (simple-icons ← svgl) |
| `audiolevel.py` | `data-volume` رو از سطح اندازه‌گیری‌شده حساب می‌کنه، بعد رندر رو تأیید می‌کنه |

مستندات عمیق‌تر در `references/` — [کامپوزیشن](references/composition.md)،
[گرافیک](references/graphics.md)، [صدا](references/audio.md).

## چهار تلهٔ فارسی

این‌ها وقت واقعی از آدم می‌گیرن و هیچ‌کدوم خودشون رو اعلام نمی‌کنن.

**`<html dir="rtl">` ویدیو رو کاملاً سیاه رندر می‌کنه.** پریویو بی‌نقص به نظر می‌رسه.
به‌جاش `direction: rtl` رو در CSS فقط روی المان‌های متنی بذار.

**`letter-spacing` منفی فاصلهٔ بین کلمات فارسی رو می‌بنده.** تیتر لاتین تراکینگ تنگ
رو تحمل می‌کنه، فارسی نه — چون در خط متصل، فاصله تنها مرز کلمه‌ست. از
`letter-spacing: 0` با `word-spacing: 0.08–0.12em` استفاده کن.

**صفر فارسی «۰» یک نقطه‌ست.** عدد ۳۰۰ پیکسلی به‌صورت یک ذره رندر می‌شه. عدد رو با
حروف بنویس.

**مدل `small` ویسپر فارسی رو خراب می‌کنه** — «می‌شنویم» رو «میشنبیم» شنید. از
large-v3 استفاده کن و باز هم بازخوانی کن.

## یک چیز دیگه

**سطح صدا رو اندازه بگیر، حدس نزن.** یک بار ده تا نشانهٔ صوتی با ولوم‌های دستی گذاشته
شد و ۹ تاشون کاملاً ناشنیدنی بودند — چون میانگین یک فایل ‎−۵ دسی‌بل بود و اون یکی
‎−۳۰٫۷. یک عدد ولوم واحد نمی‌تونه به هر دو خدمت کنه. `audiolevel.py plan` برای هرکدوم
حساب می‌کنه و `verify` ثابت می‌کنه که واقعاً شنیده می‌شه.

## لایسنس

کد MIT ـه. دو چیز عمداً داخل ریپو **نیست**:

- **فونت.** پیدا تجاریه؛ لایسنس خودت رو بیار، یا از
  [وزیرمتن](https://github.com/rastikerdar/vazirmatn) استفاده کن (SIL OFL).
- **لوگوی برندها.** `brand.py` اون‌ها رو در لحظه می‌گیره به‌جای اینکه علامت تجاری
  توزیع کنه. وقتی تطابق دقیق پیدا نکنه حدس نمی‌زنه — لوگوی اشتباهی که درست رندر
  می‌شه، بدتر از لوگوی نبوده‌ست.

</div>

---

## English

**Turn a phone talking-head clip into a finished Persian Instagram Reel — automatically.**

A [Claude](https://claude.ai) skill that packages raw selfie footage with a motion-graphics
panel, RTL captions synced to speech, hand-drawn ink sketches, sound effects and a music bed,
then renders it deterministically to MP4 through
[HyperFrames](https://github.com/heygen-com/hyperframes).

```bash
git clone https://github.com/aradazr/persian-reel ~/.claude/skills/persian-reel
```

Then talk to Claude normally — the skill triggers on any Persian short-form video request.

Everything runs locally: Whisper large-v3 for transcription, ffmpeg for cutting, a
deterministic sketch kit for illustration, 5,400+ offline icons. Only the optional music
catalogue needs an account.

**Four Persian traps this skill saves you from**, none of which announce themselves:
`<html dir="rtl">` renders a completely black video while preview looks fine; negative
`letter-spacing` closes the gaps between Persian words; the Persian zero «۰» is a dot, so a
300px numeral renders as a speck; and Whisper's `small` model mangles Persian badly enough
to be unusable.

Requirements, layout geometry, the full-frame beat technique, and the audio-levelling
procedure are documented above in Persian, and in depth under
[`references/`](references/) in English.

Code is MIT. Fonts and brand logos are deliberately not bundled — Peyda is commercial, and
`brand.py` fetches trademarks on demand rather than redistributing them.

---

<div align="center">
ساخته‌شده روی <a href="https://github.com/heygen-com/hyperframes">HyperFrames</a> ·
<a href="https://github.com/lucide-icons/lucide">Lucide</a> ·
<a href="https://github.com/simple-icons/simple-icons">simple-icons</a> ·
<a href="https://github.com/ggerganov/whisper.cpp">whisper.cpp</a>
</div>
