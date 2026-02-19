"use strict";
const MAX_TEXT_LEN = 200;
const MAX_RESULT_LEN = 500;

let current_stmt = "";
let current_arg = null;

const re_wildcard = /(?<!\$)[%_]/;
const re_special = /[$%_]/;

const re_id = /^\d{1,9}$/;
const re_value = /^\d{1,2}$/;
const re_pack = /^_?\w{4}$/;
const re_number = /^-?\d{1,10}$/;

const mtype_list = [
	TYPE_FUSION,
	TYPE_SYNCHRO,
	TYPE_XYZ,
	TYPE_LINK,
	TYPE_NORMAL,

	TYPE_EFFECT,
	TYPE_RITUAL,
	TYPE_PENDULUM,
	TYPE_TOON,
	TYPE_SPIRIT,

	TYPE_UNION,
	TYPE_DUAL,
	TYPE_TUNER,
	TYPE_FLIP,
	TYPE_SPSUMMON,
];

const exclude_list = [
	TYPE_FUSION,
	TYPE_SYNCHRO,
	TYPE_XYZ,
	TYPE_LINK,
	TYPE_NORMAL,

	TYPE_EFFECT,
	TYPE_RITUAL,
	TYPE_PENDULUM,
	TYPE_TOON,
	TYPE_SPIRIT,

	TYPE_UNION,
	TYPE_DUAL,
	TYPE_TUNER,
	TYPE_FLIP,
	TYPE_SPSUMMON,
];

const stype_list = [
	TYPE_NORMAL,
	TYPE_QUICKPLAY,
	TYPE_CONTINUOUS,
	TYPE_EQUIP,
	TYPE_RITUAL,
	TYPE_FIELD,
];

const ttype_list = [
	TYPE_NORMAL,
	TYPE_CONTINUOUS,
	TYPE_COUNTER,
];

const attr_list = [
	ATTRIBUTE_EARTH,
	ATTRIBUTE_WATER,
	ATTRIBUTE_FIRE,
	ATTRIBUTE_WIND,
	ATTRIBUTE_LIGHT,
	ATTRIBUTE_DARK,
	ATTRIBUTE_DIVINE,
];

const race_list = [
	RACE_AQUA,
	RACE_PYRO,
	RACE_THUNDER,
	RACE_DRAGON,
	RACE_BEAST,
	RACE_FISH,
	RACE_FAIRY,
	RACE_FIEND,
	RACE_ZOMBIE,
	RACE_WARRIOR,
	RACE_DINOSAUR,
	RACE_WINDBEAST,
	RACE_INSECT,
	RACE_PLANT,
	RACE_SEASERPENT,
	RACE_ROCK,
	RACE_MACHINE,
	RACE_PSYCHO,
	RACE_WYRM,
	RACE_SPELLCASTER,
	RACE_BEASTWARRIOR,
	RACE_REPTILE,
	RACE_DIVINE,
	RACE_CREATORGOD,
	RACE_CYBERSE,
	RACE_ILLUSION,
];

const marker_list = [
	LINK_MARKER_TOP_LEFT,
	LINK_MARKER_TOP,
	LINK_MARKER_TOP_RIGHT,

	LINK_MARKER_LEFT,
	LINK_MARKER_RIGHT,

	LINK_MARKER_BOTTOM_LEFT,
	LINK_MARKER_BOTTOM,
	LINK_MARKER_BOTTOM_RIGHT,
];

const interface_type = {
	"cname": 1,
	"locale": 1,
	"desc": 1,
	"keyword": 1,
	"pack": 1,
	"ctype": 1,
	"stype": 1,
	"ttype": 1,
	"page": 1,

	"mtype": 2,
	"mtype_operator": 2,
	"exclude": 2,
	"attr": 2,
	"race": 2,
	"level": 2,
	"level_from": 2,
	"level_to": 2,
	"scale": 2,
	"scale_from": 2,
	"scale_to": 2,
	"atk_from": 2,
	"atk_to": 2,
	"atkm": 2,
	"def_from": 2,
	"def_to": 2,
	"defm": 2,
	"sum": 2,

	"material": 3,
	"marker": 3,
	"marker_operator": 3,
}

