import { createSlice, PayloadAction } from '@reduxjs/toolkit'

export interface InteractionState {
  hcp_name: string
  interaction_type: string
  interaction_date: string
  duration_minutes: number | null
  sentiment: string
  specialty: string
  region: string
  products_discussed: string
  key_discussion_points: string
  action_items: string
  follow_up_date: string
  additional_notes: string
}

const initialState: InteractionState = {
  hcp_name: '',
  interaction_type: '',
  interaction_date: new Date().toISOString().split('T')[0],
  duration_minutes: null,
  sentiment: '',
  specialty: '',
  region: '',
  products_discussed: '',
  key_discussion_points: '',
  action_items: '',
  follow_up_date: '',
  additional_notes: '',
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

interface AppState {
  interaction: InteractionState
  chatMessages: ChatMessage[]
  isTyping: boolean
  conversationId: string | null
  suggestions: Array<{ suggestion: string; priority: string; timeframe: string }>
  validationResult: { is_valid: boolean; missing_fields: string[]; suggestions: string[] } | null
  hcpSearchResults: Array<{ name: string; specialty: string; region: string; last_interaction: string }>
}

const appInitialState: AppState = {
  interaction: initialState,
  chatMessages: [
    {
      role: 'assistant' as const,
      content: 'Hello! I\'m your AI assistant for logging HCP interactions. Tell me about your interaction with an HCP, and I\'ll populate the form automatically. You can also ask me to search for HCPs, edit fields, suggest next steps, or validate the form.',
    },
  ],
  isTyping: false,
  conversationId: null,
  suggestions: [],
  validationResult: null,
  hcpSearchResults: [],
}

const interactionSlice = createSlice({
  name: 'interaction',
  initialState: appInitialState,
  reducers: {
    setInteractionField: (state, action: PayloadAction<{ field: keyof InteractionState; value: string | number | null }>) => {
      (state.interaction as any)[action.payload.field] = action.payload.value
    },
    setInteraction: (state, action: PayloadAction<Partial<InteractionState>>) => {
      state.interaction = { ...state.interaction, ...action.payload }
    },
    resetInteraction: (state) => {
      state.interaction = initialState
    },
    addChatMessage: (state, action: PayloadAction<ChatMessage>) => {
      state.chatMessages.push(action.payload)
    },
    setTyping: (state, action: PayloadAction<boolean>) => {
      state.isTyping = action.payload
    },
    setConversationId: (state, action: PayloadAction<string>) => {
      state.conversationId = action.payload
    },
    setSuggestions: (state, action: PayloadAction<Array<{ suggestion: string; priority: string; timeframe: string }>>) => {
      state.suggestions = action.payload
    },
    setValidationResult: (state, action: PayloadAction<{ is_valid: boolean; missing_fields: string[]; suggestions: string[] } | null>) => {
      state.validationResult = action.payload
    },
    setHcpSearchResults: (state, action: PayloadAction<Array<{ name: string; specialty: string; region: string; last_interaction: string }>>) => {
      state.hcpSearchResults = action.payload
    },
  },
})

export const {
  setInteractionField,
  setInteraction,
  resetInteraction,
  addChatMessage,
  setTyping,
  setConversationId,
  setSuggestions,
  setValidationResult,
  setHcpSearchResults,
} = interactionSlice.actions

export default interactionSlice.reducer
