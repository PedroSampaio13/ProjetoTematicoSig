<script lang="ts">
  import Navbar from '$lib/components/Navbar.svelte';
  import Sidebar from '$lib/components/Sidebar.svelte';
  import MapComponent from '$lib/components/Map.svelte';

  let mapRef: MapComponent;

  function handleSearch(query: string) {
    console.log('Pesquisa:', query);
    // TODO: ligar ao backend FastAPI
  }

  function handleFiltersChange(filters: { categories: Set<string>; radius: number }) {
    console.log('Filtros:', filters);
    // TODO: ligar ao backend FastAPI
  }
</script>

<div class="app-layout">
  <Navbar />
  <div class="app-body">
    <Sidebar onSearch={handleSearch} onFiltersChange={handleFiltersChange} />
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
