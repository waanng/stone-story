#!/usr/bin/env python3
import json
import re
import time
import urllib.parse
import urllib.request
from html import escape
from urllib.error import HTTPError, URLError
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw_chapters"
READER_DIR = DATA_DIR / "chapter_pages"
USER_AGENT = "CodexHonglouExamMap/1.0 (local educational study site)"

CORE_CHARACTERS = [
    "贾宝玉", "林黛玉", "薛宝钗", "王熙凤", "贾母", "王夫人", "贾政", "贾赦", "贾雨村", "甄士隐",
    "秦可卿", "元春", "迎春", "探春", "惜春", "李纨", "妙玉", "史湘云", "袭人", "晴雯",
    "香菱", "紫鹃", "刘姥姥", "尤二姐", "尤三姐", "薛蟠", "贾琏", "平儿", "鸳鸯", "焦大",
]

IMPORTANT = {
    1: {
        "importance": 5,
        "summary": "以女娲补天、通灵宝玉、木石前盟开篇，点明全书的神话框架和“梦”“情”“石”的核心隐喻。",
        "events": ["女娲补天剩下一块顽石", "僧道携石入世", "甄士隐梦见太虚幻境端倪", "英莲走失，甄家命运转折"],
        "exam": ["神话开篇的象征意义", "木石前盟与宝黛关系", "梦与真实的叙事结构"],
        "question": "为什么说第一回为全书定下了“梦幻”与“悲剧”的基调？",
    },
    2: {
        "importance": 5,
        "summary": "通过冷子兴演说荣国府，集中交代贾府世系、家族格局和由盛转衰的隐患。",
        "events": ["贾雨村遇冷子兴", "冷子兴讲述荣宁二府", "宝玉衔玉而生的传闻出现", "贾府表面繁华、内里衰败的苗头显露"],
        "exam": ["四大家族与贾府结构", "由盛转衰的伏笔", "宝玉形象的初步铺垫"],
        "question": "冷子兴演说荣国府一段，为什么是理解全书家族结构的重要入口？",
    },
    3: {
        "importance": 5,
        "summary": "林黛玉初进贾府，作者借她的视角展示贾府礼法秩序、人物等级和宝黛初见。",
        "events": ["黛玉离父入京", "贾母、王夫人、王熙凤等集中出场", "黛玉小心观察贾府规矩", "宝玉与黛玉初见"],
        "exam": ["黛玉形象", "王熙凤出场描写", "贾府礼法秩序", "宝黛关系开端"],
        "question": "林黛玉进贾府一回如何通过人物出场表现贾府的等级秩序？",
    },
    4: {
        "importance": 5,
        "summary": "葫芦僧判断葫芦案，揭出护官符和四大家族盘根错节的权力网络。",
        "events": ["贾雨村审理薛蟠案", "门子讲出护官符", "四大家族关系明朗", "贾雨村徇私枉法"],
        "exam": ["四大家族", "封建权力关系", "贾雨村形象", "社会环境与人物命运"],
        "question": "“护官符”在全书中有什么结构和主题意义？",
    },
    5: {
        "importance": 5,
        "summary": "宝玉梦游太虚幻境，金陵十二钗判词和《红楼梦曲》预示主要女性人物命运。",
        "events": ["宝玉入太虚幻境", "看到金陵十二钗判词", "听《红楼梦曲》", "警幻仙姑点出情与幻"],
        "exam": ["金陵十二钗判词", "人物命运伏笔", "全书悲剧结构", "情与梦的主题"],
        "question": "第五回为什么被称为理解《红楼梦》人物命运的总纲？",
    },
    6: {
        "importance": 4,
        "summary": "刘姥姥一进荣国府，乡村贫寒家庭与豪门贾府第一次正面相遇，贾府的富贵和等级秩序被外部视角照亮。",
        "events": ["刘姥姥因家计艰难到荣国府攀亲求助", "周瑞家的引荐刘姥姥见王熙凤", "王熙凤以体面方式施舍银两", "刘姥姥成为观察贾府的外部眼睛"],
        "exam": ["刘姥姥的叙事作用", "贫富对比", "王熙凤处事手腕", "贾府日常秩序"],
        "question": "刘姥姥一进荣国府如何通过外部视角表现贾府的富贵与人情？",
    },
    7: {
        "importance": 3,
        "summary": "周瑞家的送宫花串联多个女性空间，薛宝钗正式进入读者视野，并初步呈现她稳重、会自持的性格。",
        "events": ["周瑞家的往各处送宫花", "宝钗谈冷香丸，显出身体与性格特点", "黛玉对宫花先后顺序敏感", "焦大醉骂暴露宁国府阴暗面"],
        "exam": ["宝钗初步形象", "黛玉敏感心理", "细节中的等级秩序", "焦大醉骂的伏笔意义"],
        "question": "送宫花这一日常情节，为什么能表现人物性格和贾府秩序？",
    },
    8: {
        "importance": 4,
        "summary": "宝玉探望宝钗并互看通灵宝玉与金锁，金玉良缘线索浮现，与木石前盟形成结构性对照。",
        "events": ["宝玉到梨香院看宝钗", "宝玉看宝钗金锁，宝钗看通灵宝玉", "宝玉与宝钗关系被金玉之说牵连", "黛玉到来后言语含酸"],
        "exam": ["金玉良缘", "宝黛钗关系", "黛玉心理", "物象伏笔"],
        "question": "通灵宝玉与金锁互看这一细节，怎样为宝黛钗关系埋下伏笔？",
    },
    9: {
        "importance": 2,
        "summary": "宝玉入家塾，学堂中的混乱展现贾府子弟教育的失序，也衬出宝玉不适应传统仕途教育。",
        "events": ["宝玉到家塾读书", "秦钟与宝玉亲近", "学童之间矛盾冲突升级", "学堂秩序混乱"],
        "exam": ["贾府教育问题", "宝玉性格", "家族衰败的日常表现"],
        "question": "家塾风波能反映贾府教育和家族风气中的哪些问题？",
    },
    10: {
        "importance": 3,
        "summary": "秦可卿病情加重，宁国府的奢华、人情和隐秘危机开始显露，为后文丧事和托梦铺垫。",
        "events": ["秦可卿病重", "贾珍忧心延医", "张友士诊脉分析病情", "宁国府内部气氛压抑"],
        "exam": ["秦可卿形象与命运", "宁国府危机", "病情描写的伏笔"],
        "question": "秦可卿病重的描写为什么不只是交代病情，也是在写宁国府的危机？",
    },
    11: {
        "importance": 3,
        "summary": "贾敬寿辰与秦可卿病情交织，热闹宴会和病中凄凉形成对照，宁国府的繁华与不安并置。",
        "events": ["宁国府为贾敬寿辰设宴", "王熙凤等到宁府赴会", "宝玉探望秦可卿", "秦可卿病势令人忧惧"],
        "exam": ["乐景写哀", "宁国府生活", "秦可卿悲剧伏笔", "宝玉情感敏感"],
        "question": "本回如何通过寿宴与病情的对照表现繁华背后的衰败感？",
    },
    12: {
        "importance": 3,
        "summary": "贾瑞因痴迷王熙凤而走向死亡，风月宝鉴以寓言方式警示欲望、幻象与自毁。",
        "events": ["贾瑞纠缠王熙凤", "王熙凤设局惩治贾瑞", "跛足道人送风月宝鉴", "贾瑞执迷不悟而死"],
        "exam": ["王熙凤手段", "风月宝鉴象征", "欲望与幻象", "讽刺意味"],
        "question": "风月宝鉴在本回中有什么象征意义？",
    },
    13: {
        "importance": 5,
        "summary": "秦可卿托梦王熙凤，预言贾府盛极而衰，并提出家族保全之策，是全书兴亡主题的重要节点。",
        "events": ["秦可卿临终托梦王熙凤", "提醒月满则亏、水满则溢", "提出置办祭祀产业等长远安排", "秦可卿去世，宁国府大办丧事"],
        "exam": ["秦可卿托梦", "贾府兴亡伏笔", "王熙凤能力与局限", "盛极而衰主题"],
        "question": "秦可卿托梦为什么是理解贾府衰败主题的关键情节？",
    },
    14: {
        "importance": 4,
        "summary": "王熙凤协理宁国府，展现她出色的组织、威慑和管理能力，也显露贾府治理依赖个人手腕的隐患。",
        "events": ["王熙凤受托协理秦可卿丧事", "她迅速立规矩、分职责", "严惩迟到仆妇以树威", "宁国府丧事井然有序"],
        "exam": ["王熙凤人物形象", "管理能力", "贾府内宅权力", "治家方式的利弊"],
        "question": "王熙凤协理宁国府如何表现她的才干与性格复杂性？",
    },
    15: {
        "importance": 3,
        "summary": "秦可卿丧礼铺张隆重，北静王与宝玉相见，贾府的社会地位和贵族交往网络进一步展开。",
        "events": ["秦可卿出殡场面极其隆重", "北静王路祭并召见宝玉", "宝玉获赠鹡鸰香念珠", "秦钟与智能儿情事继续牵连"],
        "exam": ["贵族礼仪与排场", "贾府社会地位", "宝玉形象", "繁华中的虚耗"],
        "question": "秦可卿丧礼的盛大排场，如何体现贾府的地位与衰败隐患？",
    },
    16: {
        "importance": 4,
        "summary": "贾元春晋封贤德妃，贾府迎来烈火烹油的荣耀；同时秦钟之死延续青春生命早逝的悲感。",
        "events": ["贾政生日时传来元春晋封消息", "贾府上下欢腾并准备省亲", "秦钟病重身亡", "宝玉再次感受亲近之人的离散"],
        "exam": ["元春晋封", "家族荣耀", "盛极而衰伏笔", "宝玉情感世界"],
        "question": "元春晋封为什么既是贾府荣耀，也是后文衰败的重要伏笔？",
    },
    17: {
        "importance": 4,
        "summary": "大观园建成并试才题对额，园林空间成为少女群体生活和诗意世界的舞台。",
        "events": ["众人游览大观园", "宝玉题写匾额对联", "大观园空间初步成型"],
        "exam": ["大观园空间意义", "宝玉才情", "诗意世界与现实家族的对照"],
        "question": "大观园为什么不只是生活空间，也是人物命运空间？",
    },
    18: {
        "importance": 5,
        "summary": "元妃省亲展现贾府烈火烹油般的繁华，也埋下经济消耗和盛极而衰的伏笔。",
        "events": ["元春省亲", "贾府铺张迎驾", "骨肉相见中有荣华也有悲感", "大观园正式获得意义"],
        "exam": ["贾府鼎盛", "盛极而衰", "元春形象", "家族荣耀背后的代价"],
        "question": "元妃省亲一回怎样同时表现贾府的荣耀与衰败隐患？",
    },
    23: {
        "importance": 4,
        "summary": "宝玉、黛玉共读《西厢记》，青春情感和礼法禁忌之间的张力开始明显化。",
        "events": ["宝玉携书入园", "宝黛共读西厢", "二人以曲文互相试探", "黛玉嗔怪又动情"],
        "exam": ["宝黛爱情", "青春意识", "礼法与真情", "语言细节"],
        "question": "共读西厢如何推动宝黛关系的发展？",
    },
    27: {
        "importance": 5,
        "summary": "宝钗扑蝶与黛玉葬花形成鲜明对照，集中呈现两位女性的性格差异和命运感。",
        "events": ["宝钗扑蝶", "小红与坠儿私语", "黛玉葬花", "《葬花吟》表达生命悲感"],
        "exam": ["黛玉形象", "宝钗形象", "人物对比", "诗歌与人物命运"],
        "question": "宝钗扑蝶和黛玉葬花放在同一回，有什么对比意义？",
    },
    33: {
        "importance": 5,
        "summary": "宝玉挨打集中爆发父子冲突、仕途观冲突和家族礼法对个人天性的压迫。",
        "events": ["忠顺王府索人", "贾环进谗", "贾政痛打宝玉", "贾母、王夫人护宝玉"],
        "exam": ["宝玉叛逆性", "父子冲突", "封建礼教", "家族权力结构"],
        "question": "宝玉挨打一事反映了哪些人物之间的价值冲突？",
    },
    37: {
        "importance": 4,
        "summary": "海棠诗社成立，大观园成为才情、友谊和青春精神集中展开的空间。",
        "events": ["探春发起诗社", "众人取号结社", "咏白海棠", "姐妹才情各有呈现"],
        "exam": ["大观园青春群像", "探春组织能力", "诗社的象征意义"],
        "question": "诗社活动如何表现大观园女儿们的精神世界？",
    },
    39: {
        "importance": 4,
        "summary": "刘姥姥二进荣国府，以外部乡村视角反衬贾府富贵，也增强小说的社会广度。",
        "events": ["刘姥姥进荣国府", "众人逗趣取乐", "乡土视角进入大观园", "贾府富贵被外部化呈现"],
        "exam": ["刘姥姥作用", "对比手法", "贾府生活", "雅俗互照"],
        "question": "刘姥姥这个人物在小说中为什么重要？",
    },
    48: {
        "importance": 4,
        "summary": "香菱学诗表现普通女性对精神生活的追求，也从侧面映照大观园的诗意环境。",
        "events": ["香菱向黛玉学诗", "黛玉讲授读诗方法", "香菱苦心练习", "终有所悟"],
        "exam": ["香菱形象", "黛玉才情", "诗歌教育", "女性精神追求"],
        "question": "香菱学诗体现了她怎样的生命追求？",
    },
    55: {
        "importance": 5,
        "summary": "探春理家展示其精明、果断和改革意识，也暴露贾府内部管理和经济问题。",
        "events": ["王熙凤病休", "探春协理家事", "处理赵姨娘相关矛盾", "提出兴利除弊"],
        "exam": ["探春形象", "贾府管理危机", "女性才干", "改革意识与局限"],
        "question": "探春理家表现出她哪些不同于一般闺阁女子的特点？",
    },
    63: {
        "importance": 4,
        "summary": "寿怡红群芳开夜宴，花名签暗示人物性格和命运，是大观园青春繁盛的高光时刻。",
        "events": ["怡红院夜宴", "众人抽花名签", "签语映照人物气质", "青春欢乐中暗含命运预兆"],
        "exam": ["群芳命运", "花名签象征", "大观园盛景", "乐中含悲"],
        "question": "花名签如何体现人物性格并预示命运？",
    },
    74: {
        "importance": 5,
        "summary": "抄检大观园标志着外部权力粗暴进入青春世界，大观园由盛转衰。",
        "events": ["王夫人等发起抄检", "各处被搜查", "探春强烈反击", "晴雯等人命运急转"],
        "exam": ["大观园衰败", "探春形象", "晴雯悲剧", "权力与青春世界冲突"],
        "question": "为什么说抄检大观园是大观园世界崩塌的重要节点？",
    },
    77: {
        "importance": 5,
        "summary": "晴雯被逐并含冤而死，集中体现美好个体在偏见、权力和礼法中的毁灭。",
        "events": ["晴雯被逐出园", "宝玉探病", "晴雯抱屈而死", "宝玉写诔文悼念"],
        "exam": ["晴雯形象", "宝玉情感", "女性悲剧", "礼法压迫"],
        "question": "晴雯的悲剧主要由哪些因素造成？",
    },
    97: {
        "importance": 5,
        "summary": "黛玉之死与宝玉成婚交错推进，宝黛爱情悲剧达到高潮。",
        "events": ["黛玉病重", "宝玉被骗成婚", "黛玉焚稿断痴情", "宝黛爱情彻底破灭"],
        "exam": ["黛玉悲剧", "宝黛爱情", "家族安排与个人情感", "悲剧结构"],
        "question": "黛玉之死为什么不只是爱情悲剧？",
    },
}

