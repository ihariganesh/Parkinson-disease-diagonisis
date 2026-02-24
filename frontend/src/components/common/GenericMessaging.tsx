import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';
import { PaperAirplaneIcon, EnvelopeIcon, PlusCircleIcon, ArrowLeftIcon, UserCircleIcon } from '@heroicons/react/24/solid';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

interface Conversation {
    id: string;
    first_name: string;
    last_name: string;
    role: string;
    last_message: string;
    last_message_at: string | null;
    unread_count: number;
}

interface Message {
    id: string;
    sender_id: string;
    recipient_id: string;
    message_text: string;
    sent_at: string | null;
    is_read: boolean;
    is_mine: boolean;
}

interface Contact {
    id: string;
    first_name: string;
    last_name: string;
    role: string;
    email: string;
    patient_id?: string;
}

export default function GenericMessaging() {
    const { state } = useAuth();
    const [conversations, setConversations] = useState<Conversation[]>([]);
    const [activePartnerId, setActivePartnerId] = useState<string | null>(null);
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [showNewChat, setShowNewChat] = useState(false);
    const [contacts, setContacts] = useState<Contact[]>([]);
    const [contactSearch, setContactSearch] = useState('');
    const [contactsLoading, setContactsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

    useEffect(() => {
        fetchConversations();
        // Poll for new messages every 5 seconds
        pollRef.current = setInterval(fetchConversations, 5000);
        return () => { if (pollRef.current) clearInterval(pollRef.current); };
    }, []);

    useEffect(() => {
        if (activePartnerId) {
            fetchMessages(activePartnerId);
            // Poll messages for active conversation
            const msgPoll = setInterval(() => fetchMessages(activePartnerId), 3000);
            return () => clearInterval(msgPoll);
        }
    }, [activePartnerId]);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const fetchConversations = async () => {
        try {
            const resp = await axios.get(`${API_BASE_URL}/messages/conversations`, {
                headers: { Authorization: `Bearer ${state.token}` }
            });
            setConversations(prev => {
                const serverConvs: Conversation[] = resp.data;
                const serverIds = new Set(serverConvs.map(c => c.id));
                const optimisticConvs = prev.filter(c => !serverIds.has(c.id) && c.last_message === '');
                return [...optimisticConvs, ...serverConvs];
            });
        } catch (err) {
            console.error('Error fetching conversations', err);
        }
    };

    const fetchMessages = async (partnerId: string) => {
        try {
            const resp = await axios.get(`${API_BASE_URL}/messages/history/${partnerId}`, {
                headers: { Authorization: `Bearer ${state.token}` }
            });
            setMessages(resp.data);
        } catch (err) {
            console.error('Error fetching messages', err);
        }
    };

    const fetchContacts = async () => {
        setContactsLoading(true);
        try {
            const resp = await axios.get(`${API_BASE_URL}/messages/contacts`, {
                headers: { Authorization: `Bearer ${state.token}` }
            });
            setContacts(resp.data);
        } catch (err) {
            console.error('Error fetching contacts', err);
        } finally {
            setContactsLoading(false);
        }
    };

    const startNewConversation = (contact: Contact) => {
        // Check if conversation already exists
        const existing = conversations.find(c => c.id === contact.id);
        if (!existing) {
            // Add temporary conversation entry
            setConversations(prev => [{
                id: contact.id,
                first_name: contact.first_name,
                last_name: contact.last_name,
                role: contact.role,
                last_message: '',
                last_message_at: null,
                unread_count: 0
            }, ...prev]);
        }
        setActivePartnerId(contact.id);
        setShowNewChat(false);
        setContactSearch('');
    };

    const sendMessage = async () => {
        if (!input.trim() || !activePartnerId) return;

        const userMessage = input.trim();
        setInput('');

        // Optimistically update
        setMessages(prev => [...prev, {
            id: `temp-${Date.now()}`,
            sender_id: state.user?.id || '',
            recipient_id: activePartnerId,
            message_text: userMessage,
            sent_at: null,
            is_read: false,
            is_mine: true
        }]);
        setLoading(true);

        try {
            await axios.post(`${API_BASE_URL}/messages/send`,
                { recipient_id: activePartnerId, message_text: userMessage },
                { headers: { Authorization: `Bearer ${state.token}` } }
            );
            fetchConversations();
            // Refresh actual message list
            fetchMessages(activePartnerId);
        } catch (error) {
            console.error('Message error:', error);
        } finally {
            setLoading(false);
        }
    };

    const activeConv = conversations.find(c => c.id === activePartnerId) || contacts.find(c => c.id === activePartnerId);

    const filteredContacts = contacts.filter(c => {
        const search = contactSearch.toLowerCase();
        return (
            c.first_name.toLowerCase().includes(search) ||
            c.last_name.toLowerCase().includes(search) ||
            c.email.toLowerCase().includes(search) ||
            (c.patient_id && c.patient_id.toLowerCase().includes(search))
        );
    });

    return (
        <div className="flex bg-white rounded-xl shadow-md border border-gray-100 overflow-hidden h-[600px]">
            {/* Conversations Sidebar */}
            <div className="w-1/3 border-r border-gray-200 bg-gray-50 flex flex-col">
                <div className="p-4 border-b border-gray-200 bg-white flex items-center justify-between">
                    <h3 className="font-bold text-gray-800 text-lg">Inbox</h3>
                    <button
                        onClick={() => { setShowNewChat(true); fetchContacts(); }}
                        className="text-blue-600 hover:text-blue-800 transition-colors p-1 rounded-full hover:bg-blue-50"
                        title="New Conversation"
                    >
                        <PlusCircleIcon className="h-7 w-7" />
                    </button>
                </div>
                <div className="flex-1 overflow-y-auto">
                    {conversations.length === 0 ? (
                        <div className="p-6 text-center">
                            <EnvelopeIcon className="h-10 w-10 mx-auto text-gray-300 mb-3" />
                            <p className="text-gray-500 text-sm mb-3">No conversations yet.</p>
                            <button
                                onClick={() => { setShowNewChat(true); fetchContacts(); }}
                                className="text-sm bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors inline-flex items-center gap-2"
                            >
                                <PlusCircleIcon className="h-4 w-4" />
                                Start a Conversation
                            </button>
                        </div>
                    ) : (
                        conversations.map(conv => (
                            <div
                                key={conv.id}
                                onClick={() => { setActivePartnerId(conv.id); setShowNewChat(false); }}
                                className={`p-4 border-b border-gray-100 cursor-pointer transition-colors ${activePartnerId === conv.id ? 'bg-blue-50 border-l-4 border-l-blue-600' : 'hover:bg-gray-100'}`}
                            >
                                <div className="flex justify-between items-center mb-1">
                                    <div className="flex items-center gap-2">
                                        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold ${conv.role === 'doctor' ? 'bg-emerald-500' : 'bg-indigo-500'}`}>
                                            {conv.first_name[0]}{conv.last_name[0]}
                                        </div>
                                        <div>
                                            <span className="font-semibold text-gray-900 text-sm">{conv.first_name} {conv.last_name}</span>
                                            <span className={`ml-2 text-[10px] font-medium uppercase tracking-wider px-1.5 py-0.5 rounded-full ${conv.role === 'doctor' ? 'bg-emerald-100 text-emerald-700' : 'bg-indigo-100 text-indigo-700'}`}>
                                                {conv.role}
                                            </span>
                                        </div>
                                    </div>
                                    {conv.unread_count > 0 && (
                                        <span className="bg-red-500 text-white text-xs font-bold px-2 py-0.5 rounded-full animate-pulse">{conv.unread_count}</span>
                                    )}
                                </div>
                                <div className="text-sm text-gray-500 truncate pl-10">{conv.last_message || 'No messages yet'}</div>
                                {conv.last_message_at && (
                                    <div className="text-[10px] text-gray-400 pl-10 mt-1">
                                        {new Date(conv.last_message_at).toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                                    </div>
                                )}
                            </div>
                        ))
                    )}
                </div>
            </div>

            {/* Chat Area */}
            <div className="flex-1 flex flex-col bg-white">
                {showNewChat ? (
                    /* New Conversation - Contact Picker */
                    <div className="flex-1 flex flex-col">
                        <div className="p-4 border-b border-gray-200 shadow-sm flex items-center gap-3">
                            <button onClick={() => setShowNewChat(false)} className="text-gray-500 hover:text-gray-700">
                                <ArrowLeftIcon className="h-5 w-5" />
                            </button>
                            <h3 className="font-bold text-gray-800">New Conversation</h3>
                        </div>
                        <div className="p-4 border-b border-gray-100">
                            <input
                                type="text"
                                value={contactSearch}
                                onChange={(e) => setContactSearch(e.target.value)}
                                placeholder="Search by name, email, or Patient ID..."
                                className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                autoFocus
                            />
                        </div>
                        <div className="flex-1 overflow-y-auto">
                            {contactsLoading ? (
                                <div className="flex items-center justify-center py-10">
                                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                                </div>
                            ) : filteredContacts.length === 0 ? (
                                <div className="text-center py-10 text-gray-500">
                                    <UserCircleIcon className="h-12 w-12 mx-auto text-gray-300 mb-3" />
                                    <p className="text-sm">{contactSearch ? 'No contacts match your search.' : 'No contacts available.'}</p>
                                </div>
                            ) : (
                                filteredContacts.map(contact => (
                                    <div
                                        key={contact.id}
                                        onClick={() => startNewConversation(contact)}
                                        className="p-4 border-b border-gray-100 cursor-pointer hover:bg-blue-50 transition-colors flex items-center gap-3"
                                    >
                                        <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white font-bold ${contact.role === 'doctor' ? 'bg-emerald-500' : 'bg-indigo-500'}`}>
                                            {contact.first_name[0]}{contact.last_name[0]}
                                        </div>
                                        <div className="flex-1">
                                            <div className="flex items-center gap-2">
                                                <span className="font-semibold text-gray-900">{contact.first_name} {contact.last_name}</span>
                                                <span className={`text-[10px] font-medium uppercase tracking-wider px-1.5 py-0.5 rounded-full ${contact.role === 'doctor' ? 'bg-emerald-100 text-emerald-700' : 'bg-indigo-100 text-indigo-700'}`}>
                                                    {contact.role}
                                                </span>
                                            </div>
                                            <div className="text-xs text-gray-500">{contact.email}</div>
                                            {contact.patient_id && (
                                                <div className="text-xs text-gray-400 mt-0.5">ID: {contact.patient_id}</div>
                                            )}
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>
                ) : activePartnerId ? (
                    <>
                        <div className="p-4 border-b border-gray-200 shadow-sm flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <div className={`w-9 h-9 rounded-full flex items-center justify-center text-white font-bold text-sm ${activeConv?.role === 'doctor' ? 'bg-emerald-500' : 'bg-indigo-500'}`}>
                                    {activeConv?.first_name?.[0]}{activeConv?.last_name?.[0]}
                                </div>
                                <div>
                                    <h3 className="font-bold text-gray-800">
                                        {activeConv?.first_name} {activeConv?.last_name}
                                    </h3>
                                    <span className={`text-[10px] font-medium uppercase tracking-wider ${activeConv?.role === 'doctor' ? 'text-emerald-600' : 'text-indigo-600'}`}>
                                        {activeConv?.role}
                                    </span>
                                </div>
                            </div>
                        </div>

                        <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-slate-50">
                            {messages.length === 0 && (
                                <div className="text-center py-10 text-gray-400">
                                    <p className="text-sm">No messages yet. Start the conversation!</p>
                                </div>
                            )}
                            {messages.map((msg, idx) => (
                                <div key={msg.id || idx} className={`flex ${msg.is_mine ? 'justify-end' : 'justify-start'}`}>
                                    <div className={`max-w-[75%] rounded-2xl p-3 ${msg.is_mine
                                        ? 'bg-blue-600 text-white rounded-tr-sm'
                                        : 'bg-white text-gray-800 shadow-sm border border-gray-200 rounded-tl-sm'}`}>
                                        <p className="whitespace-pre-wrap text-sm">{msg.message_text}</p>
                                        <div className={`text-[10px] mt-1 text-right ${msg.is_mine ? 'text-blue-200' : 'text-gray-400'}`}>
                                            {msg.sent_at ? new Date(msg.sent_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Sending...'}
                                        </div>
                                    </div>
                                </div>
                            ))}
                            <div ref={messagesEndRef} />
                        </div>

                        <div className="p-4 bg-white border-t border-gray-200">
                            <form onSubmit={(e) => { e.preventDefault(); sendMessage(); }} className="flex gap-2">
                                <input
                                    type="text"
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    placeholder="Type your message..."
                                    className="flex-1 border border-gray-300 rounded-full px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    disabled={loading}
                                />
                                <button
                                    type="submit"
                                    disabled={!input.trim() || loading}
                                    className="bg-blue-600 text-white rounded-full p-2.5 w-10 h-10 flex items-center justify-center hover:bg-blue-700 disabled:opacity-50 transition-colors"
                                >
                                    <PaperAirplaneIcon className="h-5 w-5" />
                                </button>
                            </form>
                        </div>
                    </>
                ) : (
                    <div className="flex-1 flex flex-col items-center justify-center text-gray-400">
                        <EnvelopeIcon className="h-16 w-16 mb-4 opacity-50" />
                        <p className="text-lg font-medium mb-2">Select a conversation</p>
                        <p className="text-sm mb-4">or start a new one</p>
                        <button
                            onClick={() => { setShowNewChat(true); fetchContacts(); }}
                            className="text-sm bg-blue-600 text-white px-5 py-2.5 rounded-lg hover:bg-blue-700 transition-colors inline-flex items-center gap-2"
                        >
                            <PlusCircleIcon className="h-5 w-5" />
                            New Conversation
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}
