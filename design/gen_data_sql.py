# -*- coding: utf-8 -*-
"""flight_dummy.csv 와 03_더미데이터설계서.md 의 값으로 nado_gam 의 data.sql 을 만든다.

실행: python gen_data_sql.py  (같은 폴더의 CSV 를 읽어 ../../nado_gam/src/main/resources/data.sql 을 쓴다)
BCrypt 해시는 비밀번호 1234 를 미리 해시한 값이다. 바꾸려면 ADMIN_HASH / USER_HASH 를 교체한다.
"""
import csv
import math
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "nado_gam", "src", "main", "resources", "data.sql"))

ADMIN_HASH = "$2a$10$/28dEnfkyY/xvDMFV71mqu8VARF0MC5jpDbh31V4cexP7PVMQD6l2"
USER_HASH = "$2a$10$Hv5Dp9BXiWIzFmNLl29Kjey5Qofy/kCC8cY05NzmBUrWJWx2Y7IsW"

# (코드, 한글명, 영문명, 지역)
COUNTRIES = [
    ("KR", "한국", "South Korea", "ASIA"), ("JP", "일본", "Japan", "ASIA"), ("CN", "중국", "China", "ASIA"),
    ("HK", "홍콩", "Hong Kong", "ASIA"), ("TH", "태국", "Thailand", "ASIA"), ("TW", "대만", "Taiwan", "ASIA"),
    ("SG", "싱가포르", "Singapore", "ASIA"), ("RU", "러시아", "Russia", "ASIA"),
    ("FR", "프랑스", "France", "EUROPE"), ("GB", "영국", "United Kingdom", "EUROPE"),
    ("DE", "독일", "Germany", "EUROPE"), ("ES", "스페인", "Spain", "EUROPE"), ("IT", "이탈리아", "Italy", "EUROPE"),
    ("TR", "튀르키예", "Turkiye", "EUROPE"), ("FI", "핀란드", "Finland", "EUROPE"),
    ("US", "미국", "United States", "NORTH_AMERICA"), ("CA", "캐나다", "Canada", "NORTH_AMERICA"),
    ("BR", "브라질", "Brazil", "SOUTH_AMERICA"),
    ("AE", "아랍에미리트", "United Arab Emirates", "MIDDLE_EAST"), ("QA", "카타르", "Qatar", "MIDDLE_EAST"),
    ("EG", "이집트", "Egypt", "AFRICA"), ("ZA", "남아프리카공화국", "South Africa", "AFRICA"),
    ("ET", "에티오피아", "Ethiopia", "AFRICA"),
    ("AU", "호주", "Australia", "OCEANIA"),
    # 11/19 여행지 50곳 확장
    ("NL", "네덜란드", "Netherlands", "EUROPE"), ("CZ", "체코", "Czechia", "EUROPE"),
    ("AT", "오스트리아", "Austria", "EUROPE"), ("PT", "포르투갈", "Portugal", "EUROPE"),
    ("MO", "마카오", "Macao", "ASIA"), ("VN", "베트남", "Vietnam", "ASIA"),
    ("ID", "인도네시아", "Indonesia", "ASIA"), ("MY", "말레이시아", "Malaysia", "ASIA"),
    ("MX", "멕시코", "Mexico", "NORTH_AMERICA"), ("GU", "괌", "Guam", "OCEANIA"),
]

