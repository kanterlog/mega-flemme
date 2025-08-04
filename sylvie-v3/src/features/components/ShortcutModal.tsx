import React from 'react';

interface Shortcut {
  key: string;
  label: string;
  message: string;
  icon: string;
  color?: string;
  usage?: number;
}

interface ShortcutModalProps {
  open: boolean;
  shortcuts: Shortcut[];
  setShortcuts: (shortcuts: Shortcut[]) => void;
  formShortcut: Shortcut;
  setFormShortcut: (shortcut: Shortcut) => void;
  editIndex: number | null;
  setEditIndex: (idx: number | null) => void;
  confirmDeleteIdx: number | null;
  setConfirmDeleteIdx: (idx: number | null) => void;
  dragIdx: number | null;
  setDragIdx: (idx: number | null) => void;
  setToast: (toast: any) => void;
  onClose: () => void;
}

const ShortcutModal: React.FC<ShortcutModalProps> = ({
  open,
  shortcuts,
  setShortcuts,
  formShortcut,
  setFormShortcut,
  editIndex,
  setEditIndex,
  confirmDeleteIdx,
  setConfirmDeleteIdx,
  dragIdx,
  setDragIdx,
  setToast,
  onClose,
}) => {
  if (!open) return null;

  return (
    <div style={{ position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', background: '#000a', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
      <div style={{ background: '#23242b', padding: 32, borderRadius: 16, minWidth: 340, boxShadow: '0 4px 32px #0006', color: '#e3e3e3' }}>
        <h3 style={{ marginBottom: 18 }}>Raccourcis personnalisés</h3>
        {/* Liste des raccourcis existants */}
        {shortcuts.length > 0 && (
          <div style={{ marginBottom: 18 }}>
            <ul style={{ listStyle: 'none', padding: 0 }}>
              {shortcuts.map((sc: any, idx: number) => (
                <li
                  key={sc.key}
                  style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6, cursor: 'grab', opacity: dragIdx === idx ? 0.5 : 1 }}
                  draggable
                  onDragStart={() => setDragIdx(idx)}
                  onDragOver={e => e.preventDefault()}
                  onDrop={() => {
                    if (dragIdx !== null && dragIdx !== idx) {
                      const reordered = [...shortcuts];
                      const [removed] = reordered.splice(dragIdx, 1);
                      reordered.splice(idx, 0, removed);
                      setShortcuts(reordered);
                      setToast({ message: 'Raccourci déplacé', type: 'success' });
                    }
                    setDragIdx(null);
                  }}
                  onDragEnd={() => setDragIdx(null)}
                >
                  <span style={{ fontSize: 18, color: sc.color || '#4285f4' }}>{sc.icon}</span>
                  <span style={{ fontWeight: 'bold' }}>{sc.label}</span>
                  <button
                    onClick={() => {
                      setFormShortcut({ label: sc.label, message: sc.message, icon: sc.icon, color: sc.color || '#4285f4' });
                      setEditIndex(idx);
                    }}
                    style={{ background: '#4285f4', color: '#fff', border: 'none', borderRadius: 6, padding: '2px 10px', fontSize: 13, marginLeft: 8, cursor: 'pointer' }}
                  >Éditer</button>
                  <button
                    onClick={() => setConfirmDeleteIdx(idx)}
                    style={{ background: '#ea4335', color: '#fff', border: 'none', borderRadius: 6, padding: '2px 10px', fontSize: 13, marginLeft: 4, cursor: 'pointer' }}
                  >Supprimer</button>
                  {confirmDeleteIdx === idx && (
                    <div style={{ background: '#181a20', border: '1px solid #444', borderRadius: 8, padding: 16, marginBottom: 12, color: '#e3e3e3', boxShadow: '0 2px 8px #0002' }}>
                      <div style={{ marginBottom: 10 }}>
                        Confirmer la suppression du raccourci <strong>{sc.label}</strong> ?
                      </div>
                      <div style={{ display: 'flex', gap: 12 }}>
                        <button
                          onClick={() => {
                            const updated = shortcuts.filter((item: any, i: number) => i !== idx);
                            const deletedShortcut = shortcuts[idx];
                            setShortcuts(updated);
                            if (editIndex === idx) {
                              setFormShortcut({ label: '', message: '', icon: '', color: '#4285f4' });
                              setEditIndex(null);
                            }
                            setConfirmDeleteIdx(null);
                            const undoDelete = () => {
                              const restored = [...shortcuts];
                              restored.splice(idx, 0, deletedShortcut);
                              setShortcuts(restored);
                              setToast({ message: 'Suppression annulée', type: 'success' });
                            };
                            setToast({ message: 'Raccourci supprimé', type: 'error', action: { label: 'Annuler', onClick: undoDelete } });
                          }}
                          style={{ background: '#ea4335', color: '#fff', border: 'none', borderRadius: 8, padding: '6px 18px', fontWeight: 'bold', fontSize: 15 }}
                        >Confirmer</button>
                        <button
                          onClick={() => setConfirmDeleteIdx(null)}
                          style={{ background: '#444', color: '#fff', border: 'none', borderRadius: 8, padding: '6px 18px', fontWeight: 'bold', fontSize: 15 }}
                        >Annuler</button>
                      </div>
                    </div>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}
        {/* Formulaire ajout/édition raccourci */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <input
            type="text"
            placeholder="Label du raccourci"
            value={formShortcut.label}
            onChange={e => setFormShortcut({ ...formShortcut, label: e.target.value })}
            style={{ padding: 8, borderRadius: 8, border: formShortcut.label.trim() ? '1px solid #444' : '2px solid #ea4335', fontSize: 15, background: '#181a20', color: '#e3e3e3', transition: 'border 0.2s' }}
          />
          <input
            type="text"
            placeholder="Message déclenché"
            value={formShortcut.message}
            onChange={e => setFormShortcut({ ...formShortcut, message: e.target.value })}
            style={{ padding: 8, borderRadius: 8, border: formShortcut.message.trim() ? '1px solid #444' : '2px solid #ea4335', fontSize: 15, background: '#181a20', color: '#e3e3e3', transition: 'border 0.2s' }}
          />
          <input
            type="text"
            placeholder="Emoji ou texte icône (ex: 🚀)"
            value={formShortcut.icon}
            onChange={e => setFormShortcut({ ...formShortcut, icon: e.target.value })}
            style={{ padding: 8, borderRadius: 8, border: '1px solid #444', fontSize: 15, background: '#181a20', color: '#e3e3e3' }}
          />
          <input
            type="color"
            value={formShortcut.color}
            onChange={e => setFormShortcut({ ...formShortcut, color: e.target.value })}
            style={{ width: 40, height: 40, border: 'none', borderRadius: 8, marginTop: 4, background: 'none', cursor: 'pointer' }}
            title="Couleur de la bulle"
          />
          <div style={{ display: 'flex', gap: 12, marginTop: 8 }}>
            <button
              onClick={() => {
                if (!formShortcut.label.trim() || !formShortcut.message.trim()) {
                  setToast({ message: 'Veuillez remplir tous les champs obligatoires', type: 'error' });
                  return;
                }
                let updated;
                if (editIndex !== null) {
                  const beforeEdit = shortcuts[editIndex];
                  updated = shortcuts.map((sc: any, i: number) => i === editIndex ? { ...sc, ...formShortcut } : sc);
                  const undoEdit = () => {
                    const restored = shortcuts.map((sc: any, i: number) => i === editIndex ? beforeEdit : sc);
                    setShortcuts(restored);
                    setToast({ message: 'Modification annulée', type: 'success' });
                  };
                  setToast({ message: 'Raccourci modifié avec succès', action: { label: 'Annuler', onClick: undoEdit } });
                } else {
                  const newShortcut = { ...formShortcut, key: 'custom_' + Date.now() };
                  updated = [...shortcuts, newShortcut];
                  setToast({ message: 'Raccourci ajouté avec succès' });
                }
                setShortcuts(updated);
                setFormShortcut({ label: '', message: '', icon: '', color: '#4285f4' });
                setEditIndex(null);
                onClose();
              }}
              style={{ background: '#4285f4', color: '#fff', border: 'none', borderRadius: 8, padding: '8px 18px', fontWeight: 'bold', fontSize: 15, boxShadow: '0 0 0 2px #4285f4' }}
            >{editIndex !== null ? 'Enregistrer' : 'Ajouter'}</button>
            <button
              onClick={() => {
                setFormShortcut({ label: '', message: '', icon: '', color: '#4285f4' });
                setEditIndex(null);
                onClose();
              }}
              style={{ background: '#ea4335', color: '#fff', border: 'none', borderRadius: 8, padding: '8px 18px', fontWeight: 'bold', fontSize: 15, boxShadow: '0 0 0 2px #ea4335' }}
            >Annuler</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ShortcutModal;
