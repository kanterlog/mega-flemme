import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Sylvie v3.0 - Assistant IA Google Workspace',
  description: 'Assistant IA avancé pour Google Workspace avec support MCP',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr">
      <body style={{ margin: 0, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', minHeight: '100vh' }}>
        {children}
      </body>
    </html>
  );
}
