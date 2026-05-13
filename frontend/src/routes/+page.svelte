<script lang="ts">
  import Navbar from '$lib/components/Navbar.svelte';
  import Sidebar from '$lib/components/Sidebar.svelte';
  import MapComponent from '$lib/components/Map.svelte';

  let mapRef: MapComponent;

  let places = $state<any[]>([]);
  let loading = $state(false);
  let searched = $state(false);

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
      mapRef?.addMarkers(places);
    } finally {
      loading = false;
    }
  }

  function handleSearch(query: string, categories: Set<string>) {
    fetchPlaces(query, categories);
  }

  function onPlaceClick(place: any) {
    mapRef?.focusPlace(place);
  }
</script>

<div class="app-layout">
  <Navbar />
  <div class="app-body">
    <Sidebar onSearch={handleSearch} {places} {loading} {searched} {onPlaceClick} />
    <main class="map-area">
      <MapComponent bind:this={mapRef} />
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
  }
</style>
