# Frontend Directory

React + TypeScript frontend for the Personalized Adaptive Typing Trainer.

## Structure

- `src/`
  - `components/` - Reusable React components
  - `pages/` - Page components (routing)
  - `hooks/` - Custom React hooks (state management)
  - `services/` - API and utility services
  - `types/` - TypeScript type definitions
  - `styles/` - Global CSS and Tailwind config

- `package.json` - Dependencies and scripts
- `vite.config.ts` - Vite build configuration
- `tsconfig.json` - TypeScript configuration
- `tailwind.config.js` - Tailwind CSS configuration

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start dev server:
   ```bash
   npm run dev
   ```

3. Open http://localhost:5173

## Build

```bash
npm run build
```

## Architecture

### State Management (Zustand)
- `useAuth` - Authentication state
- `useTyping` - Active typing test state
- `useSession` - Session history
- `useAdapter` - Adapter configuration and recommendations

### Services
- `api.ts` - HTTP client for backend API
- `storage.ts` - Local storage utilities
- `adapter.ts` - Adapter logic and calculations

### Styling
- **Tailwind CSS** for utility classes
- **Responsive design** with mobile-first approach
- **Dark mode** support

## Features

- ✅ User authentication (login/register)
- ✅ Real-time typing test interface
- ✅ Live metrics (WPM, accuracy)
- ✅ Progress dashboard
- ✅ Adaptive difficulty recommendations
- ✅ Session history and analytics
- ✅ User settings and preferences