/**
 * toHalfWidth()
 * @param {string} str
 * @returns
 */
function toHalfWidth(str) {
	return str.replace(/[Ａ-Ｚａ-ｚ０-９]/g, (s) => String.fromCharCode(s.charCodeAt(0) - 0xFEE0));
}

/**
 * toFullWidth()
 * @param {string} str
 * @returns 
 */
function toFullWidth(str) {
	return str.replace(/[A-Za-z0-9]/g, (s) => String.fromCharCode(s.charCodeAt(0) + 0xFEE0));
}

function is_locale(x) {
	switch (x) {
		case "en":
			return true;
		default:
			return false;
	}
}

function is_pack(x) {
	switch (x) {
		case "o":
			return true;
		case "t":
			return true;
		default:
			return re_pack.test(x) && (pack_list[x] || pre_release[x]);
	}
}

/**
 * @param {URLSearchParams} params 
 * @param {string} name 
 * @param {number} min 
 * @returns 
 */
function check_checkbox(params, name, min = 1) {
	const node_list = document.getElementsByName(name);
	if (node_list.length === 0) {
		params.delete(name);
		return;
	}
	const values = params.getAll(name);
	params.delete(name);
	for (const value of values) {
		if (!re_value.test(value))
			continue;
		if (params.has(name, value))
			continue;
		const x = Number.parseInt(value);
		if (x >= min && x <= min + node_list.length - 1)
			params.append(name, value);
	}
}

/**
 * @param {URLSearchParams} params 
 * @param {string} key 
 * @returns 
 */
function check_text(params, key) {
	if (!params.has(key))
		return false;
	const value = params.get(key);
	if (value.length === 0 || value.length > MAX_TEXT_LEN) {
		params.delete(key);
		return false;
	}
	params.set(key, value);
	return true;
}

/**
 * @param {URLSearchParams} params 
 * @param {string} key 
 * @returns 
 */
function check_plain_text(params, key) {
	if (!params.has(key))
		return false;
	const value = params.get(key);
	if (value.length === 0 || value.length > MAX_TEXT_LEN) {
		params.delete(key);
		return false;
	}
	if (re_special.test(value)) {
		params.delete(key);
		return false;
	}
	params.set(key, value);
	return true;
}

/**
 * @param {URLSearchParams} params 
 * @param {string} key 
 * @param {number} min 
 * @param {number} max 
 * @returns 
 */
function check_number(params, key, min, max) {
	if (!params.has(key))
		return false;
	const value = params.get(key);
	if (!re_number.test(value)) {
		params.delete(key);
		return false;
	}
	const x = Number.parseInt(value);
	if (!Number.isSafeInteger(x)) {
		params.delete(key);
		return false;
	}
	if (x < min || x > max) {
		params.delete(key);
		return false;
	}
	params.set(key, value);
	return true
}

/**
 * validate common keys
 * @param {URLSearchParams} params 
 * @param {boolean} extra_monster
 * @returns 
 */
