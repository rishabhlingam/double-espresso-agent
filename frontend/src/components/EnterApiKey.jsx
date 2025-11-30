import { useState } from "react";

export default function EnterApiKey({ onApiKeySaved }) {
  const [key, setKey] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();

    const trimmed = key.trim();
    if (!trimmed) {
      setError("Please enter your Google API key.");
      return;
    }

    // Save to localStorage
    localStorage.setItem("google_api_key", trimmed);

    // Clear error and notify App.jsx
    setError("");
    onApiKeySaved(trimmed);
  };

  return (
    <div className="flex h-screen w-full items-center justify-center bg-espresso text-cream px-6">
      <div className="bg-roast p-8 rounded-xl shadow-lg w-full max-w-md">

        <h1 className="text-2xl font-semibold mb-4 text-center">
          Enter Your Google API Key
        </h1>

        <p className="text-latte text-sm mb-6 text-center leading-relaxed">
          This demo uses your own Google Gemini API key.
          <br />
          Your key is <span className="text-caramel">never sent anywhere</span>
          except your browser → backend → Gemini.
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="password"
            className="w-full p-3 rounded-md bg-foam text-espresso placeholder-latte
                       border border-mocha focus:ring-2 focus:ring-caramel outline-none"
            placeholder="GOOGLE_API_KEY"
            value={key}
            onChange={(e) => setKey(e.target.value)}
          />

          {error && <div className="text-red-400 text-sm">{error}</div>}

          <button
            type="submit"
            className="w-full py-3 rounded-md bg-caramel text-espresso font-medium
                       hover:bg-gold transition"
          >
            Continue
          </button>
        </form>

      </div>
    </div>
  );
}
