import express from "express";
import { chatRouter } from "./routes/chat";
import { config } from "./config";

const app = express();

app.use(express.json());

app.get("/health", (_req, res) => {
    res.json({status: "ok"});
});

app.use("/v1", chatRouter);

app.listen(config.port, () => {
    console.log(
        `Gateway listening on http://localhost:${config.port} (provider: ${config.provider})`
    );
});