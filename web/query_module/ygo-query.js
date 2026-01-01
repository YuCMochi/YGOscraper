"use strict";
// dependency: sql.js, JSZIP
// special ID
const ID_TYLER_THE_GREAT_WARRIOR = 68811206;
const ID_DECOY = 20240828;
const ID_BLACK_LUSTER_SOLDIER = 5405695;
const CID_BLACK_LUSTER_SOLDIER = 19092;
const CARD_ARTWORK_VERSIONS_OFFSET = 20;
const MAX_CARD_ID = 99999999;

const column_names = `datas.id, datas.ot, datas.alias, datas.setcode, datas.type, datas.atk, datas.def, datas.level, datas.race, datas.attribute, texts.name, texts."desc"`;
const select_all = `SELECT ${column_names} FROM datas JOIN texts USING (id) WHERE 1`;
const select_id = `SELECT datas.id FROM datas JOIN texts USING (id) WHERE 1`;
const select_name = `SELECT datas.id, texts.name FROM datas JOIN texts USING (id) WHERE 1`;

const base_filter = ` AND datas.id != $tyler AND datas.id != $decoy AND NOT type & $token`;
const no_alt_filter = ` AND (datas.id == $luster OR abs(datas.id - alias) >= $artwork_offset)`;
const default_filter = `${base_filter}${no_alt_filter}`;
const effect_filter = ` AND (NOT type & $normal OR type & $pendulum)`;

const stmt_base = `${select_all}${base_filter}`;
const stmt_default = `${select_all}${default_filter}`;
const stmt_no_alias = `${select_id}${base_filter} AND alias == $zero`;
const regexp_mention = `(?<=「)[^「」]*「?[^「」]*」?[^「」]*(?=」)`;

const arg_default = {
	$tyler: ID_TYLER_THE_GREAT_WARRIOR,
	$decoy: ID_DECOY,
	$luster: ID_BLACK_LUSTER_SOLDIER,
	$artwork_offset: CARD_ARTWORK_VERSIONS_OFFSET,
	$zero: 0,
	$token: TYPE_TOKEN,
};

/**
 * @typedef {Object} Record
 * @property {number} id
 * @property {number} ot
 * @property {number} alias
 * @property {number[]} setcode
 * @property {number} type
 * @property {number} atk
 * @property {number} def
 * @property {number} level
 * @property {number} race
 * @property {number} attribute
 * @property {number} scale
 * 
 * @property {string} name
 * @property {string} desc
 */

/**
 * @typedef {Object} CardText
 * @property {string} desc
 * @property {string} [db_desc]
 */

/**
 * @typedef {Object} Card
 * @property {number} id
 * @property {number} ot
 * @property {number} alias
 * @property {number} artid
 * @property {number[]} setcode
 * 
 * @property {number} type
 * @property {number} atk
 * @property {number} [def]
 * @property {number} [marker]
 * @property {number} level
 * @property {number} race
 * @property {number} attribute
 * @property {number} [scale]
 * @property {number} color - Card color for sorting
 * 
 * @property {string} tw_name
 * @property {CardText} text
 * 
 * @property {number} [cid]
 * @property {number} [md_rarity]
 * @property {string} [ae_name]
 * @property {string} [en_name]
 * @property {string} [jp_name]
 * @property {string} [kr_name]
 * @property {string} [md_name_en]
 * @property {string} [md_name_jp]
 * @property {number} [pack_index]
 */

const use_bigint = !!(window.BigInt);
const extra_setcodes = {
	"8512558": [143, 84, 89, 130, 314],
	"55088578": [143, 84, 89, 130, 314],
};

/**
 * Set `card.setcode` from int64.
 * @param {Card} card 
 * @param {bigint} setcode 
 */
function set_setcode(card, setcode) {
	const mask = BigInt(0xffff);
	const len = BigInt(16);
	setcode = BigInt.asUintN(64, setcode);
	card.setcode.length = 0;
	while (setcode) {
		if (setcode & mask) {
			card.setcode.push(Number(setcode & mask));
		}
		setcode = setcode >> len;
	}
}

/**
 * Check if `card.setode` contains `value`.
 * @param {Card} card 
 * @param {number} value 
 * @returns
 */
function is_setcode(card, value) {
	const settype = value & 0x0fff;
	const setsubtype = value & 0xf000;
	for (const x of card.setcode) {
		if ((x & 0x0fff) === settype && (x & 0xf000 & setsubtype) === setsubtype)
			return true;
	}
	return false;
}

