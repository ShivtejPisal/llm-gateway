import OpenAI from "openai";
import { config } from "../config";
import { CompletionResult, Provider } from "./types";

const client = new OpenAI({
    apiKey: config.groqApiKey,
    baseURL: "https://api.groq.com/openai/v1",
});

export const groqProvider: Provider = {
    async complete(prompt: string): Promise<CompletionResult>{
        const response = await client.chat.completions.create({
            model: config.model,
            messages: [{ role: "user", content: prompt}],
            temperature: 0,
        });

        return {
            text: response.choices[0]?.message?.content ?? "",
            promptTokens: response.usage?.prompt_tokens ?? 0,
            completionTokens: response.usage?.completion_tokens ?? 0,
            model: response.model,
        };
    },
};