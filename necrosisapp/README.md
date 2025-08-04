# Cassava Necrosis Analyser Frontend
This is the React + Vite frontend for the Cassava Necrosis Analyser project. It provides a modern, user-friendly interface for uploading cassava root images, viewing analysis results, and managing analysis sessions.

# Features
1. Fast, modern React UI (Vite-powered)
2. Drag-and-drop image upload
3. Analysis results with image previews and downloadable reports(csv)
4. User authentication and session management
5. Analysis history with session renaming and image download support

#  Getting Started
1. Prerequisites
    Node.js (v16 or higher recommended)
    npm or yarn
2. Installation
    a) Clone the repository
    b) Install dependencies: npm install or yarn install
3. Start the development server
    npm run dev
    yarn dev
4. Open your browser

# Configuration
The frontend expects a backend API (Django) to be running and accessible.
If your backend is on a different host/port, update the API URLs in your frontend code (typically in src or via environment variables).

# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.