RELATIONS = [
    {"source": "贾宝玉", "target": "林黛玉", "type": "情感/知己", "note": "木石前盟，价值观相近，爱情主线"},
    {"source": "贾宝玉", "target": "薛宝钗", "type": "婚姻/对照", "note": "金玉良缘，与宝黛形成对照"},
    {"source": "林黛玉", "target": "薛宝钗", "type": "对照/竞争", "note": "才情、性格、处世方式与命运选择的对照"},
    {"source": "王熙凤", "target": "贾母", "type": "权力/依附", "note": "凤姐借贾母信任维持内宅管理权"},
    {"source": "王熙凤", "target": "贾琏", "type": "婚姻/冲突", "note": "夫妻关系中夹杂权力、欲望与利益"},
    {"source": "探春", "target": "王熙凤", "type": "管理/对照", "note": "两人都能理家，探春更有改革意识"},
    {"source": "贾宝玉", "target": "晴雯", "type": "主仆/欣赏", "note": "宝玉珍惜晴雯的率真与美，晴雯悲剧触动宝玉"},
    {"source": "林黛玉", "target": "紫鹃", "type": "主仆/情感支持", "note": "紫鹃是黛玉在贾府中重要的情感依靠"},
    {"source": "贾府", "target": "刘姥姥", "type": "贫富/外部视角", "note": "刘姥姥从外部反照贾府富贵与人情"},
]

