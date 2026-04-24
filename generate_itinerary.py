"""
Osaka Driving 2026 — PDF Itinerary Generator
Reads place descriptions (EN + Traditional Chinese) from the Google Slides source
and renders a Japan-themed A4 PDF with per-day detail pages.
"""
import math
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY

# ── fonts ─────────────────────────────────────────────────────────────────────
pdfmetrics.registerFont(TTFont('Georgia',           '/System/Library/Fonts/Supplemental/Georgia.ttf'))
pdfmetrics.registerFont(TTFont('Georgia-Bold',      '/System/Library/Fonts/Supplemental/Georgia Bold.ttf'))
pdfmetrics.registerFont(TTFont('Georgia-Italic',    '/System/Library/Fonts/Supplemental/Georgia Italic.ttf'))
pdfmetrics.registerFont(TTFont('ArialUni',          '/Library/Fonts/Arial Unicode.ttf'))  # CJK support

# ── palette ───────────────────────────────────────────────────────────────────
CRIMSON     = HexColor('#9B1B30')
SAKURA      = HexColor('#F2A7BB')
SAKURA_PALE = HexColor('#FDF0F4')
CREAM       = HexColor('#FDF6EC')
GOLD        = HexColor('#C9A84C')
INK         = HexColor('#1C1C2E')
MIST        = HexColor('#8E9BAF')
WHITE       = HexColor('#FFFFFF')
RULE        = HexColor('#D4A5B5')
LIGHT_GREY  = HexColor('#F5F5F0')

W, H = A4   # 595 x 842 pt
OUTPUT = '/Users/edwinchong/Documents/ClaudeCode/FirstTest/Osaka_Driving_2026.pdf'

# ── paragraph styles ──────────────────────────────────────────────────────────
def make_styles():
    en_body = ParagraphStyle('en_body',
        fontName='Georgia', fontSize=8.5, leading=13,
        textColor=INK, alignment=TA_JUSTIFY, spaceAfter=4)
    zh_body = ParagraphStyle('zh_body',
        fontName='ArialUni', fontSize=8.5, leading=14,
        textColor=HexColor('#3A3A5C'), alignment=TA_LEFT, spaceAfter=8)
    label   = ParagraphStyle('label',
        fontName='Georgia-Bold', fontSize=7.5, leading=10,
        textColor=CRIMSON, spaceAfter=2)
    return en_body, zh_body, label