function validate_params(params, extra_monster) {
	if (!extra_monster) {
		params.delete("mtype", "1");
		params.delete("mtype", "2");
		params.delete("mtype", "3");
		params.delete("mtype", "4");
		params.delete("exclude", "1");
		params.delete("exclude", "2");
		params.delete("exclude", "3");
		params.delete("exclude", "4");
		for (const [key, type] of Object.entries(interface_type)) {
			if (type === 3)
				params.delete(key);
		}
	}
	if (check_text(params, "keyword")) {
		params.delete("cname");
		params.delete("locale");
		params.delete("desc");
	}
	else if (check_text(params, "cname")) {
		switch (params.get("locale")) {
			case "en":
				params.set("locale", "en");
				break;
			default:
				params.delete("locale");
				break;
		}
		check_text(params, "desc");
	}
	else {
		params.delete("locale");
		check_text(params, "desc");
	}
	const pack = params.get("pack");
	if (pack && is_pack(pack)) {
		params.set("pack", pack);
	}
	else {
		params.delete("pack");
	}
	switch (params.get("ctype")) {
		case "1":
			params.set("ctype", "1");
			params.delete("stype");
			params.delete("ttype");
			check_checkbox(params, "mtype");
			check_checkbox(params, "exclude");
			if (params.get("mtype_operator") === "1")
				params.set("mtype_operator", "1");
			else
				params.set("mtype_operator", "0");
			break;
		case "2":
			params.set("ctype", "2");
			params.delete("mtype");
			params.delete("mtype_operator");
			params.delete("exclude");
			params.delete("ttype");
			check_checkbox(params, "stype");
			break;
		case "3":
			params.set("ctype", "3");
			params.delete("mtype");
			params.delete("mtype_operator");
			params.delete("exclude");
			params.delete("stype");
			check_checkbox(params, "ttype");
			break;
		default:
			params.delete("ctype");
			params.delete("mtype");
			params.delete("mtype_operator");
			params.delete("exclude");
			params.delete("stype");
			params.delete("ttype");
			break;
	}
	if (!params.has("ctype") || params.get("ctype") === "1") {
		check_text(params, "material");
		check_checkbox(params, "attr");
		check_checkbox(params, "race");
		check_checkbox(params, "level", 0);
		check_checkbox(params, "scale", 0);
		if (params.has("level")) {
			params.delete("level_from");
			params.delete("level_to");
		}
		else {
			check_number(params, "level_from", 0, 13);
			check_number(params, "level_to", 0, 13);
		}
		if (params.has("scale")) {
			params.delete("scale_from");
			params.delete("scale_to");
		}
		else {
			check_number(params, "scale_from", 0, 13);
			check_number(params, "scale_to", 0, 13);
		}
		check_checkbox(params, "marker");
		if (params.has("marker")) {
			if (params.get("marker_operator") === "1")
				params.set("marker_operator", "1");
			else
				params.set("marker_operator", "0");
		}
		else {
			params.delete("marker_operator");
		}
		check_number(params, "atk_from", -1, 100000);
		if (params.has("atk_from") && Number.parseInt(params.get("atk_from")) < 0) {
			params.delete("atk_to");
			params.delete("atkm");
			params.delete("sum");
		}
		check_number(params, "atk_to", -1, 100000);
		if (params.has("atk_to") && Number.parseInt(params.get("atk_to")) < 0) {
			params.set("atk_from", params.get("atk_to"));
			params.delete("atk_to");
			params.delete("atkm");
			params.delete("sum");
		}
		check_number(params, "atkm", 0, 999);
		check_number(params, "def_from", -2, 100000);
		if (params.has("def_from") && Number.parseInt(params.get("def_from")) < 0) {
			params.delete("def_to");
			params.delete("defm");
			params.delete("sum");
		}
		check_number(params, "def_to", -1, 100000);
		if (params.has("def_to") && Number.parseInt(params.get("def_to")) < 0) {
			params.set("def_from", params.get("def_to"));
			params.delete("def_to");
			params.delete("defm");
			params.delete("sum");
		}
		check_number(params, "defm", 0, 999);
		check_number(params, "sum", 0, 100000);
	}
	else {
		for (const [key, type] of Object.entries(interface_type)) {
			if (type === 2 || type === 3)
				params.delete(key);
		}
	}
	check_number(params, "page", 1, 1000);
	const result = new URLSearchParams();
	for (const key of Object.keys(interface_type)) {
		for (const value of params.getAll(key)) {
			result.append(key, value);
		}
	}
	return result;
}

/**
 * Validate the input of query.
 * @param {URLSearchParams} params original params
 * @returns validated params
 */
function server_validate1(params) {
	check_number(params, "code", 1, 102000000);
	if (params.has("code")) {
		const valid_params = new URLSearchParams();
		valid_params.set("code", params.get("code"));
		return valid_params;
	}
	return validate_params(params, true);
}

/**
 * Convert a string to a LIKE pattern.
 * @param {string} str 
 * @returns {string}
 */
function like_pattern(str) {
	if (!str)
		return '';
	if (re_wildcard.test(str))
		return str;
	return `%${str.replace(/\$(?![%_])/g, '$$$&')}%`;
}

/**
 * Generate the name condition of a statement.
 * @param {string} locale 
 * @param {string} name_string 
 * @param {Object} arg 
 * @returns name condition
 */
