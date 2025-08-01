export default function HomePage() {
  return (
    <div style={{ padding: '40px', fontFamily: 'Arial, sans-serif' }}>
      <div style={{ 
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        padding: '40px',
        borderRadius: '12px',
        color: 'white',
        textAlign: 'center'
      }}>
        <h1 style={{ margin: '0 0 20px 0', fontSize: '2.5rem' }}>🎉 Sylvie v3.0</h1>
        <p style={{ margin: '0 0 30px 0', fontSize: '1.2rem' }}>
          Assistant IA Google Workspace - Nouvelle Génération
        </p>
        <div style={{ 
          background: 'rgba(255, 255, 255, 0.2)',
          padding: '20px',
          borderRadius: '8px',
          backdropFilter: 'blur(10px)'
        }}>
          <h2 style={{ margin: '0 0 15px 0' }}>✨ Statut du Projet</h2>
          <p style={{ margin: 0 }}>
            ✅ Architecture Next.js 14 opérationnelle<br/>
            ✅ Interface de base fonctionnelle<br/>
            🔄 Prêt pour Phase 2 : Intégrations MCP
          </p>
        </div>
      </div>
    </div>
  );
}
