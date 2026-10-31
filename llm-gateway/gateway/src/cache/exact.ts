import Redis from "ioredis";
import { config } from "../config";
import { createHash } from "crypto";
import { CompletionResult } from "../providers/types";


const redis = new Redis(config.redisUrl);

redis.on("error", (err) => {
    console.error("Redis Error: ", err.message);
});

export function buildKey(prompt: string) : string {
    const material = JSON.stringify({
        prompt: prompt.trim(),
        model: config.model,
        temperature: 0
    });

    const digest = createHash("sha256").update(material).digest("hex");
    return `exact:${digest}`;
}


export async function get(key: string): Promise<CompletionResult | null> {
    try {
        const raw = await redis.get(key);
        return raw ? (JSON.parse(raw) as CompletionResult) : null;
    } catch (err) {
        console.error("Cache read failed: ", err);
        return null;
    }
}

export async function set(
    key: string,
    value: CompletionResult
) : Promise<void> {
    try{ 
        await redis.set(key, JSON.stringify(value), "EX", config.cacheTtlSeconds);
    } catch(err) {
        console.error("Cache write failed: ", err);
    }
}