function process_name(locale, name_string, arg) {
	if (!name_string)
		return '';
	let name_cmd = '';
	switch (locale) {
		case 'en': {
			const en_list = [];
			const en_name = name_string.toLowerCase();
			for (const [cid, name] of complete_name_table['en']) {
				if (name.toLowerCase().includes(en_name))
					en_list.push(cid_table.get(cid));
				if (en_list.length > MAX_RESULT_LEN) {
					en_list.length = 0;
					break;
				}
			}
			name_cmd = '0';
			for (let i = 0; i < en_list.length; ++i) {
				name_cmd += ` OR datas.id=@e${i}`;
				arg[`@e${i}`] = en_list[i];
			}
			break;
		}
		default: {
			name_cmd = '0';
			let is_setname = false;
			// zh, setcode
			if (!re_wildcard.test(name_string)) {
				const replace_map = Object.create(null);
				replace_map['$%'] = '%';
				replace_map['$_'] = '_';
				let zh_name = name_string.replace(/\$%|\$_/g, (x) => replace_map[x]).toLowerCase();
				for (const [keyword, value] of Object.entries(setname)) {
					if (keyword.toLowerCase() === zh_name) {
						const setcode = Number.parseInt(value);
						const setcode_str = ` OR ${setcode_condition(setcode, arg)}`;
						name_cmd += setcode_str;
						is_setname = true;
						break;
					}
				}
			}
			// zh, name
			name_cmd += ` OR name LIKE $name ESCAPE '$' OR "desc" LIKE $kanji ESCAPE '$'`;
			name_cmd += ` OR alias IN (${stmt_no_alias} AND name LIKE $name ESCAPE '$')`;
			arg.$name = like_pattern(name_string);
			arg.$kanji = `%※${like_pattern(name_string)}`;
			// ja, name
			if (!is_setname) {
				const jp_list = [];
				const jp_name = toHalfWidth(name_string);
				for (const [cid, name] of complete_name_table['ja']) {
					if (toHalfWidth(name).includes(jp_name))
						jp_list.push(cid_table.get(cid));
					if (jp_list.length > MAX_RESULT_LEN) {
						jp_list.length = 0;
						break;
					}
				}
				for (let i = 0; i < jp_list.length; ++i) {
					name_cmd += ` OR datas.id=@j${i}`;
					arg[`@j${i}`] = jp_list[i];
				}
			}
			break;
		}
	}
	return name_cmd;
}

/**
 * Parse param into sqlite statement condition.
 * @param {URLSearchParams} params 
 * @returns {[string, Object]}sqlite statement condition
 */
