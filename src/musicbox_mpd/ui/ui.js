let showingResults = false;
let elapsed = 0;
let duration = 0;
let playStatus = "stop";
let prevRowIndex = null;
let songNo = 0;

ready(start);

function start() {
  updateStatus();
  setInterval(() => updatePlayTime(), 1000);
  const input = document.getElementById("search");

  input.addEventListener("keydown", (e) => {
    if (e.code == "Enter") processCommand();
  });
}

function ready(fn) {
  if (document.readyState !== "loading") {
    fn();
  } else {
    document.addEventListener("DOMContentLoaded", fn);
  }
}

const doAjax = async (verb, endpoint, data = null) => {
  const options = {
    method: verb,
    headers: {
      "Content-type": "application/json; charset=UTF-8",
    },
  };
  if (data != null) options.body = JSON.stringify(data);
  const response = await fetch(`/${endpoint}`, options);

  if (response.ok) {
    return await response.json();
  } else {
    showError(response.statusText);
    return null;
  }
};

async function resetStatus() {
  showingResults = false;

  if (playStatus === "stop") {
    showStartScreen();
  } else {
    updateStatus();
  }
}

function updatePlayTime() {
  const playTime = document.getElementById("time");
  if (playStatus === "stop") {
    playTime.innerHTML = "";
    return;
  } else if (playStatus === "play") {
    //const playBtn = document.getElementById("play");
    //playBtn.innerHTML = "Stop";
    elapsed++;
    if (elapsed > duration) {
      updateStatus();
    }
  }

  playTime.innerHTML = `${fmtMSS(elapsed)}/${fmtMSS(duration)}`;
}

var forceRedraw = function (element) {
  if (!element) {
    return;
  }

  var n = document.createTextNode(" ");
  var disp = element.style.display; // don't worry about previous display style

  element.appendChild(n);
  element.style.display = "none";

  setTimeout(function () {
    element.style.display = disp;
    n.parentNode.removeChild(n);
  }, 20); // you can play with this timeout to make it as short as possible
};

async function updateStatus(updateContent = true) {
  const songName = document.getElementById("songName");
  const artistName = document.getElementById("artistName");
  const playBtn = document.getElementById("play");
  const playTime = document.getElementById("time");
  const songDetails = await doAjax("GET", "status");

  songName.className = songDetails.state === "pause" ? "blink" : "";
  playStatus = songDetails.state;
  songNo = Number(songDetails.song);

  if (songDetails.state === "play" || songDetails.state === "pause") {
    elapsed = songDetails.elapsed;
    duration = songDetails.duration;
    songName.innerHTML = songDetails.title;
    artistName.innerHTML = songDetails.artist;
    playBtn.innerHTML = "Stop";
    playBtn.onclick = () => stopPlay();
    forceRedraw(playBtn); // Fix IOS bug where it refuses to update text on the button
    if (updateContent && !showingResults) showCoverArt(songDetails);
    playTime.innerHTML = `${fmtMSS(songDetails.elapsed)} / ${fmtMSS(songDetails.duration)}`;
  } else {
    isPlaying = false;
    playTime.innerHTML = "";
    songName.innerHTML = "Stopped";
    artistName.innerHTML = "Playing";
    playBtn.innerHTML = "Play";
    playBtn.onclick = () => play();
    if (updateContent && !showingResults) showStartScreen();
  }
  await updateQueueStatus();
}

async function stopPlay() {
  await doAjax("POST", "stop");
  updateStatus();
}

async function pause() {
  result = await doAjax("POST", "pause");
  updateStatus();
}

async function play() {
  showingResults = false;
  const status = await doAjax("POST", "play");
  if (status.status === "Error") showError(status.message);
  else updateStatus();
}

async function playAlbum(path, listItem) {
  showingResults = false;
  const status = await doAjax("POST", "playalbum", { path: path });
  if (status.status === "Error") {
    showError(status.message);
    return;
  }
  if (status.status === "notplay") {
    showInfo("There is already a song playing.  Please stop it first before playing a new album.", "Notice");
    return;
  }
  updateStatus();
}

async function playOneSong(id, listItem) {
  showingResults = false;
  const status = await doAjax("POST", `playsong/${id}`);
  if (status.status === "Error") {
    showError(status.message);
    return;
  }
  if (status.status === "next") {
    listItem.className = "playnext";
    updateQueueStatus();
    return;
  }
  updateStatus();
}

async function skip() {
  await doAjax("POST", "skip");
  updateStatus();
}