TOPICS = [
    {"id": "first-five", "title": "前五回总纲", "chapters": [1, 2, 3, 4, 5], "focus": "神话缘起、四大家族、贾府结构、判词曲文、人物命运伏笔。"},
    {"id": "baodai-chai", "title": "宝黛钗关系", "chapters": [3, 5, 23, 27, 33, 97], "focus": "木石前盟与金玉良缘，两种价值观和两类女性形象的对照。"},
    {"id": "decline", "title": "贾府由盛转衰", "chapters": [2, 4, 18, 55, 74, 97], "focus": "繁华、权力、经济、管理危机和家族秩序崩塌。"},
    {"id": "women", "title": "女性命运", "chapters": [5, 27, 48, 55, 63, 74, 77, 97], "focus": "金陵十二钗、晴雯、香菱等人物的才情、处境与悲剧。"},
    {"id": "garden", "title": "大观园", "chapters": [17, 18, 23, 37, 39, 63, 74], "focus": "青春世界、诗意空间和最终被现实秩序侵入的过程。"},
    {"id": "answering", "title": "答题模板", "chapters": [3, 5, 27, 33, 55, 74], "focus": "训练“观点、情节、分析、主题升华”的答题结构。"},
]

CURATED_ANSWERS = {
    1: "参考答案：第一回的作用主要在于总领全书。首先，女娲补天剩石和通灵宝玉的来历，使宝玉从一开始就带有“不合世用”的象征意味。其次，木石前盟为宝玉和黛玉的情感关系埋下根源，说明二人的关系不是普通儿女情长，而带有宿命色彩。再次，甄士隐一家的变故已经预示繁华难久、人生如梦的悲剧基调。因此答题时要抓住“神话框架、宝黛前缘、盛衰无常”三个层面。",
    2: "参考答案：冷子兴演说荣国府是读懂贾府的入口。它集中交代荣宁二府的人物世系、权力格局和宝玉衔玉而生的特殊性，使读者先获得家族全景。更重要的是，冷子兴一边说贾府显赫，一边指出子孙安富尊荣、运数将尽，形成“表面繁华、内里衰败”的判断。高考答题时可指出：这一回既是人物关系说明书，也是贾府由盛转衰的早期伏笔。",
    3: "参考答案：林黛玉进贾府一回通过“外来者视角”写出贾府秩序。黛玉处处小心，说明贾府礼法森严；贾母、王夫人、王熙凤等依次出场，展示内宅权力层级；王熙凤“未见其人，先闻其声”的出场表现她受宠、有权、能言善断；宝黛初见则为爱情主线开端。答题时可从贾府等级、人物亮相、宝黛关系三个角度组织。",
    4: "参考答案：“护官符”揭示四大家族互相勾连、权力遮蔽法律的社会现实。贾雨村审案时本应主持公道，却因门子提醒四大家族关系而徇私枉法，说明个人命运常被权贵网络左右。它还补充了贾、史、王、薛的家族结构，为薛家进入贾府和后文家族兴衰铺垫。答题关键是：护官符不是小道具，而是全书社会背景和批判锋芒的集中体现。",
    5: "参考答案：第五回被称为人物命运总纲，是因为太虚幻境集中展示金陵十二钗判词和《红楼梦曲》。这些内容用隐喻方式预告主要女性的性格、遭遇和结局，也把个人命运放入“千红一哭、万艳同悲”的总体悲剧中。宝玉梦游太虚幻境还点出“情”与“幻”的主题。答题时可结合判词、曲文、女性群像和全书悲剧结构分析。",
    6: "参考答案：刘姥姥一进荣国府的价值在于引入外部视角。她来自乡村贫寒家庭，进入荣国府后，贾府的富贵、规矩和等级被她的惊异反衬出来。王熙凤接待刘姥姥时既讲体面又有施舍，表现出她善于处理人情和维持家族门面的能力。答题时可说：刘姥姥不是笑料人物，她承担着观察贾府、连接贫富世界、反衬豪门生活的叙事作用。",
    7: "参考答案：送宫花看似琐碎，却能写出人物和秩序。周瑞家的送花串联多个女性空间，显示贾府日常生活的层级和礼数；宝钗谈冷香丸，呈现她稳重、自持、带有克制感的性格；黛玉因送花先后而敏感，表现她寄人篱下后的自尊和不安；焦大醉骂则突然暴露宁国府阴暗面。答题要抓住“日常细节见人物、见等级、见伏笔”。",
    8: "参考答案：通灵宝玉与金锁互看，是“金玉良缘”正式浮出水面的关键细节。宝玉的玉和宝钗的锁在物象上构成配对，暗示家族和世俗秩序认可的婚姻可能；而黛玉的出现和言语含酸，则提示木石前盟与金玉良缘之间的张力。答题时可从物象伏笔、宝黛钗三角关系、世俗婚姻与真情冲突三方面分析。",
    9: "参考答案：家塾风波反映贾府教育的失序。学堂本应承担读书明理的功能，但其中充满嬉闹、争斗和暧昧纠纷，说明贾府子弟并未真正受到严肃教育。宝玉在家塾中的不适，也体现他与传统仕途教育之间的隔膜。答题时可联系贾府衰败：家族问题不只在经济和权力，也在下一代教育和风气。",
    10: "参考答案：秦可卿病重不只是情节交代，也写出宁国府危机。张太医论病把病情说得复杂隐晦，使秦可卿的命运带有不祥意味；贾珍等人的焦虑，则显示宁国府表面富贵之下有难以言说的混乱。答题时可指出：疾病描写在小说中常有象征意义，这里既预示秦可卿之死，也预示宁国府乃至贾府的败象。",
    11: "参考答案：本回把寿宴热闹和秦可卿病重并置，形成乐景写哀。宁国府排家宴显示豪门礼数和繁华排场，但病中的秦可卿使这种繁华笼罩上衰败阴影。宝玉探病时的敏感，也说明他能感受到繁华背后的伤感。答题时可抓住“热闹与病态的对照”，说明小说常在繁华场面中写出悲剧预兆。",
    12: "参考答案：风月宝鉴象征欲望的两面性和幻象的危险。贾瑞迷恋王熙凤，不能自制；王熙凤设局惩治，表现她手段狠辣；风月宝鉴本可警醒他反观自身，但他只看诱惑的一面，最终自取灭亡。答题时可从讽刺、警示和“正反两面”三个角度分析：小说批判的不是单纯爱情，而是被欲望支配后的迷失。",
    13: "参考答案：秦可卿托梦是贾府兴亡主题的关键节点。她提醒王熙凤“月满则亏，水满则溢”，点明盛极必衰的规律；又提出置办祭祀产业等长远安排，说明她看见了家族隐患。王熙凤虽有能力，却未能真正扭转大势。答题时可说：这一情节把个人死亡、家族管理和全书衰败主题连在一起。",
    14: "参考答案：王熙凤协理宁国府集中表现她的管理才干。她一到宁府就发现人浮于事、职责不清的问题，于是定规矩、分任务、立威信，使丧事井然有序。她的果断和威严令人佩服，但严厉手段也显示她治家的冷酷一面。答题时要避免只说“能干”，还要指出她的复杂性：能治事，也善用权、重威慑。",
    15: "参考答案：秦可卿丧礼的盛大排场，一方面表现贾府和宁国府的贵族地位，连北静王也出面路祭；另一方面也暴露豪门为维持体面而巨大消耗。王熙凤弄权铁槛寺则进一步表现权力可以介入私人命运。答题时可从“礼仪排场、社会关系、权力运作、繁华虚耗”四个角度分析。",
    16: "参考答案：元春晋封是贾府荣耀的高峰，也埋下盛极而衰的伏笔。贾府因元春入宫得势而欢腾，说明家族命运高度依附皇权；省亲准备必然带来巨大铺张，进一步消耗家族资源。与此同时秦钟之死延续青春生命早逝的悲感。答题时可说：本回一喜一悲，既写家族荣耀，也写命运无常。",
    17: "参考答案：大观园不仅是园林空间，更是人物精神世界的舞台。宝玉题对额表现他的才情和审美，也让园中各处与人物气质发生联系。后文姐妹们入住、结社、吟诗，都依托这个空间展开；而抄检大观园时，外部权力入侵这个空间，也标志青春世界崩塌。因此它兼具生活、诗意和命运象征意义。",
    18: "参考答案：元妃省亲同时写荣耀和隐忧。省亲场面极尽繁华，表现贾府烈火烹油的鼎盛；但元春与家人相见时有隔膜和哀感，说明宫廷荣耀并不等于幸福；建园和接驾的巨大开销，也为贾府经济衰败埋下伏笔。答题时可抓住“盛大场面中的悲凉感”，说明《红楼梦》常在繁华中写衰败。",
    23: "参考答案：共读《西厢记》推动宝黛关系从亲近走向精神知己。二人借曲文交流情感，说明他们都向往真情而不满足于礼法安排；黛玉表面嗔怪，内心却被触动，表现她敏感而重情。这个情节也为宝黛爱情的诗意气质奠基。答题时可从青春情感、语言试探、礼法禁忌三方面写。",
    27: "参考答案：宝钗扑蝶与黛玉葬花形成鲜明对照。宝钗扑蝶写她明朗、机敏、善于自保的一面；黛玉葬花则通过《葬花吟》表现她对生命零落和自身处境的深切悲感。二者同处一回，强化宝钗与黛玉在性格、处世方式和命运意识上的差异。答题时应避免简单褒贬，而要写出对照关系。",
    33: "参考答案：宝玉挨打集中爆发多重冲突。贾政代表仕途功名和父权秩序，宝玉则厌恶经济仕途、亲近女儿世界；忠顺王府索人和贾环进谗使矛盾激化；贾母、王夫人护宝玉又显示内宅情感和父权惩戒的冲突。答题时可从父子冲突、价值冲突、家族权力结构三个角度分析。",
    37: "参考答案：海棠诗社表现大观园女儿们的精神世界。探春发起诗社，显示她的组织能力和开阔气度；众人取号作诗，展现各自才情和性格。诗社让大观园成为青春、友谊、审美的空间，也与外部功利世界形成对照。答题时可说：诗社不是闲笔，而是女性才情和大观园理想状态的集中呈现。",
    39: "参考答案：刘姥姥二进荣国府扩大了小说的社会视野。她以乡村经验观察大观园，使贾府富贵显得具体可感；众人拿她取乐，也显示阶层差异和豪门生活的优越感。她的朴素、机智和承受力，使她不只是滑稽人物，也是外部世界的代表。答题时可从对比、反衬、社会广度三方面分析。",
    48: "参考答案：香菱学诗表现她对精神生活的追求。她出身悲苦，却仍然渴望学习诗歌，说明她不是只被命运压迫的弱者，也有审美和自我提升的愿望。黛玉教她读诗，体现黛玉的才情和真诚。答题时可联系女性命运：香菱的学诗越美好，她后来的遭遇越显悲剧。",
    55: "参考答案：探春理家表现她的才干和改革意识。她能看出贾府管理混乱、开支无度的问题，并提出兴利除弊，说明她有超出闺阁的治理能力。她处理赵姨娘相关矛盾时坚持原则，也体现她的清醒和自尊。但她终究受身份和家族大势限制，改革难以根本改变贾府衰败。答题时要写出“能力”和“局限”并存。",
    63: "参考答案：群芳夜宴是大观园青春繁华的高光时刻。众人抽花名签，签语既贴合人物性格，又暗示未来命运；宴会表面欢快，读者却能感到盛景难久。答题时可说：这一回具有“乐中含悲”的特点，用游戏方式写人物命运，是《红楼梦》诗化叙事的重要表现。",
    74: "参考答案：抄检大观园标志青春世界被外部权力粗暴侵入。大观园原本是女儿们相对自由的诗意空间，但抄检使猜疑、控制和等级权力进入其中。探春的反击显示她的尊严和政治敏感，晴雯等人的命运也因此急转直下。答题时可指出：这是大观园由盛转衰、贾府内部秩序崩坏的重要节点。",
    77: "参考答案：晴雯悲剧来自多重压迫。她美丽、率真、有尊严，却因性格不肯迎合、身份低微、又被王夫人等人误解排斥，最终被逐而死。宝玉悼念晴雯，说明他珍视这种不被世俗容纳的真性情。答题时可从人物性格、阶层身份、权力偏见、宝玉态度四方面分析。",
    97: "参考答案：黛玉之死不只是爱情悲剧。她与宝玉的真情被家族婚姻安排牺牲，说明个人情感无法抗衡礼法和家族利益；黛玉焚稿断痴情，象征诗性生命和精神知己关系的破灭；她的死亡也完成了“木石前盟”的悲剧结局。答题时可联系女性命运、家族秩序和全书悲剧主题。",
}


