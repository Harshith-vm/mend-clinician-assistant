"""
therapy_assistant.py
====================
Core GraphRAG therapy assistant. This is the central orchestrator.

Pipeline (per turn):
  1. CrisisDetector  → short-circuit if crisis detected
  2. TherapyGraphSearch → vector search + graph traversal → KG context
  3. PromptBuilder   → assemble system prompt + KG context + memory + user msg
  4. LLM call        → model-agnostic via pluggable adapter
  5. SessionMemory   → store turn, persist if configured

MODEL-AGNOSTIC DESIGN
---------------------
The GraphRAG layer (steps 1-3) never changes regardless of which LLM you use.
To integrate a different LLM, simply pass a different adapter to TherapyAssistant:

    # Ollama (local)
    assistant = TherapyAssistant(llm=OllamaAdapter(model="llama3.2"))

    # OpenAI
    assistant = TherapyAssistant(llm=OpenAIAdapter(api_key="...", model="gpt-4o"))

    # Gemini
    assistant = TherapyAssistant(llm=GeminiAdapter(api_key="...", model="gemini-pro"))

    # Your own LLM — just implement BaseLLMAdapter
    assistant = TherapyAssistant(llm=YourCustomAdapter())

PUBLIC API
----------
    result = assistant.chat(user_message, session_id="patient_001")
    print(result.response)         # LLM-generated response text
    print(result.kg_context)       # Clinical context used from the KG
    print(result.was_crisis)       # True if crisis was detected
"""

import sys
import textwrap
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

sys.path.insert(0, str(__file__).rsplit("\\", 2)[0])  # make api/ imports work

from api.crisis_detector import detect as detect_crisis
from api.session_memory import SessionMemory
from api.graph_semantic_search import TherapyGraphSearch

# ── Clinical System Prompt ──────────────────────────────────────────────────────
SYSTEM_PROMPT = """\
You are a compassionate, evidence-based mental health support assistant.
You are not a licensed therapist and you never claim to be one.
Your role is to listen with empathy, validate the person's feelings, and suggest
healthy, evidence-based coping strategies drawn from the clinical knowledge context
provided below.

STRICT RULES:
1. NEVER diagnose a mental health condition.
2. NEVER recommend specific medications or dosages.
3. ALWAYS validate and acknowledge feelings BEFORE offering any suggestion.
4. Use techniques rooted in CBT, DBT, and motivational interviewing naturally — 
   never quote technique names directly to the patient.
5. Keep responses warm, human, and conversational (3–5 sentences max).
6. If the patient seems to be in crisis, express care and direct them to professionals.
7. End each response with one open, curious question to keep the conversation going.

CLINICAL CONTEXT FROM KNOWLEDGE GRAPH (use this to ground your response):
{kg_context}

IMPORTANT: The clinical context above is for YOUR grounding only — do not recite
node names or clinical labels to the patient. Translate them into natural language.
"""


# ── Data classes ────────────────────────────────────────────────────────────────
@dataclass
class ChatResult:
    response: str
    kg_context: dict = field(default_factory=dict)
    was_crisis: bool = False
    session_id: str = "default"


# ── LLM Adapter Interface ───────────────────────────────────────────────────────
class BaseLLMAdapter(ABC):
    """
    Minimal interface that any LLM adapter must implement.
    Receives a list of dicts: [{"role": "system"|"user"|"assistant", "content": str}]
    Returns the response as a plain string.
    """

    @abstractmethod
    def generate(self, messages: list[dict]) -> str:
        ...

    def stream(self, messages: list[dict]):
        """
        Yields response tokens one by one.
        Default implementation just wraps generate() for adapters that don't
        support native streaming — override for proper token-by-token streaming.
        """
        yield self.generate(messages)

    @property
    @abstractmethod
    def model_name(self) -> str:
        ...


# ── Built-in Adapters ───────────────────────────────────────────────────────────

