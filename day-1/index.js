const axios = require('axios');

class OllamaChat {
    constructor() {
        this.OLLAMA_URL = "http://localhost:11434/api/generate";
        this.memory = new Memory();
        this.messages = [{ role: "assistant", content: "Hello! How can I help you today?" }];
    }

    async queryOllama(prompt) {
        try {
            const response = await axios.post(this.OLLAMA_URL, {
                model: "mistral",
                prompt: prompt,
                stream: true
            }, {
                headers: { "Content-Type": "application/json" },
                responseType: 'stream'
            });

            let fullResponse = "";

            return new Promise((resolve, reject) => {
                response.data.on('data', chunk => {
                    try {
                        // Split chunk data by newlines as we might receive multiple JSON objects
                        const lines = chunk.toString().split('\n');
                        
                        lines.forEach(line => {
                            if (line.trim()) {
                                const jsonResponse = JSON.parse(line);
                                const responseText = jsonResponse.response || "";
                                fullResponse += responseText;

                                // If streaming to console (for demonstration)
                                process.stdout.write(responseText);

                                if (jsonResponse.done) {
                                    // Store in memory
                                    this.memory.add(prompt, fullResponse);
                                    this.messages.push(
                                        { role: "user", content: prompt },
                                        { role: "assistant", content: fullResponse }
                                    );
                                    resolve(fullResponse);
                                }
                            }
                        });
                    } catch (error) {
                        reject(error);
                    }
                });

                response.data.on('error', error => {
                    reject(error);
                });
            });

        } catch (error) {
            console.error(`Error: ${error.message}`);
            throw error;
        }
    }

    getMessages() {
        return this.messages;
    }

    getMemory() {
        return this.memory;
    }
}

module.exports = OllamaChat;

// Example usage:
// const chat = new OllamaChat();
// chat.queryOllama("What is the capital of France?")
//     .then(response => console.log("\nFinal response:", response))
//     .catch(error => console.error("Error:", error));