def api_get(params):
    url = "https://zh.wikisource.org/w/api.php?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.load(resp)
        except HTTPError as exc:
            if exc.code != 429 or attempt == 5:
                raise
            wait_seconds = 8 * (attempt + 1)
            print(f"rate limited, waiting {wait_seconds}s before retry")
            time.sleep(wait_seconds)


def chapter_title_from_text(text, chapter):
    for line in text.splitlines()[:20]:
        clean = line.strip()
        if re.search(r"第[一二三四五六七八九十百〇零\d]+回", clean) and len(clean) > 6:
            return clean
    return f"第{chapter:03d}回"


def fetch_chapter_titles():
    params = {
        "action": "parse",
        "page": "紅樓夢",
        "prop": "text",
        "format": "json",
        "formatversion": 2,
        "variant": "zh-hans",
    }
    data = api_get(params)
    html = data["parse"]["text"]
    titles = {}
    pattern = re.compile(
        r'href="/wiki/%E7%B4%85%E6%A8%93%E5%A4%A2/%E7%AC%AC(\d{3})%E5%9B%9E"[^>]*>(.*?)</a>'
    )
    for match in pattern.finditer(html):
        chapter = int(match.group(1))
        title = re.sub(r"<.*?>", "", match.group(2)).strip()
        title = re.sub(r"\s+", " ", title)
        titles[chapter] = title
    return titles


