const API = "http://localhost:8000";

async function loadRoutes() {
  const res = await fetch(`${API}/routes`);
  const routes = await res.json();
  const grid = document.getElementById("routes");
  grid.innerHTML = "";
  routes.forEach(route => {
    const btn = document.createElement("button");
    btn.className = "route-button";
    btn.textContent = route;
    btn.onclick = () => loadStops(route);
    grid.appendChild(btn);
  });
}

async function loadStops(route) {
  const res = await fetch(`${API}/stops-for-route?route=${route}`);
  const data = await res.json();
  const stopList = document.getElementById("stops");
  stopList.innerHTML = `<h2>Stops for route ${route}</h2>`;
  data.stops.forEach(stop => {
    const btn = document.createElement("button");
    btn.className = "stop-button";
    btn.textContent = `${stop.stop_name}`;
    btn.onclick = () => showStopModal(stop);
    stopList.appendChild(btn);
  });
}

async function showStopModal(stop) {
  const res = await fetch(`${API}/arrivals?station=${encodeURIComponent(stop.stop_name)}`);
  const data = await res.json();

  document.getElementById("modal-title").textContent = stop.stop_name;

  const cardContainer = document.getElementById("arrival-cards");
  cardContainer.innerHTML = "";

  ["northbound", "southbound"].forEach(dir => {
    if (data[dir]?.length) {
      const card = document.createElement("div");
      card.className = "card";
      const title = document.createElement("h3");
      title.textContent = dir.charAt(0).toUpperCase() + dir.slice(1);
      card.appendChild(title);

      data[dir].forEach(arr => {
        const row = document.createElement("div");
        row.className = "arrival-row";
        row.innerHTML = `
          <div class="left"><span class="route-circle">${arr.route}</span> </div>
          <div class="right">${arr.minutes <= 1 ? "Arriving" : `${arr.minutes} mins`}</div>
        `;
        card.appendChild(row);
      });

      cardContainer.appendChild(card);
    }
  });

  if (stop.other_routes?.length) {
    const transferCard = document.createElement("div");
    transferCard.className = "card";
    transferCard.innerHTML = `<h3>Other Routes Here</h3>`;
    stop.other_routes.forEach(r => {
      const pill = document.createElement("span");
      pill.className = "pill";
      pill.textContent = r;
      transferCard.appendChild(pill);
    });
    cardContainer.appendChild(transferCard);
  }

  document.getElementById("modal").classList.remove("hidden");
}

document.getElementById("modal-close").onclick = () => {
  document.getElementById("modal").classList.add("hidden");
};

window.onload = loadRoutes;