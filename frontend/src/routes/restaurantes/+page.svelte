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
      mapRef?.clearRoute();
      mapRef?.addMarkers(places);
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    fetchPlaces('', new Set(['restaurante']));
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
      mapRef?.clearRoute();
      mapRef?.addMarkers(places);
    } finally {
      loading = false;
    }
  }

  async function calculateRoute(place: any) {
    if (!selectedLocation) return;

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
    } catch {
      mapRef?.clearRoute();
    }
  }

  function handleMapClick(point: { lat: number; lon: number }) {
    selectedPoint = point;
    selectedLocation = point;
    mapRef?.clearRoute();
  }

  function onPlaceClick(place: any) {
    mapRef?.focusPlace(place);
    calculateRoute(place);
  }
</script>

<div class="app-layout">
  <Navbar activeTab="restaurantes" />

  <div class="app-body">
    <Sidebar onSearch={handleSearch} onTimeSearch={handleTimeSearch} initialCategories={['restaurante']} selectedPoint={selectedPoint} {places} {loading} {searched} {onPlaceClick} />
    <main class="map-area">
      <MapComponent bind:this={mapRef} onLocationSelect={handleMapClick} onPlaceSelect={onPlaceClick} />
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
</style>