# (코드, 한글명, 영문명, 도시, 국가, 위도, 경도, 시간대, 경유거점)
AIRPORTS = [
    ("ICN", "인천국제공항", "Incheon International Airport", "인천", "KR", 37.4602, 126.4407, "Asia/Seoul", False),
    ("GMP", "김포국제공항", "Gimpo International Airport", "서울", "KR", 37.5583, 126.7906, "Asia/Seoul", False),
    ("PUS", "김해국제공항", "Gimhae International Airport", "부산", "KR", 35.1795, 128.9382, "Asia/Seoul", False),
    ("CDG", "샤를드골국제공항", "Charles de Gaulle Airport", "파리", "FR", 49.0097, 2.5479, "Europe/Paris", False),
    ("LHR", "히드로공항", "London Heathrow Airport", "런던", "GB", 51.4700, -0.4543, "Europe/London", False),
    ("BER", "브란덴부르크공항", "Berlin Brandenburg Airport", "베를린", "DE", 52.3667, 13.5033, "Europe/Berlin", False),
    ("MAD", "바라하스공항", "Adolfo Suarez Madrid-Barajas Airport", "마드리드", "ES", 40.4983, -3.5676, "Europe/Madrid", False),
    ("FCO", "피우미치노공항", "Leonardo da Vinci-Fiumicino Airport", "로마", "IT", 41.8003, 12.2389, "Europe/Rome", False),
    ("BCN", "엘프라트공항", "Barcelona-El Prat Airport", "바르셀로나", "ES", 41.2974, 2.0833, "Europe/Madrid", False),
    ("HND", "하네다공항", "Tokyo Haneda Airport", "도쿄", "JP", 35.5494, 139.7798, "Asia/Tokyo", False),
    ("NRT", "나리타국제공항", "Narita International Airport", "도쿄", "JP", 35.7720, 140.3929, "Asia/Tokyo", False),
    ("KIX", "간사이국제공항", "Kansai International Airport", "오사카", "JP", 34.4320, 135.2304, "Asia/Tokyo", False),
    ("FUK", "후쿠오카공항", "Fukuoka Airport", "후쿠오카", "JP", 33.5859, 130.4507, "Asia/Tokyo", False),
    ("CTS", "신치토세공항", "New Chitose Airport", "삿포로", "JP", 42.7752, 141.6923, "Asia/Tokyo", False),
    ("PEK", "베이징서우두공항", "Beijing Capital International Airport", "베이징", "CN", 40.0799, 116.6031, "Asia/Shanghai", False),
    ("BKK", "수완나품공항", "Suvarnabhumi Airport", "방콕", "TH", 13.6900, 100.7501, "Asia/Bangkok", False),
    ("VVO", "블라디보스토크공항", "Vladivostok International Airport", "블라디보스토크", "RU", 43.3990, 132.1480, "Asia/Vladivostok", False),
    ("JFK", "존F케네디공항", "John F. Kennedy International Airport", "뉴욕", "US", 40.6413, -73.7781, "America/New_York", False),
    ("IAD", "덜레스국제공항", "Washington Dulles International Airport", "워싱턴D.C.", "US", 38.9531, -77.4565, "America/New_York", False),
    ("LAX", "로스앤젤레스국제공항", "Los Angeles International Airport", "로스앤젤레스", "US", 33.9416, -118.4085, "America/Los_Angeles", False),
    ("HKG", "홍콩국제공항", "Hong Kong International Airport", "홍콩", "HK", 22.3080, 113.9185, "Asia/Hong_Kong", False),
    ("PVG", "푸둥국제공항", "Shanghai Pudong International Airport", "상하이", "CN", 31.1443, 121.8083, "Asia/Shanghai", False),
    ("DXB", "두바이국제공항", "Dubai International Airport", "두바이", "AE", 25.2532, 55.3657, "Asia/Dubai", True),
    ("ORD", "오헤어국제공항", "O'Hare International Airport", "시카고", "US", 41.9742, -87.9073, "America/Chicago", False),
    ("SYD", "시드니공항", "Sydney Kingsford Smith Airport", "시드니", "AU", -33.9399, 151.1753, "Australia/Sydney", False),
    ("YVR", "밴쿠버국제공항", "Vancouver International Airport", "밴쿠버", "CA", 49.1967, -123.1815, "America/Vancouver", False),
    ("GRU", "과룰류스국제공항", "Sao Paulo-Guarulhos International Airport", "상파울루", "BR", -23.4356, -46.4731, "America/Sao_Paulo", False),
    ("CAI", "카이로국제공항", "Cairo International Airport", "카이로", "EG", 30.1219, 31.4056, "Africa/Cairo", False),
    ("CPT", "케이프타운국제공항", "Cape Town International Airport", "케이프타운", "ZA", -33.9715, 18.6021, "Africa/Johannesburg", False),
    # 경유 거점
    ("FRA", "프랑크푸르트공항", "Frankfurt Airport", "프랑크푸르트", "DE", 50.0379, 8.5622, "Europe/Berlin", True),
    ("IST", "이스탄불공항", "Istanbul Airport", "이스탄불", "TR", 41.2753, 28.7519, "Europe/Istanbul", True),
    ("HEL", "헬싱키공항", "Helsinki-Vantaa Airport", "헬싱키", "FI", 60.3172, 24.9633, "Europe/Helsinki", True),
    ("DOH", "하마드국제공항", "Hamad International Airport", "도하", "QA", 25.2731, 51.6081, "Asia/Qatar", True),
    ("TPE", "타오위안국제공항", "Taiwan Taoyuan International Airport", "타이베이", "TW", 25.0777, 121.2328, "Asia/Taipei", True),
    ("SEA", "시애틀타코마국제공항", "Seattle-Tacoma International Airport", "시애틀", "US", 47.4502, -122.3088, "America/Los_Angeles", True),
    ("HNL", "호놀룰루공항", "Daniel K. Inouye International Airport", "호놀룰루", "US", 21.3187, -157.9224, "Pacific/Honolulu", True),
    ("SIN", "창이공항", "Singapore Changi Airport", "싱가포르", "SG", 1.3644, 103.9915, "Asia/Singapore", True),
    ("ADD", "볼레국제공항", "Addis Ababa Bole International Airport", "아디스아바바", "ET", 8.9779, 38.7993, "Africa/Addis_Ababa", True),
    # 11/19 여행지 50곳 확장 (IST, SIN, TPE, HNL 은 위의 경유 거점 공항을 그대로 쓴다)
    ("MXP", "밀라노말펜사공항", "Milan Malpensa Airport", "밀라노", "IT", 45.6306, 8.7281, "Europe/Rome", False),
    ("AMS", "스키폴공항", "Amsterdam Airport Schiphol", "암스테르담", "NL", 52.3105, 4.7683, "Europe/Amsterdam", False),
    ("PRG", "바츨라프하벨공항", "Vaclav Havel Airport Prague", "프라하", "CZ", 50.1008, 14.2600, "Europe/Prague", False),
    ("VIE", "빈국제공항", "Vienna International Airport", "빈", "AT", 48.1103, 16.5697, "Europe/Vienna", False),
    ("LIS", "리스본공항", "Lisbon Humberto Delgado Airport", "리스본", "PT", 38.7742, -9.1342, "Europe/Lisbon", False),
    ("EDI", "에든버러공항", "Edinburgh Airport", "에든버러", "GB", 55.9500, -3.3725, "Europe/London", False),
    ("MFM", "마카오국제공항", "Macau International Airport", "마카오", "MO", 22.1496, 113.5916, "Asia/Macau", False),
    ("DAD", "다낭국제공항", "Da Nang International Airport", "다낭", "VN", 16.0439, 108.1990, "Asia/Ho_Chi_Minh", False),
    ("CXR", "캄란국제공항", "Cam Ranh International Airport", "나트랑", "VN", 11.9982, 109.2194, "Asia/Ho_Chi_Minh", False),
    ("PQC", "푸꾸옥국제공항", "Phu Quoc International Airport", "푸꾸옥", "VN", 10.1698, 103.9931, "Asia/Ho_Chi_Minh", False),
    ("DPS", "응우라라이공항", "Ngurah Rai International Airport", "발리", "ID", -8.7482, 115.1670, "Asia/Makassar", False),
    ("HAN", "노이바이국제공항", "Noi Bai International Airport", "하노이", "VN", 21.2212, 105.8072, "Asia/Ho_Chi_Minh", False),
    ("SGN", "떤선녓국제공항", "Tan Son Nhat International Airport", "호치민", "VN", 10.8188, 106.6520, "Asia/Ho_Chi_Minh", False),
    ("KUL", "쿠알라룸푸르국제공항", "Kuala Lumpur International Airport", "쿠알라룸푸르", "MY", 2.7456, 101.7099, "Asia/Kuala_Lumpur", False),
    ("SFO", "샌프란시스코국제공항", "San Francisco International Airport", "샌프란시스코", "US", 37.6213, -122.3790, "America/Los_Angeles", False),
    ("YYZ", "토론토피어슨공항", "Toronto Pearson International Airport", "토론토", "CA", 43.6777, -79.6248, "America/Toronto", False),
    ("MEX", "베니토후아레스공항", "Mexico City International Airport", "멕시코시티", "MX", 19.4363, -99.0721, "America/Mexico_City", False),
    ("MEL", "멜버른공항", "Melbourne Airport", "멜버른", "AU", -37.6690, 144.8410, "Australia/Melbourne", False),
    ("GUM", "괌국제공항", "Antonio B. Won Pat International Airport", "괌", "GU", 13.4834, 144.7960, "Pacific/Guam", False),
]
AP = {a[0]: a for a in AIRPORTS}

