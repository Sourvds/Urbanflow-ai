import { useState } from 'react'
import { motion } from 'framer-motion'
import { Send, Bot, User } from 'lucide-react'
import { chatbot } from '../api/client'

export default function Chatbot() {
  const [messages, setMessages] = useState([
    { role: 'bot', text: 'UrbanFlow AI Assistant online. Ask about electricity, traffic, water, alerts, or city efficiency.' },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [suggestions, setSuggestions] = useState([])

  const send = async (text) => {
    if (!text.trim()) return
    setMessages((m) => [...m, { role: 'user', text }])
    setInput('')
    setLoading(true)
    try {
      const { data } = await chatbot.ask(text)
      setMessages((m) => [...m, { role: 'bot', text: data.reply }])
      setSuggestions(data.suggestions || [])
    } catch {
      setMessages((m) => [...m, { role: 'bot', text: 'Connection error. Ensure the API is running.' }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto space-y-4">
      <div>
        <h1 className="font-display text-2xl font-bold flex items-center gap-2">
          <Bot className="text-cyber-500" /> AI Operations Assistant
        </h1>
        <p className="text-gray-500 mt-1">Natural language queries for city operators</p>
      </div>
      <div className="glass flex flex-col h-[calc(100vh-220px)] min-h-[400px]">
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((m, i) => (
            <div key={i} className={`flex gap-3 ${m.role === 'user' ? 'flex-row-reverse' : ''}`}>
              <div className={`p-2 rounded-lg shrink-0 ${m.role === 'bot' ? 'bg-cyber-500/20 text-cyber-500' : 'bg-purple-500/20 text-purple-400'}`}>
                {m.role === 'bot' ? <Bot size={18} /> : <User size={18} />}
              </div>
              <div className={`p-3 rounded-2xl max-w-[80%] text-sm ${m.role === 'bot' ? 'bg-white/5' : 'bg-cyber-500/15'}`}>
                {m.text}
              </div>
            </div>
          ))}
          {loading && <p className="text-gray-500 text-sm animate-pulse">Analyzing city data...</p>}
        </div>
        {suggestions.length > 0 && (
          <div className="px-4 pb-2 flex flex-wrap gap-2">
            {suggestions.map((s) => (
              <button key={s} onClick={() => send(s)} className="text-xs px-3 py-1 rounded-full bg-white/5 text-cyber-400 hover:bg-cyber-500/10">
                {s}
              </button>
            ))}
          </div>
        )}
        <form onSubmit={(e) => { e.preventDefault(); send(input) }} className="p-4 border-t border-white/5 flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about city resources..."
            className="flex-1 px-4 py-3 rounded-xl bg-white/5 border border-white/10 outline-none focus:border-cyber-500/50"
          />
          <button type="submit" className="btn-primary p-3" disabled={loading}>
            <Send size={20} />
          </button>
        </form>
      </div>
    </div>
  )
}
