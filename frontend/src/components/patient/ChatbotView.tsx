import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';
import { PaperAirplaneIcon, ChatBubbleBottomCenterTextIcon } from '@heroicons/react/24/solid';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export default function ChatbotView() {
    const { state } = useAuth();
    const [messages, setMessages] = useState<{ role: 'user' | 'bot', text: string }[]>([
        { role: 'bot', text: 'Hello! I\'m your ParkinsonCare AI assistant, powered by Llama 3.2. How can I help you today?' }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [aiOnline, setAiOnline] = useState<boolean | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Check Llama/Ollama health on mount
    useEffect(() => {
        const checkStatus = async () => {
            try {
                const resp = await axios.get(`${API_BASE_URL}/chatbot/status`);
                setAiOnline(resp.data.available);
            } catch {
                setAiOnline(false);
            }
        };
        checkStatus();
    }, []);

    const sendMessage = async () => {
        if (!input.trim() || loading) return;

        const userMessage = input.trim();
        setInput('');
        setMessages(prev => [...prev, { role: 'user', text: userMessage }]);
        setLoading(true);

        try {
            const response = await axios.post(`${API_BASE_URL}/chatbot/ask`,
                { message: userMessage },
                { headers: { Authorization: `Bearer ${state.token}` } }
            );

            setMessages(prev => [...prev, { role: 'bot', text: response.data.reply }]);
        } catch (error) {
            console.error('Chatbot error:', error);
            setMessages(prev => [...prev, { role: 'bot', text: 'Sorry, I\'m having trouble connecting. Please make sure Ollama is running.' }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col bg-white rounded-xl shadow-md border border-gray-100 overflow-hidden h-[600px]">
            <div className="p-4 bg-indigo-600 text-white flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <ChatBubbleBottomCenterTextIcon className="h-6 w-6" />
                    <div>
                        <h3 className="font-bold text-lg">AI Health Assistant</h3>
                        <p className="text-xs text-indigo-200">Powered by 🦙 Llama 3.2</p>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <div className={`w-2.5 h-2.5 rounded-full ${aiOnline === null ? 'bg-gray-400 animate-pulse' :
                        aiOnline ? 'bg-green-400' : 'bg-red-400'
                        }`} />
                    <span className="text-xs text-indigo-200">
                        {aiOnline === null ? 'Checking...' : aiOnline ? 'Online' : 'Offline'}
                    </span>
                </div>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
                {messages.map((msg, idx) => (
                    <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-[70%] rounded-2xl p-4 ${msg.role === 'user' ? 'bg-indigo-600 text-white rounded-tr-sm' : 'bg-white text-gray-800 shadow-sm border border-gray-100 rounded-tl-sm'}`}>
                            {msg.role === 'bot' && (
                                <span className="text-xs text-indigo-400 font-medium block mb-1">🦙 Llama 3.2</span>
                            )}
                            <p className="whitespace-pre-wrap">{msg.text}</p>
                        </div>
                    </div>
                ))}
                {loading && (
                    <div className="flex justify-start">
                        <div className="bg-white px-4 py-3 rounded-2xl rounded-tl-sm shadow-sm border border-gray-100 flex items-center gap-2">
                            <span className="text-xs text-indigo-400 mr-1">🦙</span>
                            <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                            <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                            <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            <div className="p-4 bg-white border-t border-gray-200">
                <form onSubmit={(e) => { e.preventDefault(); sendMessage(); }} className="flex gap-2">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Ask about your health, symptoms, medications..."
                        className="flex-1 border border-gray-300 rounded-full px-6 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        disabled={loading}
                    />
                    <button
                        type="submit"
                        disabled={!input.trim() || loading}
                        className="bg-indigo-600 text-white rounded-full p-3 hover:bg-indigo-700 disabled:opacity-50 transition-colors"
                    >
                        <PaperAirplaneIcon className="h-6 w-6" />
                    </button>
                </form>
            </div>
        </div>
    );
}