function param_to_condition(params) {
	let qstr = "";
	const arg = { ...arg_default };
	// id, primary key
	const id = Number.parseInt(params.get("code"), 10);
	if (id) {
		document.getElementById("text_id").value = id;
		qstr += " AND datas.id == $id";
		arg.$id = id;
		return [qstr, arg];
	}

	qstr += no_alt_filter;
	// pack
	const pack = params.get("pack");
	if (pack === "o") {
		qstr += " AND datas.ot != $tcg";
		arg.$tcg = 2;
	}
	else if (pack === "t") {
		qstr += " AND datas.ot == $tcg";
		arg.$tcg = 2;
	}
	else if (pack_list[pack]) {
		qstr +=` AND ${list_condition("id", "pack", pack_list[pack], arg)}`;
		arg.pack = pack;
	}
	else if (pre_release[pack]) {
		qstr += " AND datas.id>=$begin AND datas.id<=$end";
		arg.$begin = pre_release[pack];
		arg.$end = pre_release[pack] + 998;
		arg.pack = pack;
	}
	document.getElementById("select_pack").value = pack;

	// type
	arg.$ctype = 0;
	let subtype = 0;
	let exc = 0;
	switch (params.get("ctype")) {
		case "1": {
			arg.$ctype = TYPE_MONSTER;
			for (const val of params.getAll("mtype")) {
				const idx = Number.parseInt(val) - 1;
				subtype |= mtype_list[idx];
				if (document.getElementsByName("mtype")[idx].type === "checkbox")
					document.getElementsByName("mtype")[idx].checked = true;
			}
			let mtype_operator = 0;
			if (params.get("mtype_operator") === "1") {
				mtype_operator = 1;
				select_subtype_op.value = "1";
			}
			else {
				mtype_operator = 0;
				select_subtype_op.value = "0";
			}
			if (subtype) {
				if (mtype_operator)
					qstr += " AND type & $mtype == $mtype";
				else
					qstr += " AND type & $mtype";
				arg.$mtype = subtype;
			}
			for (const val of params.getAll("exclude")) {
				const idx = Number.parseInt(val) - 1;
				exc |= exclude_list[idx];
				if (document.getElementsByName("exclude")[idx].type === "checkbox")
					document.getElementsByName("exclude")[idx].checked = true;
			}
			if (exc) {
				qstr += " AND NOT type & $exclude";
				arg.$exclude = exc;
			}
			break;
		}
		case "2": {
			qstr += " AND type & $ctype";
			arg.$ctype = TYPE_SPELL;
			for (const val of params.getAll("stype")) {
				const idx = Number.parseInt(val) - 1;
				subtype |= stype_list[idx];
				if (document.getElementsByName("stype").length)
					document.getElementsByName("stype")[idx].checked = true;
			}
			if (subtype) {
				if (subtype & TYPE_NORMAL) {
					if (subtype === TYPE_NORMAL) {
						qstr += " AND type == $ctype";
					}
					else {
						qstr += " AND (type == $ctype OR type & $stype)";
						arg.$stype = subtype & ~TYPE_NORMAL;
					}
				}
				else {
					qstr += " AND type & $stype";
					arg.$stype = subtype;
				}
			}
			break;
		}
		case "3": {
			qstr += " AND type & $ctype";
			arg.$ctype = TYPE_TRAP;
			for (const val of params.getAll("ttype")) {
				const idx = Number.parseInt(val) - 1;
				subtype |= ttype_list[idx];
				if (document.getElementsByName("ttype").length)
					document.getElementsByName("ttype")[idx].checked = true;
			}
			if (subtype) {
				if (subtype & TYPE_NORMAL) {
					if (subtype === TYPE_NORMAL) {
						qstr += " AND type == $ctype";
					}
					else {
						qstr += " AND (type == $ctype OR type & $ttype)";
						arg.$ttype = subtype & ~TYPE_NORMAL;
					}
				}
				else {
					qstr += " AND type & $ttype";
					arg.$ttype = subtype;
				}
			}
			break;
		}
		default:
			break;
	}

	if (arg.$ctype === 0 || arg.$ctype === TYPE_MONSTER) {
		// material
		if (params.has("material")) {
			const replace_map = Object.create(null);
			replace_map['%'] = '$%';
			replace_map['_'] = '$_';
			replace_map['$'] = '$$';
			const material = params.get("material").replace(/[%_$]/g, (x) => replace_map[x]);
			qstr += ` AND ("desc" LIKE $mat1 ESCAPE '$' OR "desc" LIKE $mat2 ESCAPE '$' OR "desc" LIKE $mat3 ESCAPE '$')`;
			arg.$mat1 = `「${material}」%+%`;
			arg.$mat2 = `%+「${material}」%`;
			arg.$mat3 = `%「${material}」×%`;
			arg.$ctype = TYPE_MONSTER;
			document.getElementById("text_mat").value = params.get("material");
		}

		// atk
		if (params.has("atk_from")) {
			const atk_from = Number.parseInt(params.get("atk_from"));
			arg.$ctype = TYPE_MONSTER;
			if (atk_from === -1) {
				qstr += " AND atk == $unknown";
				arg.$unknown = -2;
			}
			else {
				qstr += " AND atk >= $atk_from";
				arg.$atk_from = atk_from;
			}
			document.getElementById("text_atk1").value = atk_from;
		}
		if (params.has("atk_to")) {
			const atk_to = Number.parseInt(params.get("atk_to"));
			arg.$ctype = TYPE_MONSTER;
			qstr += " AND atk >= $zero AND atk <= $atk_to";
			arg.$zero = 0;
			arg.$atk_to = atk_to;
			document.getElementById("text_atk2").value = atk_to;
		}
		if (params.has("atkm")) {
			const atk_mod = Number.parseInt(params.get("atkm"));
			qstr += " AND atk % 1000 == $atkm";
			arg.$atkm = atk_mod;
			arg.$ctype = TYPE_MONSTER;
		}

		// def, exclude link monsters
		if (params.has("def_from") || params.has("def_to") || params.has("defm") || params.has("sum")) {
			qstr += " AND NOT type & $link";
			arg.$link = TYPE_LINK;
			arg.$ctype = TYPE_MONSTER;
		}
		if (params.has("def_from")) {
			const def_from = Number.parseInt(params.get("def_from"));
			if (def_from === -1) {
				qstr += " AND def == $unknown";
				arg.$unknown = -2;
			}
			else if (def_from === -2) {
				qstr += " AND def == atk AND def >= $zero";
				arg.$zero = 0;
			}
			else {
				qstr += " AND def >= $def_from";
				arg.$def_from = def_from;
			}
			document.getElementById("text_def1").value = def_from;
		}
		if (params.has("def_to")) {
			const def_to = Number.parseInt(params.get("def_to"));
			qstr += " AND def >= $zero AND def <= $def_to";
			arg.$zero = 0;
			arg.$def_to = def_to;
			document.getElementById("text_def2").value = def_to;
		}
		if (params.has("defm")) {
			const def_mod = Number.parseInt(params.get("defm"));
			qstr += " AND def % 1000 == $defm";
			arg.$defm = def_mod;
		}
		if (params.has("sum")) {
			const sum = Number.parseInt(params.get("sum"));
			qstr += " AND atk >= $zero AND def >= $zero AND atk + def == $sum";
			arg.$zero = 0;
			arg.$sum = sum;
			document.getElementById("text_sum").value = sum;
		}

		// lv, rank, link
		if (params.has("level") || params.has("level_from") || params.has("level_to")) {
			arg.$ctype = TYPE_MONSTER;
		}
		if (params.has("level")) {
			let level_condtion = "0";
			let index = 0;
			for (const value of params.getAll("level")) {
				const level = Number.parseInt(value);
				level_condtion += ` OR (level & $mask) == $level${index}`;
				arg[`$level${index}`] = level;
				index++;
				cb_level[level].checked = true;
			}
			qstr += ` AND (${level_condtion})`;
			arg.$mask = 0xff;
		}
		if (params.has("level_from")) {
			qstr += " AND (level & $mask) >= $level_from";
			arg.$mask = 0xff;
			arg.$level_from = Number.parseInt(params.get("level_from"));
		}
		if (params.has("level_to")) {
			qstr += " AND (level & $mask) <= $level_to";
			arg.$mask = 0xff;
			arg.$level_to = Number.parseInt(params.get("level_to"));
		}

		// scale, pendulum monster only
		if (params.has("scale") || params.has("scale_from") || params.has("scale_to")) {
			qstr += " AND type & $pendulum";
			arg.$pendulum = TYPE_PENDULUM;
			arg.$ctype = TYPE_MONSTER;
		}
		if (params.has("scale")) {
			let scale_condtion = "0";
			let index = 0;
			for (const value of params.getAll("scale")) {
				const scale = Number.parseInt(value);
				scale_condtion += ` OR (level >> $offset & $mask) == $scale${index}`;
				arg[`$scale${index}`] = scale;
				index++;
				cb_scale[scale].checked = true;
			}
			qstr += ` AND (${scale_condtion})`;
			arg.$offset = 24;
			arg.$mask = 0xff;
		}
		if (params.has("scale_from")) {
			qstr += " AND (level >> $offset & $mask) >= $scale_from";
			arg.$offset = 24;
			arg.$mask = 0xff;
			arg.$scale_from = Number.parseInt(params.get("scale_from"));
		}
		if (params.has("scale_to")) {
			qstr += " AND (level >> $offset & $mask) <= $scale_to";
			arg.$offset = 24;
			arg.$mask = 0xff;
			arg.$scale_to = Number.parseInt(params.get("scale_to"));
		}

		// attr, race
		let attr = 0;
		for (const val of params.getAll("attr")) {
			const idx = Number.parseInt(val) - 1;
			attr |= attr_list[idx];
			cb_attr[idx].checked = true;
		}
		if (attr) {
			qstr += " AND attribute & $attr";
			arg.$attr = attr;
			arg.$ctype = TYPE_MONSTER;
		}

		let race = 0;
		for (const val of params.getAll("race")) {
			const idx = Number.parseInt(val) - 1;
			race |= race_list[idx];
			cb_race[idx].checked = true;
		}
		if (race) {
			qstr += " AND race & $race";
			arg.$race = race;
			arg.$ctype = TYPE_MONSTER;
		}
		// marker
		let marker = 0;
		let marker_operator = 0;
		for (const val of params.getAll("marker")) {
			const idx = Number.parseInt(val) - 1;
			marker |= marker_list[idx];
			if (cb_marker)
				cb_marker[idx].checked = true;
		}
		if (params.get("marker_operator") === "1") {
			marker_operator = 1;
			if (document.getElementById("select_marker_op"))
				document.getElementById("select_marker_op").value = "1";
		}
		if (marker) {
			qstr += " AND type & $link";
			arg.$link = TYPE_LINK;
			if (marker_operator)
				qstr += " AND def & $marker == $marker";
			else
				qstr += " AND def & $marker";
			arg.$marker = marker;
			arg.$ctype = TYPE_MONSTER;
		}
		if (arg.$ctype === TYPE_MONSTER) {
			qstr += " AND type & $ctype";
		}
	}

	const desc_str = `"desc" LIKE $desc ESCAPE '$'`;
	const locale = params.get("locale");
	if (locale)
		document.getElementById("select_locale").value = locale;
	const keyword = params.get("keyword");
	let name_cmd = process_name(locale, keyword, arg);
	if (name_cmd) {
		// keyword
		document.getElementById("text_keyword").value = keyword;
		qstr += ` AND (${name_cmd} OR ${desc_str})`;
		arg.$desc = like_pattern(keyword);
	}
	else {
		// name
		const name = params.get("cname");
		name_cmd = process_name(locale, name, arg);
		if (name_cmd) {
			document.getElementById("text_name").value = name;
			qstr += ` AND (${name_cmd})`;
		}
		// desc
		const desc = params.get("desc");
		if (desc) {
			document.getElementById("text_effect").value = desc;
			qstr += ` AND ${desc_str}`;
			arg.$desc = like_pattern(desc);
		}
	}
	return [qstr, arg];
}

