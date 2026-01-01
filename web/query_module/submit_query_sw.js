"use strict";
function url_query() {
	if (window.location.search.substring(1) === "")
		return;
	const params = new URLSearchParams(window.location.search);
	server_analyze2(params);
}

db_ready.then(() => {
	url_query();
	document.getElementById("button1").disabled = false;
	document.getElementById("button2").disabled = false;
});
