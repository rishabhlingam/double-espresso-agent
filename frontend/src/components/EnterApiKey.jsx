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
    sessionStorage.setItem("google_api_key", trimmed);
    onApiKeySaved(trimmed);
  };

  return (
    <div className="bg-roast p-8 rounded-xl shadow-xl w-full max-w-md text-cream">

      <h1 className="text-2xl font-semibold mb-4 text-center">
        Enter Your Google API Key
      </h1>

      <p className="text-latte text-sm mb-6 text-center leading-relaxed">
        This demo uses your own Google Gemini API key.
        <br />
        Your key is <span className="text-caramel">stored only in your
        browser’s session storage</span> and is deleted when the tab is closed.
      </p>

      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="password"
          className="w-full p-3 rounded-md bg-foam text-espresso border border-mocha
                     focus:ring-2 focus:ring-caramel outline-none"
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
  );
}
