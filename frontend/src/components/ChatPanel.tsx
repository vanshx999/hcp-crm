import React, { useState, useRef, useEffect, useCallback } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { RootState, AppDispatch } from '../store'
import {
  addChatMessage,
  setTyping,
  setInteraction,
  setConversationId,
  setSuggestions,
  setValidationResult,
  setHcpSearchResults,
} from '../store/interactionSlice'
import { AgentWebSocket, AgentResponse } from '../api/agentApi'
import { Send, Bot, User, AlertCircle, Wifi, WifiOff, Loader2 } from 'lucide-react'

import type { InteractionState } from '../store/interactionSlice'

export default function ChatPanel() {
  const dispatch = useDispatch<AppDispatch>()
  const chatMessages = useSelector((state: RootState) => state.interaction.chatMessages)
  const isTyping = useSelector((state: RootState) => state.interaction.isTyping)
  const conversationId = useSelector((state: RootState) => state.interaction.conversationId)

  const [input, setInput] = useState('')
  const [connected, setConnected] = useState(false)
  const [connectionError, setConnectionError] = useState('')

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const agentRef = useRef<AgentWebSocket | null>(null)

  // Track if we've ever gotten a successful WS message (suppresses initial errors)
  const hasConnectedOnce = useRef(false)

  const handleAgentMessage = useCallback((data: AgentResponse) => {
    hasConnectedOnce.current = true
    dispatch(setTyping(false))

    if (data.conversation_id) {
      dispatch(setConversationId(data.conversation_id))
    }

    if (data.interaction && Object.keys(data.interaction).length > 0) {
      const interaction = data.interaction as unknown as InteractionState
      dispatch(setInteraction(interaction))
    }

    dispatch(addChatMessage({ role: 'assistant', content: data.reply }))
    setConnectionError('')
  }, [dispatch])

  const handleAgentError = useCallback((error: string) => {
    dispatch(setTyping(false))
    setConnectionError(error)
    // Only show error in chat if we've already seen a successful message
    if (hasConnectedOnce.current) {
      dispatch(addChatMessage({
        role: 'assistant',
        content: `⚠️ Connection issue: ${error}. Please make sure the backend server is running.`,
      }))
    }
  }, [dispatch])

  useEffect(() => {
    const agent = new AgentWebSocket(handleAgentMessage, handleAgentError)
    agentRef.current = agent
    agent.connect()

    const checkInterval = setInterval(() => {
      setConnected(agent.isConnected())
    }, 2000)

    return () => {
      agent.disconnect()
      clearInterval(checkInterval)
    }
  }, [handleAgentMessage, handleAgentError])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [chatMessages, isTyping])

  const handleSend = () => {
    const msg = input.trim()
    if (!msg || !agentRef.current) return

    setInput('')
    dispatch(addChatMessage({ role: 'user', content: msg }))
    dispatch(setTyping(true))

    if (msg.toLowerCase().includes('suggest') || msg.toLowerCase().includes('next step') || msg.toLowerCase().includes('recommend')) {
      dispatch(setSuggestions([
        { suggestion: 'Processing your request...', priority: 'Medium', timeframe: 'Now' },
      ]))
    }

    agentRef.current.send(msg, conversationId)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const examplePrompts = [
    'I met with Dr. Sarah Chen today to discuss our new cardiology product',
    'Search for cardiologists in San Francisco',
    'Suggest next steps for this interaction',
    'Validate the current interaction record',
  ]

  const isFormEmpty = useSelector((state: RootState) => {
    const i = state.interaction.interaction
    return !i.hcp_name && !i.interaction_type
  })

  return (
    <div className="h-full flex flex-col bg-gray-50">
      <div className="px-6 py-4 border-b border-gray-200 bg-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 bg-gradient-to-br from-primary-500 to-primary-700 rounded-xl flex items-center justify-center shadow-sm">
              <Bot size={18} className="text-white" />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-gray-900">AI Assistant</h2>
              <div className="flex items-center gap-1.5 mt-0.5">
                {connected ? (
                  <>
                    <Wifi size={11} className="text-green-500" />
                    <span className="text-[11px] text-green-600">Connected</span>
                  </>
                ) : (
                  <>
                    <WifiOff size={11} className="text-gray-400" />
                    <span className="text-[11px] text-gray-400">Offline</span>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-5 py-4 space-y-3">
        {chatMessages.map((msg, i) => (
          <div key={i} className={`flex items-start gap-2.5 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
            <div className={`w-7 h-7 rounded-full flex items-center justify-center shrink-0 ${
              msg.role === 'user'
                ? 'bg-primary-100 text-primary-600'
                : 'bg-teal-100 text-teal-600'
            }`}>
              {msg.role === 'user' ? <User size={14} /> : <Bot size={14} />}
            </div>
            <div className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed whitespace-pre-wrap ${
              msg.role === 'user'
                ? 'bg-primary-500 text-white rounded-tr-md'
                : 'bg-white border border-gray-200 text-gray-700 rounded-tl-md shadow-sm'
            }`}>
              {msg.content.split('\n').map((line, j) => (
                <React.Fragment key={j}>
                  {j > 0 && <br />}
                  {line}
                </React.Fragment>
              ))}
            </div>
          </div>
        ))}

        {isTyping && (
          <div className="flex items-start gap-2.5">
            <div className="w-7 h-7 bg-teal-100 rounded-full flex items-center justify-center shrink-0">
              <Bot size={14} className="text-teal-600" />
            </div>
            <div className="bg-white border border-gray-200 rounded-2xl rounded-tl-md px-4 py-3 shadow-sm">
              <div className="flex gap-1.5">
                <span className="w-2 h-2 bg-gray-300 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="w-2 h-2 bg-gray-300 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <span className="w-2 h-2 bg-gray-300 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {isFormEmpty && (
        <div className="px-5 py-3 bg-blue-50 border-t border-blue-100">
          <p className="text-[11px] font-medium text-blue-700 mb-2 uppercase tracking-wider">Try asking</p>
          <div className="flex flex-wrap gap-1.5">
            {examplePrompts.map((prompt, i) => (
              <button
                key={i}
                onClick={() => { setInput(prompt); inputRef.current?.focus() }}
                className="text-xs bg-white border border-blue-200 text-blue-700 rounded-full px-3 py-1.5 hover:bg-blue-100 transition-colors"
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="px-5 py-3 bg-white border-t border-gray-200">
        {connectionError && (
          <div className="mb-2 flex items-center gap-2 text-xs text-red-600 bg-red-50 rounded-lg px-3 py-2">
            <AlertCircle size={13} />
            {connectionError}
          </div>
        )}
        <div className="flex items-center gap-2">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Describe your HCP interaction..."
            className="flex-1 text-sm border border-gray-300 rounded-xl px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-gray-50"
            disabled={!connected}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || !connected}
            className="w-10 h-10 bg-primary-600 text-white rounded-xl flex items-center justify-center hover:bg-primary-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors shadow-sm"
          >
            <Send size={16} />
          </button>
        </div>
      </div>
    </div>
  )
}