/**
 * Query cards from `db` with statement `qstr` and binding object `arg` and put them in `ret`.
 * @param {Database} db 
 * @param {string} qstr 
 * @param {Object} arg 
 */
function query_db(db, qstr, arg) {
	const ret = [];
	const stmt = db.prepare(qstr);
	stmt.bind(arg);
	const option = use_bigint ? [null, { useBigInt: true }] : [];
	while (stmt.step()) {
		const card = stmt.getAsObject(...option);
		for (const [column, value] of Object.entries(card)) {
			switch (column) {
				case 'setcode':
					card.setcode = [];
					if (use_bigint && value) {
						if (extra_setcodes[card.id]) {
							card.setcode.push(...extra_setcodes[card.id]);
						}
						else {
							set_setcode(card, value);
						}
					}
					break;
				case 'level':
					card.level = Number(value) & 0xff;
					card.scale = Number(value) >>> 24;
					break;
				default:
					if (typeof value === 'bigint')
						card[column] = Number(value);
					break;
			}
		}
		ret.push(card);
	}
	stmt.free();
	return ret;
}

function generate_card(cdata) {
	let artid = 0;
	if (is_alternative(cdata)) {
		artid = cdata.id;
		cdata.id = cdata.alias;
		cdata.alias = 0;
	}
	/**
	 * @type {Card}
	 */
	const card = Object.create(null);
	if (id_to_cid.has(cdata.id))
		card.cid = id_to_cid.get(cdata.id);
	card.id = cdata.id;
	card.tw_name = cdata.name;
	if (card.cid) {
		for (const [locale, prop] of Object.entries(official_name)) {
			if (name_table[locale].has(card.cid))
				card[prop] = name_table[locale].get(card.cid);
			else if (md_table[locale] && md_table[locale].has(card.cid))
				card[game_name[locale]] = md_table[locale].get(card.cid);
		}
	}
	for (const [column, value] of Object.entries(cdata)) {
		switch (column) {
			case "id":
			case "name":
			case "desc":
				continue;
			case "scale":
				if (cdata.type & TYPE_PENDULUM)
					card[column] = value;
				break;
			case "def":
				if (cdata.type & TYPE_LINK)
					card.marker = value;
				else
					card[column] = value;
				break;
			default:
				card[column] = value;
				break;
		}
	}
	if (card.cid && md_card_list[card.cid])
		card.md_rarity = md_card_list[card.cid];
	card.text = Object.create(null);
	card.text.desc = cdata.desc;
	card.artid = artid;
	// color
	if (card.type & TYPE_MONSTER) {
		if (!(card.type & TYPE_EXTRA)) {
			if (card.type & TYPE_TOKEN)
				card.color = 0;
			else if (card.type & TYPE_NORMAL)
				card.color = 1;
			else if (card.type & TYPE_RITUAL)
				card.color = 3;
			else if (card.type & TYPE_EFFECT)
				card.color = 2;
			else
				card.color = -1;
		}
		else {
			if (card.type & TYPE_FUSION)
				card.color = 4;
			else if (card.type & TYPE_SYNCHRO)
				card.color = 5;
			else if (card.type & TYPE_XYZ)
				card.color = 6;
			else if (card.type & TYPE_LINK)
				card.color = 7;
			else
				card.color = -1;
		}
	}
	else if (card.type & TYPE_SPELL) {
		if (card.type === TYPE_SPELL)
			card.color = 10;
		else if (card.type & TYPE_QUICKPLAY)
			card.color = 11;
		else if (card.type & TYPE_CONTINUOUS)
			card.color = 12;
		else if (card.type & TYPE_EQUIP)
			card.color = 13;
		else if (card.type & TYPE_RITUAL)
			card.color = 14;
		else if (card.type & TYPE_FIELD)
			card.color = 15;
		else
			card.color = -1;
	}
	else if (card.type & TYPE_TRAP) {
		if (card.type === TYPE_TRAP)
			card.color = 20;
		else if (card.type & TYPE_CONTINUOUS)
			card.color = 21;
		else if (card.type & TYPE_COUNTER)
			card.color = 22;
		else
			card.color = -1;
	}
	else {
		card.color = -1;
	}
	return card;
}

