# Unusual Options Activity Frontend

A modern React/TypeScript frontend for analyzing unusual options activity with professional UI design.

## Features

- Modern React 18 with TypeScript
- Material-UI (MUI) component library
- Professional, responsive design
- Real-time data visualization
- Advanced data grid with sorting and filtering
- Comprehensive error handling
- Loading states and user feedback

## Technology Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **UI Library**: Material-UI (MUI)
- **Data Grid**: MUI X Data Grid
- **HTTP Client**: Axios
- **Styling**: Emotion (CSS-in-JS)

## Installation

1. Install dependencies:
```bash
npm install
```

## Development

Start the development server:
```bash
npm run dev
```

The app will be available at http://localhost:3000

## Build

Build for production:
```bash
npm run build
```

Preview production build:
```bash
npm run preview
```

## Project Structure

```
src/
├── components/          # React components
│   ├── TickerInput.tsx  # Ticker input component
│   └── ResultsTable.tsx # Data display component
├── services/            # API services
│   └── api.ts          # Backend communication
├── types/              # TypeScript type definitions
│   └── api.ts          # API response types
├── App.tsx             # Main application component
└── main.tsx            # Application entry point
```

## Components

### TickerInput
- Clean, professional input interface
- Real-time input validation
- Loading states during analysis
- Keyboard navigation support

### ResultsTable
- Advanced data grid with sorting
- Professional data visualization
- Color-coded importance indicators
- Responsive design
- Export capabilities

## API Integration

The frontend communicates with the FastAPI backend running on `http://localhost:8000`.

Key features:
- Automatic error handling
- Request timeout management
- Connection status monitoring
- Type-safe API responses

## Styling

The application uses a professional theme with:
- Modern color palette
- Consistent spacing and typography
- Responsive breakpoints
- Accessible design patterns
- Material Design guidelines

## Error Handling

Comprehensive error handling for:
- Network connectivity issues
- API timeouts
- Invalid ticker symbols
- Server errors
- Empty data responses

## Performance

Optimized for performance with:
- Component lazy loading
- Efficient re-rendering
- Optimized bundle size
- Fast development server (Vite)

## Browser Support

Supports all modern browsers:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

