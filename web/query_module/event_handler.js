"use strict";
const select_type = document.getElementById("select_type");
const select_subtype_op = document.getElementById("select_subtype_op");

const cb_marker = document.getElementsByName("marker");
const cb_attr = document.getElementsByName("attr");
const cb_race = document.getElementsByName("race");
const cb_level = document.getElementsByName("level");
const cb_scale = document.getElementsByName("scale");
const monster_checkbox = ["marker", "attr", "race", "level", "scale"];

const row_subtype = document.getElementsByClassName("row_subtype");
const subtype_operator = document.getElementById("subtype_operator");
const subtype_m = document.getElementById("subtype_m");
const subtype_s = document.getElementById("subtype_s");
const subtype_t = document.getElementById("subtype_t");
const row_exclude = document.getElementsByClassName("row_exclude");
const form1 = document.getElementById("form1");

const div_count = document.getElementById("div_count");
const div_page = document.getElementById("div_page");
const select_page = document.getElementById("select_page");
const table_result = document.getElementById("table_result");

function clear_cb(name) {
	for (const cb of document.getElementsByName(name)) {
		cb.checked = false;
	}
}

function disable_cb(name, status) {
	for (const cb of document.getElementsByName(name)) {
		cb.disabled = status;
	}
}

function hide_type(type, hidden) {
	switch (type) {
		case 0:
			for (const row of document.getElementsByClassName("monster_row")) {
				row.hidden = hidden;
			}
			for (const element of document.getElementsByClassName("monster_input")) {
				element.disabled = hidden;
			}
			for (const cbname of monster_checkbox) {
				disable_cb(cbname, hidden);
			}
			break;
		case 1:
			for (const row of row_subtype)
				row.hidden = hidden;
			for (const row of row_exclude)
				row.hidden = hidden;
			subtype_operator.hidden = hidden;
			subtype_m.hidden = hidden;
			select_subtype_op.disabled = hidden;
			disable_cb("mtype", hidden);
			disable_cb("exclude", hidden);
			break;
		case 2:
			for (const row of row_subtype)
				row.hidden = hidden;
			subtype_s.hidden = hidden;
			disable_cb("stype", hidden);
			break;
		case 3:
			for (const row of row_subtype)
				row.hidden = hidden;
			subtype_t.hidden = hidden;
			disable_cb("ttype", hidden);
			break;
		default:
			break;
	}
}

select_type.addEventListener("change", function (event) {
	switch (event.currentTarget.value) {
		case "1":
			hide_type(2, true);
			hide_type(3, true);
			hide_type(0, false);
			hide_type(1, false);
			break;
		case "2":
			hide_type(0, true);
			hide_type(1, true);
			hide_type(3, true);
			hide_type(2, false);
			break;
		case "3":
			hide_type(0, true);
			hide_type(1, true);
			hide_type(2, true);
			hide_type(3, false);
			break;
		default:
			hide_type(1, true);
			hide_type(2, true);
			hide_type(3, true);
			hide_type(0, false);
			break;
	}
});

document.getElementById("subtype_reset").addEventListener("click", function (event) {
	clear_cb("mtype");
	clear_cb("stype");
	clear_cb("ttype");
});
document.getElementById("exclude_reset").addEventListener("click", function (event) {
	clear_cb("exclude");
});
document.getElementById("attr_reset").addEventListener("click", function (event) {
	clear_cb("attr");
});
document.getElementById("race_reset").addEventListener("click", function (event) {
	clear_cb("race");
});
document.getElementById("level_reset").addEventListener("click", function (event) {
	clear_cb("level");
});
document.getElementById("scale_reset").addEventListener("click", function (event) {
	clear_cb("scale");
});
document.getElementById("marker_reset").addEventListener("click", function (event) {
	clear_cb("marker");
});

form1.addEventListener("reset", function (event) {
	select_type.value = "";
	select_type.dispatchEvent(new Event("change"));
});

window.addEventListener("DOMContentLoaded", function (event) {
	if (window.innerWidth > MAX_WIDTH) {
		div_count.style.width = MAX_WIDTH + "px";
		div_page.style.width = MAX_WIDTH + "px";
		table_result.style.width = MAX_WIDTH + "px";
	}
	else {
		div_count.style.width = "100%";
		div_page.style.width = "100%";
		table_result.style.width = "100%";
	}

	const params = new URLSearchParams(window.location.search);
	const ctype = params.get("ctype");
	switch (ctype) {
		case "1":
		case "2":
		case "3":
			select_type.value = ctype;
			select_type.dispatchEvent(new Event("change"));
			break;
		default:
			break;
	}
});