# ── data ─────────────────────────────────────────────────────────────────────
# Each attraction is (EN_text, ZH_text)
DAYS = [
    {
        'num': 1, 'day': 'Wednesday', 'date': '20 May 2026',
        'dest': 'Rinku Town',
        'hotel': 'Odysis Suites Osaka Airport Hotel', 'booking': 'Trip.com',
        'spots': [
            {
                'name': 'Rinku Premium Outlets',
                'en': "Western Japan's largest outlet mall with ~250 stores offering discounted luxury, fashion, sports, and Japanese brands like Coach, Gucci, Nike, Snow Peak, and Onitsuka Tiger, plus food courts, Rinku Dining hall, and seaside park views.",
                'zh': "臨空城Premium Outlet是西日本最大奧特萊斯購物中心，擁有約250家店舖，提供Coach、Gucci、Nike、Snow Peak、鬼塑虎等奢侈品、時尚、運動及日系品牌折扣，另有美食街、臨空用餐廳及海濱公園景色。",
            },
            {
                'name': 'Rinku no Hoshi Ferris Wheel',
                'en': "An 80m-tall Ferris wheel in Rinku Pleasure Town Seacle complex, offering panoramic views of Osaka Bay, airport runways, and sunsets from air-conditioned gondolas (12-min ride, ~¥600–1000).",
                'zh': "臨空之星摩天輪位於臨空Pleasure Town Seacle園區內，高80米，從冷氣艙室欣賞大阪灣、機場跑道及日落全景（12分鐘騎乘，約¥600–1000）。",
            },
        ],
    },
    {
        'num': 2, 'day': 'Thursday', 'date': '21 May 2026',
        'dest': 'Uji',
        'hotel': 'Lake Biwa Marriott Hotel', 'booking': 'Bonvoy · Breakfast incl.',
        'spots': [
            {
                'name': 'Uji — Matcha Capital',
                'en': "Japan's premier green tea (matcha) production center since the 12th century, with shaded fields yielding premium sencha, gyokuro, and matcha. Must-try: matcha soba noodles, curry udon, gyoza, takoyaki, parfait, dango, zenzai, and lattes at spots like Itoh Kyuemon or Tsuen Tea (world's oldest tea shop).",
                'zh': "宇治是日本頂級綠茶（抹茶）產地，自12世紀起以遮陰茶田產優質煎茶、玉露、抹茶聞名，口感濃郁鮮美。必嚐：抹茶蕎麥麵、咖哩烏冬、餃子、章魚燒、帕菲、團子、ぜんざい、拿鐵，在Itoh Kyuemon或Tsuen茶舖（世界最古老茶店）。",
            },
            {
                'name': 'Byodo-In Temple',
                'en': "Built in 1052 as a villa-turned-Pure Land temple, Byodo-In features the stunning Phoenix Hall (National Treasure) reflecting in a pond — UNESCO World Heritage since 1994, depicted on Japan's 10-yen coin since 1951. Houses Amida Buddha statue and 52 bodhisattvas; only original Heian building to survive wars and fires.",
                'zh': "平等院，1052年建於宇治的別墅轉淨土寺，擁有壯麗鳳凰堂（國寶）倒映池塘—1994年UNESCO世界遺產，1951年起印在10日圓硬幣背面，象徵平安時代佛教藝術。供奉阿彌陀佛像及52尊菩薩，是唯一倖存於戰火的原始平安時代建築。",
            },
        ],
    },
    {
        'num': 3, 'day': 'Friday', 'date': '22 May 2026',
        'dest': 'Omi-Hachiman',
        'hotel': 'Lake Biwa Marriott Hotel', 'booking': 'Bonvoy · Breakfast incl.',
        'spots': [
            {
                'name': 'La Collina Omi-Hachiman',
                'en': "An eco-friendly confectionery complex by architect Terunobu Fujimori, featuring grass-roofed buildings blending into satoyama landscapes near Lake Biwa. Offers Taneya sweets like fluffy castella, baumkuchen, and dorayaki; cafés, bakery, food court with okowa rice, and nature walks among rice fields and wild plants.",
                'zh': "近江八幡La Collina是由建築師藤森照信設計的環保糖果綜合體，草屋頂建築融入琵琶湖附近的里山景觀。提供Taneya甜點如蓬鬆蛋糕、斑馬蛋糕、銅鑼燒；咖啡館、烘焙坊、有赤飯的美食廣場，以及可欣賞稻田和野生植物的自然散步道。",
            },
            {
                'name': 'Hachimanyama Ropeway',
                'en': "Opened 1962, ascends Mt. Hachiman in 4 minutes to castle ruins of Toyotomi Hidetsugu, offering sweeping views of Lake Biwa, Omihachiman old town, rice fields, and seasonal scenery. Features the iconic \"LOVE\" sculpture, promenade, and goshulin stamps.",
                'zh': "1962年開業的八幡山纜車，4分鐘內爬升至豐臣秀次城跡，眺望琵琶湖、近江八幡老街、稻田及季節景色如賞花或風鈴。設有「LOVE」雕塑、散步道及御朱印。",
            },
        ],
    },
    {
        'num': 4, 'day': 'Saturday', 'date': '23 May 2026',
        'dest': 'Lake Biwa',
        'hotel': 'Lake Biwa Marriott Hotel', 'booking': 'Bonvoy · Breakfast incl.',
        'spots': [
            {
                'name': 'Mangetsuji Temple — Floating Pavilion',
                'en': "The Uki-mido (Floating Pavilion) extends 12m over Lake Biwa since the Heian era (founded by Genshin), housing 1,000 Amida Buddha statues — one of Omi's Eight Views (\"Katata Rakugan\"), inspiring poets Basho and Hiroshige. A serene pier perfect for reflections.",
                'zh': "滿月寺浮御堂（浮動涼亭）自平安時代起延伸12m於琵琶湖上，由源信建立，供奉1000尊阿彌陀佛—近江八景之「堅田落雁」—啟發芭蕉/廣重；禪靜碼頭供倒影。",
            },
            {
                'name': 'Shirahige Shrine Floating Torii',
                'en': "The floating red torii (built 1603 by Toyotomi Hideyori) rises ~1km offshore in Lake Biwa's clearest waters, dedicated to Sarutahiko (longevity). Famous for mystical dawn and moonrise views, popular for photography despite road separation from the lake.",
                'zh': "白鬚神社浮鳥居（1603年豐臣秀賴建）在琵琶湖最清澈水域中離岸約1km升起，供奉猿田彥（長壽）；晨昏/月升神秘，拍照聖地，雖與湖有道路相隔。",
            },
            {
                'name': 'Enryaku-ji & Okuhiei Driveway',
                'en': "Enryaku-ji on Mt. Hiei (UNESCO 1994), Tendai headquarters founded in 788 by Saicho, spans three precincts with Konpon Chudo (fundamental hall) and 3,000+ historical halls. The scenic Okuhiei Driveway (~12km) winds through Mt. Hiei forests with vistas of Lake Biwa and Kyoto.",
                'zh': "延曆寺在比叡山（1994年UNESCO），788年最澄創立的天台宗總部，分三區有根本中堂及3000+歷史殿堂。奧比叡車道（約12km）穿越比叡山森林，盡覽琵琶湖及京都全景。",
            },
        ],
    },
    {
        'num': 5, 'day': 'Sunday', 'date': '24 May 2026',
        'dest': 'Kayabuki-no-Sato',
        'hotel': 'Fairfield by Marriott Kyoto (Amanohashidate)', 'booking': 'Bonvoy',
        'spots': [
            {
                'name': 'Kayabuki-no-Sato Village',
                'en': "A picturesque village in Kyoto's Miyama area with ~39 preserved thatched-roof farmhouses (kayabuki style), some over 200 years old, set against forested mountains and the Yura River — a National Important Preservation District since 1993. The steep \"gassho\" roofs withstand heavy snow and create timeless rural charm.",
                'zh': "茅葺之里是京都南丹市美山地區約39棟保存完好的茅葺頂農家，有些超200年歷史，背靠森林山丘和由良川—1993年起國家重要保護地區。陡峭三角「合掌」屋頂抵禦大雪，呈現永恆的鄉村魅力，適合下午悠閒漫步。",
            },
            {
                'name': 'Yuragawa Railway Bridge',
                'en': "A 300–550m reddish-brown iron railway bridge spanning the Yura River estuary near Maizuru, where Kyoto Tango Railway trains cross between sea and sky — reminiscent of Ghibli's Spirited Away. A top photo spot for trains against blue waters, mountains, and beaches like Yura Beach.",
                'zh': "由良川鐵路橋是橫跨由良川河口約300–550m的鏽紅色鐵橋，京都丹後鐵路列車穿越海天之間—宛如宮崎駿《神隱少女》的火車跨海魔幻景象，是拍攝列車與藍水、山丘、海灘的最佳地點。",
            },
        ],
    },
    {
        'num': 6, 'day': 'Monday', 'date': '25 May 2026',
        'dest': 'Ine Bay & Amanohashidate',
        'hotel': 'Fairfield by Marriott Kyoto (Amanohashidate)', 'booking': 'Bonvoy',
        'spots': [
            {
                'name': 'Ine Bay Funaya Village',
                'en': "A scenic fishing harbor lined with ~230 traditional two-story funaya boathouses (UNESCO-recognized since 2005), where ground floors store boats and upper levels serve as homes — a unique \"floating village\" amid mountains and the Sea of Japan. One of Japan's 100 most beautiful villages.",
                'zh': "伊根灣是景美的漁港，沿岸有約230座傳統兩層舟屋（2005年UNESCO保護地區），底層存放漁船，上層住人，形成「浮動村落」—日本海與群山環繞。日本100個最美麗村落之一，適合散步、拍照、體驗鄉村漁業生活。",
            },
            {
                'name': 'Ine Bay Cruise',
                'en': "~30–40 min cruise (~¥1200–1500) glides past funaya rows, letting you feed seagulls and eagles shrimp crackers. Enjoy bay panoramas, wildlife, and fishing port vibes from open or covered boats. Popular for up-close views inaccessible by foot.",
                'zh': "伊根灣遊船（約30–40分，¥1200–1500）滑過舟屋列，可餵海鷗和老鷹蝦餅乾互動，欣賞海灣全景、野生動物、漁港氛圍——近距離欣賞步行難及的景色。",
            },
            {
                'name': 'Amanohashidate Viewland & Sandbar',
                'en': "One of Japan's top 3 scenic views, Amanohashidate is a 3.6km pine-covered sandbar across Miyazu Bay. Take the chairlift/gondola to Mt. Monju Viewland for the famous \"dragon flying to heaven\" bird's-eye view, best seen upside-down. Walkable in 30–40 min with shrines and freshwater springs.",
                'zh': "天橋立是日本三景之一，一條3.6km松林覆蓋的沙洲橫跨宮津灣。乘纜車/吊椅至文殊山View Land，欣賞著名「龍昇天」鳥瞰—最佳姿勢是股覗（彎腰倒看）。騎車或步行（30–40分），沿途有神社及磯清水泉。",
            },
        ],
    },
    {
        'num': 7, 'day': 'Tuesday', 'date': '26 May 2026',
        'dest': 'Marine World & Yumura Onsen',
        'hotel': 'Asanoya, Yumura Onsen', 'booking': 'Trip.com · Breakfast & Dinner incl.',
        'spots': [
            {
                'name': 'Kinosaki Marine World',
                'en': "A nature-integrated aquarium overlooking the Sea of Japan, featuring dolphin/sea lion shows, penguin parades, walrus feeding, 12m-deep tanks, a fish-eye dive platform, fishing experiences (catch-and-tempura), and tide pools for touching sea stars. Family-friendly with a stunning Japan Sea backdrop.",
                'zh': "城崎海洋世界是融入大自然的水族館，面向日本海，包括海豚/海獅表演、企鵝遊行、海象餵食、12m深水槽、魚眼潛水台、釣魚體驗（捕捉後天婦羅炸）、潮池觸摸海星。適合家庭，日本海美景做背景。",
            },
            {
                'name': 'Asanoya Ryokan — Yumura Onsen',
                'en': "A castle-like ryokan in Yumura Onsen (near Kinosaki), offering private/open-air hot springs (24/7 access, skin-beautifying \"bijin-no-yu\"), kaiseki dinners with Tajima beef and local ingredients, tatami rooms, and heartfelt omotenashi hospitality.",
                'zh': "淺野屋是城崎附近湯村溫泉的城堡式旅館，提供私人/露天溫泉（24小時，「美人之湯」美肌功效）、懷石晚餐配但馬牛肉及當地食材、榻榻米房間，以及真摯款待。",
            },
        ],
    },
    {
        'num': 8, 'day': 'Wednesday', 'date': '27 May 2026',
        'dest': 'Himeji',
        'hotel': 'Smile Hotel Okayama', 'booking': 'Trip.com · Breakfast incl.',
        'spots': [
            {
                'name': 'Himeji Castle',
                'en': "Nicknamed \"White Heron Castle\" for its elegant white walls, Himeji is Japan's best-preserved feudal castle — a UNESCO World Heritage Site since 1993 with 83 buildings, complex mazes, moats, and defensive features across five layers, built 1609 by Ikeda Terumasa. National Treasure; tallest original keep among 12 remaining.",
                'zh': "姬路城暱稱「白鷺城」，是日本保存最完整的封建城—1993年UNESCO世界遺產，83棟建築，複雜迷宮、護城河及五層防禦設施，1609年池田輝政建。國寶；12座現存城中最高原始天守。",
            },
            {
                'name': 'Kassui-ken in Koko-en Garden',
                'en': "Adjacent to Himeji Castle, Koko-en Garden's Kassui-ken restaurant serves seasonal kaiseki, tempura, sashimi, conger eel rice bowls, udon sets, and Harima sake tastings with stunning pond garden views — perfect lunch (~¥2000–5000). Limited bento options; matcha desserts available.",
                'zh': "好古園Kassui-ken緊鄰姬路城，提供季節懷石、天婦羅、刺身、白鰻飯蓋、烏冬套餐及播磨清酒品嚐，大窗外俯瞰庭院水景—完美午餐（¥2000–5000）。限量便當如姬御膳；抹茶甜點。",
            },
        ],
    },
    {
        'num': 9, 'day': 'Thursday', 'date': '28 May 2026',
        'dest': 'Okayama',
        'hotel': 'Smile Hotel Okayama', 'booking': 'Trip.com · Breakfast incl.',
        'spots': [
            {
                'name': 'Okayama Korakuen Garden',
                'en': "One of Japan's three finest landscape gardens (with Kenrokuen and Kairakuen), spanning 133,000 sqm with ponds, streams, hills, lawns, tea/rice fields, plum/cherry/maple groves, a Noh stage, crane aviary, and views of Okayama Castle — built in 1687 for lordly leisure.",
                'zh': "岡山後樂園是日本三名園之一（兼六園、偕樂園），佔地13.3公頃，有錦鯉池塘、小溪、丘陵、草坪、茶田/稻田、梅/楓林、能舞台、鶴鳥舍及岡山城美景—1687年藩主休閒建。",
            },
            {
                'name': 'Kibitsu Jinja Shrine',
                'en': "One of Okayama's oldest shrines (1700+ years), honouring Kibitsu-hiko-no-Mikoto (origin of the Momotaro legend), featuring the unique Kibitsu-zukuri main hall (National Treasure) and a 360m-long covered wooden corridor winding up the hillside amid rice fields.",
                'zh': "吉備津神社是岡山最古老神社之一（1700年歷史），供奉吉備津彥命（桃太郎傳說發源），擁有獨特吉備津造本殿（國寶）及360m有頂木迴廊，蜿蜒山坡旁傍依稻田。",
            },
            {
                'name': 'Kurashiki Bikan Historical Quarter',
                'en': "Preserves Edo/Meiji merchant warehouses with white plaster walls, namako tiles, and willow-lined canals (boat rides). Home to Ohara Museum, Kurashiki canvas bag shops, and charming cafés in remodelled homes — evoking \"Venice of Japan.\"",
                'zh': "倉敷美觀地區保存江戶/明治商人白牆倉庫、鯉魚磚及柳樹運河（遊船），有大原美術館、倉敷帆布包、咖啡廳在改建住宅—「日本威尼斯」。",
            },
        ],
    },
    {
        'num': 10, 'day': 'Friday', 'date': '29 May 2026',
        'dest': 'Naoshima Art Island',
        'hotel': 'Hotel Sunroute Tokushima', 'booking': 'Trip.com',
        'spots': [
            {
                'name': 'Chichu Art Museum',
                'en': "Naoshima's most famous museum, designed by Tadao Ando and built mostly underground so it harmonises with the island landscape. Features major works by Claude Monet, Walter De Maria, and James Turrell, celebrated for using natural light as an integral part of the art experience.",
                'zh': "地中美術館是直島最著名的美術館，由安藤忠雄設計，多建於地下，以與島嶼景觀和諧相融。館內有莫奈、Walter De Maria 及 James Turrell 的重要作品，以善用自然光為藝術體驗的一環聞名。",
            },
            {
                'name': "Yayoi Kusama's Pumpkin",
                'en': "One of Naoshima's most iconic artworks — a bold yellow form covered with black polka dots, set by the sea. It has become a symbol of the island and a must-visit photo spot for art lovers visiting Benesse Art Site Naoshima.",
                'zh': "草間彌生的南瓜是直島最具代表性的藝術品之一，以大膽黃色造型覆黑色圓點著稱，置於海邊，已成為島嶼象徵，是前往直島Benesse藝術場地的藝術愛好者必拍勝地。",
            },
        ],
    },
    {
        'num': 11, 'day': 'Saturday', 'date': '30 May 2026',
        'dest': 'Naruto & Kobe',
        'hotel': 'Tanimachi-Kun Hotel Ebisucho 72, Osaka', 'booking': 'Trip.com',
        'spots': [
            {
                'name': 'Naruto Whirlpools',
                'en': "World-class tidal phenomena up to 20m wide in Naruto Strait (between Shikoku and Awaji Island), caused by Pacific/Seto Inland Sea currents through narrow geography — best at spring tides (March/April). View via Uzu no Michi glass-floor walkway (under bridge) or sightseeing boats.",
                'zh': "鳴門漩渦在鳴門海峽（四國及淡路島之間），世界級潮汐現象最寬達20m，太平洋/瀨戶內海水流穿窄地理形成—最佳在大潮（3–4月）。可透過渦之道（橋下玻璃步道）或觀光遊船觀賞。",
            },
            {
                'name': "Kobe's Nada Sake District",
                'en': "The world's top sake region has ~25 historic breweries (e.g., Hakutsuru, Fukuju) using Miyamizu \"palace water,\" Yamada Nishiki rice, and Tamba toji brewers. Open tours, tastings, museums, and fresh hakoshu sake across five charming villages including Uozaki and Mikage.",
                'zh': "神戶灘地區是世界最頂清酒產區，約25家歷史酒廠（白鶴、福壽等），使用宮水「御殿水」、山田錦米、丹波杜氏。提供開放參觀/品嚐、博物館、新鮮箱酒，分佈魚崎、御影等五個村落。",
            },
            {
                'name': 'Namba Yasaka Jinja',
                'en': "Features a massive 12m-tall, 6-ton lion head (Zuijin Daigongen) carved in 1988, filling the cave-like honden with its open mouth — patronised by comedians for luck, alongside goma fire rituals and a massive cedar tree.",
                'zh': "難波八坂神社有12m高6噸「啤酒桶」獅頭（瑞津大権現，1988年雕刻），洞穴般的本殿張口—深受演員拜求好運，另有護摩火儀和大雪松。",
            },
        ],
    },
    {
        'num': 12, 'day': 'Sunday', 'date': '31 May 2026',
        'dest': 'Osaka — Discovery Day',
        'hotel': 'Tanimachi-Kun Hotel Ebisucho 72, Osaka', 'booking': 'Trip.com',
        'spots': [
            {
                'name': 'Katsuoji Temple — Daruma Army',
                'en': "In Chihaya-akasaka, houses 10,000+ daruma dolls (votive wish figures) covering every surface — dedicated to Fudo Myoo. Buy and write wishes on new ones, burn completed ones at festivals. A famous \"victory\" power spot with a picturesque pagoda.",
                'zh': "勝尾寺在千早赤阪供奉10,000+達磨娃娃（勝願絵馬），滿覆各角—供奉不動明王，購新達磨寫願，舊達磨在祭典火化—著名「勝運」聖地，配上美麗的塔。",
            },
            {
                'name': 'Osaka Ukiyoe Museum',
                'en': "In Dotonbori, showcases Kamigata ukiyo-e (Osaka/Kyoto actor prints from the Edo era) — the world's largest private collection with rotating exhibits of Hokusai, Hiroshige, tools, and theatre replicas. Fascinating contrast: realistic Kamigata style vs. Edo's stylised beauty.",
                'zh': "大阪浮世繪博物館（上方支部）在道頓堀展示上方浮世繪（江戶時代大阪/京都歌舞伎演員版畫），世界最大私人收藏，輪換展示北齋、廣重、工具、劇場複製品—現實主義vs.江戶風格化美態。",
            },
            {
                'name': 'Tombori River Cruise & Dotonbori',
                'en': "20-min cruise (~¥2000) floats the Dotonbori canal past Glico Man, Ebisu Bridge, and neon signs from yellow boats. By night the Ebisu Tower Don Quijote Ferris Wheel (80m, opened 2023) adds a prime photo-op spinning over the neon canal.",
                'zh': "道頓堀遊船（20分約¥2000）乘黃色小船飄過Glico Man、惠比壽橋、霓虹標誌；夜晚惠比壽Tower堂吉訶德摩天輪（80m，2023年）在霓虹運河上旋轉，是夜拍絕佳勝地。",
            },
        ],
    },
    {
        'num': 13, 'day': 'Monday', 'date': '1 June 2026',
        'dest': 'Osaka — City Day',
        'hotel': 'Tanimachi-Kun Hotel Ebisucho 72, Osaka', 'booking': 'Trip.com',
        'spots': [
            {
                'name': 'Umeda Shopping Hub',
                'en': "Osaka's premier shopping district featuring massive complexes like Grand Front Osaka, Hankyu and Hanshin Department Stores, and HEP Five, offering fashion, luxury goods, electronics, and souvenirs in vibrant multi-level malls. Perfect for diverse retail therapy amid dining and entertainment.",
                'zh': "大阪梅田是旗艦購物中心，包括Grand Front Osaka、阪急阪神百貨及HEP Five等，提供時裝、奢侈品、電器及紀念品在多層購物中心。完美結合娛樂、美食和購物。",
            },
            {
                'name': 'Street Kart Osaka',
                'en': "Mario Kart-style go-kart tours (1–2 hrs, ~¥9000+) in costumes through Dotonbori, Osaka Castle, and city streets — licensed, English-speaking guides, thrilling photo opportunities (international driving licence required).",
                'zh': "大阪街頭卡丁車提供馬利歐賽車式卡丁車旅程（1–2小時，¥9000+），穿著道頓堀、大阪城街道—持牌、英語導遊、刺激拍照（需國際駕照）。",
            },
        ],
    },
    {
        'num': 14, 'day': 'Tuesday', 'date': '2 June 2026',
        'dest': 'Osaka — Farewell',
        'hotel': '— Check out & fly home —', 'booking': '',
        'spots': [
            {
                'name': 'Namba & Kuromon Market',
                'en': "Namba is a bustling district centred on Dotonbori with trendy malls like Namba Parks and Shinsaibashi arcades — fashion, cosmetics, anime goods, and street food. Kuromon Market (600m arcade, ~150 stalls) sells fresh seafood (uni, tuna), wagyu, grilled scallops, and oysters — the Edo-era \"black gate\" foodie heaven.",
                'zh': "難波是以道頓堀為中心的熱鬧購物區，難波Parks及心齋橋拱廊提供時裝、美妝、動漫商品和街頭食品。黑門市場（600m拱廊，約150攤）賣新鮮海鮮（海膽、金槍魚）、和牛、烤扇貝、牡蠣—江戶時代「黑門」美食天堂。",
            },
        ],
    },
]

