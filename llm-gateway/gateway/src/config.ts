import dotenv from "dotenv";

// .env lives at the repo root; npm scripts run with cwd = gateway/
dotenv.config({ path: "../.env" });

export const config = {
  port: Number(process.env.PORT ?? 8080),
  provider: (process.env.PROVIDER ?? "mock") as "mock" | "groq",
  groqApiKey: process.env.GROQ_API_KEY ?? "",
  model: process.env.MODEL ?? "openai/gpt-oss-120b",
  mockLatencyMs: Number(process.env.MOCK_LATENCY_MS ?? 800),
  redisUrl: process.env.REDIS_URL ?? "redis://localhost:6379",
  cacheTtlSeconds: Number(process.env.CACHE_TTL_SECONDS ?? 86400),
};

if (config.provider === "groq" && !config.groqApiKey) {
  throw new Error("PROVIDER=groq requires GROQ_API_KEY to be set");
}