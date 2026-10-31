import { response, Router } from "express";
import { provider } from "../providers";
import *  as exactCache from "../cache/exact";

export const chatRouter = Router();

chatRouter.post("/chat", async (req, res) => {
    const {prompt} = req.body ?? {};

    if(typeof prompt !== "string" || prompt.trim().length === 0) {
        return res
            .status(400)
            .json({error: "Body must include a non-empt 'prompt' string "});
    }

    const startedAt = Date.now();
    const key = exactCache.buildKey(prompt);

    const cached = await exactCache.get(key);
    if(cached) {
        return res.json({
            response: cached.text,
            cache: "exact",
            latency_ms: Date.now() - startedAt,
            model: cached.model,
            usage: {
                prompt_tokens: cached.promptTokens,
                completion_tokens:cached.completionTokens
            }
        })
    }
    
    try{
        const result = await provider.complete(prompt);
        await exactCache.set(key, result);
        
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
        const detail = err instanceof Error ? err.message : String(err);
        console.log("Provider call failed:", detail);
        return res.status(502).json({
            error: "Upstream provider call failed",
            detail,
        });
    }
});