# (한글명, 영문명, 국가, 대표공항, 위도, 경도, 상태, 불가사유, 소개)
DESTINATIONS = [
    ("파리", "Paris", "FR", "CDG", 48.8566, 2.3522, "낭만과 예술이 흐르는 도시, 에펠탑과 루브르"),
    ("런던", "London", "GB", "LHR", 51.5074, -0.1278, "빅벤과 템스강, 클래식과 현대가 공존하는 도시"),
    ("베를린", "Berlin", "DE", "BER", 52.5200, 13.4050, "역사와 예술, 자유로운 분위기의 독일 수도"),
    ("마드리드", "Madrid", "ES", "MAD", 40.4168, -3.7038, "프라도 미술관과 열정적인 밤문화의 스페인 수도"),
    ("로마", "Rome", "IT", "FCO", 41.9028, 12.4964, "콜로세움과 바티칸, 도시 전체가 박물관인 영원의 도시"),
    ("바르셀로나", "Barcelona", "ES", "BCN", 41.3874, 2.1686, "가우디의 건축과 지중해가 만나는 도시"),
    ("서울", "Seoul", "KR", "ICN", 37.5665, 126.9780, "전통과 K-컬처가 어우러진 대한민국의 수도"),
    ("부산", "Busan", "KR", "PUS", 35.1796, 129.0756, "바다와 도시가 어우러진 대한민국 제2의 도시"),
    ("도쿄", "Tokyo", "JP", "NRT", 35.6762, 139.6503, "쇼핑과 미식, 전통이 가득한 일본의 수도"),
    ("오사카", "Osaka", "JP", "KIX", 34.6937, 135.5023, "먹다 망한다는 미식의 도시, 도톤보리와 오사카성"),
    ("후쿠오카", "Fukuoka", "JP", "FUK", 33.5904, 130.4017, "가깝고 먹거리 풍부한 규슈의 관문"),
    ("삿포로", "Sapporo", "JP", "CTS", 43.0618, 141.3545, "겨울 눈 축제와 라멘, 맥주의 홋카이도"),
    ("베이징", "Beijing", "CN", "PEK", 39.9042, 116.4074, "자금성과 만리장성, 중국의 수도"),
    ("방콕", "Bangkok", "TH", "BKK", 13.7563, 100.5018, "황금빛 사원과 길거리 음식의 도시"),
    ("블라디보스토크", "Vladivostok", "RU", "VVO", 43.1155, 131.8855, "러시아 극동의 항구 도시"),
    ("뉴욕", "New York", "US", "JFK", 40.7128, -74.0060, "타임스퀘어와 센트럴파크, 잠들지 않는 도시"),
    ("워싱턴D.C.", "Washington D.C.", "US", "IAD", 38.9072, -77.0369, "백악관과 스미소니언 박물관의 미국 수도"),
    ("로스앤젤레스", "Los Angeles", "US", "LAX", 34.0522, -118.2437, "할리우드와 해변, 캘리포니아의 햇살"),
    ("홍콩", "Hong Kong", "HK", "HKG", 22.3193, 114.1694, "야경과 딤섬, 동서양이 섞인 도시"),
    ("상하이", "Shanghai", "CN", "PVG", 31.2304, 121.4737, "와이탄의 야경과 초고층 빌딩의 도시"),
    ("두바이", "Dubai", "AE", "DXB", 25.2048, 55.2708, "부르즈 할리파와 사막, 쇼핑의 도시"),
    ("시카고", "Chicago", "US", "ORD", 41.8781, -87.6298, "건축과 재즈, 딥디시 피자의 도시"),
    ("시드니", "Sydney", "AU", "SYD", -33.8688, 151.2093, "오페라하우스와 하버브리지, 남반구의 항구"),
    ("밴쿠버", "Vancouver", "CA", "YVR", 49.2827, -123.1207, "산과 바다가 맞닿은 캐나다 서부의 관문"),
    ("상파울루", "Sao Paulo", "BR", "GRU", -23.5505, -46.6333, "남미 최대 도시, 다양한 문화와 미식"),
    ("카이로", "Cairo", "EG", "CAI", 30.0444, 31.2357, "피라미드와 스핑크스, 고대 문명의 도시"),
    ("케이프타운", "Cape Town", "ZA", "CPT", -33.9249, 18.4241, "테이블마운틴과 희망봉, 아프리카 남단의 보석"),
    # 11/19 여행지 50곳 확장: 유로모니터 2025·타임아웃 2026 도시 순위, 한국인 인기 해외 도시를 참고해 23곳 추가 (28~50번)
    ("밀라노", "Milan", "IT", "MXP", 45.4642, 9.1900, "패션과 디자인, 두오모의 이탈리아 북부 중심지"),
    ("암스테르담", "Amsterdam", "NL", "AMS", 52.3676, 4.9041, "운하와 자전거, 반 고흐의 도시"),
    ("이스탄불", "Istanbul", "TR", "IST", 41.0082, 28.9784, "동양과 서양이 만나는 아야소피아의 도시"),
    ("프라하", "Prague", "CZ", "PRG", 50.0755, 14.4378, "중세 건축이 그대로 남은 동유럽의 보석"),
    ("빈", "Vienna", "AT", "VIE", 48.2082, 16.3738, "음악과 커피하우스, 합스부르크의 도시"),
    ("리스본", "Lisbon", "PT", "LIS", 38.7223, -9.1393, "트램과 노을, 에그타르트의 포르투갈 수도"),
    ("에든버러", "Edinburgh", "GB", "EDI", 55.9533, -3.1883, "언덕 위 성과 축제, 스코틀랜드의 수도"),
    ("싱가포르", "Singapore", "SG", "SIN", 1.3521, 103.8198, "가든스 바이 더 베이와 미식의 도시국가"),
    ("마카오", "Macau", "MO", "MFM", 22.1987, 113.5439, "포르투갈 거리와 화려한 야경의 특별행정구"),
    ("타이베이", "Taipei", "TW", "TPE", 25.0330, 121.5654, "야시장과 온천, 가까운 대만의 수도"),
    ("다낭", "Da Nang", "VN", "DAD", 16.0544, 108.2022, "해변과 호이안 올드타운을 품은 휴양 도시"),
    ("나트랑", "Nha Trang", "VN", "CXR", 12.2388, 109.1967, "맑은 바다와 리조트의 베트남 해변 도시"),
    ("푸꾸옥", "Phu Quoc", "VN", "PQC", 10.2899, 103.9840, "에메랄드빛 바다의 베트남 최대 섬"),
    ("발리", "Bali", "ID", "DPS", -8.6500, 115.2167, "신들의 섬, 서핑과 사원과 스파"),
    ("하노이", "Hanoi", "VN", "HAN", 21.0278, 105.8342, "쌀국수와 구시가지, 베트남의 수도"),
    ("호치민", "Ho Chi Minh City", "VN", "SGN", 10.8231, 106.6297, "활기찬 오토바이 물결의 베트남 남부 도시"),
    ("쿠알라룸푸르", "Kuala Lumpur", "MY", "KUL", 3.1390, 101.6869, "페트로나스 트윈타워가 솟은 말레이시아 수도"),
    ("샌프란시스코", "San Francisco", "US", "SFO", 37.7749, -122.4194, "금문교와 언덕 길, 캘리포니아의 안개 도시"),
    ("토론토", "Toronto", "CA", "YYZ", 43.6532, -79.3832, "CN타워와 다문화, 캐나다 최대 도시"),
    ("호놀룰루", "Honolulu", "US", "HNL", 21.3069, -157.8583, "와이키키 해변과 다이아몬드헤드의 하와이"),
    ("멕시코시티", "Mexico City", "MX", "MEX", 19.4326, -99.1332, "고대 아즈텍 위에 세운 거대한 문화 도시"),
    ("멜버른", "Melbourne", "AU", "MEL", -37.8136, 144.9631, "카페와 골목 예술, 타임아웃 2026 세계 1위 도시"),
    ("괌", "Guam", "GU", "GUM", 13.4443, 144.7937, "가깝고 한적한 태평양의 휴양 섬"),
]
VVO_REASON = "전쟁·제재로 한국발 직항 운항 중단"

