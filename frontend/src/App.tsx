import React from 'react'
import InteractionForm from './components/InteractionForm'
import ChatPanel from './components/ChatPanel'
import { Activity } from 'lucide-react'

export default function App() {
  return (
    <div className="h-screen flex flex-col bg-gray-100 font-sans antialiased">
      <header className="bg-white border-b border-gray-200 px-6 py-3 shrink-0">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-primary-600 to-teal-500 rounded-lg flex items-center justify-center shadow-sm">
              <Activity size={18} className="text-white" />
            </div>
            <div>
              <h1 className="text-base font-bold text-gray-900 tracking-tight">HCP Interaction Logger</h1>
              <p className="text-[11px] text-gray-500">AI-First CRM Module</p>
            </div>
          </div>
          <div className="flex items-center gap-3 text-xs text-gray-400">
            <span className="hidden sm:inline">AI-Powered · LangGraph · Groq</span>
          </div>
        </div>
      </header>

      <main className="flex-1 flex gap-0 overflow-hidden max-w-7xl mx-auto w-full">
        <div className="w-[45%] min-w-[380px] border-r border-gray-200 bg-white shadow-sm">
          <InteractionForm />
        </div>
        <div className="flex-1 min-w-[400px]">
          <ChatPanel />
        </div>
      </main>
    </div>
  )
}
