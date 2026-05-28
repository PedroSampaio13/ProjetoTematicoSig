<script lang="ts">
  import { onMount } from 'svelte';
  import Navbar from '$lib/components/Navbar.svelte';
  import Sidebar from '$lib/components/Sidebar.svelte';
  import MapComponent from '$lib/components/Map.svelte';
  let mapRef: MapComponent;

  let places = $state<any[]>([]);
  let loading = $state(false);
  let searched = $state(false);
  let selectedPoint = $state<{ lat: number; lon: number } | null>(null);
  let selectedLocation = $state<{ lat: number; lon: number } | null>(null);
  let routeSummary = $state<{ distance_m: number; duration_min: number; estimated?: boolean } | null>(null);
  let routeError = $state<string | null>(null);

  async function fetchPlaces(query: string, categories: Set<string>) {
    loading = true;
    searched = true;
    try {
      const activeCats = [...categories];
      const results = await Promise.all(
        activeCats.map((cat) => {
          const params = new URLSearchParams({ categoria: cat });
          if (query) params.set('query', query);
          return fetch(`http://localhost:8000/places/?${params}`).then((r) => r.json());
        })
      );
      places = results.flat();
      routeSummary = null;
      routeError = null;
      mapRef?.addMarkers(places);
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    fetchPlaces('', new Set(['hospitais']));
  });

  function handleSearch(query: string, categories: Set<string>) {
    fetchPlaces(query, categories);
  }

  async function handleTimeSearch(lat: number, lon: number, radius_m: number, categories: Set<string>) {
    loading = true;
    searched = true;
    try {
      const activeCats = [...categories];
      const results = await Promise.all(
        activeCats.map((cat) => {
          const params = new URLSearchParams({ lat: String(lat), lon: String(lon), radius_m: String(radius_m), categoria: cat });
          return fetch(`http://localhost:8000/places/nearby?${params}`).then((r) => r.json());
        })
      );
      places = results.flat();
      routeSummary = null;
      routeError = null;
      mapRef?.addMarkers(places);
    } finally {
      loading = false;
    }
  }

  async function calculateRoute(place: any) {
    if (!selectedLocation) return;

    routeError = null;
    try {
      const res = await fetch('http://localhost:8000/routes/calculate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          origin: selectedLocation,
          destination: { lat: place.lat, lon: place.lon },
          profile: 'walking',
        }),
      });

      if (!res.ok) throw new Error();
      const route = await res.json();
      mapRef?.drawRoute(route.geometry);
      routeSummary = {
        distance_m: route.distance_m,
        duration_min: route.duration_min,
        estimated: route.estimated,
      };
    } catch {
      routeError = 'Nao foi possivel calcular a rota.';
      routeSummary = null;
      mapRef?.clearRoute();
    }
  }

  function onPlaceClick(place: any) {
    mapRef?.focusPlace(place);
    calculateRoute(place);
  }

  function handleLocationSelect(location: { lat: number; lon: number }) {
    selectedPoint = location;
    selectedLocation = location;
    mapRef?.clearRoute();
    routeSummary = null;
    routeError = null;
  }

  function formatDistance(meters: number) {
    if (meters < 1000) return `${meters} m`;
    return `${(meters / 1000).toFixed(1).replace('.', ',')} km`;
  }
</script>

<div class="app-layout">
  <Navbar activeTab="hospitais" />

  <div class="app-body">
    <Sidebar onSearch={handleSearch} onTimeSearch={handleTimeSearch} selectedPoint={selectedPoint} {places} {loading} {searched} {onPlaceClick} />
    <main class="map-area">
      <MapComponent
        bind:this={mapRef}
        onLocationSelect={handleLocationSelect}
        onPlaceSelect={calculateRoute}
      />
      {#if routeSummary || routeError}
        <div class="route-summary">
          {#if routeSummary}
            Rota{routeSummary.estimated ? ' estimada' : ''}: {formatDistance(routeSummary.distance_m)} · {routeSummary.duration_min} min
          {:else}
            {routeError}
          {/if}
        </div>
      {/if}
    </main>
  </div>
</div>

<style>
  .app-layout {
    display: flex;
    flex-direction: column;
    height: 100vh;
    overflow: hidden;
  }

  .app-body {
    display: flex;
    flex: 1;
    overflow: hidden;
    margin-top: var(--navbar-height);
  }

  .map-area {
    flex: 1;
    margin-left: var(--sidebar-width);
    height: 100%;
    overflow: hidden;
    position: relative;
  }

  .route-summary {
    position: absolute;
    top: 16px;
    right: 16px;
    z-index: 60;
    padding: 10px 14px;
    border-radius: var(--radius-md);
    border: 1px solid var(--border);
    background: var(--bg-secondary);
    color: var(--text-primary);
    font-size: 13px;
    font-weight: 700;
    box-shadow: var(--shadow-md);
  }
</style>