// entrance of query
function server_analyze1(params) {
	const valid_params = server_validate1(params);
	const [condition, arg_final] = param_to_condition(valid_params);
	const stmt_final = `${stmt_base}${condition};`;
	current_stmt = stmt_final;
	current_arg = arg_final;
	const result = query(stmt_final, arg_final);
	if (result.length === 1)
		document.title = result[0].tw_name;
	show_result(valid_params, result);
}

function get_sw_str(x) {
	const sw_str1 = `race == $race_${x} AND attribute != $attr_${x} AND (level & 0xff) != $lv_${x} AND atk != $atk_${x} AND def != $def_${x}`;
	const sw_str2 = ` OR race != $race_${x} AND attribute == $attr_${x} AND (level & 0xff) != $lv_${x} AND atk != $atk_${x} AND def != $def_${x}`;
	const sw_str3 = ` OR race != $race_${x} AND attribute != $attr_${x} AND (level & 0xff) == $lv_${x} AND atk != $atk_${x} AND def != $def_${x}`;
	const sw_str4 = ` OR race != $race_${x} AND attribute != $attr_${x} AND (level & 0xff) != $lv_${x} AND atk == $atk_${x} AND def != $def_${x}`;
	const sw_str5 = ` OR race != $race_${x} AND attribute != $attr_${x} AND (level & 0xff) != $lv_${x} AND atk != $atk_${x} AND def == $def_${x}`;
	return `(${sw_str1}${sw_str2}${sw_str3}${sw_str4}${sw_str5})`;
}

