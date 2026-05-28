<script lang="ts">
  import { onMount } from "svelte";
  import Navbar from "$lib/components/Navbar.svelte";
  import MapComponent from "$lib/components/Map.svelte";
  import { goto } from "$app/navigation";

  const stats = [
    {
      label: "FARMÁCIAS",
      countKey: "farmacia",
      apiCat: "farmacia",
      icon: `<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path d="M19 11h-6V5a1 1 0 0 0-2 0v6H5a1 1 0 0 0 0 2h6v6a1 1 0 0 0 2 0v-6h6a1 1 0 0 0 0-2z"/></svg>`,
      category: "farmacias",
      colorClass: "badge-farmacia",
    },
    {
      label: "HOSPITAIS",
      countKey: "hospital",
      apiCat: "hospital",
      icon: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg"><rect x="2" y="4" width="20" height="18" rx="2"/><line x1="12" y1="9" x2="12" y2="15"/><line x1="9" y1="12" x2="15" y2="12"/></svg>`,
      category: "hospitais",
      colorClass: "badge-hospital",
    },
    {
      label: "RESTAURANTES",
      countKey: "restaurante",
      apiCat: "restaurante",
      icon: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg"><path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2"/><line x1="7" y1="2" x2="7" y2="22"/><line x1="21" y1="15" x2="21" y2="22"/><path d="M21 2a5 5 0 0 0-5 5v6h5"/></svg>`,
      category: "restaurantes",
      colorClass: "badge-restaurante",
    },
  ];

  let counts = $state<Record<string, string>>({
    farmacia: "...",
    hospital: "...",
    restaurante: "...",
  });

  onMount(async () => {
    try {
      const [farmacias, hospitais, restaurantes] = await Promise.all([
        fetch("http://localhost:8000/places/?categoria=farmacia").then((r) => r.json()),
        fetch("http://localhost:8000/places/?categoria=hospital").then((r) => r.json()),
        fetch("http://localhost:8000/places/?categoria=restaurante").then((r) => r.json()),
      ]);
      counts.farmacia = String(farmacias.length);
      counts.hospital = String(hospitais.length);
      counts.restaurante = String(restaurantes.length);
    } catch {
      counts.farmacia = "—";
      counts.hospital = "—";
      counts.restaurante = "—";
    }
  });

  function handleQuickSearch(category: string) {
    goto(`/${category}`);
  }
</script>

<div class="hero-page-wrapper">
  <Navbar activeTab="inicio" />
  <!-- HERO -->
  <section class="hero-container">
    <div class="hero-content">
      <!-- Badge -->
      <div class="location-badge">
        <span class="dot"></span>
        Portugal · 308 Municípios
      </div>

      <!-- Título -->
      <h1 class="hero-title">
        Encontra o que <br />
        precisas
        <span class="highlight"> perto de ti </span>
      </h1>

      <!-- Subtítulo -->
      <p class="hero-subtitle">
        Pesquisa farmácias, hospitais e restaurantes em Portugal.
        <br />
        Filtra por proximidade, horário e categoria num mapa interativo.
      </p>

      <!-- Botão -->
      <div class="cta-buttons">
        <button class="btn-primary" onclick={() => goto('/farmacias')}>
          Começar a Pesquisar
        </button>
      </div>

      <!-- Estatísticas -->
      <div class="stats-container">
        {#each stats as stat}
          <button
            class="stat-card"
            onclick={() => handleQuickSearch(stat.category)}
          >
            <span class="stat-badge {stat.colorClass}">
              {@html stat.icon}
              {stat.label.charAt(0) + stat.label.slice(1).toLowerCase()}
            </span>
            <span class="stat-number">{counts[stat.countKey]}</span>
            <span class="stat-label">{stat.label}</span>
          </button>
        {/each}
      </div>
    </div>

    <div class="map-area">
      <MapComponent />
    </div>
  </section>
</div>

<style>
  :global(body) {
    margin: 0;
    background: var(--bg-primary);
    overflow: hidden;
    font-family:
      "Inter",
      system-ui,
      -apple-system,
      sans-serif;
  }

  .hero-page-wrapper {
    position: relative;
    height: 100vh;
    overflow: hidden;
    background: var(--bg-primary);
  }

  /* HERO */
  .hero-container {
    position: relative;
    z-index: 10;
    display: flex;
    height: 100%;
    padding-left: 60px;
    gap: 40px;
    align-items: stretch;
  }

  .hero-content {
    width: 620px;
    max-width: 620px;
    flex-shrink: 0;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 24px;
    z-index: 20;
  }

  .map-area {
    flex: 1;
    min-width: 0;
    position: relative;
    overflow: hidden;
  }

  /* garante altura total ao mapa */
  .map-area :global(.map-wrapper),
  .map-area :global(.map) {
    width: 100%;
    height: 100%;
  }

  /* Badge */
  .location-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    width: fit-content;
    padding: 7px 14px;
    border-radius: var(--radius-full);
    background: var(--color-farmacia-10);
    border: 1px solid var(--border);
    color: var(--color-farmacia);
    font-size: 13px;
    font-weight: 500;
  }

  .dot {
    width: 8px;
    height: 8px;
    border-radius: var(--radius-full);
    background: var(--color-farmacia);
  }

  /* Título */
  .hero-title {
    margin: 0;
    font-family: "Sora", sans-serif;
    font-size: 50px;
    line-height: 1.02;
    letter-spacing: -0.04em;
    font-weight: 800;
    color: var(--text-primary);
  }

  .highlight {
    color: var(--color-farmacia);
  }

  /* Texto */
  .hero-subtitle {
    margin: 0;
    max-width: 560px;
    font-size: 18px;
    line-height: 1.8;
    color: var(--text-secondary);
  }

  /* Botões */
  .cta-buttons {
    display: flex;
    gap: 16px;
    margin-top: 8px;
  }

  .btn-primary {
    height: 52px;
    padding: 0 28px;
    border: none;
    border-radius: var(--radius-md);
    background: var(--color-farmacia);
    color: var(--text-inverse);
    font-size: 15px;
    font-weight: 700;
    cursor: pointer;
    transition:
      transform var(--transition),
      background var(--transition);
  }

  .btn-primary:hover {
    transform: translateY(-2px);
  }

  /* Estatísticas */
  .stats-container {
    display: flex;
    flex-wrap: wrap;
    gap: 42px;
    margin-top: 20px;
  }

  .stat-card {
    background: transparent;
    border: none;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 8px;
    text-align: left;
    cursor: pointer;
    transition: transform var(--transition);
  }

  .stat-card:hover {
    transform: translateY(-3px);
  }

  .stat-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    width: fit-content;
    padding: 5px 10px;
    border-radius: var(--radius-full);
    font-size: 11px;
    font-weight: 700;
  }

  .badge-farmacia {
    background: var(--color-farmacia-10);
    color: var(--color-farmacia);
  }

  .badge-hospital {
    background: var(--color-hospital-10);
    color: var(--color-hospital);
  }

  .badge-restaurante {
    background: var(--color-restaurante-10);
    color: var(--color-restaurante);
  }

  .stat-number {
    font-size: 25px;
    line-height: 1;
    font-weight: 800;
    color: var(--text-primary);
  }

  .stat-label {
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.12em;
    color: var(--text-muted);
  }

  /* RESPONSIVO */
  @media (max-width: 1024px) {
    .hero-container {
      flex-direction: column;
      height: auto;
      min-height: calc(100vh - 70px);
      padding: 40px 28px;
    }

    .hero-content {
      width: 100%;
      max-width: 100%;
    }

    .map-area {
      width: 100%;
      height: 500px;
      min-height: 500px;
    }

    .hero-title {
      font-size: 48px;
    }
  }

  @media (max-width: 768px) {
    .hero-container {
      padding: 30px 22px;
    }

    .hero-title {
      font-size: 42px;
    }

    .hero-subtitle {
      font-size: 16px;
    }

    .stats-container {
      gap: 28px;
    }

    .stat-number {
      font-size: 40px;
    }

    .cta-buttons {
      flex-direction: column;
      align-items: stretch;
    }

    .btn-primary {
      width: 100%;
    }

    .map-area {
      height: 420px;
      min-height: 420px;
    }
  }
</style>
