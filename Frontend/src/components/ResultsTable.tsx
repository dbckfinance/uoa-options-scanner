import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Chip,
  Alert,
  Grid,
  Card,
  CardContent,
  Avatar,
  Divider,
  IconButton,
  Collapse,
} from '@mui/material';
import {
  TrendingUp as CallIcon,
  TrendingDown as PutIcon,
  ExpandMore as ExpandMoreIcon,
  Info as InfoIcon,
  AccessTime as TimeIcon,
  AttachMoney as MoneyIcon,
  ShowChart as ChartIcon,
  Speed as RatioIcon,
  BarChart as VolumeIcon,
  LocalAtm as PriceIcon,
} from '@mui/icons-material';
import { OptionContract, UOAResponse } from '../types/api';

interface ResultsTableProps {
  data: UOAResponse | null;
  isLoading: boolean;
  error: string | null;
}

const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
};

const formatLargeCurrency = (value: number): string => {
  if (value >= 1000000) {
    return `$${(value / 1000000).toFixed(2)}M`;
  } else if (value >= 1000) {
    return `$${(value / 1000).toFixed(0)}K`;
  }
  return formatCurrency(value);
};

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
};

// Modern Option Card Component
const OptionCard: React.FC<{ contract: OptionContract; index: number }> = ({ contract, index }) => {
  const [expanded, setExpanded] = useState(false);
  
  const isCall = contract.type === 'call';
  const isHighVolume = contract.volumeToOiRatio >= 4.0;
  const isLargePremium = contract.premiumSpent >= 100000;

  // Calculate time to expiration for visual indicator
  const expirationDate = new Date(contract.expirationDate);
  const daysToExpiry = Math.floor((expirationDate.getTime() - Date.now()) / (1000 * 60 * 60 * 24));
  
  const getSignalStrength = () => {
    if (contract.volumeToOiRatio >= 6) return 'EXTREME';
    if (contract.volumeToOiRatio >= 3) return 'HIGH'; 
    return 'MODERATE';
  };

  const getSignalColor = () => {
    const strength = getSignalStrength();
    if (strength === 'EXTREME') return '#5f7a9a'; // Goldman Sachs dark blue
    if (strength === 'HIGH') return '#8fa3c4';    // Goldman Sachs light blue
    return '#7792b3';                             // Goldman Sachs blue
  };

  return (
    <Card
      sx={{
        mb: 2,
        borderRadius: '16px',
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        border: `2px solid ${isHighVolume ? getSignalColor() : 'rgba(0,0,0,0.12)'}`,
        position: 'relative',
        overflow: 'hidden',
        animation: `slideInUp 0.6s ease-out ${index * 0.1}s both`,
        '@keyframes slideInUp': {
          from: { 
            opacity: 0, 
            transform: 'translateY(30px)',
          },
          to: { 
            opacity: 1, 
            transform: 'translateY(0)',
          },
        },
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: `0 12px 40px rgba(${isCall ? '143, 163, 196' : '95, 122, 154'}, 0.3)`,
            borderColor: isCall ? '#8fa3c4' : '#5f7a9a',
          },
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          width: '4px',
          height: '100%',
          background: `linear-gradient(180deg, ${isCall ? '#8fa3c4' : '#5f7a9a'}, ${isCall ? '#7792b3' : '#8fa3c4'})`,
        }
      }}
    >
      <CardContent sx={{ p: 3 }}>
        {/* Header Row */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Avatar
              sx={{
                bgcolor: isCall ? '#8fa3c4' : '#5f7a9a',
                width: 48,
                height: 48,
                animation: 'pulse 2s infinite',
                '@keyframes pulse': {
                  '0%, 100%': { boxShadow: `0 0 0 0 ${isCall ? 'rgba(143, 163, 196, 0.7)' : 'rgba(95, 122, 154, 0.7)'}` },
                  '50%': { boxShadow: `0 0 0 8px ${isCall ? 'rgba(143, 163, 196, 0)' : 'rgba(95, 122, 154, 0)'}` },
                },
              }}
            >
              {isCall ? <CallIcon fontSize="large" /> : <PutIcon fontSize="large" />}
            </Avatar>
            
            <Box>
              <Typography variant="h6" sx={{ fontWeight: 700, color: 'white' }}>
                ${contract.strike} {contract.type.toUpperCase()}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.9rem' }}>
                Expires {formatDate(contract.expirationDate)} • {daysToExpiry} days
              </Typography>
            </Box>
          </Box>

          <Box sx={{ textAlign: 'right' }}>
            <Chip
              label={getSignalStrength()}
              sx={{
                bgcolor: getSignalColor(),
                color: 'white',
                fontWeight: 700,
                fontSize: '0.8rem',
                animation: isHighVolume ? 'glow 2s ease-in-out infinite alternate' : 'none',
                '@keyframes glow': {
                  from: { boxShadow: `0 0 5px ${getSignalColor()}` },
                  to: { boxShadow: `0 0 20px ${getSignalColor()}` },
                },
              }}
            />
          </Box>
        </Box>

        {/* Modern Interactive Metrics Row */}
        <Grid container spacing={2} sx={{ mb: 2 }}>
          {/* Volume/OI Ratio - Interactive Card */}
          <Grid item xs={6} sm={3}>
            <Box sx={{ 
              textAlign: 'center', 
              p: 2.5, 
              background: 'linear-gradient(135deg, rgba(26, 54, 93, 0.1) 0%, rgba(45, 74, 105, 0.05) 100%)',
              borderRadius: '16px',
              border: '2px solid rgba(26, 54, 93, 0.15)',
              position: 'relative',
              cursor: 'pointer',
              overflow: 'hidden',
              transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
              animation: `metricSlideIn 0.6s ease-out ${0 * 0.1}s both`,
              backdropFilter: 'blur(10px)',
              boxShadow: '0 4px 20px rgba(26, 54, 93, 0.1)',
              '&:hover': { 
                bgcolor: 'rgba(26, 54, 93, 0.08)',
                transform: 'translateY(-4px) scale(1.02)',
                boxShadow: '0 12px 35px rgba(26, 54, 93, 0.25)',
                border: '2px solid rgba(26, 54, 93, 0.3)',
                '&::before': {
                  opacity: 1,
                },
              },
              '&::before': {
                content: '""',
                position: 'absolute',
                top: 0,
                left: '-100%',
                width: '100%',
                height: '100%',
                background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent)',
                transition: 'left 0.6s ease',
                opacity: 0,
              },
              '&:hover::before': {
                left: '100%',
                opacity: 1,
              },
              '@keyframes metricSlideIn': {
                from: { opacity: 0, transform: 'translateY(20px) scale(0.95)' },
                to: { opacity: 1, transform: 'translateY(0) scale(1)' },
              },
            }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 1 }}>
                <Avatar sx={{ 
                  bgcolor: 'rgba(26, 54, 93, 0.15)', 
                  width: 36, 
                  height: 36,
                  animation: 'pulse 2s infinite',
                  '@keyframes pulse': {
                    '0%, 100%': { transform: 'scale(1)', opacity: 0.8 },
                    '50%': { transform: 'scale(1.1)', opacity: 1 },
                  },
                }}>
                  <RatioIcon sx={{ fontSize: '1.2rem', color: '#1a365d' }} />
                </Avatar>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ 
                fontSize: '0.7rem', 
                mb: 1, 
                fontWeight: 700,
                letterSpacing: '0.05em',
                textTransform: 'uppercase'
              }}>
                Volume/OI Ratio
              </Typography>
              <Typography variant="h5" sx={{ 
                fontWeight: 800, 
                color: '#212121',
                fontSize: '1.5rem',
                textShadow: '0 2px 4px rgba(0,0,0,0.1)',
              }}>
                {contract.volumeToOiRatio.toFixed(2)}x
              </Typography>
            </Box>
          </Grid>
          
          {/* Premium Spent - Interactive Card */}
          <Grid item xs={6} sm={3}>
            <Box sx={{ 
              textAlign: 'center', 
              p: 2.5, 
              background: 'linear-gradient(135deg, rgba(212, 175, 55, 0.1) 0%, rgba(230, 197, 71, 0.05) 100%)',
              borderRadius: '16px',
              border: '2px solid rgba(212, 175, 55, 0.15)',
              position: 'relative',
              cursor: 'pointer',
              overflow: 'hidden',
              transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
              animation: `metricSlideIn 0.6s ease-out ${1 * 0.1}s both`,
              backdropFilter: 'blur(10px)',
              boxShadow: '0 4px 20px rgba(212, 175, 55, 0.1)',
              '&:hover': { 
                bgcolor: 'rgba(212, 175, 55, 0.08)',
                transform: 'translateY(-4px) scale(1.02)',
                boxShadow: '0 12px 35px rgba(212, 175, 55, 0.25)',
                border: '2px solid rgba(212, 175, 55, 0.3)',
                '&::before': {
                  opacity: 1,
                },
              },
              '&::before': {
                content: '""',
                position: 'absolute',
                top: 0,
                left: '-100%',
                width: '100%',
                height: '100%',
                background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent)',
                transition: 'left 0.6s ease',
                opacity: 0,
              },
              '&:hover::before': {
                left: '100%',
                opacity: 1,
              },
            }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 1 }}>
                <Avatar sx={{ 
                  bgcolor: 'rgba(212, 175, 55, 0.15)', 
                  width: 36, 
                  height: 36,
                  animation: 'pulse 2s infinite 0.3s',
                  '@keyframes pulse': {
                    '0%, 100%': { transform: 'scale(1)', opacity: 0.8 },
                    '50%': { transform: 'scale(1.1)', opacity: 1 },
                  },
                }}>
                  <MoneyIcon sx={{ fontSize: '1.2rem', color: '#d4af37' }} />
                </Avatar>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ 
                fontSize: '0.7rem', 
                mb: 1, 
                fontWeight: 700,
                letterSpacing: '0.05em',
                textTransform: 'uppercase'
              }}>
                Premium Spent
              </Typography>
              <Typography variant="h5" sx={{ 
                fontWeight: 800, 
                color: '#212121',
                fontSize: '1.5rem',
                textShadow: '0 2px 4px rgba(0,0,0,0.1)',
              }}>
                {formatLargeCurrency(contract.premiumSpent)}
              </Typography>
            </Box>
          </Grid>

          {/* Volume - Interactive Card */}
          <Grid item xs={6} sm={3}>
            <Box sx={{ 
              textAlign: 'center', 
              p: 2.5, 
              background: 'linear-gradient(135deg, rgba(75, 85, 99, 0.1) 0%, rgba(107, 114, 128, 0.05) 100%)',
              borderRadius: '16px',
              border: '2px solid rgba(75, 85, 99, 0.15)',
              position: 'relative',
              cursor: 'pointer',
              overflow: 'hidden',
              transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
              animation: `metricSlideIn 0.6s ease-out ${2 * 0.1}s both`,
              backdropFilter: 'blur(10px)',
              boxShadow: '0 4px 20px rgba(75, 85, 99, 0.1)',
              '&:hover': { 
                bgcolor: 'rgba(75, 85, 99, 0.08)',
                transform: 'translateY(-4px) scale(1.02)',
                boxShadow: '0 12px 35px rgba(75, 85, 99, 0.25)',
                border: '2px solid rgba(75, 85, 99, 0.3)',
                '&::before': {
                  opacity: 1,
                },
              },
              '&::before': {
                content: '""',
                position: 'absolute',
                top: 0,
                left: '-100%',
                width: '100%',
                height: '100%',
                background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent)',
                transition: 'left 0.6s ease',
                opacity: 0,
              },
              '&:hover::before': {
                left: '100%',
                opacity: 1,
              },
            }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 1 }}>
                <Avatar sx={{ 
                  bgcolor: 'rgba(75, 85, 99, 0.15)', 
                  width: 36, 
                  height: 36,
                  animation: 'pulse 2s infinite 0.6s',
                  '@keyframes pulse': {
                    '0%, 100%': { transform: 'scale(1)', opacity: 0.8 },
                    '50%': { transform: 'scale(1.1)', opacity: 1 },
                  },
                }}>
                  <VolumeIcon sx={{ fontSize: '1.2rem', color: '#4b5563' }} />
                </Avatar>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ 
                fontSize: '0.7rem', 
                mb: 1, 
                fontWeight: 700,
                letterSpacing: '0.05em',
                textTransform: 'uppercase'
              }}>
                Volume
              </Typography>
              <Typography variant="h5" sx={{ 
                fontWeight: 800, 
                color: '#212121',
                fontSize: '1.5rem',
                textShadow: '0 2px 4px rgba(0,0,0,0.1)',
              }}>
                {contract.volume.toLocaleString()}
              </Typography>
            </Box>
          </Grid>

          {/* Last Price - Interactive Card */}
          <Grid item xs={6} sm={3}>
            <Box sx={{ 
              textAlign: 'center', 
              p: 2.5, 
              background: 'linear-gradient(135deg, rgba(49, 130, 206, 0.1) 0%, rgba(99, 179, 237, 0.05) 100%)',
              borderRadius: '16px',
              border: '2px solid rgba(49, 130, 206, 0.15)',
              position: 'relative',
              cursor: 'pointer',
              overflow: 'hidden',
              transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
              animation: `metricSlideIn 0.6s ease-out ${3 * 0.1}s both`,
              backdropFilter: 'blur(10px)',
              boxShadow: '0 4px 20px rgba(49, 130, 206, 0.1)',
              '&:hover': { 
                bgcolor: 'rgba(49, 130, 206, 0.08)',
                transform: 'translateY(-4px) scale(1.02)',
                boxShadow: '0 12px 35px rgba(49, 130, 206, 0.25)',
                border: '2px solid rgba(49, 130, 206, 0.3)',
                '&::before': {
                  opacity: 1,
                },
              },
              '&::before': {
                content: '""',
                position: 'absolute',
                top: 0,
                left: '-100%',
                width: '100%',
                height: '100%',
                background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent)',
                transition: 'left 0.6s ease',
                opacity: 0,
              },
              '&:hover::before': {
                left: '100%',
                opacity: 1,
              },
            }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 1 }}>
                <Avatar sx={{ 
                  bgcolor: 'rgba(49, 130, 206, 0.15)', 
                  width: 36, 
                  height: 36,
                  animation: 'pulse 2s infinite 0.9s',
                  '@keyframes pulse': {
                    '0%, 100%': { transform: 'scale(1)', opacity: 0.8 },
                    '50%': { transform: 'scale(1.1)', opacity: 1 },
                  },
                }}>
                  <PriceIcon sx={{ fontSize: '1.2rem', color: '#3182ce' }} />
                </Avatar>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ 
                fontSize: '0.7rem', 
                mb: 1, 
                fontWeight: 700,
                letterSpacing: '0.05em',
                textTransform: 'uppercase'
              }}>
                Last Price
              </Typography>
              <Typography variant="h5" sx={{ 
                fontWeight: 800, 
                color: '#212121',
                fontSize: '1.5rem',
                textShadow: '0 2px 4px rgba(0,0,0,0.1)',
              }}>
                {formatCurrency(contract.lastPrice)}
              </Typography>
            </Box>
          </Grid>
        </Grid>

        {/* Expand Button */}
        <Box sx={{ display: 'flex', justifyContent: 'center' }}>
          <IconButton
            onClick={() => setExpanded(!expanded)}
            sx={{
              transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)',
              transition: 'transform 0.3s',
              bgcolor: 'rgba(0,0,0,0.04)',
              '&:hover': { bgcolor: 'rgba(0,0,0,0.08)' },
            }}
          >
            <ExpandMoreIcon />
          </IconButton>
        </Box>

        {/* Expanded Details */}
        <Collapse in={expanded}>
          <Divider sx={{ my: 2 }} />
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                <TimeIcon sx={{ fontSize: 16, mr: 1, verticalAlign: 'middle' }} />
                Contract Details
              </Typography>
              <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.85rem', mb: 1 }}>
                {contract.contractSymbol}
              </Typography>
              <Typography variant="body2">
                Open Interest: <strong>{contract.openInterest.toLocaleString()}</strong>
              </Typography>
              <Typography variant="body2">
                Underlying: <strong>{formatCurrency(contract.underlyingPrice)}</strong>
              </Typography>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                <ChartIcon sx={{ fontSize: 16, mr: 1, verticalAlign: 'middle' }} />
                Risk Indicators
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {daysToExpiry <= 7 && (
                  <Chip 
                    label="SHORT DTE" 
                    size="small" 
                    sx={{ 
                      bgcolor: '#8fa3c4', 
                      color: 'white', 
                      fontWeight: 600,
                      fontSize: '0.75rem'
                    }} 
                  />
                )}
                {isLargePremium && (
                  <Chip 
                    label="BIG MONEY" 
                    size="small" 
                    sx={{ 
                      bgcolor: '#5f7a9a', 
                      color: 'white', 
                      fontWeight: 600,
                      fontSize: '0.75rem'
                    }} 
                  />
                )}
                {contract.volumeToOiRatio >= 5 && (
                  <Chip 
                    label="HOT FLOW" 
                    size="small" 
                    sx={{ 
                      bgcolor: '#7792b3', 
                      color: 'white', 
                      fontWeight: 600,
                      fontSize: '0.75rem'
                    }} 
                  />
                )}
              </Box>
            </Grid>
          </Grid>
        </Collapse>
      </CardContent>
    </Card>
  );
};

