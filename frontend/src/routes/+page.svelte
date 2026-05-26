<script lang="ts">
  import Navbar from "$lib/components/Navbar.svelte";
  import MapComponent from "$lib/components/Map.svelte";
  import ProximidadeModal from "$lib/components/ProximidadeModal.svelte";
  import { goto } from "$app/navigation";

  interface Props {
    onSearch: (query: string, categories: Set<string>) => void;
  }

  let { onSearch }: Props = $props();

  let mapRef: MapComponent;
  let proximityModalRef: ProximidadeModal;

  let places = $state<any[]>([]);
  let loading = $state(false);
  let searched = $state(false);

  let selectedLocation = $state<{
    lat: number;
    lon: number;
  } | null>(null);

  let routeSummary = $state<{
    distance_m: number;
    duration_min: number;
    estimated?: boolean;
  } | null>(null);

  let routeError = $state<string | null>(null);

  // Estatísticas
  const stats = [
    {
      label: "FARMÁCIAS",
      count: "2.8k+",
      icon: "💊",
      category: "farmacias",
      colorClass: "badge-farmacia",
    },
    {
      label: "HOSPITAIS",
      count: "120+",
      icon: "🏥",
      category: "hospitais",
      colorClass: "badge-hospital",
    },
    {
      label: "RESTAURANTES",
      count: "45k+",
      icon: "🍽️",
      category: "restaurantes",
      colorClass: "badge-restaurante",
    },
  ];

  // Buscar locais
  async function fetchPlaces(query: string, categories: Set<string>) {
    loading = true;
    searched = true;

    try {
      const activeCats = [...categories];

      const results = await Promise.all(
        activeCats.map((cat) => {
          const params = new URLSearchParams({
            categoria: cat,
          });

          if (query) {
            params.set("query", query);
          }

          return fetch(`http://localhost:8000/places/?${params}`).then((r) =>
            r.json(),
          );
        }),
      );

      places = results.flat();
      mapRef?.clearRouteArea();
      mapRef?.clearRoute();
      routeSummary = null;
      routeError = null;
      mapRef?.addMarkers(places);
    } finally {
      loading = false;
    }
  }

  // Pesquisa principal
  function handleSearch(query: string, categories: Set<string>) {
    onSearch(query, categories);
    fetchPlaces(query, categories);
  }

  // Botões rápidos
  function handleQuickSearch(category: string) {
    goto(`/${category}`);
  }

  // Botão principal
  function handleMainSearch() {
    const allCategories = new Set(["farmacias", "hospitais", "restaurantes"]);

    handleSearch("", allCategories);
  }

  // Rotas
  async function calculateRoute(place: any) {
    if (!selectedLocation) return;

    routeError = null;

    try {
      const res = await fetch("http://localhost:8000/routes/calculate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          origin: selectedLocation,
          destination: {
            lat: place.lat,
            lon: place.lon,
          },
          profile: "walking",
        }),
      });

      if (!res.ok) {
        throw new Error();
      }

      const route = await res.json();

      mapRef?.drawRoute(route.geometry);

      routeSummary = {
        distance_m: route.distance_m,
        duration_min: route.duration_min,
        estimated: route.estimated,
      };
    } catch {
      routeError = "Não foi possível calcular a rota.";
      routeSummary = null;
      mapRef?.clearRoute();
    }
  }

  // Seleção de localização
  function handleLocationSelect(location: { lat: number; lon: number }) {
    selectedLocation = location;
    mapRef?.clearRoute();
    routeSummary = null;
    routeError = null;
    proximityModalRef?.open();
  }

  // Modal proximidade
  function handleProximityResults(results: any[]) {
    places = results;
    searched = true;
    mapRef?.addMarkers(results);
  }

  function handleCenter(lat: number, lon: number) {
    mapRef?.centerMap(lat, lon, 14);
  }

  function handleRouteArea(routeArea: object | null) {
    if (routeArea) {
      mapRef?.drawRouteArea(routeArea);
    } else {
      mapRef?.clearRouteArea();
    }
  }

  // Distância
  function formatDistance(meters: number) {
    if (meters < 1000) {
      return `${meters} m`;
    }

    return `${(meters / 1000).toFixed(1).replace(".", ",")} km`;
  }
</script>

@ -1,601 +1,266 @@
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

      <!-- Botões -->
      <div class="cta-buttons">
        <button class="btn-primary" onclick={handleMainSearch}>
          Começar a Pesquisar
        </button>

        <button class="btn-secondary"> Ver Demonstração </button>
      </div>

      <!-- Estatísticas -->
      <div class="stats-container">
        {#each stats as stat}
          <button
            class="stat-card"
            onclick={() => handleQuickSearch(stat.category)}
          >
            <span class="stat-badge {stat.colorClass}">
              {stat.icon}

              {stat.label.charAt(0) + stat.label.slice(1).toLowerCase()}
            </span>

            <span class="stat-number">
              {stat.count}
            </span>

            <span class="stat-label">
              {stat.label}
            </span>
          </button>
        {/each}
      </div>
    </div>

    <div class="map-area">
      <MapComponent
        bind:this={mapRef}
        onLocationSelect={handleLocationSelect}
        onPlaceSelect={calculateRoute}
      />
      {#if routeSummary || routeError}
        <div class="route-summary">
          {#if routeSummary}
            Rota{routeSummary.estimated ? " estimada" : ""}: {formatDistance(routeSummary.distance_m)} · {routeSummary.duration_min}
            min
          {:else}
            {routeError}
          {/if}
        </div>
      {/if}
      <ProximidadeModal
        bind:this={proximityModalRef}
        onResults={handleProximityResults}
        onCenter={handleCenter}
        onRouteArea={handleRouteArea}
        {selectedLocation}
      />
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

  /* Resumo rota */
  .route-summary {
    position: absolute;
    top: 20px;
    right: 20px;
    z-index: 30;

    padding: 10px 14px;
    border-radius: var(--radius-md);

    background: var(--bg-primary);
    border: 1px solid var(--border);

    color: var(--text-primary);
    font-size: 13px;
    font-weight: 700;

    box-shadow: var(--shadow-lg);
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

  .btn-secondary {
    height: 52px;
    padding: 0 28px;

    border-radius: var(--radius-md);

    background: var(--bg-input);
    border: 1px solid var(--border);

    color: var(--text-primary);

    font-size: 15px;
    font-weight: 600;

    cursor: pointer;

    transition: background var(--transition);
  }

  .btn-secondary:hover {
    background: var(--bg-hover);
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

    .btn-primary,
    .btn-secondary {
      width: 100%;
    }

    .map-area {
      height: 420px;
      min-height: 420px;
    }
  }
</style>
