"use strict";
const select_subtype_op = document.getElementById("select_subtype_op");

const cb_attr = document.getElementsByName("attr");
const cb_race = document.getElementsByName("race");
const cb_level = document.getElementsByName("level");
const cb_scale = document.getElementsByName("scale");
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

document.getElementById("subtype_reset").addEventListener("click", function (event) {
	clear_cb("mtype");
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
});
