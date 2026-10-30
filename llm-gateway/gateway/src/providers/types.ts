export interface CompletionResult {
    text: string;
    promptTokens: number;
    completionTokens: number;
    model: string;
}

export interface Provider {
    complete(prompt: string): Promise<CompletionResult>;
}