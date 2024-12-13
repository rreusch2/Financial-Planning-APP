import React, { useState } from 'react';
import { MessageSquare, Send, Loader } from 'lucide-react';

export function FinancialAssistant() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Will integrate with Gemini API later
    setLoading(true);
    setTimeout(() => setLoading(false), 1000);
  };

  return (
    <div className="bg-white rounded-xl shadow-sm p-6">
      <div className="flex items-center gap-3 mb-6">
        <MessageSquare className="h-6 w-6 text-indigo-600" />
        <div>
          <h3 className="text-xl font-semibold text-gray-900">Financial Assistant</h3>
          <p className="text-sm text-gray-500">Powered by Google Gemini</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="relative">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask anything about your finances..."
            className="w-full px-4 py-3 rounded-lg border border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          />
          <button
            type="submit"
            disabled={loading || !query}
            className="absolute right-2 top-1/2 -translate-y-1/2 p-2 text-indigo-600 hover:text-indigo-700 disabled:opacity-50"
          >
            {loading ? (
              <Loader className="h-5 w-5 animate-spin" />
            ) : (
              <Send className="h-5 w-5" />
            )}
          </button>
        </div>
      </form>

      <div className="mt-6 space-y-4">
        {/* Chat history will go here */}
      </div>
    </div>
  );
}