/**
 * @param {string} cdata 
 * @returns 
 */
function get_single_card(cdata) {
	if (!cdata)
		return [null, 0];

	const qstr0 = `${stmt_default} AND type & $monster AND NOT type & $ext`;
	const arg = {
		...arg_default,
		$monster: TYPE_MONSTER,
		$ext: TYPE_EXTRA,
	};

	if (re_id.test(cdata)) {
		const id = Number.parseInt(cdata);
		const qstr = `${qstr0} AND datas.id == $id;`;
		arg.$id = id;
		const list1 = query(qstr, arg);
		if (list1.length === 1)
			return [list1[0], 1];
	}

	let qstr = `${qstr0} AND name == $exact;`;
	arg.$exact = cdata;
	const list2 = query(qstr, arg);
	if (list2.length === 1)
		return [list2[0], 1];

	let target_cid = 0;
	for (const [cid, name] of complete_name_table['ja']) {
		if (toHalfWidth(name) === toHalfWidth(cdata))
			target_cid = cid;
	}
	if (target_cid) {
		const nid = cid_table.get(target_cid);
		qstr = `${qstr0} AND datas.id == $nid;`;
		arg.$nid = nid;
		const list3 = query(qstr, arg);
		if (list3.length === 1)
			return [list3[0], 1];
	}

	qstr = `${qstr0} AND name LIKE $fuzzy ESCAPE '$';`;
	arg.$fuzzy = like_pattern(cdata);
	const list4 = query(qstr, arg);
	if (list4.length === 1)
		return [list4[0], 1];
	return [null, list4.length];
}