# 항공사 코드: (한글명, 영문명, FSC/LCC)
AIRLINES = {  # 모두 실제와 무관한 가상 항공사(이름·코드). 코드: (한글명, 영문명, FSC 일반 / LCC 저비용)
    "MG": ("민국항공", "Minguk Air", "FSC"),
    "AQ": ("아리아항공", "Aria Airlines", "FSC"),
    "BD": ("에어바다", "Air Bada", "LCC"),
    "HR": ("한라에어", "Halla Air", "LCC"),
    "NU": ("에어누리", "Air Nuri", "LCC"),
    "BS": ("푸른하늘항공", "Blue Sky Airlines", "LCC"),
    "GL": ("에어갈리아", "Air Gallia", "FSC"),
    "RH": ("라인에어", "Rhein Air", "FSC"),
    "BP": ("보스포루스항공", "Bosphorus Airlines", "FSC"),
    "LP": ("라플란드항공", "Lapland Air", "FSC"),
    "OA": ("오아시스항공", "Oasis Airways", "FSC"),
    "GF": ("걸프스타항공", "Gulfstar Airways", "FSC"),
    "SM": ("시암항공", "Siam Airways", "FSC"),
    "EB": ("에버블루항공", "Everblue Air", "FSC"),
    "SK": ("사쿠라항공", "Sakura Airlines", "FSC"),
    "DS": ("용성항공", "Dragonstar Air", "FSC"),
    "AZ": ("청룡항공", "Azure Dragon Air", "FSC"),
    "PC": ("태평양항공", "Pacific Crest Airways", "FSC"),
    "AT": ("아틀라스항공", "Atlas Airlines", "FSC"),
    "UW": ("유니온항공", "Union Airways", "FSC"),
    "RI": ("무지개섬항공", "Rainbow Isles Air", "FSC"),
    "HX": ("항구익스프레스", "Harbor Express", "LCC"),
    "SB": ("봄바람항공", "Spring Breeze Air", "LCC"),
    "SX": ("남십자성항공", "Southern Cross Airways", "FSC"),
    "LC": ("라이언시티항공", "Lion City Airways", "FSC"),
    "ML": ("메이플항공", "Maple Leaf Air", "FSC"),
    "BN": ("블루나일항공", "Blue Nile Airlines", "FSC"),
    "TL": ("튤립항공", "Tulip Airways", "FSC"),
    "AP": ("알프스항공", "Alpine Airways", "FSC"),
    "TH": ("템스항공", "Thames Airways", "FSC"),
    "LT": ("라이트제트", "Lightjet", "LCC"),
    "PL": ("주강항공", "Pearl River Air", "FSC"),
    "FM": ("포모사항공", "Formosa Airlines", "FSC"),
    "RR": ("홍강항공", "Red River Airlines", "FSC"),
    "MJ": ("메콩제트", "Mekong Jet", "LCC"),
    "NS": ("누사항공", "Nusa Airways", "FSC"),
    "MA": ("물라카항공", "Malacca Airlines", "FSC"),
    "BO": ("보르네오엑스", "Borneo X", "LCC"),
    "ZT": ("아즈텍항공", "Aztec Airlines", "FSC"),
}
NAME_TO_CODE = {v[0]: k for k, v in AIRLINES.items()}

