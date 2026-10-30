import { CompletionResult, Provider } from "./types";
import { config } from "../config";
import { createHash } from "node:crypto";


function sleep(ms:number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

export const mockProvider: Provider = {
    async complete(prompt: string): Promise<CompletionResult>{
        await sleep(config.mockLatencyMs);

        const fingerprint = createHash("sha256")
            .update(prompt)
            .digest("hex")
            .slice(0, 8);

        return {
            text: `[mock: ${fingerprint}] Response to: ${prompt}`,
            promptTokens: Math.ceil(prompt.length / 4),
            completionTokens: 32,
            model: "mock-v1",
        };
    },
};