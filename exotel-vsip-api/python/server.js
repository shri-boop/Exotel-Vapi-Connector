import express from "express";
import { createServer } from "http";
import { WebSocketServer } from "ws";
import fetch from "node-fetch";
import dotenv from "dotenv";

dotenv.config();

const app = express();
app.use(express.json());

const server = createServer(app);
const wss = new WebSocketServer({ server });

/* -------------------------
   HEALTH CHECK
-------------------------- */
app.get("/health", (req, res) => {
  res.json({ status: "ok" });
});

/* -------------------------
   INBOUND WEBSOCKET (Exotel → Vapi)
-------------------------- */
wss.on("connection", async (ws, req) => {
  console.log("Exotel connected via WebSocket");

  // Create Vapi streaming session
  const vapiResponse = await fetch(
    `https://api.vapi.ai/assistant/${process.env.VAPI_ASSISTANT_ID}/stream`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${process.env.VAPI_API_KEY}`,
        "Content-Type": "application/json"
      }
    }
  );

  const vapiWsUrl = (await vapiResponse.json()).url;
  const vapiWs = new WebSocket(vapiWsUrl);

  // Pipe Exotel → Vapi
  ws.on("message", (data) => {
    if (vapiWs.readyState === 1) {
      vapiWs.send(data);
    }
  });

  // Pipe Vapi → Exotel
  vapiWs.on("message", (data) => {
    if (ws.readyState === 1) {
      ws.send(data);
    }
  });

  ws.on("close", () => {
    vapiWs.close();
  });
});

/* -------------------------
   OUTBOUND CALL TRIGGER
-------------------------- */
app.post("/outbound", async (req, res) => {
  const { to } = req.body;

  const exotelResponse = await fetch(
    `https://api.exotel.com/v1/Accounts/${process.env.EXOTEL_ACCOUNT_SID}/Calls/connect.json`,
    {
      method: "POST",
      headers: {
        Authorization:
          "Basic " +
          Buffer.from(
            `${process.env.EXOTEL_API_KEY}:${process.env.EXOTEL_API_TOKEN}`
          ).toString("base64"),
        "Content-Type": "application/x-www-form-urlencoded"
      },
      body: new URLSearchParams({
        From: process.env.EXOTEL_VIRTUAL_NUMBER,
        To: to
      })
    }
  );

  const data = await exotelResponse.json();
  res.json(data);
});

/* -------------------------
   START SERVER
-------------------------- */
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Bridge running on port ${PORT}`);
});