/**
 * entrance of small world
 * @param {URLSearchParams} params 
 * @returns 
 */
function server_analyze2(params) {
	if (!check_text(params, "begin") || !check_text(params, "end"))
		return;
	// id or name
	const cdata1 = params.get("begin");
	document.getElementById("text_id1").value = cdata1;
	const cdata2 = params.get("end");
	document.getElementById("text_id2").value = cdata2;
	const [card_begin, result_len1] = get_single_card(cdata1);
	if (result_len1 > 1) {
		const row0 = table_result.insertRow(-1);
		const cell0 = row0.insertCell(-1);
		table_result.style.border = "1px solid black";
		cell0.textContent = "起點數量太多。";
		return;
	}
	else if (result_len1 < 1) {
		const row0 = table_result.insertRow(-1);
		const cell0 = row0.insertCell(-1);
		table_result.style.border = "1px solid black";
		cell0.textContent = "找不到起點。";
		return;
	}

	const [card_end, result_len2] = get_single_card(cdata2);
	if (result_len2 > 1) {
		const row0 = table_result.insertRow(-1);
		const cell0 = row0.insertCell(-1);
		table_result.style.border = "1px solid black";
		cell0.textContent = "終點數量太多。";
		return;
	}
	else if (result_len2 < 1) {
		const row0 = table_result.insertRow(-1);
		const cell0 = row0.insertCell(-1);
		table_result.style.border = "1px solid black";
		cell0.textContent = "找不到終點。";
		return;
	}

	params.set("ctype", "1");
	const valid_params = validate_params(params, false);
	valid_params.set("begin", card_begin.id);
	valid_params.set("end", card_end.id);
	const qstr0 = `${stmt_default} AND NOT type & $extra`;
	const [condition, arg_final] = param_to_condition(valid_params);
	arg_final.$extra = TYPE_EXTRA;
	const stmt_final = `${qstr0} AND ${get_sw_str("begin")} AND ${get_sw_str("end")}${condition};`;
	arg_final.$race_begin = card_begin.race;
	arg_final.$attr_begin = card_begin.attribute;
	arg_final.$lv_begin = card_begin.level;
	arg_final.$atk_begin = card_begin.atk;
	arg_final.$def_begin = card_begin.def;

	arg_final.$race_end = card_end.race;
	arg_final.$attr_end = card_end.attribute;
	arg_final.$lv_end = card_end.level;
	arg_final.$atk_end = card_end.atk;
	arg_final.$def_end = card_end.def;
	current_stmt = stmt_final;
	current_arg = arg_final;
	const result = query(stmt_final, arg_final);
	show_result(valid_params, result);
}