def matched_characters(text):
    hits = []
    for name in CORE_CHARACTERS:
        short = name[1:] if name.startswith("贾") and len(name) == 3 else name
        if name in text or short in text:
            hits.append(name)
    return hits[:10]


def extract_quote(text):
    lines = [re.sub(r"\s+", "", line) for line in text.splitlines()]
    lines = [line for line in lines if line and "上一回" not in line and "下一回" not in line and "回目录" not in line]
    joined = "。".join(lines)
    return joined[:260]


def split_title_parts(title):
    title = re.sub(r"^第[一二三四五六七八九十百〇零\d]+回\s*", "", title).strip()
    parts = re.split(r"\s+", title, maxsplit=1)
    if len(parts) == 1:
        mid = len(title) // 2
        return [title[:mid], title[mid:]]
    return parts


def generic_question(chapter, title, exam_points):
    point = exam_points[0] if exam_points else "情节作用"
    clean_title = re.sub(r"^第[一二三四五六七八九十百〇零\d]+回\s*", "", title).strip()
    return f"结合第{chapter}回《{clean_title}》，分析本回如何体现“{point}”，并说明它和全书人物关系或主题发展的联系。"


def generic_answer(chapter, title, summary, events, characters, exam_points):
    parts = split_title_parts(title)
    char_text = "、".join(characters[:4]) if characters else "本回相关人物"
    point_text = "、".join(exam_points[:3]) if exam_points else "情节推进、人物关系、前后照应"
    event_text = "；".join(events[:3])
    return (
        f"参考答案：第{chapter}回可以先从回目线索入手。"
        f"“{parts[0]}”和“{parts[1] if len(parts) > 1 else parts[0]}”提示本回至少包含两条情节或人物线索，阅读时不要只记事件表面。"
        f"本回的基本作用是：{summary}"
        f"具体答题时可抓三点：第一，看情节推进，{event_text}；"
        f"第二，看人物表现，围绕{char_text}分析其性格、处境或关系变化；"
        f"第三，看全书联系，把本回放到{point_text}等角度中理解。"
        f"这样回答既有本回情节依据，也能上升到整本书阅读要求。"
    )