class OllamaAdapter(BaseLLMAdapter):
    """
    Local LLM via Ollama. Requires: pip install ollama
    and Ollama installed at https://ollama.com
    """
    def __init__(self, model: str = "llama3.1:8b", host: str = "http://localhost:11434"):
        try:
            import ollama
            self._client = ollama.Client(host=host)
            self._model = model
        except ImportError:
            raise ImportError("Run: pip install ollama")

    @property
    def model_name(self) -> str:
        return f"ollama/{self._model}"

    # Sampling tuned for warm, varied therapeutic language (less repetition,
    # fewer stock openers like "It sounds like...").
    _GEN_OPTIONS = {
        "temperature": 0.8,
        "top_p": 0.9,
        "repeat_penalty": 1.2,   # discourage repeated phrases/openers
        "repeat_last_n": 256,    # ...across recent context, not just this reply
    }

    def generate(self, messages: list[dict]) -> str:
        resp = self._client.chat(
            model=self._model, messages=messages, options=self._GEN_OPTIONS
        )
        return resp.message.content.strip()

    def stream(self, messages: list[dict]):
        """
        Simulates streaming for Ollama by yielding word-by-word from a normal
        generate() call.  We do NOT use stream=True because it triggers a
        stack-buffer overrun in llama-server on some CUDA setups.
        The GPU still runs the full inference — only the delivery is simulated.
        """
        full = self.generate(messages)
        # Yield word-by-word so the UI shows a typewriter effect
        for word in full.split(" "):
            yield word + " "



class OpenAIAdapter(BaseLLMAdapter):
    """
    OpenAI API. Requires: pip install openai
    """
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        try:
            from openai import OpenAI
            self._client = OpenAI(api_key=api_key)
            self._model = model
        except ImportError:
            raise ImportError("Run: pip install openai")

    @property
    def model_name(self) -> str:
        return f"openai/{self._model}"

    def generate(self, messages: list[dict]) -> str:
        resp = self._client.chat.completions.create(
            model=self._model, messages=messages, temperature=0.7
        )
        return resp.choices[0].message.content.strip()

    def stream(self, messages: list[dict]):
        """Stream tokens from OpenAI."""
        for chunk in self._client.chat.completions.create(
            model=self._model, messages=messages, temperature=0.7, stream=True
        ):
            token = chunk.choices[0].delta.content
            if token:
                yield token


class GeminiAdapter(BaseLLMAdapter):
    """
    Google Gemini API. Requires: pip install google-generativeai
    """
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self._model_name = model
            self._genai = genai
        except ImportError:
            raise ImportError("Run: pip install google-generativeai")

    @property
    def model_name(self) -> str:
        return f"gemini/{self._model_name}"

    def generate(self, messages: list[dict]) -> str:
        model = self._genai.GenerativeModel(self._model_name)
        # Convert role-based format to Gemini's expected format
        history = []
        prompt = ""
        for m in messages:
            if m["role"] == "system":
                prompt = m["content"] + "\n\n"
            elif m["role"] == "user":
                history.append({"role": "user", "parts": [m["content"]]})
            elif m["role"] == "assistant":
                history.append({"role": "model", "parts": [m["content"]]})
        chat = model.start_chat(history=history[:-1] if history else [])
        last_user = history[-1]["parts"][0] if history else prompt
        resp = chat.send_message(prompt + last_user)
        return resp.text.strip()

    def stream(self, messages: list[dict]):
        """Stream tokens from Gemini."""
        model = self._genai.GenerativeModel(self._model_name)
        history = []
        prompt = ""
        for m in messages:
            if m["role"] == "system":
                prompt = m["content"] + "\n\n"
            elif m["role"] == "user":
                history.append({"role": "user", "parts": [m["content"]]})
            elif m["role"] == "assistant":
                history.append({"role": "model", "parts": [m["content"]]})
        chat = model.start_chat(history=history[:-1] if history else [])
        last_user = history[-1]["parts"][0] if history else prompt
        for chunk in chat.send_message(prompt + last_user, stream=True):
            if chunk.text:
                yield chunk.text