async function updateQueueStatus() {
  const status = await doAjax("GET", "queuestatus");
  const playButton = document.getElementById("play");
  playButton.disabled = status.queueCount == 0 && playStatus == "stop";
  if (playStatus == "stop") {
    document.getElementById("songName").innerHTML = "Queue";
    document.getElementById("artistName").innerHTML = `${status.queueCount} Songs (${fmtMSS(status.queueLength)})`;
    document.getElementById("queue").innerHTML = "";
  } else {
    document.getElementById("queue").innerHTML = `${songNo + 1} of ${status.queueCount}`;
  }
}

async function queueAlbum(path, listItem) {
  await doAjax("POST", "queuealbum", { path: path });
  updateStatus();
  //listItem = document.getElementById(`row${row}`);
  listItem.className = "added";
}

async function queueSong(id, listItem) {
  const result = await doAjax("POST", `add/${id}`);
  await updateQueueStatus();
  //listItem = document.getElementById(`row${row}`);
  listItem.className = "added";
}

async function getAlbum(name, rowIndex) {
  //name = decodeURIComponent(name);
  //console.log("id of element", o.id);
  prevRowIndex = rowIndex;
  var songs = await doAjax("GET", `album?search=${encodeURIComponent(name)}`);
  if (songs === null) return;
  let i = 1;
  document.getElementById("content").innerHTML = "";
  for (const song of songs) {
    const listItem = document.createElement("li");
    listItem.className = "list-item";
    const divText = document.createElement("div");
    listItem.id = `song_row${i}`;
    divText.innerHTML = `<h4>${i++}. ${song.tracktitle} ${fmtMSS(song.length)}</h4>
    <p>${song.artist} - ${song.album}</p>`;

    const divButtons = document.createElement("div");
    divButtons.appendChild(addButton("Play", () => playOneSong(song.id, listItem)));
    divButtons.appendChild(addButton("Add", () => queueSong(song.id, listItem)));

    listItem.appendChild(divText);
    listItem.appendChild(divButtons);
    document.getElementById("content").appendChild(listItem);
  }
  const firstRow = document.getElementById("song_row1");
  firstRow?.scrollIntoView({ behavior: "instant", block: "center", inline: "center" });
}

async function getMixtapes() {
  var mixtapes = await doAjax("GET", "mix");
  if (mixtapes === null) return;
  let i = 1;
  document.getElementById("content").innerHTML = "";
  for (const tape of mixtapes) {
    const listItem = document.createElement("li");
    listItem.className = "list-item";
    const divText = document.createElement("div");
    divText.innerHTML = `<h4>${i++}. ${tape.playlist}</h4>`;

    const divButtons = document.createElement("div");
    divButtons.appendChild(addButton("Save", () => mixtapeSave(tape.playlist)));
    divButtons.appendChild(addButton("Load", () => mixtapeAdd(tape.playlist)));
    divButtons.appendChild(addButton("Delete", () => mixtapeDelete(tape.playlist)));

    listItem.appendChild(divText);
    listItem.appendChild(divButtons);
    document.getElementById("content").appendChild(listItem);
  }
}

async function mixtapeSave(name) {
  await doAjax("POST", `savemix/${encodeURIComponent(name)}`);
  updateStatus();
}

async function mixtapeAdd(name) {
  await doAjax("POST", `loadmix/${encodeURIComponent(name)}`);
  updateStatus();
}

function mixtapeDelete(name) {
  const searchText = document.getElementById("search");
  searchText.value = `:delmix ${name}`;
}

function addButton(text, clickEvent) {
  let button = document.createElement("button");
  button.textContent = text;
  button.onclick = clickEvent;
  button.style.margin = "3px";
  return button;
}

async function doCommand(command) {
  if (command.startsWith(":c")) {
    //:clear
    await doAjax("DELETE", "all");
    updateStatus();
  } else if (command === ":mix") {
    await getMixtapes();
  } else if (command.startsWith(":mix ")) {
    var name = command.substring(5);
    await doAjax("POST", `mix/${name}`);
  } else if (command.startsWith(":delmix ")) {
    var name = command.substring(8);
    await doAjax("DELETE", `mix/${name}`);
  } else if (command.startsWith(":rand ")) {
    var num = parseInt(command.substring(6));
    if (num > 0) await doAjax("POST", `rand/${num}`);
  } else if (command.startsWith(":u")) {
    //:update
    await doAjax("POST", "update");
  } else if (command.startsWith(":se")) {
    //:settings
    showSettings();
  } else if (command.startsWith(":e")) {
    //:error
    checkError();
  } else if (command.startsWith(":sh")) {
    //:shuffle
    await doAjax("POST", "shuffle");
  } else if (command.startsWith(":a")) {
    ver = await doAjax("GET", "version");
    showInfo(`<p>Musicbox Version: ${ver.musicbox}</p> <p>MPD Version: ${ver.mpd}</p>`, "About MusicBox");
  } else {
    return;
  }
  document.getElementById("search").value = "";
}