def build_question_and_answer(chapter, title, summary, events, characters, exam_points, question):
    if chapter in CURATED_ANSWERS:
        return question, CURATED_ANSWERS[chapter]
    if question.startswith("本回情节和前后章节"):
        question = generic_question(chapter, title, exam_points)
    answer = generic_answer(chapter, title, summary, events, characters, exam_points)
    return question, answer


def write_reader_page(chapter, title, text):
    READER_DIR.mkdir(parents=True, exist_ok=True)
    body_lines = []
    for line in text.splitlines():
        clean = line.strip()
        if not clean or clean in {"上一回　回目录　下一回", "上一回 回目录 下一回"}:
            continue
        body_lines.append(f"<p>{escape(clean)}</p>")
    prev_link = f"chapter_{chapter - 1:03d}.html" if chapter > 1 else ""
    next_link = f"chapter_{chapter + 1:03d}.html" if chapter < 120 else ""
    nav_parts = ['<a href="../../index.html">返回学习地图</a>']
    if prev_link:
        nav_parts.append(f'<a href="{prev_link}">上一回</a>')
    if next_link:
        nav_parts.append(f'<a href="{next_link}">下一回</a>')
    html = f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{escape(title)} · 红楼梦原文</title>
    <style>
      :root {{
        --paper: #f5efe3;
        --ink: #231f1a;
        --muted: #73685d;
        --line: rgba(60, 42, 26, 0.18);
        --cinnabar: #a33b2b;
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        color: var(--ink);
        background: var(--paper);
        font-family: "Noto Serif SC", "Songti SC", "STSong", serif;
      }}
      .reader {{
        width: min(920px, calc(100vw - 32px));
        margin: 0 auto;
        padding: 32px 0 72px;
      }}
      nav {{
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        margin-bottom: 22px;
      }}
      nav a {{
        color: var(--cinnabar);
        text-decoration: none;
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 8px 12px;
        background: rgba(255,255,255,0.38);
      }}
      article {{
        border: 1px solid var(--line);
        border-radius: 8px;
        background: rgba(255, 250, 239, 0.72);
        padding: clamp(22px, 5vw, 52px);
        box-shadow: 0 18px 52px rgba(55, 38, 18, 0.1);
      }}
      h1 {{
        margin: 0 0 24px;
        color: var(--cinnabar);
        font-size: clamp(28px, 4.5vw, 46px);
        line-height: 1.25;
      }}
      p {{
        margin: 0 0 1.05em;
        color: var(--ink);
        font-size: 19px;
        line-height: 2.05;
        text-align: justify;
      }}
      .source {{
        margin-top: 28px;
        color: var(--muted);
        font-size: 14px;
        line-height: 1.7;
      }}
      @media (max-width: 640px) {{
        .reader {{ width: min(100vw - 20px, 920px); padding-top: 14px; }}
        article {{ padding: 18px; }}
        p {{ font-size: 17px; line-height: 1.92; }}
      }}
    </style>
  </head>
  <body>
    <main class="reader">
      <nav>{''.join(nav_parts)}</nav>
      <article>
        <h1>{escape(title)}</h1>
        {''.join(body_lines)}
        <div class="source">文本来源：维基文库《紅樓夢》。本页为本地学习阅读页，已声明 UTF-8 编码以避免中文乱码。</div>
      </article>
    </main>
  </body>
