// src/hooks/useNLQ.ts
import { useState } from 'react'
import { apiClient } from '../api/client'
import { toast } from '../store/toastStore'

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  isLoading?: boolean
}

export function useNLQ() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: 'Namaste! 👋 Main tumhara personal finance assistant hoon. Apne finances ke baare mein kuch bhi poochho!',
      timestamp: new Date(),
    }
  ])
  const [isLoading, setIsLoading] = useState(false)

  const sendMessage = async (query: string) => {
    if (!query.trim() || isLoading) return

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: query,
      timestamp: new Date(),
    }

    const loadingMsg: ChatMessage = {
      id: 'loading',
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      isLoading: true,
    }

    setMessages(prev => [...prev, userMsg, loadingMsg])
    setIsLoading(true)

    try {
      const res = await apiClient.post('/nlq/query', { query })
      const answer = res.data?.data?.answer || 'Koi answer nahi mila.'

      setMessages(prev => prev.map(m =>
        m.id === 'loading'
          ? { ...m, id: Date.now().toString(), content: answer, isLoading: false }
          : m
      ))
    } catch (err: any) {
      const errMsg = err.response?.data?.detail || 'Kuch gadbad ho gayi!'
      setMessages(prev => prev.map(m =>
        m.id === 'loading'
          ? { ...m, id: Date.now().toString(), content: errMsg, isLoading: false }
          : m
      ))
      toast.error('Query failed', errMsg)
    } finally {
      setIsLoading(false)
    }
  }

  const clearChat = () => {
    setMessages([{
      id: 'welcome',
      role: 'assistant',
      content: 'Namaste! 👋 Main tumhara personal finance assistant hoon.',
      timestamp: new Date(),
    }])
  }

  return { messages, sendMessage, isLoading, clearChat }
}