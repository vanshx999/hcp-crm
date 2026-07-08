import React from 'react'
import { useSelector } from 'react-redux'
import { RootState } from '../store'
import {
  User, Phone, Mail, Calendar, Clock, Smile, Stethoscope,
  MapPin, Pill, FileText, ListChecks, CalendarCheck, FileEdit,
  AlertCircle, CheckCircle2, Lightbulb
} from 'lucide-react'

const FieldIcon: Record<string, React.ReactNode> = {
  hcp_name: <User size={16} />,
  interaction_type: <Phone size={16} />,
  interaction_date: <Calendar size={16} />,
  duration_minutes: <Clock size={16} />,
  sentiment: <Smile size={16} />,
  specialty: <Stethoscope size={16} />,
  region: <MapPin size={16} />,
  products_discussed: <Pill size={16} />,
  key_discussion_points: <FileText size={16} />,
  action_items: <ListChecks size={16} />,
  follow_up_date: <CalendarCheck size={16} />,
  additional_notes: <FileEdit size={16} />,
}

export default function InteractionForm() {
  const interaction = useSelector((state: RootState) => state.interaction.interaction)
  const validationResult = useSelector((state: RootState) => state.interaction.validationResult)
  const hcpSearchResults = useSelector((state: RootState) => state.interaction.hcpSearchResults)
  const suggestions = useSelector((state: RootState) => state.interaction.suggestions)

  const fields = [
    { key: 'hcp_name', label: 'HCP Name', type: 'text', required: true },
    { key: 'interaction_type', label: 'Interaction Type', type: 'select', required: true,
      options: ['', 'Call', 'Email', 'Meeting', 'Other'] },
    { key: 'interaction_date', label: 'Interaction Date', type: 'date', required: true },
    { key: 'duration_minutes', label: 'Duration (min)', type: 'number' },
    { key: 'sentiment', label: 'Sentiment', type: 'select',
      options: ['', 'Positive', 'Neutral', 'Negative'] },
    { key: 'specialty', label: 'Specialty', type: 'text' },
    { key: 'region', label: 'Region', type: 'text' },
    { key: 'products_discussed', label: 'Products Discussed', type: 'textarea' },
    { key: 'key_discussion_points', label: 'Key Discussion Points', type: 'textarea' },
    { key: 'action_items', label: 'Action Items', type: 'textarea' },
    { key: 'follow_up_date', label: 'Follow-Up Date', type: 'date' },
    { key: 'additional_notes', label: 'Additional Notes', type: 'textarea' },
  ]

  const hasAnyData = fields.some(f => {
    const val = (interaction as any)[f.key]
    return val !== '' && val !== null
  })

  return (
    <div className="h-full flex flex-col bg-white">
      <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-primary-600 to-primary-700">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
          <FileEdit size={20} />
          Interaction Details
        </h2>
        <p className="text-primary-100 text-xs mt-0.5">Managed by AI Assistant</p>
      </div>

      <div className="flex-1 overflow-y-auto px-6 py-5 space-y-4">
        {!hasAnyData && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm text-blue-800 flex items-start gap-3">
            <Lightbulb size={18} className="shrink-0 mt-0.5 text-blue-500" />
            <div>
              <p className="font-medium">No interaction data yet</p>
              <p className="text-blue-600 mt-1">Use the chat panel on the right to describe your HCP interaction. The AI will populate this form automatically.</p>
            </div>
          </div>
        )}

        {validationResult && !validationResult.is_valid && (
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-sm flex items-start gap-2">
            <AlertCircle size={16} className="shrink-0 mt-0.5 text-amber-500" />
            <div>
              <p className="font-medium text-amber-800">Validation Issues</p>
              {validationResult.missing_fields.length > 0 && (
                <p className="text-amber-700 mt-1">Missing: {validationResult.missing_fields.join(', ')}</p>
              )}
            </div>
          </div>
        )}

        {validationResult && validationResult.is_valid && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-3 text-sm flex items-start gap-2">
            <CheckCircle2 size={16} className="shrink-0 mt-0.5 text-green-500" />
            <span className="text-green-800">Interaction record is complete and valid</span>
          </div>
        )}

        {hcpSearchResults.length > 0 && (
          <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-3">
            <p className="text-xs font-semibold text-indigo-700 uppercase tracking-wider mb-2">Search Results</p>
            {hcpSearchResults.map((hcp, i) => (
              <div key={i} className="text-sm text-indigo-900 py-1 border-b border-indigo-100 last:border-0">
                <span className="font-medium">{hcp.name}</span> — {hcp.specialty}, {hcp.region}
                {hcp.last_interaction && <span className="text-indigo-500 text-xs ml-2">Last: {hcp.last_interaction}</span>}
              </div>
            ))}
          </div>
        )}

        {suggestions.length > 0 && (
          <div className="bg-teal-50 border border-teal-200 rounded-lg p-3">
            <p className="text-xs font-semibold text-teal-700 uppercase tracking-wider mb-2">Suggested Next Steps</p>
            {suggestions.map((s, i) => (
              <div key={i} className="text-sm py-1.5 border-b border-teal-100 last:border-0">
                <div className="flex items-start gap-2">
                  <span className={`text-xs font-semibold px-1.5 py-0.5 rounded ${
                    s.priority === 'High' ? 'bg-red-100 text-red-700' :
                    s.priority === 'Medium' ? 'bg-amber-100 text-amber-700' :
                    'bg-blue-100 text-blue-700'
                  }`}>
                    {s.priority}
                  </span>
                  <div>
                    <p className="text-teal-900">{s.suggestion}</p>
                    <p className="text-teal-600 text-xs mt-0.5">{s.timeframe}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {hasAnyData && (
          <div className="space-y-3">
            {fields.map(({ key, label, type, required, options }) => {
              const val = (interaction as any)[key] ?? ''
              const isMissing = validationResult && !validationResult.is_valid &&
                validationResult.missing_fields.includes(key)

              return (
                <div key={key} className={`${isMissing ? 'bg-red-50 rounded-lg p-3 -mx-3 border border-red-200' : ''}`}>
                  <label className="block text-xs font-medium text-gray-600 mb-1.5 flex items-center gap-1.5">
                    {FieldIcon[key]}
                    {label}
                    {required && <span className="text-red-400">*</span>}
                  </label>

                  {type === 'textarea' ? (
                    <textarea
                      value={val as string}
                      readOnly
                      rows={3}
                      className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 bg-gray-50 text-gray-700 resize-none cursor-not-allowed"
                    />
                  ) : type === 'select' ? (
                    <select
                      value={val as string}
                      disabled
                      className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 bg-gray-50 text-gray-700 cursor-not-allowed appearance-none"
                    >
                      {options?.map(opt => (
                        <option key={opt} value={opt}>{opt || 'Select...'}</option>
                      ))}
                    </select>
                  ) : (
                    <input
                      type={type}
                      value={val as string}
                      readOnly
                      className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 bg-gray-50 text-gray-700 cursor-not-allowed"
                    />
                  )}
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
