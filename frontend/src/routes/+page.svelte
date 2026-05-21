<script lang="ts">
  import Navbar from "$lib/components/Navbar.svelte";
  import MapComponent from "$lib/components/Map.svelte";
  import ProximidadeModal from "$lib/components/ProximidadeModal.svelte";
  import { goto } from '$app/navigation';

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

<div class="hero-page-wrapper">
  <Navbar activeTab="mapa" />

  <!-- MAPA -->
  <div class="map-background">
    <MapComponent
      bind:this={mapRef}
      onLocationSelect={handleLocationSelect}
      onPlaceSelect={calculateRoute}
    />

    <!-- Overlay escuro -->
    <div class="map-overlay"></div>

    <!-- Resumo rota -->
    {#if routeSummary || routeError}
      <div class="route-summary">
        {#if routeSummary}
          Rota:
          {formatDistance(routeSummary.distance_m)}
          ·
          {routeSummary.duration_min}
          min
        {:else}
          {routeError}
        {/if}
      </div>
    {/if}
  </div>

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
  </section>

  <!-- MODAL -->
  <ProximidadeModal
    bind:this={proximityModalRef}
    onResults={handleProximityResults}
    onCenter={handleCenter}
    onRouteArea={handleRouteArea}
    {selectedLocation}
  />
</div>

<style>
  :global(body) {
    margin: 0;
    background: #020817;
    overflow: hidden;
    font-family:
      system-ui,
      -apple-system,
      BlinkMacSystemFont,
      "Segoe UI",
      sans-serif;
  }

  .hero-page-wrapper {
    position: relative;
    min-height: 100vh;
    overflow: hidden;
    background: #020817;
  }

  /* HERO */
  .hero-container {
    position: relative;
    z-index: 10;
    display: flex;
    align-items: center;
    min-height: calc(100vh - 70px);
    padding: 0 60px;
  }

  .hero-content {
    width: 100%;
    max-width: 620px;
    display: flex;
    flex-direction: column;
    gap: 24px;
  }

  /* MAPA */
  .map-background {
    position: absolute;
    top: 70px;
    right: 0;
    width: 62%;
    height: calc(100vh - 70px);
    overflow: hidden;
    border-top-left-radius: 28px;
    border-bottom-left-radius: 28px;
    z-index: 1;
  }

  /* Leaflet */
  .map-background :global(.leaflet-container) {
    width: 100%;
    height: 100%;
    background: #0f172a;
  }

  /* Overlay */
  .map-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(
      90deg,
      rgba(2, 8, 23, 0.96) 0%,
      rgba(2, 8, 23, 0.78) 16%,
      rgba(2, 8, 23, 0.35) 34%,
      rgba(2, 8, 23, 0.08) 52%,
      transparent 72%
    );
    pointer-events: none;
    z-index: 5;
  }

  /* Resumo rota */
  .route-summary {
    position: absolute;
    top: 20px;
    right: 20px;
    z-index: 30;
    padding: 10px 14px;
    border-radius: 12px;
    background: rgba(3, 9, 20, 0.95);
    border: 1px solid rgba(255, 255, 255, 0.08);
    color: white;
    font-size: 13px;
    font-weight: 700;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
  }

  /* Badge */
  .location-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    width: fit-content;
    padding: 7px 14px;
    border-radius: 999px;
    background: rgba(22, 168, 94, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.08);
    color: #16A85E;
    font-size: 13px;
    font-weight: 500;
  }

  .dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #10b981;
  }

  /* Título */
  .hero-title {
    margin: 0;
    font-size: 72px;
    line-height: 1.02;
    letter-spacing: -0.04em;
    font-weight: 800;
    color: white;
  }

  .highlight {
    color: #10b981;
  }

  /* Texto */
  .hero-subtitle {
    margin: 0;
    font-size: 18px;
    line-height: 1.8;
    color: #94a3b8;
    max-width: 560px;
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
    border-radius: 12px;
    background: #10b981;
    color: #02120d;
    font-size: 15px;
    font-weight: 700;
    cursor: pointer;
    transition:
      transform 0.2s ease,
      background 0.2s ease;
  }

  .btn-primary:hover {
    background: #059669;
    transform: translateY(-2px);
  }

  .btn-secondary {
    height: 52px;
    padding: 0 28px;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: white;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s ease;
  }

  .btn-secondary:hover {
    background: rgba(255, 255, 255, 0.08);
  }

  /* Estatísticas */
  .stats-container {
    display: flex;
    gap: 42px;
    margin-top: 20px;
    flex-wrap: wrap;
  }

  .stat-card {
    background: none;
    border: none;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 8px;
    text-align: left;
    cursor: pointer;
    transition: transform 0.2s ease;
  }

  .stat-card:hover {
    transform: translateY(-3px);
  }

  .stat-badge {
    width: fit-content;
    padding: 5px 10px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 700;
  }

  .badge-farmacia {
    background: rgba(16, 185, 129, 0.12);
    color: #10b981;
  }

  .badge-hospital {
    background: rgba(59, 130, 246, 0.12);
    color: #3b82f6;
  }

  .badge-restaurante {
    background: rgba(245, 158, 11, 0.12);
    color: #f59e0b;
  }

  .stat-number {
    font-size: 52px;
    line-height: 1;
    font-weight: 800;
    color: white;
  }

  .stat-label {
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.12em;
    color: #64748b;
  }

  /* RESPONSIVO */
  @media (max-width: 1200px) {
    .hero-title {
      font-size: 58px;
    }

    .map-background {
      width: 58%;
    }
  }

  @media (max-width: 1024px) {
    .hero-container {
      padding: 40px 28px;
    }

    .hero-title {
      font-size: 48px;
    }

    .map-background {
      opacity: 0.45;
      width: 100%;
    }

    .map-overlay {
      background: linear-gradient(
        180deg,
        rgba(2, 8, 23, 0.82) 0%,
        rgba(2, 8, 23, 0.92) 100%
      );
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
      align-items: flex-start;
    }

    .btn-primary,
    .btn-secondary {
      width: 100%;
    }
  }
</style>
