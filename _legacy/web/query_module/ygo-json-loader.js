"use strict";
const last_pack = "26PP#3";
const unknown_index = {
};

function object_to_map(obj) {
	const map = new Map();
	for (const [key, value] of Object.entries(obj))
		map.set(Number.parseInt(key), value);
	return map;
}

let SQL = null;
const db_list = [];
const fetch_list = [];
// sqlite
const promise_sql = initSqlJs({ locateFile: filename => `https://cdnjs.cloudflare.com/ajax/libs/sql.js/1.12.0/${filename}` });
const promise_db = fetch('https://salix5.github.io/archive/cards.zip')
	.then(response => response.blob())
	.then(JSZip.loadAsync)
	.then(zip_file => zip_file.file("cards.cdb").async("uint8array"));
const promise_db2 = fetch('https://salix5.github.io/cdb/expansions/pre-release.cdb')
	.then(response => response.arrayBuffer())
	.then(buf => new Uint8Array(buf));
fetch_list.push(Promise.all([promise_sql, promise_db, promise_db2])
	.then(([sql, file1, file2]) => {
		SQL = sql;
		db_list.push(new SQL.Database(file1));
		db_list.push(new SQL.Database(file2));
	}));

const bls_postfix = Object.create(null);
bls_postfix['en'] = ' (Normal)';
bls_postfix['ja'] = '（通常モンスター）';
bls_postfix['ko'] = ' (일반)';
bls_postfix['zh-tw'] = '（通常怪獸）';

const official_name = Object.create(null);
official_name['en'] = 'en_name';
official_name['ja'] = 'jp_name';

const game_name = Object.create(null);
game_name['en'] = 'md_name_en';
game_name['ja'] = 'md_name_jp';

let cid_table = null
const name_table = Object.create(null);
const md_table = Object.create(null);
const complete_name_table = Object.create(null);
const replace_name = Object.create(null);
const pre_release = Object.create(null);
const wiki_link = Object.create(null);

const setname = Object.create(null);
const ltable_md = Object.create(null);
const md_card_list = Object.create(null);
fetch_list.push(fetch(`text/md_name_jp.json`).then(response => response.json()).then(data => { md_table['ja'] = object_to_map(data) }));
fetch_list.push(fetch(`text/md_name_en.json`).then(response => response.json()).then(data => { md_table['en'] = object_to_map(data) }));
fetch_list.push(fetch(`text/setname.json`).then(response => response.json()).then(data => Object.assign(setname, data)));
fetch_list.push(fetch(`text/lflist_md.json`).then(response => response.json()).then(data => Object.assign(ltable_md, data)));
fetch_list.push(fetch(`text/CardList.json`).then(response => response.json()).then(data => Object.assign(md_card_list, data)));
fetch_list.push(fetch(`text/replace_name.json`).then(response => response.json()).then(data => Object.assign(replace_name, data)));
fetch_list.push(fetch(`pack/pre_release.json`).then(response => response.json()).then(data => Object.assign(pre_release, data)));
fetch_list.push(fetch(`pack/wiki_link.json`).then(response => response.json()).then(data => Object.assign(wiki_link, data)));

// local
const cid_object = Object.create(null);
const jp_object = Object.create(null);
const en_object = Object.create(null);
const pack_list = Object.create(null);
const ltable_ocg = Object.create(null);
const ltable_tcg = Object.create(null);
const from_local = false;
if (localStorage.getItem("last_pack") === last_pack) {
	try {
		Object.assign(cid_object, JSON.parse(localStorage.getItem("cid_table")));
		Object.assign(jp_object, JSON.parse(localStorage.getItem("name_table_jp")));
		Object.assign(en_object, JSON.parse(localStorage.getItem("name_table_en")));
		Object.assign(pack_list, JSON.parse(localStorage.getItem("pack_list")));
		Object.assign(ltable_ocg, JSON.parse(localStorage.getItem("ltable_ocg")));
		Object.assign(ltable_tcg, JSON.parse(localStorage.getItem("ltable_tcg")));
		from_local = true;
	}
	catch (ex) {
		localStorage.removeItem("last_pack");
	}
}
if (!from_local) {
	localStorage.clear();
	fetch_list.push(fetch(`text/cid_table.json`).then(response => response.json()).then(data => Object.assign(cid_object, data)));
	fetch_list.push(fetch(`text/name_table_jp.json`).then(response => response.json()).then(data => Object.assign(jp_object, data)));
	fetch_list.push(fetch(`text/name_table_en.json`).then(response => response.json()).then(data => Object.assign(en_object, data)));
	fetch_list.push(fetch(`pack/pack_list.json`).then(response => response.json()).then(data => Object.assign(pack_list, data)));
	fetch_list.push(fetch(`text/lflist.json`).then(response => response.json()).then(data => Object.assign(ltable_ocg, data)));
	fetch_list.push(fetch(`text/lflist_tcg.json`).then(response => response.json()).then(data => Object.assign(ltable_tcg, data)));
}

let id_to_cid = new Map();
const db_ready = Promise.all(fetch_list)
	.then(() => {
		cid_table = object_to_map(cid_object);
		name_table['ja'] = object_to_map(jp_object);
		name_table['en'] = object_to_map(en_object);
		for (const locale of Object.keys(official_name)) {
			const table1 = new Map(name_table[locale]);
			if (md_table[locale]) {
				for (const [cid, name] of md_table[locale]) {
					table1.set(cid, name);
				}
			}
			complete_name_table[locale] = table1;
		}
		id_to_cid = inverse_mapping(cid_table);
		if (!from_local) {
			try {
				localStorage.setItem("cid_table", JSON.stringify(cid_object));
				localStorage.setItem("name_table_jp", JSON.stringify(jp_object));
				localStorage.setItem("name_table_en", JSON.stringify(en_object));
				localStorage.setItem("pack_list", JSON.stringify(pack_list));
				localStorage.setItem("ltable_ocg", JSON.stringify(ltable_ocg));
				localStorage.setItem("ltable_tcg", JSON.stringify(ltable_tcg));
				localStorage.setItem("last_pack", last_pack);
			} catch (ex) {
			}
		}
	});