# ── helpers ───────────────────────────────────────────────────────────────────

def draw_sakura(c, cx, cy, size=14, alpha=0.55):
    c.saveState()
    c.setFillColor(SAKURA)
    c.setFillAlpha(alpha)
    c.setStrokeColor(CRIMSON)
    c.setStrokeAlpha(alpha * 0.6)
    c.setLineWidth(0.4)
    for i in range(5):
        angle = math.radians(i * 72 - 90)
        px = cx + math.cos(angle) * size * 0.55
        py = cy + math.sin(angle) * size * 0.55
        c.saveState()
        c.transform(math.cos(angle), math.sin(angle),
                    -math.sin(angle), math.cos(angle), px, py)
        c.ellipse(-size * 0.28, -size * 0.42, size * 0.28, size * 0.42,
                  stroke=1, fill=1)
        c.restoreState()
    c.setFillColor(GOLD)
    c.setFillAlpha(alpha)
    c.circle(cx, cy, size * 0.12, stroke=0, fill=1)
    c.restoreState()

def draw_seigaiha(c, cx, cy, r=18, rows=4, cols=5, alpha=0.06):
    c.saveState()
    c.setFillColor(CRIMSON)
    c.setStrokeColor(CRIMSON)
    c.setFillAlpha(alpha)
    c.setStrokeAlpha(alpha * 1.5)
    c.setLineWidth(0.5)
    for row in range(rows):
        for col in range(cols):
            x = cx + col * r * 1.8 - (row % 2) * r * 0.9
            y = cy + row * r * 1.1
            p = c.beginPath()
            p.arc(x - r, y - r, x + r, y + r, 0, 180)
            p.close()
            c.drawPath(p, fill=1, stroke=1)
    c.restoreState()

