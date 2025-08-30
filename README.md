<div align="center">

```
__      __    _        _      _   _   _ 
\ \    / /   /_\      /_\    | \ | | (_)
 \ \  / /   / _ \    / _ \   |  \| | | |
  \____/   /_/ \_\  /_/ \_\  |_|\__| |_|
```

# Vaani AI: Your Personal Conversational AI Assistant

**A bespoke voice assistant, crafted with Python, that understands, assists, and interacts with the digital world through the power of natural conversation.**

</div>

<p align="center">
  <img src="https://img.shields.io/badge/Challenge-30_Days_of_AI-blueviolet" alt="Challenge Badge">
  <img src="https://img.shields.io/badge/Python-3.9+-blue?logo=python" alt="Python Version">
  <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code Style: Black">
</p>

---

> Vaani AI is more than just code; it's a step towards a future where technology adapts to us. Born from the "30 Days of AI Voice Agents" challenge, Vaani can manage my schedule, provide real-time information from the web, and serve as a seamless bridge between me and my digital life.

### 🎬 Vaani AI in Action

![Demo of Vaani AI talking to me sarcastically](https://drive.google.com/file/d/1_fn-BRRXs2LLTjASlabphP7yTu89BxzX/view?usp=sharing)

---

### 🚀 The 29-Day Journey: From Silence to Symphony

This project is a testament to rapid, iterative development. Here’s how Vaani AI came to life, week by week.

<details>
<summary><strong>Click to Unfold the Development Chronicle</strong></summary>

* **🌱 Week 1 (Days 1-7): The Spark of Life.** The initial focus was on the fundamentals: giving Vaani a voice and ears. We established the core audio pipeline, capturing microphone input and generating speech. The week culminated in a magical moment: the first successful, end-to-end conversation where Vaani listened to a sentence and spoke a response.

* **🧠 Week 2 (Days 8-15): The Dawn of Intelligence.** This week, we gave Vaani a mind. By integrating a state-of-the-art Large Language Model (LLM), Vaani transitioned from a simple script to a thinking entity. We meticulously crafted its system prompt to define its personality—helpful, concise, and professional—and implemented conversational memory to maintain context.

* **👂 Week 3 (Days 16-22): Achieving Awareness.** To make Vaani a true assistant, it needed to be present but unobtrusive. We integrated a low-resource wake word engine ("Hey, Vaani"), allowing it to listen passively. This week was a deep dive into optimization, relentlessly tuning the system to minimize latency for fluid, real-time interactions.

* **🛠️ Week 4 (Days 23-29): Granting Superpowers.** The final and most transformative week. We unlocked Vaani's ability to act in the real world through **Function Calling**. This powerful technique allows the LLM to request the execution of custom Python code, enabling Vaani to connect to external APIs and perform meaningful tasks. This is where Vaani learned to check the weather in Indore, manage my Google Calendar, and more.

</details>

### ✨ Core Capabilities

* **🗣️ Fluid Conversation:** Employs cutting-edge STT and TTS engines for interactions that feel natural and immediate.
* **🧠 Context-Aware Intelligence:** Leverages a powerful LLM to understand nuances, recall previous parts of the conversation, and provide insightful responses.
* **👂 Always-On Wake Word:** Stays dormant until called with "Hey, Vaani," ensuring privacy and responsiveness.
* **🎭 Customizable Persona:** Vaani's personality can be easily sculpted via the main system prompt, from a formal assistant to a witty companion.

### 🔧 Advanced Integrations (The "Superpowers")

Vaani uses a "toolbelt" of functions to interact with the outside world:

* **🌦️ Real-Time Meteorologist:** Connects to live weather APIs.
    * *Example: "Hey Vaani, will I need an umbrella for my evening walk in Indore?"*
* **📅 Proactive Calendar Assistant:** Integrates directly with Google Calendar API.
    * *Example: "Hey Vaani, add 'Project discussion with the team' to my calendar for tomorrow at 4 PM."*
* **💡 Smart Home Conductor (Optional):** Designed to be extensible for APIs like Philips Hue or Home Assistant.
    * *Example: "Hey Vaani, dim the study lights to 50%."*

---

### 💻 The Technology Stack

Vaani is built on a foundation of powerful and modern technologies.

| Category      | Technology                                    | Purpose                                                 |
| :------------ | :-------------------------------------------- | :------------------------------------------------------ |
| **Core Logic**| Python 3.9+                                   | The backbone of the entire application.                 |
| **The Brain** | OpenAI GPT-4o / Google Gemini API               | For advanced understanding, reasoning, and tool use.    |
| **Voice I/O** | OpenAI Whisper (STT) & ElevenLabs (TTS)       | For best-in-class speech recognition and lifelike voice.|
| **Awareness** | Picovoice Porcupine                           | For highly accurate, on-device wake word detection.     |
| **Tooling** | PyAudio, python-dotenv, google-api-python-client | For audio handling, config management, and API access.|

---

### ⚡ Getting Started

Ready to bring Vaani AI to life on your own machine?

#### **1. Clone the Repository**
```bash
git clone [https://github.com/your-username/vaani-ai.git](https://github.com/your-username/vaani-ai.git)
cd vaani-ai
```

#### **2. Set Up the Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### **3. Configure Your Secrets**
Create a `.env` file in the root directory and populate it with your API keys, using `.env.example` as a template.
```ini
# .env - Your secret keys
OPENAI_API_KEY="sk-..."
ELEVENLABS_API_KEY="..."
PICOVOICE_ACCESS_KEY="..."
GOOGLE_CREDENTIALS_PATH="credentials.json"
```

#### **4. Run Vaani AI**
```bash
python main.py
```
Wait for the "Listening..." prompt, say "Hey, Vaani," and start your conversation!

---
<div align="center">
Made with ❤️ in Indore, India.
</div>
