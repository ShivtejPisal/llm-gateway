import { config } from "../config";
import { groqProvider } from "./groq";
import { mockProvider } from "./mock";
import { Provider } from "./types";


export const provider: Provider = 
    config.provider === "groq" ? groqProvider : mockProvider