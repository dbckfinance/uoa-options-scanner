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

// Goldman Sachs official colors theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#7792b3', // Official Goldman Sachs blue
      light: '#8fa3c4',
      dark: '#5f7a9a',
    },
    secondary: {
      main: '#212121', // Goldman Sachs dark text
      light: '#424242',
      dark: '#000000',
    },
    background: {
      default: '#f7fafc',
      paper: '#ffffff',
    },
    success: {
      main: '#4caf50', // Professional green
      light: '#81c784',
      dark: '#388e3c',
    },
    error: {
      main: '#f44336', // Professional red
      light: '#ef5350',
      dark: '#d32f2f',
    },
    warning: {
      main: '#ff9800', // Professional orange
      light: '#ffb74d',
      dark: '#f57c00',
    },
    info: {
      main: '#7792b3', // Goldman Sachs blue
      light: '#8fa3c4',
      dark: '#5f7a9a',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: { fontWeight: 800, letterSpacing: '-0.02em', color: '#212121' },
    h2: { fontWeight: 800, letterSpacing: '-0.02em', color: '#212121' },
    h3: { fontWeight: 700, letterSpacing: '-0.01em', color: '#212121' },
    h4: { fontWeight: 700, letterSpacing: '-0.01em', color: '#212121' },
    h5: { fontWeight: 600, color: '#424242' },
    h6: { fontWeight: 600, color: '#424242' },
    subtitle1: { fontWeight: 500, color: '#4a5568' },
    button: { fontWeight: 600, letterSpacing: '0.02em', textTransform: 'none' },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          textTransform: 'none',
          fontWeight: 600,
          padding: '12px 24px',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: '0 8px 25px rgba(26, 54, 93, 0.25)',
          },
          '&:active': {
            transform: 'translateY(0)',
          },
        },
        contained: {
          background: 'linear-gradient(135deg, #7792b3 0%, #5f7a9a 100%)',
          '&:hover': {
            background: 'linear-gradient(135deg, #5f7a9a 0%, #7792b3 100%)',
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          boxShadow: '0 4px 20px rgba(119, 146, 179, 0.08)',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 8,
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
          borderRadius: 12,
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          boxShadow: '0 2px 12px rgba(119, 146, 179, 0.1)',
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

  const handleAnalyze = async (ticker: string, mode: string) => {
    setIsLoading(true);
    setError(null);
    setResults(null);

    try {
      const data = await fetchUoaData(ticker, mode);
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
          background: 'linear-gradient(135deg, #7792b3 0%, #5f7a9a 25%, #212121 50%, #5f7a9a 75%, #7792b3 100%)',
          backgroundSize: '400% 400%',
          animation: 'gradientShift 20s ease infinite',
          position: 'relative',
          py: 4,
          '&::before': {
            content: '""',
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: `
              radial-gradient(circle at 20% 20%, rgba(119, 146, 179, 0.15) 0%, transparent 50%),
              radial-gradient(circle at 80% 80%, rgba(33, 33, 33, 0.1) 0%, transparent 50%),
              radial-gradient(circle at 50% 50%, rgba(255, 255, 255, 0.05) 0%, transparent 70%)
            `,
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
        {/* Floating Elements Background - Goldman Sachs Style */}
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
              top: '15%',
              left: '15%',
              width: 120,
              height: 120,
              borderRadius: '50%',
              background: 'radial-gradient(circle, rgba(119, 146, 179, 0.2) 0%, rgba(119, 146, 179, 0.05) 50%, transparent 100%)',
              animation: 'float 8s ease-in-out infinite',
            },
            '&::after': {
              content: '""',
              position: 'absolute',
              bottom: '20%',
              right: '20%',
              width: 180,
              height: 180,
              borderRadius: '50%',
              background: 'radial-gradient(circle, rgba(33, 33, 33, 0.15) 0%, rgba(33, 33, 33, 0.03) 50%, transparent 100%)',
              animation: 'float 10s ease-in-out infinite reverse',
            },
            '@keyframes float': {
              '0%, 100%': { transform: 'translate(0, 0) rotate(0deg) scale(1)' },
              '33%': { transform: 'translate(40px, -40px) rotate(120deg) scale(1.1)' },
              '66%': { transform: 'translate(-30px, 30px) rotate(240deg) scale(0.9)' },
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

