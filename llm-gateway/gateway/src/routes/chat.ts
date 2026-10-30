import { response, Router } from "express";
import { provider } from "../providers";


export const chatRouter = Router();

chatRouter.post("/chat", async (req, res) => {
    const {prompt} = req.body ?? {};

    if(typeof prompt !== "string" || prompt.trim().length === 0) {
        return res
            .status(400)
            .json({error: "Body must include a non-empt 'prompt' string "});
    }

    const startedAt = Date.now();

    try{
        const result = await provider.complete(prompt);
        
        return res.json({
            response: result.text,
            cache: "miss",
            latency_ms: Date.now() - startedAt,
            model: result.model,
            usage: {
                prompt_tokens: result.promptTokens,
                completion_tokens: result.completionTokens,
            },
        });
    } catch (err) {
        console.log("Provider call failed:", err);
        return res.status(502).json({error: "Upstream provider call failed"});
    }
});