CABINS = [("E", "ECONOMY"), ("P", "PREMIUM"), ("B", "BUSINESS"), ("F", "FIRST")]
SEATS_FSC = {"ECONOMY": 180, "PREMIUM": 30, "BUSINESS": 24, "FIRST": 8}
MILEAGE = {"ECONOMY": 1.00, "PREMIUM": 1.25, "BUSINESS": 1.50, "FIRST": 2.00}
CHANGE_DIV = {"ECONOMY": 1, "PREMIUM": 2}  # 일반석 전액, 프리미엄 절반, 비즈니스·일등석 무료

# 베스트셀러: (여행지, 여행지 내 순위) -> 누적 판매(더미). 여행지 합계 순서가 도쿄 > 로스앤젤레스 > 홍콩이 되도록 정했다.
BEST_SALES = {
    ("도쿄", 1): 1284, ("도쿄", 2): 1102, ("도쿄", 3): 986, ("도쿄", 4): 541, ("도쿄", 5): 327,
    ("로스앤젤레스", 1): 1050, ("로스앤젤레스", 2): 880, ("로스앤젤레스", 3): 520,
    ("홍콩", 1): 980, ("홍콩", 2): 760, ("홍콩", 3): 520,
}

# 이달의 특별기획 3곳. 항공편 번호 -> {등급: (특가, 정가, 한정좌석)}. 정가는 CSV 의 실제 가격과 같아야 한다.
PLANS = [
    {
        "dest": "로마", "title": "로마의 휴일, 지금 떠나요", "subtitle": "인천→로마 항공권 최대 33% 겨울 특가",
        "badge": "최대 33% OFF",
        "highlights": ["콜로세움·바티칸을 하루에", "젤라토와 파스타의 본고장", "유럽 겨울 비수기, 한적한 시즌"],
        "flights": {
            "F013": {"ECONOMY": (690000, 980000, 20), "PREMIUM": (1099000, 1570000, 6), "BUSINESS": (2198000, 3140000, 4)},
            "F014": {"ECONOMY": (490000, 720000, 30), "PREMIUM": (780000, 1150000, 8), "BUSINESS": (1550000, 2300000, 4)},
            "F015": {"ECONOMY": (520000, 760000, 30), "PREMIUM": (830000, 1220000, 8), "BUSINESS": (1660000, 2430000, 4)},
        },
    },
    {
        "dest": "삿포로", "title": "설국 삿포로, 눈부신 겨울 특가", "subtitle": "홋카이도 직항·경유 최대 25% 특가",
        "badge": "최대 25% OFF",
        "highlights": ["인천→삿포로 직항 2시간 40분", "눈 축제와 온천, 라멘과 징기스칸", "가까운 겨울 여행지 1순위"],
        "flights": {
            "F036": {"ECONOMY": (290000, 360000, 20), "BUSINESS": (840000, 1050000, 4)},
            "F037": {"ECONOMY": (159000, 210000, 30)},
            "F038": {"ECONOMY": (210000, 280000, 20), "BUSINESS": (640000, 820000, 4)},
        },
    },
    {
        "dest": "케이프타운", "title": "아프리카 남단, 케이프타운으로", "subtitle": "희망봉을 향한 경유 항공권 최대 26% 특가",
        "badge": "최대 26% OFF",
        "highlights": ["테이블마운틴과 희망봉", "펭귄이 사는 볼더스 비치", "와이너리 투어까지 한 번에"],
        "flights": {
            "F078": {"ECONOMY": (1180000, 1480000, 15), "PREMIUM": (1890000, 2370000, 6), "BUSINESS": (3790000, 4740000, 3)},
            "F079": {"ECONOMY": (1050000, 1380000, 15), "PREMIUM": (1690000, 2210000, 6), "BUSINESS": (3360000, 4420000, 3)},
            "F080": {"ECONOMY": (920000, 1250000, 15), "BUSINESS": (2300000, 3000000, 3)},
        },
    },
]

