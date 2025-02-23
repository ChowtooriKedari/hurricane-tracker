import React, { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup, Polyline, Rectangle } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import axios from "axios";
import L from "leaflet";
import "./App.css"; // Import CSS for loader
import hurricaneImage from "./assets/hurricane.png"; // Local hurricane icon

const hurricaneIcon = new L.Icon({
  iconUrl: hurricaneImage,
  iconSize: [30, 30],
  iconAnchor: [15, 15],
  popupAnchor: [0, -15],
});

// Function to Convert Date & Time to EST
const convertToEST = (dateStr, timeStr) => {
  if (!dateStr || !timeStr) return "Invalid Date/Time";

  // Parse Date (YYYYMMDD → MM/DD/YYYY)
  const year = dateStr.substring(0, 4);
  const month = dateStr.substring(4, 6);
  const day = dateStr.substring(6, 8);
  const formattedDate = `${month}/${day}/${year}`;

  // Parse Time (HHMM → HH:MM AM/PM EST)
  const utcHours = parseInt(timeStr.substring(0, 2), 10);
  const minutes = timeStr.substring(2, 4);

  // Convert UTC to EST (UTC-5 or UTC-4 during DST)
  let estHours = utcHours - 5; // Convert from UTC to EST
  if (estHours < 0) estHours += 24; // Adjust for midnight wrap-around

  const ampm = estHours >= 12 ? "PM" : "AM";
  const displayHours = estHours % 12 === 0 ? 12 : estHours % 12; // Convert to 12-hour format

  const formattedTime = `${displayHours}:${minutes} ${ampm} EST`;

  return `${formattedDate} ${formattedTime}`;
};

const floridaBounds = [
  [24.5, -87.6], // Bottom-left (SW)
  [31.0, -79.8], // Top-right (NE)
];

function App() {
  const [hurricanes, setHurricanes] = useState([]);
  const [landfalls, setLandfalls] = useState([]);
  const [selectedYear, setSelectedYear] = useState("1900");
  const [years, setYears] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    axios.get("https://backend-api-2r7i.onrender.com/api/florida-landfalls").then((response) => {
      setLandfalls(response.data);

      // Extract unique years from landfalls data
      const uniqueYears = [...new Set(response.data.map((entry) => entry.Year))]
        .filter((year) => year >= 1900)
        .sort((a, b) => b - a);
      setYears(uniqueYears);
    });

    axios.get("https://backend-api-2r7i.onrender.com/api/hurricanes").then((response) => {
      setHurricanes(response.data);
      setLoading(false);
    });
  }, []);

  return (
    <div>
      <h1 style={{ textAlign: "center" }}>Hurricane Tracker</h1>

      {loading && (
        <div className="loader-container">
          <div className="spinner"></div>
          <p>Loading hurricane data...</p>
        </div>
      )}

      {!loading && (
        <div style={{ textAlign: "center", marginBottom: "10px" }}>
          <label htmlFor="year-select">Select Year: </label>
          <select id="year-select" value={selectedYear} onChange={(e) => setSelectedYear(e.target.value)}>
            {years.map((year) => (
              <option key={year} value={year}>
                {year}
              </option>
            ))}
          </select>
        </div>
      )}

      {!loading && (
        <MapContainer center={[27.5, -83.5]} zoom={5} style={{ height: "600px", width: "100%" }}>
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

          <Rectangle bounds={floridaBounds} pathOptions={{ color: "red", weight: 2 }} />

          {hurricanes
            .filter((storm) => storm.Year === selectedYear)
            .map((storm) =>
              storm.Entries.map((entry, index) => (
                <Polyline
                  key={`${storm.Name}-${storm.Year}-${storm.Cyclone_Number}-${entry.Date}-${entry.Time}-${entry.Latitude}-${entry.Longitude}-${entry.Max_Wind_Speed}-${index}`}
                  positions={storm.Entries.map((e) => [e.Latitude, e.Longitude])}
                  pathOptions={{ color: "blue", weight: 1 }}
                />
              ))
            )}

          {/* Florida Landfall Markers with Custom Icon & Hover Popup */}
          {landfalls
            .filter((entry) => entry.Year === selectedYear)
            .map((entry, index) => (
              <Marker
                key={index}
                position={[entry.Latitude, entry.Longitude]}
                icon={hurricaneIcon}
                eventHandlers={{
                  mouseover: (e) => e.target.openPopup(),
                  mouseout: (e) => e.target.closePopup(),
                }}
              >
                <Popup>
                  <strong>{entry.Hurricane}</strong> <br />
                  Date & Time: {convertToEST(entry.Date, entry.Time)} <br />
                  Wind Speed: {entry["Max Wind Speed (knots)"]} knots
                </Popup>
              </Marker>
            ))}
        </MapContainer>
      )}
    </div>
  );
}

export default App;
