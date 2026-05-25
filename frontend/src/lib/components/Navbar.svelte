<script lang="ts">
  import { theme } from "$lib/stores/theme";

  // tab activa — definida pela página que usa este componente
  let {
    activeTab = "inicio",
  }: { activeTab?: "inicio" | "farmacias" | "hospitais" | "restaurantes" | "sobre"} = $props();

  const tabs = [
    { id: "inicio", label: "Página Inicial", href: "/" },
    { id: "farmacias", label: "Farmácias", href: "/farmacias" },
    { id: "hospitais", label: "Hospitais", href: "/hospitais" },
    { id: "restaurantes", label: "Restaurantes", href: "/restaurantes" },
    { id: "sobre", label: "Sobre", href: "/sobre" },
  ] as const;

  let isDark = $derived($theme === "dark");
</script>

<header class="navbar">
  <!-- Logo -->
  <a href="/" class="navbar-logo" aria-label="MapSIG — início">
    <div class="logo-icon">
      <svg
        width="22"
        height="22"
        viewBox="0 0 22 22"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M11 2C7.13 2 4 5.13 4 9c0 5.25 7 11 7 11s7-5.75 7-11c0-3.87-3.13-7-7-7z"
          fill="currentColor"
        />
        <circle cx="11" cy="9" r="2.5" fill="white" />
      </svg>
    </div>
    <span class="logo-text">Map<strong>SIG</strong></span>
  </a>

  <!-- Tabs de navegação -->
  <nav class="navbar-tabs" aria-label="Categorias">
    {#each tabs as tab}
      <a
        href={tab.href}
        role="tab"
        aria-selected={activeTab === tab.id}
        class="nav-tab"
        class:active={activeTab === tab.id}
      >
        {tab.label}
      </a>
    {/each}
  </nav>

  <!-- Ações à direita -->
  <div class="navbar-actions">
    <!-- Botão para mudar o tema -->
    <button
      class="theme-toggle"
      onclick={theme.toggle}
      aria-label={isDark ? "Ativar modo claro" : "Ativar modo escuro"}
      title={isDark ? "Modo claro" : "Modo escuro"}
    >
      {#if isDark}
        <!-- Ícone de sol (modo escuro activo) -->
        <svg
          width="18"
          height="18"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <circle cx="12" cy="12" r="5" />
          <line x1="12" y1="1" x2="12" y2="3" />
          <line x1="12" y1="21" x2="12" y2="23" />
          <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
          <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
          <line x1="1" y1="12" x2="3" y2="12" />
          <line x1="21" y1="12" x2="23" y2="12" />
          <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
          <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
        </svg>
      {:else}
        <!-- Ícone de lua (modo claro activo) -->
        <svg
          width="18"
          height="18"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
        </svg>
      {/if}
    </button>
  </div>
</header>

<style>
  .navbar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 100;
    height: var(--navbar-height);
    background: var(--bg-navbar);
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    padding: 0 20px;
    gap: 24px;
    box-shadow: var(--shadow-sm);
    transition:
      background-color var(--transition-slow),
      border-color var(--transition-slow);
  }

  /* Logo */
  .navbar-logo {
    display: flex;
    align-items: center;
    gap: 8px;
    text-decoration: none;
    color: var(--text-primary);
    flex-shrink: 0;
  }

  .logo-icon {
    width: 34px;
    height: 34px;
    background: var(--color-farmacia);
    border-radius: var(--radius-md);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    box-shadow: 0 2px 8px rgba(22, 168, 94, 0.35);
  }

  .logo-text {
    font-family: "Sora", sans-serif;
    font-size: 17px;
    font-weight: 500;
    letter-spacing: -0.3px;
    color: var(--text-primary);
  }

  .logo-text strong {
    font-weight: 700;
    color: var(--color-farmacia);
  }

  /* Tabs */
  .navbar-tabs {
    display: flex;
    align-items: center;
    gap: 2px;
    margin-left: 8px;
  }

  .nav-tab {
    padding: 6px 14px;
    border: none;
    background: transparent;
    font-family: "Inter", sans-serif;
    font-size: 13.5px;
    font-weight: 500;
    color: var(--text-secondary);
    border-radius: var(--radius-sm);
    cursor: pointer;
    transition:
      color var(--transition),
      background var(--transition);
    white-space: nowrap;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
  }

  .nav-tab:hover {
    color: var(--text-primary);
    background: var(--bg-hover);
  }

  .nav-tab.active {
    color: var(--color-farmacia);
    background: var(--color-farmacia-10);
    font-weight: 600;
  }

  /* Ações */
  .navbar-actions {
    margin-left: auto;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .theme-toggle {
    width: 36px;
    height: 36px;
    border: 1px solid var(--border);
    background: var(--bg-input);
    border-radius: var(--radius-md);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-secondary);
    transition: all var(--transition);
  }

  .theme-toggle:hover {
    color: var(--text-primary);
    border-color: var(--color-farmacia);
    background: var(--color-farmacia-10);
  }
</style>
