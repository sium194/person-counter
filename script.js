const API_BASE = "http://127.0.0.1:8000/api";

function render(data) {
  document.getElementById("maxCap").value = data.max_capacity;
  document.getElementById("currentCount").textContent = data.current_count;
  document.getElementById("capView").textContent = `${data.current_count} / ${data.max_capacity}`;
  document.getElementById("totalIn").textContent = data.total_entered;
  document.getElementById("totalOut").textContent = data.total_exited;
  document.getElementById("statusBox").textContent = `Status: ${data.status}`;

  const logBox = document.getElementById("logBox");
  logBox.innerHTML = "";

  if (!data.logs || data.logs.length === 0) {
    logBox.innerHTML = "<div>No activity yet.</div>";
    return;
  }

  data.logs.forEach((line) => {
    const item = document.createElement("div");
    item.textContent = line;
    logBox.appendChild(item);
  });
}

async function loadStatus() {
  try {
    const res = await fetch(`${API_BASE}/status`);
    if (!res.ok) throw new Error("Server error");
    const data = await res.json();
    render(data);
  } catch (e) {
    document.getElementById("statusBox").textContent = "Backend unreachable — start backend.py first";
  }
}

async function sendAction(action) {
  try {
    const res = await fetch(`${API_BASE}/${action}`, { method: "POST" });
    if (!res.ok) throw new Error("Action failed");
    const data = await res.json();
    render(data);
  } catch (e) {
    document.getElementById("statusBox").textContent = "Error connecting to backend";
  }
}

async function updateCapacity() {
  const inputVal = parseInt(document.getElementById("maxCap").value, 10);
  const maxCapacity = Number.isNaN(inputVal) || inputVal < 1 ? 1 : inputVal;

  try {
    const res = await fetch(`${API_BASE}/capacity`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ max_capacity: maxCapacity }),
    });
    if (!res.ok) throw new Error("Capacity update failed");
    const data = await res.json();
    render(data);
  } catch (e) {
    document.getElementById("statusBox").textContent = "Could not update capacity";
  }
}

loadStatus();