import { writable } from 'svelte/store';
import { browser } from '$app/environment';

type Theme = 'dark' | 'light';

function createThemeStore() {
  // Lê preferência guardada ou usa preferência do sistema
  const getInitial = (): Theme => {
    if (!browser) return 'dark';
    const saved = localStorage.getItem('mapsig-theme') as Theme | null;
    if (saved) return saved;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  };

  const { subscribe, set, update } = writable<Theme>(getInitial());

  // Aplica o atributo no <html> sempre que muda
  subscribe((theme) => {
    if (!browser) return;
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('mapsig-theme', theme);
  });

  return {
    subscribe,
    toggle: () => update(t => (t === 'dark' ? 'light' : 'dark')),
    set,
  };
}

export const theme = createThemeStore();
