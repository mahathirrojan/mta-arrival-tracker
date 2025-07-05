const API_BASE = "http://localhost:8000";

async function loadStations() {
  const response = await fetch(`${API_BASE}/stations`);
  const stations = await response.json();

  const select = document.getElementById("station");
  stations.forEach((name) => {
    const opt = document.createElement("option");
    opt.value = name;
    opt.textContent = name;
    select.appendChild(opt);
  });
}

async function loadArrivals() {
  const station = document.getElementById("station").value;
  const res = await fetch(
    `${API_BASE}/arrivals?station=${encodeURIComponent(station)}`
  );
  const data = await res.json();

  const container = document.getElementById("results");
  container.innerHTML = "";

  for (let direction of ["northbound", "southbound"]) {
    if (data[direction].length > 0) {
      const card = document.createElement("div");
      card.className = "card";
      const title = document.createElement("h2");
      title.textContent =
        direction.charAt(0).toUpperCase() + direction.slice(1);
      card.appendChild(title);

      data[direction].forEach((arrival) => {
        const pill = document.createElement("span");
        pill.className = "pill";
        pill.textContent = `${arrival.route} → ${arrival.minutes} min`;
        card.appendChild(pill);
      });

      container.appendChild(card);
    }
  }
}

window.onload = loadStations;