# 카드 포스터 색상 (from, to). 사진 대신 CSS 그라데이션으로 포스터를 만든다. 없으면 화면에서 기본 색을 쓴다.
POSTER = {
    "로마": ("#b5382d", "#f2a65a"), "삿포로": ("#2f6fed", "#9fd6ff"), "케이프타운": ("#0f766e", "#f59e0b"),
    "도쿄": ("#be123c", "#fb7185"), "로스앤젤레스": ("#7c3aed", "#f97316"), "홍콩": ("#0e7490", "#db2777"),
}


# 이벤트 팝업 더미 (제목, 본문, QR 이동 주소, 시작, 끝, 노출 여부). 거코·삐삐 이벤트 문구는 가상이다.
POPUPS = [
    ("나도 감 오픈 기념, 거코와 삐삐가 쏜다!",
     "11월 한 달, 이달의 특별기획 3곳을 특가로 만나 보세요. 삐삐가 뿜는 불꽃 같은 할인을 놓치지 마세요.",
     "/special", "2026-11-01 00:00:00", "2026-12-31 23:59:59", True),
    ("겨울 방학 얼리버드 이벤트",
     "내년 1월 한 달간 해외 여행 예약 고객께 거코 굿즈를 드려요. (이벤트 예정)",
     "/travel", "2027-01-01 00:00:00", "2027-01-31 23:59:59", True),
    ("가을 단풍 여행 특가 (종료)",
     "10월 한 달 진행했던 가을 여행 이벤트입니다.",
     "/bestseller", "2026-10-01 00:00:00", "2026-10-31 23:59:59", True),
]


def q(v):
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    if isinstance(v, (int, float)):
        return str(v)
    return "'" + str(v).replace("'", "''") + "'"


def km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (AP[a][5], AP[a][6], AP[b][5], AP[b][6]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(h))


def minutes(s):  # "14h20" -> 860
    h, m = s.split("h")
    return int(h) * 60 + int(m)


