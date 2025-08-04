"use strict";
// Fichier de constantes pour l’application Sylvie v3
// Utilisation : import { THEME } from '../constants/theme';
Object.defineProperty(exports, "__esModule", { value: true });
exports.THEME = void 0;
exports.THEME = {
    colors: {
        background: '#181a20',
        text: '#e3e3e3',
        primary: '#4285f4',
        error: '#ea4335',
        card: '#23242b',
        border: '#444',
        success: '#34a853',
    },
    durations: {
        toast: 3000,
    },
    layout: {
        sidebarWidth: 320,
        borderRadius: 8,
    },
};
// Export CommonJS pour compatibilité Jest
module.exports = { THEME: exports.THEME };
