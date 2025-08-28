import React, { useState, useEffect } from 'react';
import {
  Box,
  TextField,
  Button,
  Paper,
  Typography,
  InputAdornment,
  Chip,
  Avatar,
} from '@mui/material';
import { 
  Search as SearchIcon,
  TrendingUp,
  Analytics,
  Speed
} from '@mui/icons-material';

interface TickerInputProps {
  onAnalyze: (ticker: string) => void;
  isLoading: boolean;
}

const TickerInput: React.FC<TickerInputProps> = ({ onAnalyze, isLoading }) => {
  const [ticker, setTicker] = useState<string>('');
  const [animationPhase, setAnimationPhase] = useState<number>(0);

  // Animation cycle for background gradient
  useEffect(() => {
    const interval = setInterval(() => {
      setAnimationPhase(prev => (prev + 1) % 4);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (ticker.trim() && !isLoading) {
      onAnalyze(ticker.trim().toUpperCase());
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.toUpperCase().replace(/[^A-Z]/g, '');
    setTicker(value);
  };

  // Popular tickers for suggestion chips
  const popularTickers = ['AAPL', 'TSLA', 'NVDA', 'MSFT', 'META', 'GOOGL'];

  // Dynamic gradient based on animation phase - PROFESSIONAL BLUE-GREEN
  const getAnimatedGradient = () => {
    const gradients = [
      'linear-gradient(135deg, #667eea 0%, #4facfe 50%, #00d4aa 100%)',
      'linear-gradient(135deg, #2196f3 0%, #21cbf3 50%, #00bcd4 100%)', 
      'linear-gradient(135deg, #00bcd4 0%, #4dd0e1 50%, #26a69a 100%)',
      'linear-gradient(135deg, #5b73e8 0%, #3f51b5 50%, #2196f3 100%)'
    ];
    return gradients[animationPhase];
  };

  return (
    <Paper
      elevation={6}
      sx={{
        p: 4,
        mb: 4,
        background: getAnimatedGradient(),
        color: 'white',
        position: 'relative',
        overflow: 'hidden',
        transition: 'all 0.8s cubic-bezier(0.4, 0, 0.2, 1)',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'radial-gradient(circle at 20% 80%, rgba(255,255,255,0.1) 0%, transparent 50%)',
          pointerEvents: 'none',
        },
        '&::after': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'radial-gradient(circle at 80% 20%, rgba(255,255,255,0.15) 0%, transparent 50%)',
          pointerEvents: 'none',
        }
      }}
    >
      {/* Header with Icons */}
      <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <Avatar 
            sx={{ 
              bgcolor: 'rgba(255,255,255,0.2)', 
              animation: 'pulse 2s infinite',
              '@keyframes pulse': {
                '0%, 100%': { transform: 'scale(1)', opacity: 0.8 },
                '50%': { transform: 'scale(1.1)', opacity: 1 },
              }
            }}
          >
            <TrendingUp />
          </Avatar>
          <Avatar 
            sx={{ 
              bgcolor: 'rgba(255,255,255,0.2)', 
              animation: 'pulse 2s infinite 0.5s',
              '@keyframes pulse': {
                '0%, 100%': { transform: 'scale(1)', opacity: 0.8 },
                '50%': { transform: 'scale(1.1)', opacity: 1 },
              }
            }}
          >
            <Analytics />
          </Avatar>
          <Avatar 
            sx={{ 
              bgcolor: 'rgba(255,255,255,0.2)', 
              animation: 'pulse 2s infinite 1s',
              '@keyframes pulse': {
                '0%, 100%': { transform: 'scale(1)', opacity: 0.8 },
                '50%': { transform: 'scale(1.1)', opacity: 1 },
              }
            }}
          >
            <Speed />
          </Avatar>
        </Box>
      </Box>

      <Typography
        variant="h3"
        component="h1"
        gutterBottom
        sx={{
          fontWeight: 700,
          textAlign: 'center',
          mb: 1,
          background: 'linear-gradient(45deg, #ffffff 30%, rgba(255,255,255,0.8) 100%)',
          backgroundClip: 'text',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          textShadow: '0 2px 4px rgba(0,0,0,0.1)',
          letterSpacing: '-0.5px',
        }}
      >
        UOA Scanner Pro
      </Typography>
      
      <Typography
        variant="subtitle1"
        sx={{
          textAlign: 'center',
          mb: 3,
          opacity: 0.95,
          fontSize: '1.1rem',
          fontWeight: 300,
          letterSpacing: '0.5px',
        }}
      >
        🚀 Advanced Options Flow Analysis • Real-time Smart Money Detection
      </Typography>

      {/* Popular Tickers Chips */}
      <Box sx={{ display: 'flex', justifyContent: 'center', mb: 3, flexWrap: 'wrap', gap: 1 }}>
        {popularTickers.map((symbol) => (
          <Chip
            key={symbol}
            label={symbol}
            onClick={() => !isLoading && setTicker(symbol)}
            sx={{
              bgcolor: 'rgba(255,255,255,0.15)',
              color: 'white',
              border: '1px solid rgba(255,255,255,0.3)',
              fontSize: '0.85rem',
              fontWeight: 600,
              cursor: isLoading ? 'not-allowed' : 'pointer',
              transition: 'all 0.2s ease',
              '&:hover': {
                bgcolor: isLoading ? 'rgba(255,255,255,0.15)' : 'rgba(255,255,255,0.25)',
                transform: isLoading ? 'none' : 'translateY(-2px)',
                boxShadow: isLoading ? 'none' : '0 4px 12px rgba(0,0,0,0.2)',
              },
            }}
          />
        ))}
      </Box>

      {/* Main Input Form */}
      <Box
        component="form"
        onSubmit={handleSubmit}
        sx={{
          display: 'flex',
          gap: 2,
          maxWidth: 600,
          mx: 'auto',
          alignItems: 'center',
          flexDirection: { xs: 'column', sm: 'row' },
        }}
      >
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Enter ticker symbol..."
          value={ticker}
          onChange={handleInputChange}
          disabled={isLoading}
          inputProps={{
            maxLength: 10,
            style: { 
              textAlign: 'center', 
              fontSize: '1.4rem', 
              fontWeight: 700,
              letterSpacing: '2px',
            },
          }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon sx={{ color: 'rgba(0, 0, 0, 0.5)', fontSize: '1.5rem' }} />
              </InputAdornment>
            ),
          }}
          sx={{
            '& .MuiOutlinedInput-root': {
              backgroundColor: 'rgba(255, 255, 255, 0.95)',
              borderRadius: '16px',
              height: '64px',
              fontSize: '1.2rem',
              backdropFilter: 'blur(10px)',
              border: '2px solid rgba(255,255,255,0.2)',
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 1)',
                transform: 'translateY(-2px)',
                boxShadow: '0 8px 25px rgba(0,0,0,0.15)',
                border: '2px solid rgba(255,255,255,0.4)',
              },
              '&.Mui-focused': {
                backgroundColor: 'rgba(255, 255, 255, 1)',
                transform: 'translateY(-2px)',
                boxShadow: '0 12px 35px rgba(0,0,0,0.2)',
                border: '2px solid rgba(255,255,255,0.6)',
              },
            },
          }}
        />
        
        <Button
          type="submit"
          variant="contained"
          size="large"
          disabled={!ticker.trim() || isLoading}
          sx={{
            minWidth: 150,
            height: 64,
            borderRadius: '16px',
            bgcolor: 'rgba(255, 255, 255, 0.2)',
            border: '2px solid rgba(255, 255, 255, 0.4)',
            color: 'white',
            fontWeight: 700,
            fontSize: '1.1rem',
            letterSpacing: '1px',
            textTransform: 'uppercase',
            position: 'relative',
            overflow: 'hidden',
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            '&::before': {
              content: '""',
              position: 'absolute',
              top: 0,
              left: '-100%',
              width: '100%',
              height: '100%',
              background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent)',
              transition: 'left 0.5s',
            },
            '&:hover': {
              bgcolor: 'rgba(255, 255, 255, 0.3)',
              border: '2px solid rgba(255, 255, 255, 0.6)',
              transform: 'translateY(-3px)',
              boxShadow: '0 10px 25px rgba(0,0,0,0.2)',
              '&::before': {
                left: '100%',
              },
            },
            '&:active': {
              transform: 'translateY(-1px)',
            },
            '&:disabled': {
              bgcolor: 'rgba(255, 255, 255, 0.1)',
              border: '2px solid rgba(255, 255, 255, 0.2)',
              color: 'rgba(255, 255, 255, 0.5)',
              transform: 'none',
              boxShadow: 'none',
            },
          }}
        >
          {isLoading ? (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box
                sx={{
                  width: 20,
                  height: 20,
                  borderRadius: '50%',
                  border: '2px solid rgba(255,255,255,0.3)',
                  borderTop: '2px solid white',
                  animation: 'spin 1s linear infinite',
                  '@keyframes spin': {
                    '0%': { transform: 'rotate(0deg)' },
                    '100%': { transform: 'rotate(360deg)' },
                  },
                }}
              />
              Analyzing
            </Box>
          ) : (
            'Analyze'
          )}
        </Button>
      </Box>
      
      {ticker && !isLoading && (
        <Typography
          variant="body2"
          sx={{
            textAlign: 'center',
            mt: 3,
            opacity: 0.9,
            fontSize: '0.95rem',
            animation: 'fadeIn 0.5s ease-in',
            '@keyframes fadeIn': {
              from: { opacity: 0, transform: 'translateY(10px)' },
              to: { opacity: 0.9, transform: 'translateY(0)' },
            },
          }}
        >
          ⚡ Ready to scan <strong>{ticker}</strong> for unusual options activity
        </Typography>
      )}
    </Paper>
  );
};

export default TickerInput;

