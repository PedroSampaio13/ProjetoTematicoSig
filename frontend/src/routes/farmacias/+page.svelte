<script lang="ts">
  import { onMount } from 'svelte';
  import Navbar from '$lib/components/Navbar.svelte';
  import Sidebar from '$lib/components/Sidebar.svelte';
  import MapComponent from '$lib/components/Map.svelte';

  let mapRef: MapComponent;

  type SelectedPoint = {
    lat: number;
    lon: number;
  } | null;

  let places = $state<any[]>([]);
  let loading = $state(false);
  let searched = $state(false);
  let selectedPoint = $state<SelectedPoint>(null);

  async function fetchPlaces(query: string, categories: Set<string>) {
    loading = true;
    searched = true;

    try {
      const activeCats = [...categories];

      const results = await Promise.all(
        activeCats.map((cat) => {
          const params = new URLSearchParams({ categoria: cat });

          if (query) {
            params.set('query', query);
          }

          return fetch(`http://localhost:8000/places/?${params}`).then((r) =>
            r.json()
          );
        })
      );

      places = results.flat();
      mapRef?.addMarkers(places);
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    fetchPlaces('', new Set(['farmacia']));
  });

  function handleSearch(query: string, categories: Set<string>) {
    fetchPlaces(query, categories);
  }

  function handleMapClick(point: { lat: number; lon: number }) {
    selectedPoint = point;
    console.log('Ponto selecionado no mapa:', selectedPoint);
  }

  async function handleTimeSearch(
  lat: number,
  lon: number,
  radius_m: number,
  categories: Set<string>
) {
  loading = true;
  searched = true;

  try {
    const activeCats = [...categories];

    const results = await Promise.all(
      activeCats.map((cat) => {
        const params = new URLSearchParams({
          lat: String(lat),
          lon: String(lon),
          radius_m: String(radius_m),
          categoria: cat
        });

        return fetch(`http://localhost:8000/places/nearby?${params}`).then(
          (r) => r.json()
        );
      })
    );

    const flatResults = results.flat();

    console.log('Raio pesquisado:', radius_m);
    console.log('Resultados recebidos:', flatResults.length);

    places = flatResults;
    mapRef?.addMarkers(places);
  } finally {
    loading = false;
  }
}

  function onPlaceClick(place: any) {
    mapRef?.focusPlace(place);
  }
</script>

<div class="app-layout">
  <Navbar activeTab="farmacias" />

  <div class="app-body">
    <Sidebar
      onSearch={handleSearch}
      onTimeSearch={handleTimeSearch}
      selectedPoint={selectedPoint}
      {places}
      {loading}
      {searched}
      {onPlaceClick}
    />

    <main class="map-area">
      <MapComponent bind:this={mapRef} onLocationSelect={handleMapClick} />
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