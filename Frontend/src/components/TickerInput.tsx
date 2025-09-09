import React, { useState, useEffect } from 'react';
import {
  Box,
  TextField,
  Button,
  Paper,
  Typography,
  InputAdornment,
  Chip,
  ToggleButton,
  ToggleButtonGroup,
  Tooltip,
} from '@mui/material';
import { 
  Search as SearchIcon,
  TrendingUp,
  Analytics,
  Speed,
  FlashOn,
  Assessment
} from '@mui/icons-material';

interface TickerInputProps {
  onAnalyze: (ticker: string, mode: string) => void;
  isLoading: boolean;
}

const TickerInput: React.FC<TickerInputProps> = ({ onAnalyze, isLoading }) => {
  const [ticker, setTicker] = useState<string>('');
  const [mode, setMode] = useState<string>('auto');
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
      onAnalyze(ticker.trim().toUpperCase(), mode);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.toUpperCase().replace(/[^A-Z]/g, '');
    setTicker(value);
  };

  const handleModeChange = (_event: React.MouseEvent<HTMLElement>, newMode: string | null) => {
    if (newMode !== null) {
      setMode(newMode);
    }
  };

  // Popular tickers for suggestion chips
  const popularTickers = ['AAPL', 'TSLA', 'NVDA', 'MSFT', 'META', 'GOOGL'];

  // Dynamic gradient based on animation phase - Goldman Sachs Professional
  // Note: Currently using static gradient, but keeping animationPhase for future use

  return (
    <Paper
      elevation={0}
      sx={{
        p: { xs: 3, sm: 4, md: 6 },
        mb: 4,
        background: 'linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 50%, #1a1a1a 100%)',
        color: 'white',
        position: 'relative',
        overflow: 'hidden',
        borderRadius: '24px',
        border: '1px solid rgba(119, 146, 179, 0.2)',
        backdropFilter: 'blur(20px)',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.05)',
        transition: 'all 0.8s cubic-bezier(0.4, 0, 0.2, 1)',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'radial-gradient(circle at 30% 20%, rgba(119, 146, 179, 0.1) 0%, transparent 60%)',
          pointerEvents: 'none',
        },
        '&::after': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'radial-gradient(circle at 70% 80%, rgba(33, 33, 33, 0.3) 0%, transparent 60%)',
          pointerEvents: 'none',
        }
      }}
    >
      {/* Institutional-Grade Header */}
      <Box sx={{ 
        display: 'flex', 
        flexDirection: 'column', 
        alignItems: 'center',
        mb: 4,
        position: 'relative',
      }}>
        {/* Professional Badge */}
        <Box sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1,
          mb: 3,
          px: 3,
          py: 1,
          borderRadius: '24px',
          background: 'rgba(119, 146, 179, 0.15)',
          border: '1px solid rgba(119, 146, 179, 0.3)',
          backdropFilter: 'blur(20px)',
        }}>
          <Box sx={{
            width: 8,
            height: 8,
            borderRadius: '50%',
            background: '#00ff88',
            animation: 'pulse 2s infinite',
            '@keyframes pulse': {
              '0%, 100%': { opacity: 1 },
              '50%': { opacity: 0.5 },
            }
          }} />
          <Typography variant="caption" sx={{
            color: 'rgba(255, 255, 255, 0.9)',
            fontSize: '0.75rem',
            fontWeight: 600,
            letterSpacing: '0.5px',
            textTransform: 'uppercase',
          }}>
            Live Market Data
          </Typography>
        </Box>

        {/* Main Title - Institutional Style */}
        <Typography
          variant="h1"
          component="h1"
          sx={{
            fontWeight: 300,
            textAlign: 'center',
            mb: 2,
            color: '#ffffff',
            fontSize: { xs: '2.8rem', sm: '3.5rem', md: '4.2rem' },
            letterSpacing: '-0.02em',
            lineHeight: 1.1,
            fontFamily: '"Inter", "Helvetica Neue", Arial, sans-serif',
          }}
        >
          UOA Scanner
        </Typography>

        {/* Subtitle with Professional Styling */}
        <Typography
          variant="h5"
          sx={{
            textAlign: 'center',
            mb: 4,
            color: 'rgba(255, 255, 255, 0.7)',
            fontSize: '1.1rem',
            fontWeight: 400,
            letterSpacing: '0.02em',
            lineHeight: 1.4,
            maxWidth: '600px',
            fontFamily: '"Inter", "Helvetica Neue", Arial, sans-serif',
          }}
        >
          Institutional-grade options flow analysis for professional traders
        </Typography>

        {/* Feature Pills - Professional Grid */}
        <Box sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', sm: 'repeat(3, 1fr)' },
          gap: 2,
          maxWidth: '800px',
          width: '100%',
        }}>
          {[
            { icon: TrendingUp, label: 'Real-time Flow Detection', desc: 'Millisecond latency' },
            { icon: Analytics, label: 'Institutional Analytics', desc: 'Professional-grade data' },
            { icon: Speed, label: 'Advanced Algorithms', desc: 'AI-powered insights' }
          ].map((feature, index) => (
            <Box key={index} sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 2,
              p: 2,
              borderRadius: '12px',
              background: 'rgba(119, 146, 179, 0.08)',
              border: '1px solid rgba(119, 146, 179, 0.15)',
              transition: 'all 0.3s ease',
              '&:hover': {
                background: 'rgba(119, 146, 179, 0.12)',
                transform: 'translateY(-2px)',
              }
            }}>
              <Box sx={{
                width: 40,
                height: 40,
                borderRadius: '10px',
                background: 'rgba(119, 146, 179, 0.2)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
              }}>
                <feature.icon sx={{ color: 'white', fontSize: '1.2rem' }} />
              </Box>
              <Box>
                <Typography variant="body2" sx={{
                  color: 'white',
                  fontWeight: 600,
                  fontSize: '0.9rem',
                  mb: 0.5,
                }}>
                  {feature.label}
                </Typography>
                <Typography variant="caption" sx={{
                  color: 'rgba(255, 255, 255, 0.6)',
                  fontSize: '0.75rem',
                }}>
                  {feature.desc}
                </Typography>
              </Box>
            </Box>
          ))}
        </Box>
      </Box>

      {/* Mode Toggle */}
      <Box sx={{ display: 'flex', justifyContent: 'center', mb: 3 }}>
        <ToggleButtonGroup
          value={mode}
          exclusive
          onChange={handleModeChange}
          disabled={isLoading}
          sx={{
            bgcolor: 'rgba(119, 146, 179, 0.2)',
            borderRadius: '16px',
            border: '2px solid rgba(119, 146, 179, 0.4)',
            '& .MuiToggleButton-root': {
              color: 'white',
              border: 'none',
              borderRadius: '12px',
              px: 3,
              py: 1,
              fontWeight: 600,
              fontSize: '0.9rem',
              transition: 'all 0.3s ease',
              '&:hover': {
                bgcolor: 'rgba(119, 146, 179, 0.3)',
                transform: 'translateY(-1px)',
              },
              '&.Mui-selected': {
                bgcolor: 'rgba(119, 146, 179, 0.5)',
                color: 'white',
                fontWeight: 700,
                '&:hover': {
                  bgcolor: 'rgba(119, 146, 179, 0.6)',
                },
              },
            },
          }}
        >
          <Tooltip title="Auto-detect based on market activity" arrow>
            <ToggleButton value="auto">
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Speed sx={{ fontSize: '1.1rem' }} />
                Auto
              </Box>
            </ToggleButton>
          </Tooltip>
          <Tooltip title="Live Trading - Volume-based analysis (Market Open)" arrow>
            <ToggleButton value="live">
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <FlashOn sx={{ fontSize: '1.1rem' }} />
                Live Trading
              </Box>
            </ToggleButton>
          </Tooltip>
          <Tooltip title="Position Analysis - Open Interest-based analysis (Pre-market)" arrow>
            <ToggleButton value="position">
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Assessment sx={{ fontSize: '1.1rem' }} />
                Position Analysis
              </Box>
            </ToggleButton>
          </Tooltip>
        </ToggleButtonGroup>
      </Box>

      {/* Popular Tickers Chips */}
      <Box sx={{ display: 'flex', justifyContent: 'center', mb: 3, flexWrap: 'wrap', gap: 1 }}>
        {popularTickers.map((symbol) => (
          <Chip
            key={symbol}
            label={symbol}
            onClick={() => !isLoading && setTicker(symbol)}
            sx={{
              bgcolor: 'rgba(119, 146, 179, 0.2)',
              color: 'white',
              border: '2px solid rgba(119, 146, 179, 0.4)',
              fontSize: '0.85rem',
              fontWeight: 600,
              cursor: isLoading ? 'not-allowed' : 'pointer',
              transition: 'all 0.2s ease',
              '&:hover': {
                bgcolor: isLoading ? 'rgba(119, 146, 179, 0.2)' : 'rgba(119, 146, 179, 0.4)',
                transform: isLoading ? 'none' : 'translateY(-2px)',
                boxShadow: isLoading ? 'none' : '0 4px 12px rgba(119, 146, 179, 0.3)',
                border: '2px solid rgba(119, 146, 179, 0.6)',
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
                <SearchIcon sx={{ color: 'rgba(255, 255, 255, 0.7)', fontSize: '1.5rem' }} />
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
              border: '2px solid rgba(119, 146, 179, 0.3)',
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 1)',
                transform: 'translateY(-2px)',
                boxShadow: '0 8px 25px rgba(119, 146, 179, 0.2)',
                border: '2px solid rgba(119, 146, 179, 0.5)',
              },
              '&.Mui-focused': {
                backgroundColor: 'rgba(255, 255, 255, 1)',
                transform: 'translateY(-2px)',
                boxShadow: '0 12px 35px rgba(119, 146, 179, 0.3)',
                border: '2px solid rgba(119, 146, 179, 0.7)',
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
            bgcolor: 'rgba(119, 146, 179, 0.3)',
            border: '2px solid rgba(119, 146, 179, 0.6)',
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
              background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent)',
              transition: 'left 0.5s',
            },
            '&:hover': {
              bgcolor: 'rgba(119, 146, 179, 0.5)',
              border: '2px solid rgba(119, 146, 179, 0.8)',
              transform: 'translateY(-3px)',
              boxShadow: '0 10px 25px rgba(119, 146, 179, 0.3)',
              '&::before': {
                left: '100%',
              },
            },
            '&:active': {
              transform: 'translateY(-1px)',
            },
            '&:disabled': {
              bgcolor: 'rgba(119, 146, 179, 0.1)',
              border: '2px solid rgba(119, 146, 179, 0.3)',
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
          {mode === 'live' && '🔴 Ready to scan <strong>{ticker}</strong> for live trading activity (Volume-based)'}
          {mode === 'position' && '🔵 Ready to scan <strong>{ticker}</strong> for position analysis (Open Interest-based)'}
          {mode === 'auto' && '🤖 Ready to scan <strong>{ticker}</strong> for unusual options activity (Auto-detect mode)'}
        </Typography>
      )}
    </Paper>
  );
};

export default TickerInput;