class AnthropicAdapter(BaseLLMAdapter):
    """
    Anthropic API (model set via ANTHROPIC_MODEL). Requires: pip install anthropic
    """
    def __init__(self, api_key: str, model: str = ""):
        try:
            import anthropic
            self._client = anthropic.Anthropic(api_key=api_key)
            self._model = model
        except ImportError:
            raise ImportError("Run: pip install anthropic")

    @property
    def model_name(self) -> str:
        return f"anthropic/{self._model}"

    def generate(self, messages: list[dict]) -> str:
        system = next((m["content"] for m in messages if m["role"] == "system"), "")
        chat_msgs = [m for m in messages if m["role"] != "system"]
        resp = self._client.messages.create(
            model=self._model,
            max_tokens=1024,
            system=system,
            messages=chat_msgs,
        )
        return resp.content[0].text.strip()

    def stream(self, messages: list[dict]):
        """Stream tokens from Anthropic."""
        system = next((m["content"] for m in messages if m["role"] == "system"), "")
        chat_msgs = [m for m in messages if m["role"] != "system"]
        with self._client.messages.stream(
            model=self._model,
            max_tokens=1024,
            system=system,
            messages=chat_msgs,
        ) as s:
            for token in s.text_stream:
                yield token


# ── Core Assistant ──────────────────────────────────────────────────────────────
class TherapyAssistant:
    """
    The main GraphRAG therapy assistant.

    Parameters
    ----------
    llm : BaseLLMAdapter
        Any LLM adapter (Ollama, OpenAI, Gemini, Anthropic, or custom).
    neo4j_uri : str
    neo4j_user : str
    neo4j_password : str
    top_k : int
        Number of KG sessions to retrieve per query.
    similarity_threshold : float
        Minimum cosine similarity to accept a KG result.
    max_memory_turns : int
        Number of conversation turns to keep in memory.
    sessions_dir : str | None
        Directory to persist session JSON files. None = no persistence.
    """

    def __init__(
        self,
        llm: BaseLLMAdapter,
        neo4j_uri: str = "bolt://localhost:7687",
        neo4j_user: str = "neo4j",
        neo4j_password: str = "neo4jpassword",
        top_k: int = 3,
        similarity_threshold: float = 0.35,
        max_memory_turns: int = 8,
        sessions_dir: str | None = None,
    ):
        self.llm = llm
        self.top_k = top_k
        self.threshold = similarity_threshold
        self.max_turns = max_memory_turns
        self.sessions_dir = sessions_dir

        print(f"[GraphRAG] Loading knowledge graph search engine...")
        self.kg = TherapyGraphSearch(uri=neo4j_uri, user=neo4j_user, password=neo4j_password)
        print(f"[GraphRAG] LLM adapter: {llm.model_name}")
        print(f"[GraphRAG] Ready.\n")

        # Per-session memory store
        self._memories: dict[str, SessionMemory] = {}

    def _get_memory(self, session_id: str) -> SessionMemory:
        if session_id not in self._memories:
            persist = None
            if self.sessions_dir:
                import os
                persist = os.path.join(self.sessions_dir, f"{session_id}.json")
            self._memories[session_id] = SessionMemory(
                max_turns=self.max_turns,
                session_id=session_id,
                persist_path=persist,
            )
        return self._memories[session_id]

    def _build_kg_context_string(self, results: list[dict]) -> str:
        """Formats KG search results into a compact clinical context block."""
        if not results:
            return "No specific clinical context retrieved for this query."

        lines = []
        seen_disorders, seen_symptoms, seen_emotions = set(), set(), set()
        seen_techniques, seen_contexts, seen_behaviours = set(), set(), set()

        for r in results:
            ctx = r.get("graph_context", {})
            seen_disorders.update(ctx.get("Disorders", []))
            seen_symptoms.update(ctx.get("Symptoms", []))
            seen_emotions.update(ctx.get("Emotions", []))
            seen_techniques.update(ctx.get("Techniques", []))
            seen_contexts.update(ctx.get("Contexts", []))
            seen_behaviours.update(ctx.get("Behaviours", []))

        if seen_disorders:
            lines.append(f"Clinical presentations: {', '.join(sorted(seen_disorders))}")
        if seen_symptoms:
            lines.append(f"Reported symptoms: {', '.join(sorted(seen_symptoms))}")
        if seen_emotions:
            lines.append(f"Emotional states: {', '.join(sorted(seen_emotions))}")
        if seen_techniques:
            lines.append(f"Evidence-based techniques: {', '.join(sorted(seen_techniques))}")
        if seen_contexts:
            lines.append(f"Contextual factors: {', '.join(sorted(seen_contexts))}")
        if seen_behaviours:
            lines.append(f"Observed behaviours: {', '.join(sorted(seen_behaviours))}")

        return "\n".join(lines) if lines else "No specific clinical context retrieved."

    def chat(self, user_message: str, session_id: str = "default") -> ChatResult:
        """
        Process one patient message and return a ChatResult.
        This is the single method to call for integration.
        """
        # ── Step 1: Crisis check ──────────────────────────────────────────────
        crisis = detect_crisis(user_message)
        if crisis.is_crisis:
            memory = self._get_memory(session_id)
            memory.add_user(user_message)
            memory.add_assistant(crisis.response)
            if self.sessions_dir:
                memory.save()
            return ChatResult(
                response=crisis.response,
                kg_context={},
                was_crisis=True,
                session_id=session_id,
            )

        # ── Step 2: KG retrieval ──────────────────────────────────────────────
        kg_results = self.kg.search(
            user_message, top_k=self.top_k, similarity_threshold=self.threshold
        )
        kg_context_str = self._build_kg_context_string(kg_results)

        # Collect raw context dict for caller
        raw_context = {
            "Disorders":  sorted({d for r in kg_results for d in r["graph_context"]["Disorders"]}),
            "Symptoms":   sorted({s for r in kg_results for s in r["graph_context"]["Symptoms"]}),
            "Emotions":   sorted({e for r in kg_results for e in r["graph_context"]["Emotions"]}),
            "Techniques": sorted({t for r in kg_results for t in r["graph_context"]["Techniques"]}),
            "Contexts":   sorted({c for r in kg_results for c in r["graph_context"]["Contexts"]}),
            "Behaviours": sorted({b for r in kg_results for b in r["graph_context"]["Behaviours"]}),
        }

        # ── Step 3: Build prompt with memory ─────────────────────────────────
        system = SYSTEM_PROMPT.format(kg_context=kg_context_str)
        memory = self._get_memory(session_id)
        memory.add_user(user_message)
        messages = memory.get_messages(system_prompt=system)

        # ── Step 4: LLM call ──────────────────────────────────────────────────
        response_text = self.llm.generate(messages)

        # ── Step 5: Store response in memory ──────────────────────────────────
        memory.add_assistant(response_text)
        if self.sessions_dir:
            memory.save()

        return ChatResult(
            response=response_text,
            kg_context=raw_context,
            was_crisis=False,
            session_id=session_id,
        )

    def close(self):
        self.kg.close()


