import React, { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup, Rectangle } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import * as d3 from "d3";
import L from "leaflet";
import "./App.css";
import hurricaneImage from "./assets/hurricane.png";

const hurricaneIcon = new L.DivIcon({
  html: `<img src="${hurricaneImage}" class="hurricane-icon spin" alt="Hurricane Icon" />`,
  className: "",
  iconSize: [20, 20],
  iconAnchor: [10, 10],
  popupAnchor: [0, -10],
});

const floridaBounds = [
  [24.5, -87.6],
  [31.0, -79.8],
];

const convertToEST = (dateStr, timeStr) => {
  if (!dateStr || !timeStr) return "Invalid Date/Time";

  const year = dateStr.substring(0, 4);
  const month = dateStr.substring(4, 6);
  const day = dateStr.substring(6, 8);
  const formattedDate = `${month}/${day}/${year}`;

  let utcHours = parseInt(timeStr.substring(0, 2), 10);
  const minutes = timeStr.substring(2, 4);

  let estHours = utcHours - 5;
  if (estHours < 0) estHours += 24;

  const ampm = estHours >= 12 ? "PM" : "AM";
  const displayHours = estHours % 12 === 0 ? 12 : estHours % 12;
  const formattedTime = `${displayHours}:${minutes} ${ampm} EST`;

  return `${formattedDate} ${formattedTime}`;
};

function App() {
  const [landfalls, setLandfalls] = useState([]);
  const [selectedYear, setSelectedYear] = useState("");
  const [years, setYears] = useState([]);
  const [usingL, setUsingL] = useState(true);

  // Function to Load CSV Data for the Selected Year
  const loadCSVData = (file, year) => {
    d3.csv(file).then((data) => {
      if (!data || data.length === 0) {
        console.error("CSV file is empty:", file);
        return;
      }

      const parsedData = data
        .filter((row) => row.Year.trim() === year)
        .map((row, index) => ({
          id: `${row.Year}-${row.Name}-${index}`,
          Year: row.Year.trim(),
          Hurricane: row.Name?.trim(),
          Date: row.Date.trim(),
          Time: row.Time.trim(),
          Latitude: parseFloat(row.Latitude),
          Longitude: parseFloat(row.Longitude),
          WindSpeed: row.Max_Wind_Speed,
        }));

      setLandfalls(parsedData);
    });
  };

  // Function to Load Years from CSV
  const loadYears = (file) => {
    d3.csv(file).then((data) => {
      if (!data || data.length === 0) {
        console.error("CSV file is empty:", file);
        return;
      }

      const uniqueYears = [...new Set(data.map((entry) => entry.Year.trim()))]
        .filter((year) => year >= 1900)
        .sort((a, b) => b - a);

      setYears(uniqueYears);
      setSelectedYear(uniqueYears[0] || "");
    });
  };

  useEffect(() => {
    const file = usingL ? "/florida_landfalls_using_L.csv" : "/florida_landfalls_without_using_L.csv";
    loadYears(file);
  }, [usingL]);

  useEffect(() => {
    if (selectedYear) {
      const file = usingL ? "/florida_landfalls_using_L.csv" : "/florida_landfalls_without_using_L.csv";
      loadCSVData(file, selectedYear);
    }
  }, [selectedYear, usingL]);

  return (
    <div>
      {/* Header Section */}
      <header className="header">
        <video autoPlay loop muted className="background-video">
          <source src="bg.mp4" type="video/mp4" />
        </video>
        <h1 className="header-title">Florida Hurricane Tracker</h1>
 

      {/* Warning Message (only when 'Without L' is selected) */}
      {!usingL && (
        <div className="warning-banner">
          Results may contain false positives due to approximations used in landfall detection
        </div>
      )}
     </header>
      {/* Toggle Switch */}
      <div className="toggle-container">
        <span className="toggle-label">Without L</span>
        <label className="toggle-switch">
          <input type="checkbox" checked={usingL} onChange={() => setUsingL(!usingL)} />
          <span className="slider"></span>
        </label>
        <span className="toggle-label">Using L</span>
      </div>

      {/* Year Selection Dropdown */}
      <div className="dropdown-container">
        <label htmlFor="year-select">Select Year: </label>
        <select
          id="year-select"
          value={selectedYear}
          onChange={(e) => setSelectedYear(e.target.value)}
        >
          {years.map((year) => (
            <option key={`year-${year}`} value={year}>
              {year}
            </option>
          ))}
        </select>
      </div>

      {/* Map Display */}
      <MapContainer center={[27.5, -83.5]} zoom={5} style={{ height: "600px", width: "100%" }}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        <Rectangle bounds={floridaBounds} pathOptions={{ color: "red", weight: 2 }} />

        {landfalls.map((entry) => (
        <Marker
          key={entry.id}
          position={[entry.Latitude, entry.Longitude]}
          icon={hurricaneIcon}
          eventHandlers={{
            mouseover: (e) => e.target.openPopup(),
            mouseout: (e) => e.target.closePopup(),
          }}
        >
          <Popup>
            <div className="popup-box">
              <div className="popup-title">{entry.Hurricane}</div>
              <div className="popup-date">
                Date & Time: {convertToEST(entry.Date, entry.Time)}
              </div>
              <div className="popup-wind">
                Wind Speed: {entry.WindSpeed} knots 🌪
              </div>
            </div>
          </Popup>
        </Marker>
      ))}
      </MapContainer>
    </div>
  );
}

export default App;
