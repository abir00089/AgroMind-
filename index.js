const express = require("express");
const app = express();

app.use(express.json());

// Store latest sensor data
let sensorData = {};

// POST API (ESP32 sends data here)
app.post("/data", (req, res) => {
  sensorData = req.body;
  console.log("📡 Received Data:", sensorData);
  res.status(200).send("Data received successfully");
});

// GET API (for Streamlit / browser)
app.get("/", (req, res) => {
  res.json(sensorData);
});

// Optional: check server health
app.get("/health", (req, res) => {
  res.send("Server is running 🚀");
});

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
  console.log(`✅ Server running on port ${PORT}`);
});