def tax_fuel(total_min):
    if total_min <= 240:
        return 30000
    if total_min <= 600:
        return 60000
    if total_min <= 1200:
        return 120000
    return 150000


def change_fee_base(total_min):
    if total_min <= 240:
        return 50000
    if total_min <= 600:
        return 100000
    return 150000


def aircraft(total_min, direct, code):
    if code == "OA":
        return "A380-800"
    if AIRLINES[code][2] == "LCC":
        return "B737-800" if total_min <= 180 else "A321neo"
    if direct and total_min <= 180:
        return "A321neo"
    if direct and total_min <= 360:
        return "A330-300"
    return "B777-300ER" if code in ("MG", "GL", "RH", "BP", "GF", "ML", "UW", "AT") else "A350-900"


def main():
    rows = list(csv.DictReader(open(os.path.join(HERE, "flight_dummy.csv"), encoding="utf-8")))
    dest_id = {d[0]: i + 1 for i, d in enumerate(DESTINATIONS)}
    rng = random.Random(4)
    out = []
    w = out.append

    w("-- nado_gam 더미데이터. design/gen_data_sql.py 가 flight_dummy.csv 로 생성한 파일이다. 직접 고치지 말고 스크립트를 고친다.")
    w("-- 모든 항공편·편명·가격은 실제 노선을 참고한 가상 데이터이다.")
    w("")
    w("-- [A] 관리자 / [U] 사용자 계정 (비밀번호 1234 의 BCrypt 해시)")
    w("INSERT INTO admin_account (login_id, password_hash, name, phone, email, role, status) VALUES "
      f"('admin', {q(ADMIN_HASH)}, 'admin', '010-1234-5678', 'admin@gmail.com', 'ROLE_ADMIN', 'ACTIVE');")
    w("INSERT INTO member (login_id, password_hash, name, phone, email, role, status) VALUES "
      f"('user', {q(USER_HASH)}, 'user', '010-1111-2222', 'user@naver.com', 'ROLE_USER', 'ACTIVE');")
    w("")
    w("-- [M] 국가")
    for c in COUNTRIES:
        w(f"INSERT INTO country (country_code, name_ko, name_en, region) VALUES ({q(c[0])}, {q(c[1])}, {q(c[2])}, {q(c[3])});")
    w("")
    w("-- [M] 공항 (좌표는 지구본용)")
    for a in AIRPORTS:
        w("INSERT INTO airport (airport_code, name_ko, name_en, city_name_ko, country_code, latitude, longitude, timezone, is_hub) VALUES "
          f"({q(a[0])}, {q(a[1])}, {q(a[2])}, {q(a[3])}, {q(a[4])}, {a[5]}, {a[6]}, {q(a[7])}, {q(a[8])});")
    w("")
    w("-- [M] 여행지 27개 (destination_id 는 1부터 순서대로)")
    for i, d in enumerate(DESTINATIONS):
        unavailable = d[0] == "블라디보스토크"
        c1, c2 = POSTER.get(d[0], (None, None))
        w("INSERT INTO destination (name_ko, name_en, country_code, main_airport, latitude, longitude, status, unavailable_reason, summary, poster_color_from, poster_color_to, sort_order) VALUES "
          f"({q(d[0])}, {q(d[1])}, {q(d[2])}, {q(d[3])}, {d[4]}, {d[5]}, "
          f"{q('UNAVAILABLE' if unavailable else 'AVAILABLE')}, {q(VVO_REASON if unavailable else None)}, {q(d[6])}, {q(c1)}, {q(c2)}, {i + 1});")
    w("")
    w("-- [M] 항공사")
    for code, (ko, en, t) in AIRLINES.items():
        w(f"INSERT INTO airline (airline_code, name_ko, name_en, carrier_type) VALUES ({q(code)}, {q(ko)}, {q(en)}, {q(t)});")
    w("")

    flight_sql, seg_sql, fare_sql, stat_sql, planflight_sql = [], [], [], [], []
    fid_of = {}
    for n, r in enumerate(rows, start=1):
        fid = n
        fid_of[r["id"]] = fid
        code = NAME_TO_CODE[r["airline"]]
        lcc = AIRLINES[code][2] == "LCC"
        direct = r["type"] == "직항"
        total = minutes(r["duration"])
        origin, via, arr = r["origin"], r["via"], r["arr_airport"]
        flight_sql.append(
            "INSERT INTO flight (flight_no, airline_code, destination_id, origin_airport, arrival_airport, flight_type, stops, "
            "departure_time, arrival_time, arrival_day_offset, duration_minutes, aircraft, baggage_kg, meal_included, operating_days, status) VALUES "
            f"({q(r['flight_no'])}, {q(code)}, {dest_id[r['dest']]}, {q(origin)}, {q(arr)}, {q('DIRECT' if direct else 'CONNECTING')}, "
            f"{0 if direct else 1}, {q(r['dep'] + ':00')}, {q(r['arr'] + ':00')}, {int(r['arr_day'])}, {total}, "
            f"{q(aircraft(total, direct, code))}, {15 if lcc else 23}, {q(not lcc)}, '1111111', 'ON_SALE');")

        if direct:
            seg_sql.append(f"INSERT INTO flight_segment (flight_id, seq, from_airport, to_airport, duration_minutes, layover_minutes) VALUES ({fid}, 1, {q(origin)}, {q(arr)}, {total}, NULL);")
        else:
            e1 = round(km(origin, via) / 820 * 60) + 30
            e2 = round(km(via, arr) / 820 * 60) + 30
            layover = total - e1 - e2
            if layover < 60:  # 추정 구간 시간이 너무 길면 대기 90분을 확보하도록 비율로 줄인다
                scale = (total - 90) / (e1 + e2)
                e1, e2 = round(e1 * scale), round(e2 * scale)
                layover = total - e1 - e2
            assert layover >= 60, (r["id"], layover)
            seg_sql.append(f"INSERT INTO flight_segment (flight_id, seq, from_airport, to_airport, duration_minutes, layover_minutes) VALUES ({fid}, 1, {q(origin)}, {q(via)}, {e1}, {layover});")
            seg_sql.append(f"INSERT INTO flight_segment (flight_id, seq, from_airport, to_airport, duration_minutes, layover_minutes) VALUES ({fid}, 2, {q(via)}, {q(arr)}, {e2}, NULL);")

        tax = tax_fuel(total)
        for key, cabin in CABINS:
            price = r[key]
            if not price:
                continue
            price = int(price)
            seats = 180 if lcc else SEATS_FSC[cabin]
            left = max(1, int(seats * rng.uniform(0.15, 0.9)))
            if lcc:
                refundable, change, mileage = False, 60000, 0.0
            else:
                refundable = True
                change = change_fee_base(total) // CHANGE_DIV[cabin] if cabin in CHANGE_DIV else 0
                mileage = MILEAGE[cabin]
            fare_sql.append(
                "INSERT INTO flight_fare (flight_id, cabin_class, base_price, tax_fuel, seats_total, seats_left, refundable, change_fee, mileage_rate) VALUES "
                f"({fid}, {q(cabin)}, {price - tax}, {tax}, {seats}, {left}, {q(refundable)}, {change}, {mileage:.2f});")

        tag = r["tag"]
        if tag.startswith("BEST"):
            rank = int(tag[-1])
            stat_sql.append(f"INSERT INTO flight_sales_stat (flight_id, sales_count, rank_no) VALUES ({fid}, {BEST_SALES[(r['dest'], rank)]}, {rank});")
        else:
            stat_sql.append(f"INSERT INTO flight_sales_stat (flight_id, sales_count, rank_no) VALUES ({fid}, {rng.randint(3, 240)}, NULL);")

    w("-- [M] 항공편 " + str(len(rows)) + "편")
    out.extend(flight_sql)
    w("")
    w("-- [M] 항공편 구간 (직항 1구간, 경유 2구간)")
    out.extend(seg_sql)
    w("")
    w("-- [M] 좌석등급별 요금 (표시 가격 = base_price + tax_fuel)")
    out.extend(fare_sql)
    w("")
    w("-- [M] 판매 집계 (베스트셀러 3개 여행지 도쿄 5편·로스앤젤레스 3편·홍콩 3편만 여행지 내 순위 부여)")
    out.extend(stat_sql)
    w("")

    w("-- [M] 이달의 특별기획 3곳: 로마, 삿포로, 케이프타운 (2026-11-01 ~ 2026-12-31)")
    for plan_id, plan in enumerate(PLANS, start=1):
        w("INSERT INTO monthly_plan (plan_month, destination_id, title, subtitle, badge_text, highlights, start_at, end_at, is_active) VALUES "
          f"('2026-11', {dest_id[plan['dest']]}, {q(plan['title'])}, {q(plan['subtitle'])}, {q(plan['badge'])}, "
          f"{q(chr(10).join(plan['highlights']))}, '2026-11-01 00:00:00', '2026-12-31 23:59:59', TRUE);")
        for order, (fno, cabins) in enumerate(plan["flights"].items(), start=1):
            for cabin, (sale, orig, limit) in cabins.items():
                planflight_sql.append(
                    "INSERT INTO monthly_plan_flight (plan_id, flight_id, cabin_class, sale_price, original_price, limited_seats, display_order) VALUES "
                    f"({plan_id}, {fid_of[fno]}, {q(cabin)}, {sale}, {orig}, {limit}, {order});")
    out.extend(planflight_sql)
    w("")

    w("-- [A] 이벤트 팝업 3개: 노출 중 1, 예정 1, 기간 지남 1 (메인은 노출 중이고 기간 안인 팝업 1개만 보여 준다)")
    for title, body, url, start, end, active in POPUPS:
        w("INSERT INTO popup_event (title, body, qr_target_url, start_at, end_at, is_active, created_by) VALUES "
          f"({q(title)}, {q(body)}, {q(url)}, '{start}', '{end}', {'TRUE' if active else 'FALSE'}, 1);")
    w("")

    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out))
    print("wrote", OUT, "-", len(rows), "flights,", len(fare_sql), "fares,", len(seg_sql), "segments")


if __name__ == "__main__":
    main()
