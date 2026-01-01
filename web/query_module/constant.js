"use strict";
const MAX_WIDTH = 900;
// type
const TYPE_MONSTER = 0x1;
const TYPE_SPELL = 0x2;
const TYPE_TRAP = 0x4;

// color type
const TYPE_NORMAL = 0x10;
const TYPE_EFFECT = 0x20;
const TYPE_FUSION = 0x40;
const TYPE_RITUAL = 0x80;
const TYPE_SYNCHRO = 0x2000;
const TYPE_XYZ = 0x800000;
const TYPE_PENDULUM = 0x1000000;
const TYPE_LINK = 0x4000000;
const TYPE_EXTRA = TYPE_FUSION | TYPE_SYNCHRO | TYPE_XYZ | TYPE_LINK;

// extype
const TYPE_SPIRIT = 0x200;
const TYPE_UNION = 0x400;
const TYPE_DUAL = 0x800;
const TYPE_TUNER = 0x1000;
const TYPE_TOKEN = 0x4000;
const TYPE_FLIP = 0x200000;
const TYPE_TOON = 0x400000;
const TYPE_SPSUMMON = 0x2000000;

// spell type
const TYPE_QUICKPLAY = 0x10000;
const TYPE_CONTINUOUS = 0x20000;
const TYPE_EQUIP = 0x40000;
//const TYPE_RITUAL
const TYPE_FIELD = 0x80000;

// trap type
//const TYPE_CONTINUOUS
const TYPE_COUNTER = 0x100000;

// race
const RACE_WARRIOR = 0x1;
const RACE_SPELLCASTER = 0x2;
const RACE_FAIRY = 0x4;
const RACE_FIEND = 0x8;
const RACE_ZOMBIE = 0x10;
const RACE_MACHINE = 0x20;
const RACE_AQUA = 0x40;
const RACE_PYRO = 0x80;
const RACE_ROCK = 0x100;
const RACE_WINDBEAST = 0x200;
const RACE_PLANT = 0x400;
const RACE_INSECT = 0x800;
const RACE_THUNDER = 0x1000;
const RACE_DRAGON = 0x2000;
const RACE_BEAST = 0x4000;
const RACE_BEASTWARRIOR = 0x8000;
const RACE_DINOSAUR = 0x10000;
const RACE_FISH = 0x20000;
const RACE_SEASERPENT = 0x40000;
const RACE_REPTILE = 0x80000;
const RACE_PSYCHO = 0x100000;
const RACE_DIVINE = 0x200000;
const RACE_CREATORGOD = 0x400000;
const RACE_WYRM = 0x800000;
const RACE_CYBERSE = 0x1000000;
const RACE_ILLUSION = 0x2000000;

// attr
const ATTRIBUTE_EARTH = 0x01;
const ATTRIBUTE_WATER = 0x02;
const ATTRIBUTE_FIRE = 0x04;
const ATTRIBUTE_WIND = 0x08;
const ATTRIBUTE_LIGHT = 0x10;
const ATTRIBUTE_DARK = 0x20;
const ATTRIBUTE_DIVINE = 0x40;

// Link Marker
const LINK_MARKER_BOTTOM_LEFT = 0x001;
const LINK_MARKER_BOTTOM = 0x002;
const LINK_MARKER_BOTTOM_RIGHT = 0x004;

const LINK_MARKER_LEFT = 0x008;
const LINK_MARKER_RIGHT = 0x020;

const LINK_MARKER_TOP_LEFT = 0x040;
const LINK_MARKER_TOP = 0x080;
const LINK_MARKER_TOP_RIGHT = 0x100;

const attribute_name = {
	unknown: '？',
	[ATTRIBUTE_EARTH]: '地',
	[ATTRIBUTE_WATER]: '水',
	[ATTRIBUTE_FIRE]: '炎',
	[ATTRIBUTE_WIND]: '風',
	[ATTRIBUTE_LIGHT]: '光',
	[ATTRIBUTE_DARK]: '闇',
	[ATTRIBUTE_DIVINE]: '神',
};

const race_name = {
	unknown: '？族',
	[RACE_WARRIOR]: '戰士族',
	[RACE_SPELLCASTER]: '魔法使族',
	[RACE_FAIRY]: '天使族',
	[RACE_FIEND]: '惡魔族',
	[RACE_ZOMBIE]: '不死族',
	[RACE_MACHINE]: '機械族',
	[RACE_AQUA]: '水族',
	[RACE_PYRO]: '炎族',
	[RACE_ROCK]: '岩石族',
	[RACE_WINDBEAST]: '鳥獸族',
	[RACE_PLANT]: '植物族',
	[RACE_INSECT]: '昆蟲族',
	[RACE_THUNDER]: '雷族',
	[RACE_DRAGON]: '龍族',
	[RACE_BEAST]: '獸族',
	[RACE_BEASTWARRIOR]: '獸戰士族',
	[RACE_DINOSAUR]: '恐龍族',
	[RACE_FISH]: '魚族',
	[RACE_SEASERPENT]: '海龍族',
	[RACE_REPTILE]: '爬蟲類族',
	[RACE_PSYCHO]: '超能族',
	[RACE_DIVINE]: '幻神獸族',
	[RACE_CREATORGOD]: '創造神族',
	[RACE_WYRM]: '幻龍族',
	[RACE_CYBERSE]: '電子界族',
	[RACE_ILLUSION]: '幻想魔族',
};

const type_name = {
	[TYPE_MONSTER]: '怪獸',
	[TYPE_SPELL]: '魔法',
	[TYPE_TRAP]: '陷阱',

	[TYPE_NORMAL]: '通常',
	[TYPE_EFFECT]: '效果',
	[TYPE_FUSION]: '融合',
	[TYPE_RITUAL]: '儀式',
	[TYPE_SYNCHRO]: '同步',
	[TYPE_XYZ]: '超量',
	[TYPE_PENDULUM]: '靈擺',
	[TYPE_LINK]: '連結',

	[TYPE_SPIRIT]: '靈魂',
	[TYPE_UNION]: '聯合',
	[TYPE_DUAL]: '二重',
	[TYPE_TUNER]: '協調',
	[TYPE_TOKEN]: '衍生物',
	[TYPE_FLIP]: '反轉',
	[TYPE_TOON]: '卡通',
	[TYPE_SPSUMMON]: '特殊召喚',

	[TYPE_QUICKPLAY]: '速攻',
	[TYPE_CONTINUOUS]: '永續',
	[TYPE_EQUIP]: '裝備',
	[TYPE_FIELD]: '場地',
	[TYPE_COUNTER]: '反擊',
};

const value_name = {
	atk: '攻',
	def: '守',
	scale: '靈擺刻度',
};

const limit_name = {
	0: '禁止',
	1: '限制',
	2: '準限制',
};

const marker_char = {
	[LINK_MARKER_BOTTOM_LEFT]: '🟥',
	[LINK_MARKER_BOTTOM]: '🟥',
	[LINK_MARKER_BOTTOM_RIGHT]: '🟥',

	[LINK_MARKER_LEFT]: '🟥',
	[LINK_MARKER_RIGHT]: '🟥',

	[LINK_MARKER_TOP_LEFT]: '🟥',
	[LINK_MARKER_TOP]: '🟥',
	[LINK_MARKER_TOP_RIGHT]: '🟥',

	default: '⬜',
};

const rarity = {
	1: 'N',
	2: 'R',
	3: 'SR',
	4: 'UR',
}
