import express from "express";
import { WebSocketServer } from "ws";
import dotenv from "dotenv";
import fetch from "node-fetch";
import http from "http";

dotenv.config();

const app = express();
app.use(express.json());

const PORT = process.env.PORT || 3000;

const server = http.createServer(app);
const wss = new WebSocketServer({ server, path: "/exotel-ws" });

/* -----------------------
   HEALTH CHECK
------------------------*/
app.get("/health", (req, res) => {
  res.status(200).json({
    status: "ok",
    service: "Firepulse Exotel ↔ Vapi Bridge"
  });
});

/* -----------------------
   OUTBOUND CALL TRIGGER
------------------------*/
app.post("/outbound", async (req, res) => {
  const { to } = req.body;

  if (!to) {
    return res.status(400).json({ error: "Missing 'to' number" });
  }

  try {
    const exotelResponse = await fetch(
      `https://api.exotel.com/v1/Accounts/${process.env.EXOTEL_ACCOUNT_SID}/Calls/connect.json`,
      {
        method: "POST",
        headers: {
          Authorization:
            "Basic " +
            Buffer.from(
              process.env.EXOTEL_API_KEY +
                ":" +
                process.env.EXOTEL_API_TOKEN
            ).toString("base64"),
          "Content-Type": "application/x-www-form-urlencoded"
        },
        body: new URLSearchParams({
          From: process.env.EXOTEL_VIRTUAL_NUMBER,
          To: to,
          CallerId: process.env.EXOTEL_VIRTUAL_NUMBER
        })
      }
    );

    const data = await exotelResponse.json();
    res.json(data);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: "Outbound call failed" });
  }
});

/* -----------------------
   EXOTEL WEBSOCKET → VAPI
------------------------*/
wss.on("connection", (ws) => {
  console.log("Exotel connected via WebSocket");

  ws.on("message", async (message) => {
    console.log("Received from Exotel:", message.toString());

    // Here we would forward audio frames to Vapi streaming API
    // This is where the real audio bridge logic will go next
  });

  ws.on("close", () => {
    console.log("Exotel WebSocket closed");
  });
});

server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