/**
 * @param {Card[]} result 
 * @param {string} pack_name 
 * @returns 
 */
function create_index(result, pack_name) {
	if (!pack_list[pack_name])
		return;
	const index_table = new Map();
	const pack = pack_list[pack_name];
	for (let i = 0; i < pack.length; ++i) {
		if (pack[i] > 1)
			index_table.set(pack[i], i);
	}
	for (const card of result) {
		card.pack_index = index_table.get(card.id);
	}
}

/**
 * Query cards and push into ret.
 * @param {string} qstr sqlite command
 * @param {Object} arg binding object
 * @returns 
 */
function query(qstr, arg) {
	const ret = [];
	for (const db of db_list) {
		for (const cdata of query_db(db, qstr, arg)) {
			ret.push(generate_card(cdata));
		}
	}
	if (arg.pack && pack_list[arg.pack])
		create_index(ret, arg.pack);
	return ret;
}

/**
 * Return the link to DB page.
 * @param {number} cid 
 * @param {string} request_locale 
 * @returns URL
 */
function print_db_link(cid, request_locale) {
	return `https://www.db.yugioh-card.com/yugiohdb/card_search.action?ope=2&cid=${cid}&request_locale=${request_locale}`;
}

/**
 * Return the link to Yugipedia page.
 * @param {number} id
 * @returns URL
 */
function print_yp_link(id) {
	return `https://yugipedia.com/wiki/${id.toString().padStart(8, '0')}`;
}

/**
 * Return the link to Q&A page.
 * @param {number} cid database id
 * @returns page address
 */
function print_qa_link(cid) {
	return `https://www.db.yugioh-card.com/yugiohdb/faq_search.action?ope=4&cid=${cid}&sort=2&request_locale=ja`;
}

/**
 * Check if the card is an alternative artwork card.
 * @param {Record} card
 * @returns 
 */
function is_alternative(card) {
	if (card.id === ID_BLACK_LUSTER_SOLDIER)
		return false;
	else
		return Math.abs(card.id - card.alias) < CARD_ARTWORK_VERSIONS_OFFSET;
}

/**
 * Check if the card has an official card name.
 * @param {Card} card 
 * @returns 
 */
function is_released(card) {
	return !!(card.jp_name || card.en_name);
}

/**
 * Generate the setcode condition of a statement.
 * @param {number} setcode
 * @param {Object} arg
 * @returns setcode condition
 */
function setcode_condition(setcode, arg) {
	const setcode_str1 = `(setcode & $mask12) == $setname AND (setcode & $settype) == $settype`;
	const setcode_str2 = `(setcode >> $sec1 & $mask12) == $setname AND (setcode >> $sec1 & $settype) == $settype`;
	const setcode_str3 = `(setcode >> $sec2 & $mask12) == $setname AND (setcode >> $sec2 & $settype) == $settype`;
	const setcode_str4 = `(setcode >> $sec3 & $mask12) == $setname AND (setcode >> $sec3 & $settype) == $settype`;
	const ret = `(${setcode_str1} OR ${setcode_str2} OR ${setcode_str3} OR ${setcode_str4})`;
	arg.$setname = setcode & 0x0fff;
	arg.$settype = setcode & 0xf000;
	arg.$mask12 = 0x0fff;
	arg.$sec1 = 16;
	arg.$sec2 = 32;
	arg.$sec3 = 48;
	return ret;
}

/**
 * Print the card data (without Link Marker).
 * @param {Card} card
 * @param {string} newline newline char
 * @returns card data
 */