async function processCommand() {
  showingResults = true;
  const command = document.getElementById("search").value;
  if (command.length > 0 && command[0] == ":") await doCommand(command);
  else await doSearch();

  await updateStatus(false);
}

async function doSearch() {
  const search = document.getElementById("search").value;
  const albums = await doAjax("GET", `search?search=${search}`);
  let i = 0;
  document.getElementById("content").innerHTML = "";
  for (const album of albums) {
    const listItem = document.createElement("li");
    listItem.className = "list-item";
    listItem.id = `row${i++}`;
    const divText = document.createElement("div");
    if (album.tracktitle) {
      divText.innerHTML = `<h4>${album.tracktitle}</h4><p>${album.artist} - ${album.album}</a></p>`;
    } else {
      divText.innerHTML = `<h4>${album.artist}</h4><p><a href="#" onclick="getAlbum('${encodeURIComponent(
        album.path
      ).replace(/'/g, "%27")}', ${i - 1})"> ${album.album}</a></p>`;
    }
    const divButtons = document.createElement("div");
    if (album.tracktitle) {
      divButtons.appendChild(addButton("Play", () => playOneSong(album.id, listItem)));
      divButtons.appendChild(addButton("Add", () => queueSong(album.id, listItem)));
    } else {
      divButtons.appendChild(addButton("Play", () => playAlbum(album.path, listItem)));
      divButtons.appendChild(addButton("Add", () => queueAlbum(album.path, listItem)));
    }
    listItem.appendChild(divText);
    listItem.appendChild(divButtons);
    document.getElementById("content").appendChild(listItem);
  }
  if (prevRowIndex != null) {
    //if (prevRowIndex > 0) prevRowIndex--;
    const prevElement = `row${prevRowIndex}`;
    const element = document.getElementById(prevElement);
    element?.scrollIntoView({ behavior: "instant", block: "center", inline: "center" });
    prevRowIndex = 0;
  }
}

function fmtMSS(seconds) {
  if (!seconds) return "";
  const hours = Math.floor(seconds / 3600);
  const mins = Math.floor(seconds / 60) % 60;
  const secs = Math.floor(seconds % 60);
  if (hours > 0) return `${hours}:${mins.toString().padStart(2, 0)}:${secs.toString().padStart(2, 0)}`;

  return `${mins}:${secs.toString().padStart(2, 0)}`;
}

async function removeFromQueue(id, row) {
  const result = await doAjax("DELETE", `remove/${id}`);
  await updateQueueStatus();
  row.parentNode.removeChild(row);
}

async function getQueue() {
  showingResults = true;
  const queue = await doAjax("GET", "queue");
  let i = 1;
  document.getElementById("content").innerHTML = "";

  for (const song of queue) {
    const listItem = document.createElement("li");
    listItem.className = "list-item";
    const divText = document.createElement("div");
    divText.innerHTML = `<h4>${i++}. ${song.title ?? song.file} ${fmtMSS(song.duration)}</h4>
    <p>${song.artist ?? ""} - ${song.album ?? ""}</p>`;

    const divButtons = document.createElement("div");
    divButtons.appendChild(addButton("Del", () => removeFromQueue(song.id, listItem)));

    listItem.appendChild(divText);
    listItem.appendChild(divButtons);
    document.getElementById("content").appendChild(listItem);
  }
  await updateQueueStatus();
}

let adjustingVolume = false;
async function volume(amount) {
  const result = await doAjax("POST", `volume/${amount}`);
  const vol = document.getElementById("vol");
  vol.innerHTML = `${result.status} %`;
  vol.classList = " center fade-in-text";
  if (adjustingVolume) return;

  setTimeout(() => {
    vol.classList = "center fade-out-text";
    adjustingVolume = false;
  }, 20000);

  adjustingVolume = true;
}

function showCoverArt(songDetails) {
  const doc = document.getElementById("content");
  doc.innerHTML = `
  <img id = "coverart" class="center" style="object-fit: contain" width=300 height=300 src="coverart/${songDetails.libraryid}" />
  <div class="center" id="songDetails">

  </div>
  <div class="center">
    <ul class="controls">
      <li style="background-color: black;" class="list-item">
        <button onclick="volume(-5);">-</button>
      </li>
      <li style="background-color: black;" class="list-item">
        <button onclick="skip();">Skip</button>
      </li>
      <li style="background-color: black;" class="list-item">
        <button id="pause" onclick="pause()">Pause</button>
      </li>
      <li style="background-color: black;" class="list-item">
        <button onclick="volume(5);">+</button>
      </li>
    </ul>
  </div>
  <div class="center" id="vol"></div>
  `;

  document.getElementById("coverart")?.scrollIntoView({ behavior: "instant", block: "center", inline: "center" });

  if (songDetails.bitrate == 0) {
    setTimeout(async () => {
      const sd = await doAjax("GET", "status");
      setSongDetails(sd);
    }, 500);
  } else {
    setSongDetails(songDetails);
  }
}