# ── Interactive CLI (for standalone testing) ────────────────────────────────────
if __name__ == "__main__":
    import os

    print("=" * 60)
    print("  Mental Health Support Assistant (GraphRAG)")
    print("=" * 60)
    print("\nChoose LLM backend:")
    print("  1. Ollama / llama3.2 (local, free)")
    print("  2. Ollama / mistral  (local, free, larger)")
    print("  3. OpenAI  (requires OPENAI_API_KEY env var)")
    print("  4. Gemini  (requires GEMINI_API_KEY env var)")
    choice = input("\nEnter choice [1]: ").strip() or "1"

    if choice == "1":
        adapter = OllamaAdapter(model="llama3.2")
    elif choice == "2":
        adapter = OllamaAdapter(model="mistral")
    elif choice == "3":
        key = os.environ.get("OPENAI_API_KEY", input("OpenAI API key: "))
        adapter = OpenAIAdapter(api_key=key)
    elif choice == "4":
        key = os.environ.get("GEMINI_API_KEY", input("Gemini API key: "))
        adapter = GeminiAdapter(api_key=key)
    else:
        print("Invalid choice, defaulting to Ollama/llama3.2")
        adapter = OllamaAdapter(model="llama3.2")

    assistant = TherapyAssistant(llm=adapter)
    session_id = f"cli_{os.getpid()}"

    print("\nType your message (or 'quit' / 'clear' to exit/reset).\n")
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            break
        if user_input.lower() == "clear":
            assistant._get_memory(session_id).clear()
            print("[Memory cleared]\n")
            continue

        result = assistant.chat(user_input, session_id=session_id)

        print(f"\nAssistant: {result.response}")

        if result.kg_context.get("Disorders") or result.kg_context.get("Emotions"):
            print("\n  [KG Context]")
            for k, v in result.kg_context.items():
                if v:
                    print(f"    {k}: {', '.join(v)}")
        print()

    assistant.close()
    print("\nSession ended. Take care.")
