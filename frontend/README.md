# VALIS Frontend - React Dashboard

## Temporal-Safe AI Democratization Interface

Built with Doc Brown's UI-201, UI-202, UI-203 specifications for universal AI access.

### Features

- **UI-201: Main Layout Architecture** ✅
  - Header with VALIS logo and system status
  - Collapsible sidebar with persona selector and session management
  - Main view with chat interface and system diagnostics

- **UI-202: Persona Selector System** ✅
  - Visual card-style persona selection
  - Real-time persona availability status
  - Highlighted current persona in chat session

- **UI-203: Chat Interface Implementation** ✅
  - Real-time message display with timestamps
  - Loading states and error handling
  - Provider badges showing which AI handled each response
  - Auto-scroll and keyboard navigation
  - Message history persistence

### Tech Stack

- **React 18** with TypeScript
- **Vite** for development and building
- **Tailwind CSS** for styling
- **shadcn/ui** component patterns
- **TanStack Query** for API state management
- **Lucide React** for icons
- **date-fns** for date formatting

### Temporal Safeguards

- **Error Boundaries** - Prevent component failures from crashing the app
- **API Error Handling** - Graceful degradation when backend is unavailable
- **Loading States** - Proper user feedback during async operations
- **Input Validation** - Message length limits and sanitization
- **Accessibility** - Keyboard navigation and screen reader support
- **Responsive Design** - Works on desktop and mobile devices

### Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### API Integration

The frontend connects to the VALIS FastAPI backend at `http://localhost:8000`:

- `/api/chat` - Send messages to AI personas
- `/api/personas` - Get available AI personas
- `/api/sessions` - Manage chat sessions
- `/api/health` - System health monitoring
- `/api/admin/stats` - System statistics

### File Structure

```
src/
├── components/
│   ├── ui/           # shadcn/ui base components
│   ├── MainLayout.tsx    # Main application layout
│   ├── Header.tsx        # Header with logo and status
│   ├── Sidebar.tsx       # Persona selector and sessions
│   ├── ChatInterface.tsx # Main chat interface
│   └── SystemDiagnostics.tsx # System monitoring
├── lib/
│   ├── api.ts        # API client with error handling
│   └── utils.ts      # Utility functions
├── types/
│   └── index.ts      # TypeScript type definitions
├── App.tsx           # Main app component with providers
├── main.tsx          # React entry point
└── index.css         # Global styles and CSS variables
```

### Deployment

1. Build the frontend: `npm run build`
2. Serve the `dist` folder with any static file server
3. Ensure the VALIS API backend is running on port 8000

The frontend will automatically proxy API requests to the backend during development.
