#!/usr/bin/env python3
"""
Sprint 8B: Quick Frontend Test
Start both backend and simple HTML frontend
"""

import subprocess
import time
import webbrowser
from pathlib import Path

def create_simple_frontend():
    """Create a simple HTML frontend for testing"""
    
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VALIS Memory-Aware Chat</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .memory-layer { transition: all 0.3s ease; }
        .tag-highlight { background: linear-gradient(45deg, #fef3c7, #fbbf24); }
    </style>
</head>
<body class="bg-gray-50 font-sans">
    <div class="flex h-screen">
        <!-- Sidebar -->
        <div class="w-64 bg-white border-r border-gray-200 p-4">
            <h2 class="text-lg font-bold mb-4">VALIS Personas</h2>
            <div id="personas-list" class="space-y-2">
                <!-- Personas will be loaded here -->
            </div>
        </div>
        
        <!-- Chat Area -->
        <div class="flex-1 flex">
            <div class="flex-1 flex flex-col">
                <!-- Chat Header -->
                <div class="bg-white border-b border-gray-200 p-4">
                    <h1 class="text-xl font-bold">Memory-Aware Chat</h1>
                    <p class="text-sm text-gray-600" id="persona-info">Select a persona to start chatting</p>
                </div>
                
                <!-- Messages -->
                <div class="flex-1 overflow-y-auto p-4 space-y-4" id="messages">
                    <div class="text-center text-gray-500">
                        <p>Select a persona and start chatting to see memory-aware responses</p>
                    </div>
                </div>
                
                <!-- Dev Tools -->
                <div class="bg-yellow-50 border-t border-yellow-200 p-3">
                    <div class="flex items-center space-x-3">
                        <button id="force-canon" class="px-3 py-1 bg-yellow-500 text-white rounded text-sm">
                            Force #canon
                        </button>
                        <button id="test-prompt" class="px-3 py-1 bg-blue-500 text-white rounded text-sm">
                            Test Prompt
                        </button>
                        <div id="tags-display" class="text-sm text-gray-600"></div>
                    </div>
                </div>
                
                <!-- Input -->
                <div class="bg-white border-t border-gray-200 p-4">
                    <div class="flex space-x-2">
                        <input 
                            type="text" 
                            id="message-input" 
                            placeholder="Type your message..."
                            class="flex-1 border border-gray-300 rounded px-3 py-2 focus:outline-none focus:border-blue-500"
                            maxlength="1000"
                        />
                        <button 
                            id="send-btn" 
                            class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
                        >
                            Send
                        </button>
                    </div>
                    <div class="flex justify-between mt-2 text-xs text-gray-500">
                        <span>Memory tags: #canon, #client_fact, #working_memory</span>
                        <span id="char-count">0/1000</span>
                    </div>
                </div>
            </div>
            
            <!-- Memory Panel -->
            <div class="w-80 bg-white border-l border-gray-200 p-4 overflow-y-auto">
                <h3 class="font-bold mb-3">Memory Diagnostics</h3>
                <div id="memory-display" class="space-y-3">
                    <div class="text-sm text-gray-500">Select a persona to view memory layers</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let selectedPersona = null;
        let sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        let forceCanon = false;
        
        // Load personas
        fetch('/api/personas')
            .then(r => r.json())
            .then(personas => {
                const list = document.getElementById('personas-list');
                list.innerHTML = '';
                
                personas.forEach(persona => {
                    const div = document.createElement('div');
                    div.className = 'p-2 rounded cursor-pointer hover:bg-gray-100 border';
                    div.innerHTML = `
                        <div class="font-medium">${persona.name}</div>
                        <div class="text-xs text-gray-500">${persona.role}</div>
                    `;
                    div.onclick = () => selectPersona(persona);
                    list.appendChild(div);
                });
            });
            
        function selectPersona(persona) {
            selectedPersona = persona;
            document.getElementById('persona-info').textContent = 
                `Chatting with ${persona.name} - ${persona.role}`;
            
            // Update session
            sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
            
            // Clear messages
            document.getElementById('messages').innerHTML = '';
            
            // Load memory
            loadMemory();
        }
        
        function loadMemory() {
            if (!selectedPersona) return;
            
            fetch(`/api/memory/${selectedPersona.id}?session=${sessionId}`)
                .then(r => r.json())
                .then(memory => {
                    const display = document.getElementById('memory-display');
                    display.innerHTML = `
                        <div class="memory-layer border rounded p-2 mb-2">
                            <div class="font-medium text-blue-700">Core Biography</div>
                            <div class="text-xs text-gray-600">${Object.keys(memory.core_biography || {}).length} entries</div>
                        </div>
                        <div class="memory-layer border rounded p-2 mb-2">
                            <div class="font-medium text-yellow-700">Canonized Identity</div>
                            <div class="text-xs text-gray-600">${(memory.canonized_identity || []).length} entries</div>
                        </div>
                        <div class="memory-layer border rounded p-2 mb-2">
                            <div class="font-medium text-green-700">Client Profile</div>
                            <div class="text-xs text-gray-600">${Object.keys(memory.client_profile?.facts || {}).length} facts</div>
                        </div>
                        <div class="memory-layer border rounded p-2 mb-2">
                            <div class="font-medium text-purple-700">Working Memory</div>
                            <div class="text-xs text-gray-600">${(memory.working_memory || []).length} entries</div>
                        </div>
                        <div class="memory-layer border rounded p-2">
                            <div class="font-medium text-gray-700">Session History</div>
                            <div class="text-xs text-gray-600">${(memory.session_history || []).length} messages</div>
                        </div>
                    `;
                })
                .catch(e => console.error('Memory load failed:', e));
        }
        
        function sendMessage(message) {
            if (!selectedPersona || !message.trim()) return;
            
            // Add user message
            addMessage('user', message);
            
            // Add loading message
            const loadingId = 'loading-' + Date.now();
            addMessage('assistant', 'Thinking...', loadingId, true);
            
            // Send to API
            fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: sessionId,
                    persona_id: selectedPersona.id,
                    message: message
                })
            })
            .then(r => r.json())
            .then(response => {
                // Remove loading message
                document.getElementById(loadingId)?.remove();
                
                // Add response
                addMessage('assistant', response.response || 'No response', null, false, response.provider);
                
                // Show tags if any
                if (response.memory_info?.tags_processed?.length) {
                    document.getElementById('tags-display').textContent = 
                        'Tags: ' + response.memory_info.tags_processed.map(t => '#' + t).join(', ');
                }
                
                // Reload memory
                setTimeout(loadMemory, 500);
            })
            .catch(e => {
                document.getElementById(loadingId)?.remove();
                addMessage('assistant', 'Error: ' + e.message, null, false, 'Error');
            });
        }
        
        function addMessage(type, content, id, loading = false, provider = '') {
            const messages = document.getElementById('messages');
            const div = document.createElement('div');
            div.id = id || `msg-${Date.now()}`;
            div.className = `flex ${type === 'user' ? 'justify-end' : 'justify-start'}`;
            
            const bubble = document.createElement('div');
            bubble.className = `max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                type === 'user' 
                    ? 'bg-blue-500 text-white' 
                    : loading 
                        ? 'bg-gray-200 text-gray-600'
                        : 'bg-white border border-gray-300'
            }`;
            
            bubble.innerHTML = `
                <div class="text-sm">${content}</div>
                ${provider ? `<div class="text-xs opacity-75 mt-1">${provider}</div>` : ''}
            `;
            
            div.appendChild(bubble);
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
        }
        
        // Event listeners
        document.getElementById('send-btn').onclick = () => {
            const input = document.getElementById('message-input');
            let message = input.value.trim();
            
            if (forceCanon && !message.includes('#canon')) {
                message += ' #canon';
                forceCanon = false;
                document.getElementById('force-canon').classList.remove('bg-red-500');
                document.getElementById('force-canon').classList.add('bg-yellow-500');
            }
            
            if (message) {
                sendMessage(message);
                input.value = '';
                updateCharCount();
            }
        };
        
        document.getElementById('message-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                document.getElementById('send-btn').click();
            }
        });
        
        document.getElementById('message-input').addEventListener('input', updateCharCount);
        
        document.getElementById('force-canon').onclick = () => {
            forceCanon = !forceCanon;
            const btn = document.getElementById('force-canon');
            if (forceCanon) {
                btn.classList.remove('bg-yellow-500');
                btn.classList.add('bg-red-500');
            } else {
                btn.classList.remove('bg-red-500');
                btn.classList.add('bg-yellow-500');
            }
        };
        
        document.getElementById('test-prompt').onclick = () => {
            const prompts = [
                'I successfully resolved the team conflict using structured communication #canon',
                'The client prefers direct communication #client_fact',
                'Team shows signs of burnout - need to address workload #working_memory'
            ];
            const prompt = prompts[Math.floor(Math.random() * prompts.length)];
            document.getElementById('message-input').value = prompt;
            updateCharCount();
        };
        
        function updateCharCount() {
            const input = document.getElementById('message-input');
            document.getElementById('char-count').textContent = `${input.value.length}/1000`;
        }
        
        // Auto-refresh memory every 10 seconds
        setInterval(() => {
            if (selectedPersona) loadMemory();
        }, 10000);
    </script>
