import React, { useState } from 'react';
import {
  Container,
  CssBaseline,
  Box,
  Alert,
  Snackbar,
} from '@mui/material';
import { ThemeProvider, createTheme } from '@mui/material/styles';

import TickerInput from './components/TickerInput';
import ResultsTable from './components/ResultsTable';
import { fetchUoaData, ApiError } from './services/api';
import { UOAResponse } from './types/api';

// Ultra-modern, professional theme with enhanced animations
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#667eea',
      light: '#8fa7ff',
      dark: '#4f56c9',
    },
    secondary: {
      main: '#764ba2',
      light: '#a478d6',
      dark: '#543770',
    },
    background: {
      default: '#f8fafc',
      paper: '#ffffff',
    },
    success: {
      main: '#4caf50',
      light: '#81c784',
      dark: '#388e3c',
    },
    error: {
      main: '#f44336',
      light: '#ef5350',
      dark: '#d32f2f',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: { fontWeight: 800, letterSpacing: '-0.02em' },
    h2: { fontWeight: 800, letterSpacing: '-0.02em' },
    h3: { fontWeight: 700, letterSpacing: '-0.01em' },
    h4: { fontWeight: 700, letterSpacing: '-0.01em' },
    h5: { fontWeight: 600 },
    h6: { fontWeight: 600 },
    subtitle1: { fontWeight: 500 },
    button: { fontWeight: 600, letterSpacing: '0.02em' },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          textTransform: 'none',
          fontWeight: 700,
          padding: '12px 24px',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: '0 8px 25px rgba(0,0,0,0.15)',
          },
          '&:active': {
            transform: 'translateY(0)',
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 20,
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          fontWeight: 600,
          transition: 'all 0.2s ease',
          '&:hover': {
            transform: 'translateY(-1px)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        },
      },
    },
  },
});

const App: React.FC = () => {
  const [results, setResults] = useState<UOAResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [snackbarOpen, setSnackbarOpen] = useState<boolean>(false);

  const handleAnalyze = async (ticker: string) => {
    setIsLoading(true);
    setError(null);
    setResults(null);

    try {
      const data = await fetchUoaData(ticker);
      setResults(data);
      
      // Show success snackbar
      if (data.unusualContracts.length === 0) {
        setSnackbarOpen(true);
      }
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('An unexpected error occurred. Please try again.');
      }
      console.error('Error analyzing ticker:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSnackbarClose = () => {
    setSnackbarOpen(false);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box
        sx={{
          minHeight: '100vh',
          background: 'linear-gradient(135deg, #667eea 0%, #4facfe 25%, #00d4aa 50%, #5b73e8 75%, #2196f3 100%)',
          backgroundSize: '400% 400%',
          animation: 'gradientShift 15s ease infinite',
          position: 'relative',
          py: 4,
          '&::before': {
            content: '""',
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'radial-gradient(circle at 25% 25%, rgba(255,255,255,0.2) 0%, transparent 50%), radial-gradient(circle at 75% 75%, rgba(255,255,255,0.1) 0%, transparent 50%)',
            pointerEvents: 'none',
            zIndex: 0,
          },
          '@keyframes gradientShift': {
            '0%': { backgroundPosition: '0% 50%' },
            '50%': { backgroundPosition: '100% 50%' },
            '100%': { backgroundPosition: '0% 50%' },
          },
        }}
      >
        {/* Floating Elements Background */}
        <Box
          sx={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            pointerEvents: 'none',
            zIndex: 0,
            '&::before': {
              content: '""',
              position: 'absolute',
              top: '10%',
              left: '10%',
              width: 100,
              height: 100,
              borderRadius: '50%',
              background: 'rgba(255,255,255,0.1)',
              animation: 'float 6s ease-in-out infinite',
            },
            '&::after': {
              content: '""',
              position: 'absolute',
              bottom: '10%',
              right: '10%',
              width: 150,
              height: 150,
              borderRadius: '50%',
              background: 'rgba(255,255,255,0.08)',
              animation: 'float 8s ease-in-out infinite reverse',
            },
            '@keyframes float': {
              '0%, 100%': { transform: 'translate(0, 0) rotate(0deg)' },
              '33%': { transform: 'translate(30px, -30px) rotate(120deg)' },
              '66%': { transform: 'translate(-20px, 20px) rotate(240deg)' },
            },
          }}
        />
        
        <Container 
          maxWidth="xl" 
          sx={{ 
            position: 'relative', 
            zIndex: 1,
            animation: 'fadeInUp 0.8s ease-out',
            '@keyframes fadeInUp': {
              from: { opacity: 0, transform: 'translateY(30px)' },
              to: { opacity: 1, transform: 'translateY(0)' },
            },
          }}
        >
          <Box
            sx={{
              transition: 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)',
              transform: isLoading ? 'scale(0.98)' : 'scale(1)',
            }}
          >
            <TickerInput onAnalyze={handleAnalyze} isLoading={isLoading} />
          </Box>
          
          <Box
            sx={{
              animation: results ? 'slideInFromBottom 0.6s ease-out' : 'none',
              '@keyframes slideInFromBottom': {
                from: { opacity: 0, transform: 'translateY(50px)' },
                to: { opacity: 1, transform: 'translateY(0)' },
              },
            }}
          >
            <ResultsTable data={results} isLoading={isLoading} error={error} />
          </Box>
        </Container>
      </Box>

      {/* Enhanced Success Snackbar */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={5000}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        sx={{
          '& .MuiSnackbarContent-root': {
            borderRadius: '16px',
            minWidth: 'none',
          },
        }}
      >
        <Alert 
          onClose={handleSnackbarClose} 
          severity="info" 
          variant="filled"
          sx={{
            borderRadius: '16px',
            fontWeight: 600,
            fontSize: '1rem',
            boxShadow: '0 8px 25px rgba(0,0,0,0.15)',
            animation: 'slideInUp 0.4s ease-out',
            '@keyframes slideInUp': {
              from: { opacity: 0, transform: 'translateY(50px)' },
              to: { opacity: 1, transform: 'translateY(0)' },
            },
          }}
        >
          ✅ Analysis completed • No unusual activity detected for this ticker
        </Alert>
      </Snackbar>
    </ThemeProvider>
  );
};

export default App;