function print_data(card, newline) {
	let mtype = '';
	let subtype = '';
	let lvstr = '\u2605';
	let data = '';

	if (card.type & TYPE_MONSTER) {
		mtype = type_name[TYPE_MONSTER];
		if (card.type & TYPE_RITUAL)
			subtype = `/${type_name[TYPE_RITUAL]}`;
		else if (card.type & TYPE_FUSION)
			subtype = `/${type_name[TYPE_FUSION]}`;
		else if (card.type & TYPE_SYNCHRO)
			subtype = `/${type_name[TYPE_SYNCHRO]}`;
		else if (card.type & TYPE_XYZ) {
			subtype = `/${type_name[TYPE_XYZ]}`;
			lvstr = `\u2606`;
		}
		else if (card.type & TYPE_LINK) {
			subtype = `/${type_name[TYPE_LINK]}`;
			lvstr = `LINK-`;
		}
		if (card.type & TYPE_PENDULUM) {
			subtype += `/${type_name[TYPE_PENDULUM]}`;
		}

		// extype
		if (card.type & TYPE_NORMAL)
			subtype += `/${type_name[TYPE_NORMAL]}`;
		if (card.type & TYPE_SPIRIT)
			subtype += `/${type_name[TYPE_SPIRIT]}`;
		if (card.type & TYPE_UNION)
			subtype += `/${type_name[TYPE_UNION]}`;
		if (card.type & TYPE_DUAL)
			subtype += `/${type_name[TYPE_DUAL]}`;
		if (card.type & TYPE_TUNER)
			subtype += `/${type_name[TYPE_TUNER]}`;
		if (card.type & TYPE_FLIP)
			subtype += `/${type_name[TYPE_FLIP]}`;
		if (card.type & TYPE_TOON)
			subtype += `/${type_name[TYPE_TOON]}`;
		if (card.type & TYPE_SPSUMMON)
			subtype += `/${type_name[TYPE_SPSUMMON]}`;
		if (card.type & TYPE_EFFECT)
			subtype += `/${type_name[TYPE_EFFECT]}`;
		data = `[${mtype}${subtype}]${newline}`;

		data += `${lvstr}${card.level === 0 ? '?' : card.level}`;
		if (card.attribute)
			data += `/${attribute_name[card.attribute]}`;
		else
			data += `/${attribute_name['unknown']}`;
		if (card.race)
			data += `/${race_name[card.race]}`;
		else
			data += `/${race_name['unknown']}`;
		data += newline;

		data += `${value_name['atk']}${print_ad(card.atk)}`;
		if (!(card.type & TYPE_LINK)) {
			data += `/${value_name['def']}${print_ad(card.def)}`;
		}
		data += newline;

		if (card.type & TYPE_PENDULUM) {
			data += `🔹${card.scale}/${card.scale}🔸${newline}`;
		}
	}
	else if (card.type & TYPE_SPELL) {
		mtype = `${type_name[TYPE_SPELL]}`;
		if (card.type & TYPE_QUICKPLAY)
			subtype = `/${type_name[TYPE_QUICKPLAY]}`;
		else if (card.type & TYPE_CONTINUOUS)
			subtype = `/${type_name[TYPE_CONTINUOUS]}`;
		else if (card.type & TYPE_EQUIP)
			subtype = `/${type_name[TYPE_EQUIP]}`;
		else if (card.type & TYPE_RITUAL)
			subtype = `/${type_name[TYPE_RITUAL]}`;
		else if (card.type & TYPE_FIELD)
			subtype = `/${type_name[TYPE_FIELD]}`;
		else
			subtype = `/${type_name[TYPE_NORMAL]}`;
		data = `[${mtype}${subtype}]${newline}`;
	}
	else if (card.type & TYPE_TRAP) {
		mtype = `${type_name[TYPE_TRAP]}`;
		if (card.type & TYPE_CONTINUOUS)
			subtype = `/${type_name[TYPE_CONTINUOUS]}`;
		else if (card.type & TYPE_COUNTER)
			subtype = `/${type_name[TYPE_COUNTER]}`;
		else
			subtype = `/${type_name[TYPE_NORMAL]}`;
		data = `[${mtype}${subtype}]${newline}`;
	}
	return data;
}

/**
 * Create the inverse mapping of `table`.
 * @param {Map} table 
 * @returns 
 */
function inverse_mapping(table) {
	const inverse = new Map();
	for (const [key, value] of table) {
		if (inverse.has(value)) {
			console.error('non-invertible', `${key}: ${value}`);
			return (new Map());
		}
		inverse.set(value, key);
	}
	return inverse;
}


/**
 * The sqlite condition for a list.
 * @param {string} column 
 * @param {string} prefix 
 * @param {Array} list 
 * @param {Object} arg 
 * @returns {string}
 */
function list_condition(column, prefix, list, arg) {
	const set1 = new Set(list);
	const tokens = [];
	let index = 0;
	for (const value of set1) {
		if (!Number.isSafeInteger(value)) {
			continue;
		}
		tokens.push(`@${prefix}${index}`);
		arg[`@${prefix}${index}`] = value;
		index++;
	}
	return `${column} IN (${tokens.join(', ')})`;
}