</html>
"""
    (READER_DIR / f"chapter_{chapter:03d}.html").write_text(html, encoding="utf-8")


def build_chapters():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    chapters = []
    try:
        chapter_titles = fetch_chapter_titles()
    except Exception as exc:
        print(f"could not fetch title index: {exc}")
        chapter_titles = {}
    for chapter in range(1, 121):
        raw_path = RAW_DIR / f"chapter_{chapter:03d}.txt"
        if raw_path.exists() and raw_path.stat().st_size > 200:
            text = raw_path.read_text(encoding="utf-8").strip()
        else:
            page = f"紅樓夢/第{chapter:03d}回"
            params = {
                "action": "query",
                "prop": "extracts",
                "explaintext": 1,
                "titles": page,
                "format": "json",
                "formatversion": 2,
                "variant": "zh-hans",
            }
            try:
                data = api_get(params)
                text = data["query"]["pages"][0].get("extract", "").strip()
                if not text:
                    raise RuntimeError(f"empty chapter text: {chapter}")
                raw_path.write_text(text, encoding="utf-8")
                time.sleep(1.4)
            except (HTTPError, URLError, TimeoutError, OSError) as exc:
                print(f"network unavailable for chapter {chapter:03d}: {exc}")
                text = ""

        title = chapter_titles.get(chapter) or (chapter_title_from_text(text, chapter) if text else f"第{chapter:03d}回（原文待下载）")
        curated = IMPORTANT.get(chapter)
        chars = matched_characters(text) if text else []
        if curated:
            importance = curated["importance"]
            summary = curated["summary"]
            events = curated["events"]
            exam = curated["exam"]
            question = curated["question"]
        else:
            importance = 3 if chapter in {6, 7, 8, 12, 13, 14, 21, 22, 28, 30, 32, 34, 40, 41, 45, 49, 50, 56, 57, 62, 67, 69, 70, 71, 78, 79, 80, 82, 87, 89, 90, 95, 96, 98, 102, 105, 106, 107, 108, 111, 113, 119, 120} else 2
            title_parts = split_title_parts(title)
            if len(title_parts) > 1:
                summary = f"本回围绕“{title_parts[0]}”与“{title_parts[1]}”两条线索展开，主要作用是承接前后情节、推进人物关系，并为相关人物的性格和处境变化提供依据。"
            else:
                summary = f"本回围绕“{title_parts[0]}”展开，主要作用是承接前后情节、推进人物关系，并为相关人物的性格和处境变化提供依据。"
            if len(title_parts) > 1:
                events = [
                    f"围绕“{title_parts[0]}”展开第一条情节线",
                    f"围绕“{title_parts[1]}”展开第二条情节线",
                    "通过人物言行推进前后章节的关系变化",
                ]
            else:
                events = [
                    f"围绕“{title_parts[0]}”展开本回核心情节",
                    "通过人物言行推进前后章节的关系变化",
                    "为后续情节或人物命运埋下线索",
                ]
            exam = ["情节定位", "人物关系", "前后照应"]
            question = "本回情节和前后章节有什么承接关系？涉及人物的处境是否发生变化？"

        if text:
            write_reader_page(chapter, title, text)
        question, reference_answer = build_question_and_answer(
            chapter, title, summary, events, chars, exam, question
        )

        chapters.append({
            "chapter": chapter,
            "title": title,
            "importance": importance,
            "summary": summary,
            "events": events,
            "characters": chars,
            "exam_points": exam,
            "possible_question": question,
            "reference_answer": reference_answer,
            "quote": extract_quote(text) if text else "本回原文尚未下载到本地。可稍后重新运行 scripts/build_honglou_data.py 自动补齐。",
            "raw_file": f"data/raw_chapters/chapter_{chapter:03d}.txt" if text else "",
            "reader_file": f"data/chapter_pages/chapter_{chapter:03d}.html" if text else "",
            "raw_available": bool(text),
        })
    return chapters


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    chapters = build_chapters()
    payload = {
        "source": {
            "name": "维基文库《紅樓夢》",
            "url": "https://zh.wikisource.org/wiki/%E7%B4%85%E6%A8%93%E5%A4%A2",
            "note": "古典公有领域文本，用于本地学习检索和章节整理。"
        },
        "chapters": chapters,
        "relations": RELATIONS,
        "topics": TOPICS,
    }
    (DATA_DIR / "honglou_data.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {len(chapters)} chapters to {DATA_DIR / 'honglou_data.json'}")


if __name__ == "__main__":
    main()