function setSongDetails(songDetails) {
  file_extension = songDetails.file.split(".").pop().toUpperCase();
  const audio = songDetails.audio?.split(":");
  let details = `${songDetails.bitrate}kbps`;
  if (audio && file_extension == "FLAC") {
    details = `${audio[0] / 1000}kHz ${audio[1]}bit`;
  }
  if (file_extension == "M4A") file_extension = "AAC";
  document.getElementById("songDetails").innerHTML = `${file_extension} ${details}`;
}

function popSearch(command) {
  const element = document.getElementById("search");
  element.value = command;
}

function showStartScreen() {
  const doc = document.getElementById("content");

  doc.innerHTML = `
        <li class="list-item">
          <div style="max-width: 100%;">
            <h2>MusicBox</h2>
            <h3>Commands</h3>
            <p><strong><a href="#" onclick="popSearch(':clear')">:clear</a></strong>  - clear the current queue</p>
            <p><strong><a href="#" onclick="popSearch(':mix')">:mix</a></strong>  - list all mixtapes</p>
            <p><strong><a href="#" onclick="popSearch(':mix ')">:mix [name]</a></strong> - save contents of current queue to a 'mixtape' (aka playlist)</p>
            <p><strong><a href="#" onclick="popSearch(':delmix ')">:delmix [name]</a></strong> - delete a mixtape</p>
            <p><strong><a href="#" onclick="popSearch(':rand ')">:rand [x]</a></strong> - add 'x' number of random songs to the queue</p>
            <p><strong><a href="#" onclick="popSearch(':update')">:update</a></strong> - re-scan music library</p>
            <p><strong><a href="#" onclick="popSearch(':settings')">:settings</a></strong> - MPD settings</p>
            <p><strong><a href="#" onclick="popSearch(':shuffle')">:shuffle</a></strong> - shuffle queue</p>
          </div>
        </li>
  `;
}

async function showSettings() {
  const doc = document.getElementById("content");

  const response = await fetch(`/ui/settings.html`);
  let html;
  if (response.ok) {
    html = await response.text();
  } else {
    showError("Error loading settings static HTML page.  Maybe a network issue or server is not running?");
    return;
  }
  doc.innerHTML = html;

  const status = await doAjax("GET", "status");

  document.getElementById("random").checked = status.random == 1;
  document.getElementById("repeat").checked = status.repeat == 1;
  document.getElementById("consume").checked = status.consume == 1;

  const replaygain = await doAjax("GET", "replaygain");
  if (replaygain.status === "OK") {
    const val = replaygain.message;
    document.getElementById("rg_off").checked = val == "off";
    document.getElementById("rg_track").checked = val == "track";
    document.getElementById("rg_album").checked = val == "album";
    document.getElementById("rg_auto").checked = val == "auto";
  } else if (replaygain.status === "Error") {
    showError(replaygain.message);
  }
}

async function setReplayGain() {
  const mode = document.querySelector('input[name="replaygain"]:checked').value;
  const response = await doAjax("POST", "replaygain", { mode: mode });
  if (response.status === "Error") {
    showError(response.message);
  }
}

function changeSetting(setting) {
  //document.getElementById(setting).checked = !document.getElementById(setting).checked;
  const value = document.getElementById(setting).checked;
  console.log("Changing setting", setting, value);
  //console.log(setting, value);
  const bitValue = value ? 1 : 0;
  const result = doAjax("POST", `setting/${setting}/${bitValue}`);
}

async function checkError() {
  const status = await doAjax("GET", "status");
  if (status.error) {
    showError(status.error);
  }
}

function showError(message) {
  const doc = document.getElementById("content");
  doc.innerHTML = `<div class="error">
    <h2>Error</h2>
    <p>
    ${message}
    </p>
  </div>`;
  doc.scrollIntoView({ behavior: "instant", block: "center", inline: "center" });
}

function showInfo(message, title) {
  const doc = document.getElementById("content");
  doc.innerHTML = `<div class="info">
    <h2>${title}</h2>
    <p>
    ${message}
    </p>
  </div>`;
  doc.scrollIntoView({ behavior: "instant", block: "center", inline: "center" });
}