def h_rule(c, x, y, w, col=RULE, thick=0.6):
    c.saveState()
    c.setStrokeColor(col)
    c.setLineWidth(thick)
    c.line(x, y, x + w, y)
    c.restoreState()

def page_bg(c):
    c.setFillColor(WHITE)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(CRIMSON)
    c.rect(0, 0, 6, H, fill=1, stroke=0)
    draw_seigaiha(c, W - 15, 15, r=16, rows=3, cols=4, alpha=0.05)

def page_footer(c):
    c.setFillColor(RULE)
    c.rect(0, 0, W, 20, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont('Georgia-Italic', 7.5)
    c.drawCentredString(W / 2, 6, 'Osaka Driving 2026  ·  Personal Travel Itinerary')

def draw_paragraph(c, style, text, x, y, width):
    """Draw a Paragraph and return the height consumed."""
    p = Paragraph(text.replace('&', '&amp;'), style)
    w, h = p.wrap(width, 9999)
    p.drawOn(c, x, y - h)
    return h

# ── cover ─────────────────────────────────────────────────────────────────────

def cover(c):
    c.setFillColor(INK)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    c.setFillColor(CRIMSON)
    c.rect(0, 0, 18, H, fill=1, stroke=0)

    c.setFillColor(CREAM)
    c.rect(18, 60, W - 18, H - 120, fill=1, stroke=0)

    draw_seigaiha(c, W - 80, H - 10, r=22, rows=5, cols=4, alpha=0.07)

    for pos in [(W-55, H-55, 20, 0.5), (W-95, H-80, 14, 0.4),
                (W-40, H-100, 11, 0.3), (60, 110, 18, 0.45),
                (90, 80, 13, 0.35), (W-70, 130, 15, 0.4)]:
        draw_sakura(c, *pos)

    c.saveState()
    c.setFillColor(CRIMSON)
    c.setFillAlpha(0.12)
    c.circle(W - 90, H - 90, 130, stroke=0, fill=1)
    c.restoreState()

    c.saveState()
    c.setFont('Georgia-Italic', 9)
    c.setFillColor(CRIMSON)
    c.setFillAlpha(0.55)
    for i, ch in enumerate(['大', '阪', 'ド', 'ラ', 'イ', 'ブ']):
        c.drawString(26, H - 130 - i * 22, ch)
    c.restoreState()

    ty = H - 180
    c.setFillColor(CRIMSON)
    c.setFont('Georgia-Bold', 38)
    c.drawString(50, ty, 'Osaka Driving')
    c.setFillColor(GOLD)
    c.setFont('Georgia', 38)
    c.drawString(50, ty - 48, '2026')

    c.setStrokeColor(GOLD)
    c.setLineWidth(1.2)
    c.line(50, ty - 62, 340, ty - 62)

    c.setFillColor(INK)
    c.setFont('Georgia-Italic', 14)
    c.drawString(50, ty - 82, 'A 14-Day Road Journey Through the Heart of Japan')

    c.setFillColor(CRIMSON)
    c.setFont('Georgia-Bold', 12)
    c.drawString(50, ty - 115, '20 MAY  —  2 JUNE 2026')
    c.setFillColor(MIST)
    c.setFont('Georgia', 10)
    c.drawString(50, ty - 132, 'Departing Singapore 19 May  ·  Returning 3 June')

    # intro blurb box
    by = 145
    bh = 175
    c.setStrokeColor(RULE)
    c.setLineWidth(0.8)
    c.setFillColor(SAKURA_PALE)
    c.roundRect(50, by, W - 100, bh, 6, fill=1, stroke=1)

    c.setFillColor(CRIMSON)
    c.setFont('Georgia-Bold', 9)
    c.drawString(66, by + bh - 16, 'THE JOURNEY')
    h_rule(c, 66, by + bh - 22, W - 132, RULE, 0.5)

    en_style = ParagraphStyle('cover_en', fontName='Georgia', fontSize=8,
                              leading=12, textColor=INK, alignment=TA_JUSTIFY)
    zh_style = ParagraphStyle('cover_zh', fontName='ArialUni', fontSize=8,
                              leading=13, textColor=HexColor('#3A3A5C'), alignment=TA_LEFT)

    en_txt = ("Buckle up for a thrilling 14-day Japan road trip — stunning landscapes, historic gems, "
              "and foodie bliss, all by car with minimal walking! We start early and end early.")
    zh_txt = "準備好14天日本公路旅行盛宴，震撼景觀、歷史奇觀、美食天堂—全車可達步行極少，讓您盡享開車刺激！我們會早開始早結束。"

    ep = Paragraph(en_txt.replace('&', '&amp;'), en_style)
    ew, eh = ep.wrap(W - 132, 9999)
    ep.drawOn(c, 66, by + bh - 40 - eh)

    zp = Paragraph(zh_txt.replace('&', '&amp;'), zh_style)
    zw, zh_h = zp.wrap(W - 132, 9999)
    zp.drawOn(c, 66, by + bh - 44 - eh - zh_h)

    c.setFillColor(MIST)
    c.setFont('Georgia-Italic', 8)
    c.drawCentredString(W / 2, 38, '✦  Itinerary prepared for personal travel  ✦')

    c.showPage()

# ── hotel overview ─────────────────────────────────────────────────────────────

def hotels_page(c):
    page_bg(c)
    y = H - 52
    c.setFillColor(CRIMSON)
    c.setFont('Georgia-Bold', 16)
    c.drawString(40, y, 'Accommodation Overview')
    y -= 24
    h_rule(c, 40, y, W - 80)
    y -= 16

    rows = [
        ('Night(s)', 'Date(s)', 'Hotel', 'Booking'),
        ('1',  '20 May',       'Odysis Suites Osaka Airport Hotel',          'Trip.com'),
        ('3',  '21–23 May',    'Lake Biwa Marriott Hotel',                   'Bonvoy · B'),
        ('2',  '24–25 May',    'Fairfield by Marriott Kyoto (Amanohashidate)','Bonvoy'),
        ('1',  '26 May',       'Asanoya, Yumura Onsen',                      'Trip.com · B+D'),
        ('2',  '27–28 May',    'Smile Hotel Okayama',                        'Trip.com · B'),
        ('1',  '29 May',       'Hotel Sunroute Tokushima',                   'Trip.com'),
        ('3',  '30 May–1 Jun', 'Tanimachi-Kun Hotel Ebisucho 72, Osaka',     'Trip.com'),
    ]
    col_x = [42, 82, 145, 430]

    for i, row in enumerate(rows):
        rh = 22 if i == 0 else 26
        if i == 0:
            c.setFillColor(CRIMSON)
            c.rect(42, y - rh + 6, W - 84, rh, fill=1, stroke=0)
            c.setFillColor(WHITE)
            c.setFont('Georgia-Bold', 9)
        else:
            if i % 2 == 0:
                c.setFillColor(SAKURA_PALE)
                c.rect(42, y - rh + 6, W - 84, rh, fill=1, stroke=0)
            c.setFillColor(INK)
            c.setFont('Georgia', 9.5)
        for j, cell in enumerate(row):
            c.drawString(col_x[j] + 4, y - 2, cell)
        y -= rh

    y -= 10
    h_rule(c, 40, y, W - 80)
    y -= 16
    c.setFillColor(MIST)
    c.setFont('Georgia-Italic', 8.5)
    c.drawString(42, y, 'B = Breakfast included    D = Dinner included    Bonvoy = Marriott Bonvoy member rate')

    draw_sakura(c, W - 60, 90, 16, 0.4)
    draw_sakura(c, W - 95, 65, 11, 0.3)
    page_footer(c)
    c.showPage()

# ── day page ──────────────────────────────────────────────────────────────────

MARGIN = 40
CONTENT_W = W - MARGIN * 2

def day_page(c, day, en_style, zh_style, label_style):
    page_bg(c)

    # ── header band ──
    hband_h = 52
    c.setFillColor(CRIMSON)
    c.rect(0, H - hband_h, W, hband_h, fill=1, stroke=0)

    # day badge circle
    c.setFillColor(SAKURA_PALE)
    c.circle(MARGIN + 20, H - hband_h / 2, 16, stroke=0, fill=1)
    c.setFillColor(CRIMSON)
    c.setFont('Georgia-Bold', 10)
    num_str = str(day['num'])
    c.drawCentredString(MARGIN + 20, H - hband_h / 2 - 4, num_str)

    # destination
    c.setFillColor(WHITE)
    c.setFont('Georgia-Bold', 15)
    c.drawString(MARGIN + 44, H - 22, day['dest'])
    c.setFillColor(SAKURA)
    c.setFont('Georgia-Italic', 9)
    c.drawString(MARGIN + 44, H - 38, day['day'] + '  ·  ' + day['date'])

    # right: small sakura cluster
    draw_sakura(c, W - 35, H - hband_h / 2 + 8, 11, 0.45)
    draw_sakura(c, W - 58, H - hband_h / 2 - 6, 9, 0.35)

    # ── body ──
    y = H - hband_h - 14

    for spot in day['spots']:
        # spot name label
        if y < 80:
            c.showPage()
            page_bg(c)
            y = H - 30

        # spot name tag
        tag_h = 16
        c.setFillColor(SAKURA_PALE)
        c.roundRect(MARGIN, y - tag_h, CONTENT_W, tag_h, 4, fill=1, stroke=0)
        c.setFillColor(CRIMSON)
        c.circle(MARGIN + 9, y - tag_h / 2, 3.5, stroke=0, fill=1)
        c.setFont('Georgia-Bold', 9)
        c.drawString(MARGIN + 17, y - tag_h + 4, spot['name'])
        y -= tag_h + 4

        # English text
        ep = Paragraph(spot['en'].replace('&', '&amp;'), en_style)
        ew, eh = ep.wrap(CONTENT_W, 9999)
        if y - eh < 80:
            c.showPage(); page_bg(c); y = H - 30
        ep.drawOn(c, MARGIN, y - eh)
        y -= eh + 3

        # Chinese text
        zp = Paragraph(spot['zh'].replace('&', '&amp;'), zh_style)
        zw, zh_h = zp.wrap(CONTENT_W, 9999)
        if y - zh_h < 80:
            c.showPage(); page_bg(c); y = H - 30
        zp.drawOn(c, MARGIN, y - zh_h)
        y -= zh_h + 12

    # ── hotel strip ──
    strip_h = 34
    sx = MARGIN
    sy = 28
    c.setFillColor(SAKURA_PALE)
    c.roundRect(sx, sy, CONTENT_W, strip_h, 5, fill=1, stroke=0)
    h_rule(c, sx, sy + strip_h, CONTENT_W, RULE, 0.4)

    c.setFillColor(CRIMSON)
    c.setFont('Georgia-Bold', 7.5)
    c.drawString(sx + 10, sy + strip_h - 12, 'STAY')
    c.setFillColor(INK)
    c.setFont('Georgia', 8.5)
    hotel = day['hotel'] if len(day['hotel']) < 52 else day['hotel'][:49] + '…'
    c.drawString(sx + 38, sy + strip_h - 12, hotel)
    if day['booking']:
        c.setFillColor(MIST)
        c.setFont('Georgia-Italic', 7.5)
        c.drawString(sx + 38, sy + 8, day['booking'])

    page_footer(c)
    c.showPage()

# ── main ─────────────────────────────────────────────────────────────────────

def build():
    c = canvas.Canvas(OUTPUT, pagesize=A4)
    c.setTitle('Osaka Driving 2026 — Itinerary')
    c.setAuthor('Personal Travel Plan')

    en_style, zh_style, label_style = make_styles()

    cover(c)
    hotels_page(c)

    for day in DAYS:
        day_page(c, day, en_style, zh_style, label_style)

    c.save()
    print(f'PDF saved → {OUTPUT}')

build()
