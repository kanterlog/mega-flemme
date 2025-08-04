const { THEME } = require('../../../dist/sylvie-v3/src/constants/theme.js');

describe('THEME constant (JS compiled)', () => {
  it('doit contenir les couleurs principales attendues', () => {
    expect(THEME.colors.background).toBe('#181a20');
    expect(THEME.colors.text).toBe('#e3e3e3');
    expect(THEME.colors.primary).toBe('#4285f4');
    expect(THEME.colors.error).toBe('#ea4335');
    expect(THEME.colors.card).toBe('#23242b');
    expect(THEME.colors.border).toBe('#444');
    expect(THEME.colors.success).toBe('#34a853');
  });

  it('doit contenir la durée du toast', () => {
    expect(THEME.durations.toast).toBe(3000);
  });

  it('doit contenir les paramètres de layout', () => {
    expect(THEME.layout.sidebarWidth).toBe(320);
    expect(THEME.layout.borderRadius).toBe(8);
  });
});
