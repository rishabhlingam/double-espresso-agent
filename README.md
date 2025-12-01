# **Double Espresso Agent** ☕☕

## **Problem Statement**

Learning through LLMs is meaningful only when users can stay focused on the core discussion, but in practice, conversations become bloated very quickly. Whenever an LLM introduces an unfamiliar term or concept, users naturally ask clarifying questions. These clarifications are rarely the main topic, yet they expand the chat thread dramatically and force the user to scroll repeatedly to relocate the original point. Over time, this creates friction that interrupts learning, breaks concentration, and often leads to abandoning the conversation altogether. Curiosity rarely follows a straight line; it branches. However, the traditional chat interface forces everything into a single vertical scroll, creating mental clutter and unnecessary navigation overhead. This issue affects anyone who uses LLMs as a study companion or research assistant, especially for complex subjects that require multiple layers of explanation which should not coexist in the same linear discussion.

## **Solution Statement**

Double Espresso Agent introduces a branching conversation experience that aligns with the natural flow of curiosity. Instead of forcing all follow-up questions into the main discussion, the user can fork the conversation at any moment and open a secondary chat panel dedicated entirely to auxiliary questions. This secondary thread inherits the context up to the point of forking, enabling the user to dive deeper into confusing terms, explore subtopics, or request step-by-step clarifications without inflating the primary discussion. The main chat remains concise and readable, while the secondary chat becomes a structured space for side explorations that remain persistent and accessible. Built on Google ADK’s multi-agent architecture, the system maintains consistency across both threads, keeps each agent context-aware, and provides a more organized, efficient, and cognitively lightweight learning experience.

---

# **Technical Architecture**

Double Espresso Agent is implemented as a two-layer system: a backend centered around Google ADK and persistent session storage, and a minimal React frontend that communicates via HTTP REST. The emphasis of the project is on the backend, where the orchestration, session management, and multi-agent logic reside.

The application is built using **Python 3.12**, **FastAPI**, **SQLAlchemy 2.0**, and **google-adk 0.3**. The system uses two persistent databases: `chat.db` for application-level chat and message storage, and `adk_sessions.db` for all ADK-managed session transcripts. This separation allows the application to maintain its own structured chat state while delegating LLM conversation history, state, and rehydration logic to Google ADK’s database session service.

### **Multi-Agent Design**

Two agents are defined in `agents.py` :

* **Primary Agent**
  A general conversational assistant with concise, structured response behavior. It handles the main linear conversation.

* **Secondary Agent**
  A clarification-focused agent that is activated whenever the user forks a message. It receives the parent message explicitly as contextual input, ensuring that explanations remain anchored to that specific point rather than the broader chat history.

Both agents use **Gemini 2.0 Flash** and are orchestrated through ADK runners.

### **ADK Session Management**

The core orchestration is implemented in `session_manager.py` , which encapsulates:

* Creation of new ADK sessions for primary or secondary chats
* Long-term session persistence through `DatabaseSessionService`
* Temporary per-request API key injection
* Running LLM calls through ADK’s event-streaming interface
* Extracting final responses from streamed events
* Session rehydration and continuation across multiple messages

Each chat record in the application database stores its associated ADK session ID, guaranteeing that every new message re-enters the exact same agent context maintained by ADK. This ensures deterministic continuation, stable memory, and coherent multi-turn reasoning.

### **Database Schema**

SQLAlchemy models are defined in `models.py`  with corresponding Pydantic schemas in `schemas.py` . The schema includes:

* **Chat Model**
  Contains chat type (primary or secondary), optional parent message, and a foreign-key reference to the ADK session ID.

* **Message Model**
  Stores each user or assistant message with timestamps and direct chat linkage.

The design ensures that primary and secondary chats remain structurally connected, while message-level forking is enforced through a uniqueness constraint on secondary chats per parent message.

The database engine and session factories are configured in `base.py` .


### **Observability**

Observability is integrated at multiple layers:

* All ADK events (partial and final) are logged with identifiers, authorship, and content.
* Metrics counters (e.g., `agent.calls`, `agent.calls.primary`, `agent.calls.secondary`) provide insight into system usage.
* Runner events expose timing, event flow, and model behavior for debugging and performance analysis.

This instrumentation allows the system to be monitored in real time and provides a foundation for future performance dashboards.

---

# **Frontend Overview**

The frontend, built with **React + Vite + Tailwind**, is intentionally light. It communicates exclusively over REST and maintains no internal LLM logic. The primary functionality is implemented in `useChatManager.js` , which handles chat loading, message posting, forking, and the simulation of incremental typing for assistant responses. All API calls are centralized in `api/chats.js` , which attaches the user-provided Gemini API key to each request.

---

# **Future Features**

- Context transfer back to the primary chat from the secondary chat. This will give the user a more continuous learning/reading experience when they resume conversation in the primary chat.

- The system could also learn from forking and questining behavior of the user and offer suggestive question when creating a secondary chat.

- Multimodal capabilities such as forking an image-based explanation or exploring diagrams in separate secondary conversation.