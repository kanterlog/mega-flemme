import type { NextApiRequest, NextApiResponse } from 'next';

// Mock DB in-memory (à remplacer par une vraie base plus tard)
let conversations: any[] = [];

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'GET') {
    res.status(200).json(conversations);
  } else if (req.method === 'POST') {
    const conv = req.body;
    conv.id = conversations.length + 1;
    conversations.push(conv);
    res.status(201).json(conv);
  } else if (req.method === 'PUT') {
    const { id, ...update } = req.body;
    conversations = conversations.map(c => c.id === id ? { ...c, ...update } : c);
    res.status(200).json({ success: true });
  } else if (req.method === 'DELETE') {
    const { id } = req.body;
    conversations = conversations.filter(c => c.id !== id);
    res.status(200).json({ success: true });
  } else {
    res.status(405).end();
  }
}
