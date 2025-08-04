import React, { useEffect, useState } from 'react';
import { THEME } from '../constants/theme';
// Utilise le PNG fourni par l'utilisateur dans /public/assets/splash.png
const splashImgUrl = '/assets/splash.png';

interface SplashScreenProps {
  duration?: number;
  onFinish?: () => void;
  error?: boolean;
  errorImageUrl?: string;
  errorText?: string;
}

/**
 * SplashScreen
 * Affiche l'image d'ouverture pendant le chargement de l'interface.
 */
const SplashScreen: React.FC<SplashScreenProps> = ({ duration = 1800, onFinish, error, errorImageUrl, errorText }) => {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setVisible(false);
      if (onFinish) onFinish();
    }, duration);
    return () => clearTimeout(timer);
  }, [duration, onFinish]);

  return visible ? (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        background: THEME.colors.background,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 3000,
        transition: 'opacity 0.7s',
        opacity: visible ? 1 : 0,
        flexDirection: 'column',
      }}
    >
      <img
        src={error ? errorImageUrl || '/no-internet.png' : splashImgUrl}
        alt={error ? 'Erreur réseau' : 'Splash Sylvie'}
        style={{
          maxWidth: '80vw',
          maxHeight: '60vh',
          borderRadius: 24,
          boxShadow: '0 8px 32px #0006',
        }}
      />
      {error && (
        <div style={{
          marginTop: 32,
          color: THEME.colors.error,
          fontWeight: 'bold',
          fontSize: 22,
          textAlign: 'center',
          background: '#fff',
          borderRadius: 12,
          padding: '18px 32px',
          boxShadow: '0 2px 12px #0002',
        }}>
          {errorText || 'Connexion Internet indisponible'}
        </div>
      )}
    </div>
  ) : null;
};

export default SplashScreen;