const ResultsTable: React.FC<ResultsTableProps> = ({ data, isLoading, error }) => {
  if (isLoading) {
    return (
      <Box sx={{ position: 'relative', minHeight: '400px' }}>
        {/* Modern Loading Screen */}
        <Paper
          elevation={3}
          sx={{
            p: 6,
            textAlign: 'center',
            background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
            position: 'relative',
            overflow: 'hidden',
          }}
        >
          {/* Animated Background */}
          <Box
            sx={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: 'linear-gradient(45deg, rgba(103, 126, 234, 0.1), rgba(118, 75, 162, 0.1))',
              animation: 'wave 3s ease-in-out infinite',
              '@keyframes wave': {
                '0%, 100%': { transform: 'translateX(-100%)' },
                '50%': { transform: 'translateX(100%)' },
              },
            }}
          />
          
          {/* Loading Content */}
          <Box sx={{ position: 'relative', zIndex: 1 }}>
            {/* Animated Logo */}
            <Box sx={{ display: 'flex', justifyContent: 'center', mb: 3 }}>
              <Box
                sx={{
                  width: 80,
                  height: 80,
                  borderRadius: '50%',
                  background: 'linear-gradient(45deg, #667eea, #4facfe)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  animation: 'rotate 2s linear infinite',
                  '@keyframes rotate': {
                    '0%': { transform: 'rotate(0deg)' },
                    '100%': { transform: 'rotate(360deg)' },
                  },
                }}
              >
                <Box
                  sx={{
                    width: 60,
                    height: 60,
                    borderRadius: '50%',
                    background: 'white',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <CallIcon sx={{ fontSize: '2rem', color: '#667eea' }} />
                </Box>
              </Box>
            </Box>

            <Typography
              variant="h4"
              sx={{
                fontWeight: 700,
                color: '#2d3748',
                mb: 2,
                background: 'linear-gradient(45deg, #667eea, #4facfe)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              Analyzing Options Flow
            </Typography>

            {/* Progress Steps */}
            <Box sx={{ mb: 4, display: 'flex', justifyContent: 'center', gap: 2 }}>
              {['Fetching Price', 'Loading Chains', 'Analyzing Flows'].map((step, index) => (
                <Chip
                  key={step}
                  label={step}
                  sx={{
                    bgcolor: 'rgba(103, 126, 234, 0.1)',
                    border: '2px solid rgba(103, 126, 234, 0.2)',
                    animation: `pulse ${1.5 + index * 0.3}s ease-in-out infinite`,
                    '@keyframes pulse': {
                      '0%, 100%': { opacity: 0.5, transform: 'scale(1)' },
                      '50%': { opacity: 1, transform: 'scale(1.05)' },
                    },
                  }}
                />
              ))}
            </Box>

            {/* Animated Progress Bar */}
            <Box
              sx={{
                width: '100%',
                maxWidth: 400,
                mx: 'auto',
                height: 8,
                bgcolor: 'rgba(0,0,0,0.1)',
                borderRadius: 4,
                overflow: 'hidden',
                position: 'relative',
              }}
            >
              <Box
                sx={{
                  width: '30%',
                  height: '100%',
                  background: 'linear-gradient(90deg, #667eea, #4facfe)',
                  borderRadius: 4,
                  animation: 'loading 2s ease-in-out infinite',
                  '@keyframes loading': {
                    '0%': { transform: 'translateX(-100%)' },
                    '100%': { transform: 'translateX(350%)' },
                  },
                }}
              />
            </Box>

            <Typography variant="body1" sx={{ mt: 2, color: 'text.secondary', fontWeight: 500 }}>
              🔍 Scanning for smart money flows...
            </Typography>
          </Box>
        </Paper>
      </Box>
    );
  }

  if (error) {
    return (
      <Paper elevation={2} sx={{ p: 3 }}>
        <Alert severity="error" sx={{ fontSize: '1rem' }}>
          <Typography variant="h6" gutterBottom>
            Analysis Failed
          </Typography>
          {error}
        </Alert>
      </Paper>
    );
  }

  if (!data) {
    return (
      <Paper elevation={2} sx={{ p: 4, textAlign: 'center' }}>
        <Typography variant="h6" color="text.secondary">
          Enter a ticker symbol above to start analyzing unusual options activity
        </Typography>
      </Paper>
    );
  }

  if (data.unusualContracts.length === 0) {
    // Determine mode based on topSignals
    const isPositionMode = data.topSignals?.some(signal => signal.includes('POSITION ANALYSIS')) || false;
    const modeText = isPositionMode ? 'No Significant Positions' : 'No Unusual Activity';
    const descriptionText = isPositionMode 
      ? `No significant options positions for ${data.ticker} meet our analysis criteria`
      : `No options contracts for ${data.ticker} meet our smart money criteria`;

    return (
      <Paper 
        elevation={3} 
        sx={{ 
          p: 6, 
          textAlign: 'center',
          background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
          borderRadius: '20px',
        }}
      >
        <Box sx={{ mb: 3 }}>
          <Avatar
            sx={{
              width: 80,
              height: 80,
              bgcolor: isPositionMode ? '#8b5cf6' : '#667eea',
              mx: 'auto',
              mb: 2,
              animation: 'bounce 1s ease-in-out infinite',
              '@keyframes bounce': {
                '0%, 100%': { transform: 'translateY(0)' },
                '50%': { transform: 'translateY(-10px)' },
              },
            }}
          >
            <InfoIcon fontSize="large" />
          </Avatar>
          
          {/* Mode Indicator */}
          <Chip
            label={isPositionMode ? 'POSITION ANALYSIS MODE' : 'LIVE TRADING MODE'}
            sx={{
              bgcolor: isPositionMode ? '#8b5cf6' : '#667eea',
              color: 'white',
              fontWeight: 700,
              fontSize: '0.9rem',
              mb: 2,
              animation: 'pulse 2s ease-in-out infinite',
              '@keyframes pulse': {
                '0%, 100%': { opacity: 0.8 },
                '50%': { opacity: 1 },
              },
            }}
          />
          
          <Typography variant="h4" gutterBottom sx={{ fontWeight: 700, color: '#2d3748' }}>
            {modeText}
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ fontSize: '1.1rem', mb: 2 }}>
            {descriptionText}
          </Typography>
          
          {/* Stats Chips */}
          <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, flexWrap: 'wrap' }}>
            <Chip
              icon={<MoneyIcon />}
              label={`Price: ${formatCurrency(data.underlyingPrice)}`}
              color="primary"
              sx={{ fontSize: '1rem', p: 1 }}
            />
            <Chip
              icon={<ChartIcon />}
              label={`${data.totalContracts.toLocaleString()} Contracts Analyzed`}
              color="secondary"
              sx={{ fontSize: '1rem', p: 1 }}
            />
            {isPositionMode && (
              <Chip
                icon={<TimeIcon />}
                label="Pre-Market Analysis"
                sx={{ 
                  bgcolor: '#8b5cf6', 
                  color: 'white', 
                  fontSize: '1rem', 
                  p: 1,
                  fontWeight: 600
                }}
              />
            )}
          </Box>
        </Box>
      </Paper>
    );
  }

  // Calculate statistics for dashboard
  const callContracts = data.unusualContracts.filter(c => c.type === 'call');
  const putContracts = data.unusualContracts.filter(c => c.type === 'put');
  const totalPremium = data.unusualContracts.reduce((sum, c) => sum + c.premiumSpent, 0);
  const avgRatio = data.unusualContracts.reduce((sum, c) => sum + c.volumeToOiRatio, 0) / data.unusualContracts.length;
  const extremeFlows = data.unusualContracts.filter(c => c.volumeToOiRatio >= 6).length;
  
  // Determine mode
  const isPositionMode = data.topSignals?.some(signal => signal.includes('POSITION ANALYSIS')) || false;

  return (
    <Box sx={{ position: 'relative' }}>
      {/* Modern Header with Stats */}
      <Paper
        elevation={0}
        sx={{
          p: { xs: 3, sm: 4, md: 5 },
          mb: 4,
          background: 'linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 50%, #1a1a1a 100%)',
          color: 'white',
          borderRadius: '24px',
          position: 'relative',
          overflow: 'hidden',
          border: '1px solid rgba(119, 146, 179, 0.2)',
          backdropFilter: 'blur(20px)',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.05)',
        }}
      >
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'radial-gradient(circle at 30% 20%, rgba(119, 146, 179, 0.1) 0%, transparent 60%)',
            pointerEvents: 'none',
          }}
        />
        
        <Box sx={{ position: 'relative', zIndex: 1 }}>
          {/* Premium Status Badge */}
          <Box sx={{ display: 'flex', justifyContent: 'center', mb: 4 }}>
            <Box sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 1.5,
              px: 4,
              py: 1.5,
              borderRadius: '32px',
              background: 'rgba(119, 146, 179, 0.12)',
              border: '1px solid rgba(119, 146, 179, 0.25)',
              backdropFilter: 'blur(24px)',
              boxShadow: '0 8px 32px rgba(119, 146, 179, 0.15)',
            }}>
              <Box sx={{
                width: 10,
                height: 10,
                borderRadius: '50%',
                background: 'linear-gradient(45deg, #00ff88, #00cc6a)',
                animation: 'pulse 2s infinite',
                boxShadow: '0 0 12px rgba(0, 255, 136, 0.4)',
                '@keyframes pulse': {
                  '0%, 100%': { opacity: 1, transform: 'scale(1)' },
                  '50%': { opacity: 0.7, transform: 'scale(1.1)' },
                }
              }} />
              <Typography variant="caption" sx={{
                color: 'rgba(255, 255, 255, 0.95)',
                fontSize: '0.8rem',
                fontWeight: 700,
                letterSpacing: '0.8px',
                textTransform: 'uppercase',
                fontFamily: '"Inter", "Helvetica Neue", Arial, sans-serif',
              }}>
                {isPositionMode ? 'Position Analysis Mode' : 'Live Trading Mode'}
              </Typography>
            </Box>
          </Box>
          
          {/* Premium Main Title */}
          <Typography
            variant="h1"
            component="h1"
            sx={{
              fontWeight: 200,
              textAlign: 'center',
              mb: 5,
              color: '#ffffff',
              fontSize: { xs: '2.8rem', sm: '3.6rem', md: '4.2rem' },
              letterSpacing: '-0.03em',
              lineHeight: 1.05,
              fontFamily: '"Inter", "Helvetica Neue", Arial, sans-serif',
              textShadow: '0 4px 20px rgba(0, 0, 0, 0.3)',
            }}
          >
            {data.ticker} {isPositionMode ? 'Position Analysis' : 'Options Flow'}
          </Typography>
          
          {/* Premium Metrics Grid */}
          <Grid container spacing={4} sx={{ mt: 3 }}>
            {[
              { 
                value: data.unusualContracts.length, 
                label: isPositionMode ? 'Significant Positions' : 'Unusual Flows',
                color: '#ffffff'
              },
              { 
                value: formatLargeCurrency(totalPremium), 
                label: 'Total Premium',
                color: '#ffffff'
              },
              { 
                value: `${callContracts.length}C / ${putContracts.length}P`, 
                label: 'Call/Put Split',
                color: '#ffffff'
              },
              { 
                value: `${avgRatio.toFixed(1)}x`, 
                label: 'Avg Vol/OI',
                color: '#ffffff'
              }
            ].map((metric, index) => (
              <Grid item xs={12} sm={6} md={3} key={index}>
                <Box sx={{
                  textAlign: 'center',
                  p: 4,
                  borderRadius: '20px',
                  background: 'rgba(119, 146, 179, 0.06)',
                  border: '1px solid rgba(119, 146, 179, 0.12)',
                  backdropFilter: 'blur(20px)',
                  transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                  position: 'relative',
                  overflow: 'hidden',
                  '&::before': {
                    content: '""',
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    background: 'linear-gradient(135deg, rgba(119, 146, 179, 0.05) 0%, transparent 100%)',
                    opacity: 0,
                    transition: 'opacity 0.4s ease',
                  },
                  '&:hover': {
                    background: 'rgba(119, 146, 179, 0.1)',
                    transform: 'translateY(-4px)',
                    border: '1px solid rgba(119, 146, 179, 0.2)',
                    boxShadow: '0 20px 40px rgba(119, 146, 179, 0.15)',
                    '&::before': {
                      opacity: 1,
                    },
                  }
                }}>
                  <Typography variant="h2" sx={{ 
                    fontWeight: 200, 
                    mb: 2, 
                    color: metric.color,
                    fontSize: { xs: '2.5rem', sm: '3rem', md: '3.5rem' },
                    letterSpacing: '-0.04em',
                    fontFamily: '"Inter", "Helvetica Neue", Arial, sans-serif',
                    textShadow: '0 2px 8px rgba(0, 0, 0, 0.2)',
                  }}>
                    {metric.value}
                  </Typography>
                  <Typography variant="body2" sx={{ 
                    opacity: 0.85, 
                    color: 'rgba(255, 255, 255, 0.8)',
                    fontSize: '0.85rem',
                    fontWeight: 600,
                    letterSpacing: '0.1em',
                    textTransform: 'uppercase',
                    fontFamily: '"Inter", "Helvetica Neue", Arial, sans-serif',
                  }}>
                    {metric.label}
                  </Typography>
                </Box>
              </Grid>
            ))}
          </Grid>

          {/* Premium Indicators */}
          <Box sx={{ 
            display: 'flex', 
            justifyContent: 'center', 
            gap: 3, 
            mt: 5, 
            flexWrap: 'wrap' 
          }}>
            <Box sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 2,
              px: 4,
              py: 2,
              borderRadius: '24px',
              background: 'rgba(119, 146, 179, 0.1)',
              border: '1px solid rgba(119, 146, 179, 0.2)',
              backdropFilter: 'blur(24px)',
              boxShadow: '0 8px 32px rgba(119, 146, 179, 0.1)',
              transition: 'all 0.3s ease',
              '&:hover': {
                background: 'rgba(119, 146, 179, 0.15)',
                transform: 'translateY(-2px)',
                boxShadow: '0 12px 40px rgba(119, 146, 179, 0.15)',
              }
            }}>
              <Typography variant="body2" sx={{
                color: 'rgba(255, 255, 255, 0.85)',
                fontSize: '0.8rem',
                fontWeight: 600,
                letterSpacing: '0.1em',
                textTransform: 'uppercase',
                fontFamily: '"Inter", "Helvetica Neue", Arial, sans-serif',
              }}>
                Current Price
              </Typography>
              <Typography variant="h5" sx={{
                color: '#ffffff',
                fontSize: '1.3rem',
                fontWeight: 300,
                fontFamily: '"Inter", "Helvetica Neue", Arial, sans-serif',
                letterSpacing: '-0.02em',
              }}>
                {formatCurrency(data.underlyingPrice)}
              </Typography>
            </Box>
            
            {extremeFlows > 0 && (
              <Box sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1,
                px: 3,
                py: 1.5,
                borderRadius: '20px',
                background: 'rgba(95, 122, 154, 0.2)',
                border: '1px solid rgba(95, 122, 154, 0.4)',
                backdropFilter: 'blur(20px)',
              }}>
                <Box sx={{
                  width: 6,
                  height: 6,
                  borderRadius: '50%',
                  background: '#5f7a9a',
                  animation: 'pulse 2s infinite',
                  '@keyframes pulse': {
                    '0%, 100%': { opacity: 1 },
                    '50%': { opacity: 0.5 },
                  }
                }} />
                <Typography variant="body2" sx={{
                  color: '#ffffff',
                  fontSize: '0.8rem',
                  fontWeight: 600,
                  letterSpacing: '0.02em',
                  textTransform: 'uppercase',
                }}>
                  {extremeFlows} EXTREME FLOWS
                </Typography>
              </Box>
            )}
            
            {callContracts.length > putContracts.length * 2 && (
              <Box sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1,
                px: 3,
                py: 1.5,
                borderRadius: '20px',
                background: 'rgba(143, 163, 196, 0.2)',
                border: '1px solid rgba(143, 163, 196, 0.4)',
                backdropFilter: 'blur(20px)',
              }}>
                <Box sx={{
                  width: 6,
                  height: 6,
                  borderRadius: '50%',
                  background: '#8fa3c4',
                }} />
                <Typography variant="body2" sx={{
                  color: '#ffffff',
                  fontSize: '0.8rem',
                  fontWeight: 600,
                  letterSpacing: '0.02em',
                  textTransform: 'uppercase',
                }}>
                  BULLISH BIAS
                </Typography>
              </Box>
            )}
            
            {putContracts.length > callContracts.length * 2 && (
              <Box sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1,
                px: 3,
                py: 1.5,
                borderRadius: '20px',
                background: 'rgba(95, 122, 154, 0.2)',
                border: '1px solid rgba(95, 122, 154, 0.4)',
                backdropFilter: 'blur(20px)',
              }}>
                <Box sx={{
                  width: 6,
                  height: 6,
                  borderRadius: '50%',
                  background: '#5f7a9a',
                }} />
                <Typography variant="body2" sx={{
                  color: '#ffffff',
                  fontSize: '0.8rem',
                  fontWeight: 600,
                  letterSpacing: '0.02em',
                  textTransform: 'uppercase',
                }}>
                  BEARISH BIAS
                </Typography>
              </Box>
            )}
          </Box>
        </Box>
      </Paper>

      {/* Options Cards */}
      <Box>
        {data.unusualContracts.map((contract, index) => (
          <OptionCard key={`${contract.contractSymbol}-${index}`} contract={contract} index={index} />
        ))}
      </Box>

      {/* Enhanced Footer */}
      <Paper
        elevation={2}
        sx={{
          mt: 4,
          p: 3,
          background: 'linear-gradient(135deg, #f8f9ff 0%, #e8f0ff 100%)',
          borderRadius: '16px',
          border: '1px solid rgba(103, 126, 234, 0.1)',
        }}
      >
        <Typography variant="h6" gutterBottom sx={{ color: '#2d3748', fontWeight: 600 }}>
          📋 {isPositionMode ? 'Position Analysis Criteria' : 'Analysis Criteria'}
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={4}>
            <Typography variant="body2" color="text.secondary">
              <strong>{isPositionMode ? 'Position Threshold:' : 'Smart Money Threshold:'}</strong><br />
              {isPositionMode ? (
                <>
                  • Open Interest ≥ 25 contracts<br />
                  • Theoretical Premium ≥ $25,000<br />
                  • Valid price data required
                </>
              ) : (
                <>
                  • Volume/OI Ratio ≥ 2.5x<br />
                  • Premium Spent ≥ $25,000<br />
                  • Minimum Volume: 100 contracts
                </>
              )}
            </Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="body2" color="text.secondary">
              <strong>{isPositionMode ? 'Position Size:' : 'Signal Strength:'}</strong><br />
              {isPositionMode ? (
                <>
                  • SMALL: 25-99 contracts<br />
                  • MEDIUM: 100-499 contracts<br />
                  • LARGE: 500+ contracts
                </>
              ) : (
                <>
                  • MODERATE: 2.5x - 4.9x ratio<br />
                  • HIGH: 5.0x - 7.9x ratio<br />  
                  • EXTREME: 8.0x+ ratio
                </>
              )}
            </Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="body2" color="text.secondary">
              <strong>Data Source:</strong><br />
              • Yahoo Finance API<br />
              • {isPositionMode ? 'Historical positions data' : 'Real-time options chains'}<br />
              • Updated: {formatDate(data.analysisDate)}
            </Typography>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
};

export default ResultsTable;

