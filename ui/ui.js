let showingResults = false;
let elapsed = 0;
let duration = 0;
let playStatus = "stop";

ready(start);

function start() {
  updateStatus();
  //setInterval(() => updateStatus(), 1000 * 10);
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
    return null;
  }
};

async function resetStatus() {
  showingResults = false;
  const songDetails = await doAjax("GET", "status");

  if (songDetails.playing === 1) {
    showCoverArt(songDetails.libraryid);
  } else {
    showStartScreen();
  }
}

function updatePlayTime() {
  const playTime = document.getElementById("time");
  if (playStatus === "stop") {
    playTime.innerHTML = "";
    return;
  } else if (playStatus === "play") {
    elapsed++;
    if (elapsed > duration) {
      updateStatus();
    }
  }

  playTime.innerHTML = `${fmtMSS(elapsed)} / ${fmtMSS(duration)}`;
}

async function updateStatus(updateContent = true) {
  const statusDiv = document.getElementById("status");
  const playBtn = document.getElementById("play");
  const playTime = document.getElementById("time");
  const songDetails = await doAjax("GET", "status");

  statusDiv.className = songDetails.state === "pause" ? "blink" : "";
  playStatus = songDetails.state;

  if (songDetails.state === "play" || songDetails.state === "pause") {
    elapsed = songDetails.elapsed;
    duration = songDetails.duration;

    const statusText = `<p>Now playing: ${songDetails.title} by ${songDetails.artist}</p>`;
    if (statusDiv.innerHTML != statusText) {
      statusDiv.innerHTML = statusText;
      playBtn.innerHTML = "Stop";
      playBtn.onclick = () => stopPlay();
      if (updateContent && !showingResults) showCoverArt(songDetails.libraryid);
      playTime.innerHTML = `${fmtMSS(songDetails.elapsed)} / ${fmtMSS(songDetails.duration)}`;
    }
  } else {
    isPlaying = false;
    playTime.innerHTML = "";
    statusDiv.innerHTML = "<p>Not Playing</p>";
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

async function stopRadio() {
  clearPaused();
  await doAjax("GET", "radio/stop");
  const statusDiv = document.getElementById("status");
  const playBtn = document.getElementById("play");
  statusDiv.innerHTML = "<p>Not Playing</p>";
  playBtn.innerHTML = "Play";
  playBtn.onclick = () => play();
}

async function pause() {
  result = await doAjax("POST", "pause");
  updateStatus();
}

// function clearPaused() {
//   const status = document.getElementById("status");
//   status.className = "";
// }

// function setPaused(paused) {
//   const status = document.getElementById("status");
//   status.className = paused ? "blink" : "";
// }

async function play() {
  // clearPaused();
  showingResults = false;
  const status = await doAjax("POST", "play");
  //if (status.status === "play started") showCoverArt(status.id);
  updateStatus();
}

async function playAlbum(path) {
  showingResults = false;
  const status = await doAjax("POST", "playalbum", { path: path });
  //if (status.status === "play started") showCoverArt(status.id);
  updateStatus();
}

async function queueAlbum(path) {
  await doAjax("POST", "queuealbum", { path: path });
  updateStatus();
}

async function skip() {
  // clearPaused();
  await doAjax("POST", "skip");
  updateStatus();
}

async function updateQueueStatus() {
  const status = await doAjax("GET", "queuestatus");
  document.getElementById("queue").innerHTML = `Queue (${status.queueCount}/${fmtMSS(status.queueLength)})`;
}

async function queueSong(id) {
  const result = await doAjax("POST", `add/${id}`);
  await updateQueueStatus();
}

async function getAlbum(name) {
  //name = decodeURIComponent(name);
  var songs = await doAjax("GET", `album?search=${encodeURIComponent(name)}`);
  if (songs === null) return;
  let i = 1;
  document.getElementById("content").innerHTML = "";
  for (const song of songs) {
    const listItem = document.createElement("li");
    const divText = document.createElement("div");
    divText.innerHTML = `<h4>${i++}. ${song.tracktitle} ${fmtMSS(song.length)}</h4>
    <p>${song.artist} - ${song.album}</p>`;

    const divButtons = document.createElement("div");
    divButtons.appendChild(addButton("Play", () => playOneSong(song.id)));
    divButtons.appendChild(addButton("Add", () => queueSong(song.id)));

    listItem.appendChild(divText);
    listItem.appendChild(divButtons);
    document.getElementById("content").appendChild(listItem);
  }
}

function addButton(text, clickEvent) {
  let button = document.createElement("button");
  button.textContent = text;
  button.onclick = clickEvent;
  return button;
}

async function doCommand(command) {
  if (command == ":clear") await doAjax("DELETE", "all");
  else if (command.startsWith(":mix ")) {
    var name = command.substring(5);
    await doAjax("POST", `mix/${name}`);
  } else if (command.startsWith(":delmix ")) {
    var name = command.substring(8);
    await doAjax("DELETE", `mix/${name}`);
  } else if (command.startsWith(":rand ")) {
    var num = parseInt(command.substring(6));
    if (num > 0) await doAjax("POST", `rand/${num}`);
  } else if (command.startsWith(":hist")) {
    await getHistory();
  } else if (command.startsWith(":wrapped")) {
    await showWrapped();
  } else if (command.startsWith(":radio")) {
    await radioStations();
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

  document.getElementById("content").innerHTML = "";
  for (const album of albums) {
    const listItem = document.createElement("li");
    const divText = document.createElement("div");
    if (album.tracktitle) {
      divText.innerHTML = `<h4>${album.tracktitle}</h4><p>${album.artist} - ${album.album}</a></p>`;
    } else {
      divText.innerHTML = `<h4>${album.artist}</h4><p><a href="#" onclick="getAlbum('${encodeURIComponent(
        album.path
      ).replace(/'/g, "%27")}')"> ${album.album}</a></p>`;
    }
    const divButtons = document.createElement("div");
    if (album.tracktitle) {
      divButtons.appendChild(addButton("Play", () => playOneSong(album.id)));
      divButtons.appendChild(addButton("Add", () => queueSong(album.id)));
    } else {
      divButtons.appendChild(addButton("Play", () => playAlbum(album.path)));
      divButtons.appendChild(addButton("Add", () => queueAlbum(album.path)));
    }
    listItem.appendChild(divText);
    listItem.appendChild(divButtons);
    document.getElementById("content").appendChild(listItem);
  }
}

function fmtMSS(s) {
  const stringDate = new Date(s * 1000).toISOString();
  return s < 3600 ? stringDate.substring(14, 19) : stringDate.substring(11, 19);
  //return (s - (s %= 60)) / 60 + (9 < s ? ":" : ":0") + s;
}

async function removeFromQueue(id, row) {
  const result = await doAjax("DELETE", `${id}`);
  await updateQueueStatus();
  row.parentNode.removeChild(row);
}

async function playOneSong(id) {
  await doAjax("POST", `playsong/${id}`);
  updateStatus();
}

async function getQueue() {
  showingResults = true;
  const queue = await doAjax("GET", "queue");
  let i = 1;
  document.getElementById("content").innerHTML = "";

  for (const song of queue) {
    const listItem = document.createElement("li");
    const divText = document.createElement("div");
    divText.innerHTML = `<h4>${i++}. ${song.title} ${fmtMSS(song.duration)}</h4>
    <p>${song.artist} - ${song.album}</p>`;

    const divButtons = document.createElement("div");
    divButtons.appendChild(addButton("Del", () => removeFromQueue(song.id, listItem)));

    listItem.appendChild(divText);
    listItem.appendChild(divButtons);
    document.getElementById("content").appendChild(listItem);
  }
  await updateQueueStatus();
}

async function getHistory() {
  const hist = await doAjax("GET", "history");
  document.getElementById("content").innerHTML = "";

  for (const song of hist) {
    const listItem = document.createElement("li");
    const divText = document.createElement("div");
    divText.innerHTML = `<h4>${song.tracktitle} </h4>
    <p>Played on: ${song.dateplayed}</p>
    <p>${song.artist} - ${song.album}</p>`;

    listItem.appendChild(divText);
    document.getElementById("content").appendChild(listItem);
  }
}

function showCoverArt(id) {
  const doc = document.getElementById("content");
  doc.innerHTML = `
  <img class="center" width=300 height=300 src="coverart/${id}" />
  <div class="center">
    <ul class="controls">
      <li>
        <button onclick="skip();">Skip</button>
      </li>
      <li>
        <button id="pause" onclick="pause()">Pause</button>
      </li>
    </ul>
  </div>
  `;
}

function showStartScreen() {
  const doc = document.getElementById("content");
  doc.innerHTML = `
        <li>
          <div style="max-width: 100%;">
            <h2>MusicBox</h2>
            <h3>Commands</h3>
            <p><strong>:clear</strong>  - clear the current queue</p>
            <p><strong>:mix [name of mixtape]</strong> - save contents of current queue to a 'mixtape' (aka playlist)</p>
            <p><strong>:delmix [name of mixtape]</strong> - delete a mixtape</p>
            <p><strong>:rand [x]</strong> - add 'x' number of random songs to the queue</p>
            <p><strong>:hist</strong> - show history of songs played</p>
            <p><strong>:radio</strong> - show radio stations</p>
            <p><strong>:wrapped</strong> - MusicBox Wrapped!</p>
          </div>
        </li>
  `;
}

async function showWrapped() {
  const pastYear = new Date().getFullYear() - 1;
  const doc = document.getElementById("content");
  const artists = await doAjax("GET", `wrapped/artist/${pastYear}`);
  let artists_html = "";
  let i = 0;
  for (const a of artists) {
    artists_html += `<li>${++i} ${a.artist}</li>`;
  }
  const albums = await doAjax("GET", `wrapped/album/${pastYear}`);
  let albums_html = "";
  i = 0;
  for (const a of albums) {
    albums_html += `<li>${++i} ${a.album}</li>`;
  }
  const songs = await doAjax("GET", `wrapped/song/${pastYear}`);
  let songs_html = "";
  i = 0;
  for (const a of songs) {
    songs_html += `<li>${++i} ${a.song}</li>`;
  }
  const listenTime = await doAjax("GET", `wrapped/time/${pastYear}`);
  doc.innerHTML = `
        
          <div style="max-width: 100%;">
            <h1 class="rainbow">MusicBox Wrapped ${pastYear}</h1>
            <h3 class="rainbow2">Top Artists</h3>
            ${artists_html}
            <h3 class="rainbow2">Top Songs</h3>
            ${songs_html}
            <h3 class="rainbow2">Top Albums</h3>
            ${albums_html}
            <h2 class="rainbow2">Total listening time: ${listenTime.seconds / 60} minutes</h2>
          </div>
        
  `;
}
