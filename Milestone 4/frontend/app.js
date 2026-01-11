const API = "https://flight-booking-simulator-ig6q.onrender.com/api";
/* ---------------- FLIGHT SEARCH ---------------- */
function searchFlights() {
  const origin = document.getElementById("origin").value;
  const destination = document.getElementById("destination").value;
  const rawDate = document.getElementById("date").value;
  const date = new Date(rawDate).toISOString().split("T")[0];
  fetch(`${API}/flights/search?origin=${origin}&destination=${destination}&travel_date=${date}`)
    .then(res => res.json())
    .then(data => renderFlights(data))
    .catch(err => console.error(err));
}
function renderFlights(flights) {
  const container = document.getElementById("flights-container");
  container.innerHTML = "";
  if (!Array.isArray(flights)) {
    container.innerHTML = `<p>${flights.detail || "No flights found"}</p>`;
    return;
  }
  flights.forEach(f => {
    container.innerHTML += `
      <div class="flight-card">
        <h3>${f.airline_name}</h3>
        <div>${f.origin} ➜ ${f.destination}</div>
        <div>${new Date(f.departure_time).toLocaleTimeString()}</div>
        <div class="price">
          ₹ ${Math.round(f.dynamic_price)} <br>
          <span style="color:#d32f2f;font-size:0.85rem">
            ${f.seats_available} seats left
          </span>
        </div>
        <button class="book-btn"
          onclick="selectFlight(${f.id}, ${f.dynamic_price})">
          Book
        </button>
      </div>
    `;
  });
}
function selectFlight(flightId, price) {
  localStorage.setItem("flightId", flightId);
  localStorage.setItem("price", price);
  window.location.href = "booking.html";
}
/* ---------------- BOOKING ---------------- */
function bookFlight() {
  const flightId = localStorage.getItem("flightId");
  const name = document.getElementById("name").value;
  const seat = document.getElementById("seat").value;
  fetch(`${API}/bookings`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      flight_id: flightId,
      passenger_name: name,
      seat_no: seat
    })
  })
  .then(res => res.json())
  .then(data => {
    localStorage.setItem("pnr", data.pnr);
    window.location.href = `payment.html?pnr=${data.pnr}`;
  })
  .catch(err => alert("Booking failed"));
}
/* ---------------- CONFIRMATION ---------------- */
function loadReceipt() {
  const params = new URLSearchParams(window.location.search);
  const pnr = params.get("pnr");
  if (!pnr) {
    alert("Invalid booking reference");
    return;
  }
  fetch(`${API}/bookings/${pnr}`)
    .then(res => {
      if (!res.ok) throw new Error("Booking not found");
      return res.json();
    })
    .then(data => {
      document.getElementById("receipt").innerHTML = `
        <p><b>PNR:</b> ${data.pnr}</p>
        <p><b>Passenger:</b> ${data.passenger_name}</p>
        <p><b>Flight ID:</b> ${data.flight_id}</p>
        <p><b>Seat:</b> ${data.seat_no || "Auto Assigned"}</p>
        <p>
          <b>Status:</b>
          <span style="color:${data.status === "PAID" ? "green" : "red"}">
            ${data.status}
          </span>
        </p>
        <p><b>Price:</b> ₹ ${data.price}</p>
      `;
      window.receiptData = data;
    })
    .catch(() => {
      alert("Failed to load booking details");
    });
}
function downloadReceipt() {
  const dataStr =
    "data:text/json;charset=utf-8," +
    encodeURIComponent(JSON.stringify(window.receiptData, null, 2));
  const a = document.createElement("a");
  a.href = dataStr;
  a.download = `receipt_${window.receiptData.pnr}.json`;
  a.click();
}
/* ---------------- CANCEL BOOKING ---------------- */
function cancelBooking() {
  const pnr = document.getElementById("cancelPNR").value;
  fetch(`${API}/bookings/${pnr}`, { method: "DELETE" })
    .then(res => res.json())
    .then(data => {
      document.getElementById("cancelResult").innerText =
        data.message || "Booking cancelled";
    })
    .catch(() => alert("Cancellation failed"));
}
/* ---------------- PAYMENT ---------------- */
async function makePayment() {
  const params = new URLSearchParams(window.location.search);
  const pnr = params.get("pnr");
  if (!pnr) {
    alert("PNR missing. Please book again.");
    return;
  }
  try {
    const res = await fetch(`${API}/bookings/${pnr}/pay`, {
      method: "POST"
    });
    const data = await res.json();
    if (data.status === "PAID") {
      window.location.href = `confirmation.html?pnr=${pnr}`;
    } else {
      document.getElementById("paymentStatus").innerText =
        "❌ Payment Failed. Try again.";
    }
  } catch {
    document.getElementById("paymentStatus").innerText =
      "❌ Payment Error";
  }

}
