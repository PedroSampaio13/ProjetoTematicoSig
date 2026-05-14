<script lang="ts">
  import Navbar from '$lib/components/Navbar.svelte';
  import Sidebar from '$lib/components/Sidebar.svelte';
  import MapComponent from '$lib/components/Map.svelte';
  import ProximidadeModal from '$lib/components/ProximidadeModal.svelte';

  let mapRef: MapComponent;
  let proximityModalRef: ProximidadeModal;

  let places = $state<any[]>([]);
  let loading = $state(false);
  let searched = $state(false);
  let selectedLocation = $state<{ lat: number; lon: number } | null>(null);
  let routeSummary = $state<{ distance_m: number; duration_min: number } | null>(null);
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
      mapRef?.clearRouteArea();
      mapRef?.clearRoute();
      routeSummary = null;
      routeError = null;
      mapRef?.addMarkers(places);
    } finally {
      loading = false;
    }
  }

  function handleSearch(query: string, categories: Set<string>) {
    fetchPlaces(query, categories);
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
          profile: 'driving',
        }),
      });

      if (!res.ok) throw new Error();
      const route = await res.json();
      mapRef?.drawRoute(route.geometry);
      routeSummary = {
        distance_m: route.distance_m,
        duration_min: route.duration_min,
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

  function handleLocationSelect(location: { lat: number; lon: number }) {
    selectedLocation = location;
    mapRef?.clearRoute();
    routeSummary = null;
    routeError = null;
    proximityModalRef?.open();
  }

  function formatDistance(meters: number) {
    if (meters < 1000) return `${meters} m`;
    return `${(meters / 1000).toFixed(1).replace('.', ',')} km`;
  }
</script>

<div class="app-layout">
  <Navbar activeTab="mapa" />

  <div class="app-body">
    <Sidebar onSearch={handleSearch} {places} {loading} {searched} {onPlaceClick} />
    <main class="map-area">
      <MapComponent
        bind:this={mapRef}
        onLocationSelect={handleLocationSelect}
        onPlaceSelect={calculateRoute}
      />
      {#if routeSummary || routeError}
        <div class="route-summary">
          {#if routeSummary}
            Rota: {formatDistance(routeSummary.distance_m)} · {routeSummary.duration_min} min
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