</body>
</html>"""
    
    # Write the HTML file
    html_file = Path(__file__).parent.parent / "simple_frontend.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return html_file

def main():
    print("SPRINT 8B: MEMORY-AWARE FRONTEND DEPLOYMENT")
    print("=" * 50)
    
    # Create simple frontend
    html_file = create_simple_frontend()
    print(f"Created simple frontend: {html_file}")
    
    # Backend should already be running on port 3001
    print("Opening frontend...")
    
    # Try to open the file in browser
    try:
        webbrowser.open(f"file://{html_file.absolute()}")
    except:
        print(f"Manual: Open {html_file} in your browser")
    
    print("\nFrontend Features:")
    print("- Persona selection from API")
    print("- Memory-aware chat with real-time diagnostics")
    print("- Memory layer visualization (5 layers)")
    print("- Dev tools: Force #canon, test prompts")
    print("- Tag detection and display")
    print("- Real-time memory updates")
    
    print("\nAPI Endpoints used:")
    print("- GET /api/personas - Load available personas")
    print("- POST /api/chat - Send messages with memory")
    print("- GET /api/memory/{persona_id} - Live memory diagnostics")
    
    print("\nBackend should be running on http://127.0.0.1:3001")
    print("Frontend will connect to backend APIs")

if __name__ == "__main__":
    main()
