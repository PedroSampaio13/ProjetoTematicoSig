<script lang="ts">
  type Category = 'farmacia' | 'hospital' | 'restaurante';

  type Place = {
    id: string | number;
    nome: string;
    morada?: string;
    lat: number;
    lon: number;
    categoria: Category;
    distancia_m?: number;
    tempo_min?: number;
    estado: boolean;
    24: boolean;
  };

  type SelectedPoint = {
  lat: number;
  lon: number;
} | null;

let {
  onSearch = (_q: string, _c: Set<Category>) => {},
  onTimeSearch = (_lat: number, _lon: number, _radius_m: number, _c: Set<Category>) => {},
  onPlaceClick = (_p: Place) => {},
  selectedPoint = null as SelectedPoint,
  places = [] as Place[],
  loading = false,
  searched = false,
}: {
  onSearch?: (query: string, categories: Set<Category>) => void;
  onTimeSearch?: (lat: number, lon: number, radius_m: number, categories: Set<Category>) => void;
  onPlaceClick?: (place: Place) => void;
  selectedPoint?: SelectedPoint;
  places?: Place[];
  loading?: boolean;
  searched?: boolean;
} = $props();

  let searchQuery = $state("");
  let activeCategories = $state<Set<Category>>(
    new Set(["farmacia", "hospital", "restaurante"]),
  );
  let activeTime = $state<number>(15);
  let geoLoading = $state<number | null>(null);
  let geoError = $state<string | null>(null);

  const CATEGORIES = [
    {id: "farmacia" as Category, label: "Farmácias", color: "var(--color-farmacia)", icon: "💊"},
    {id: "hospital" as Category, label: "Hospitais", color: "var(--color-hospital)", icon: "🏥"},
    {id: "restaurante" as Category, label: "Restaurantes", color: "var(--color-restaurante)", icon: "🍽️",},
  ];

  const CAT_COLORS: Record<Category, string> = {
    farmacia: "var(--color-farmacia)",
    hospital: "var(--color-hospital)",
    restaurante: "var(--color-restaurante)",
  };

  const CAT_LABELS: Record<Category, string> = {
    farmacia: "Farmácia",
    hospital: "Hospital",
    restaurante: "Restaurante",
  };

  const TIMES = [5, 15, 25];
  const TIME_RADII: Record<number, number> = { 5: 415, 15: 1245, 25: 2075 };

  function toggleCategory(cat: Category) {
    const next = new Set(activeCategories);
    if (next.has(cat)) {
      if (next.size > 1) next.delete(cat);
    } else {
      next.add(cat);
    }
    activeCategories = next;
  }

  function handleTimeClick(t: number) {
  activeTime = t;
  geoError = null;

  if (!selectedPoint) {
    geoError = 'Clica primeiro num ponto no mapa para pesquisares nessa zona.';
    return;
  }

  onTimeSearch(
    selectedPoint.lat,
    selectedPoint.lon,
    TIME_RADII[t],
    activeCategories
  );
}

  function handleSearch(e: Event) {
    e.preventDefault();
    onSearch(searchQuery, activeCategories);
  }

  function clearSearch() {
    searchQuery = "";
    onSearch("", activeCategories);
  }

  function formatDistance(meters: number) {
    if (meters < 1000) return `${meters} m`;
    return `${(meters / 1000).toFixed(1).replace(".", ",")} km`;
  }
</script>

<aside class="sidebar">
  <!-- Pesquisa -->
  <div class="sidebar-section">
    <form class="search-wrapper" onsubmit={handleSearch}>
      <span class="search-icon">
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <circle cx="11" cy="11" r="8" /><line
            x1="21"
            y1="21"
            x2="16.65"
            y2="16.65"
          />
        </svg>
      </span>
      <input
        type="search"
        class="search-input"
        placeholder="Pesquisar local..."
        bind:value={searchQuery}
        aria-label="Pesquisar local"
      />
      {#if searchQuery}
        <button
          type="button"
          class="search-clear"
          onclick={clearSearch}
          aria-label="Limpar pesquisa"
        >
          <svg
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2.5"
            stroke-linecap="round"
          >
            <line x1="18" y1="6" x2="6" y2="18" /><line
              x1="6"
              y1="6"
              x2="18"
              y2="18"
            />
          </svg>
        </button>
      {/if}
    </form>
  </div>

  <div class="sidebar-divider"></div>

  <!-- Filtros de categoria -->
  <div class="sidebar-section">
    <p class="section-label">Categoria</p>
    <div class="category-chips">
      {#each CATEGORIES as cat}
        {@const isActive = activeCategories.has(cat.id)}
        <button
          class="chip"
          class:chip-active={isActive}
          style="--chip-color: {cat.color}"
          onclick={() => toggleCategory(cat.id)}
          aria-pressed={isActive}
        >
          <span class="chip-dot"></span>
          {cat.label}
        </button>
      {/each}
    </div>
  </div>

  <div class="sidebar-divider"></div>

  <!-- Filtro de tempo a pé -->
  <div class="sidebar-section">
    <p class="section-label">Tempo de deslocação</p>
    <div class="radius-buttons">
      {#each TIMES as t}
        <button
          class="radius-btn"
          class:radius-active={activeTime === t}
          onclick={() => handleTimeClick(t)}
          aria-pressed={activeTime === t}
          disabled={geoLoading !== null}
        >
          {#if geoLoading === t}
            <span class="spinner-sm" aria-label="A obter localização"></span>
          {:else}
            {t} min
          {/if}
        </button>
      {/each}
    </div>
    {#if geoError}
      <p class="geo-error">{geoError}</p>
    {/if}
  </div>

  <div class="sidebar-divider"></div>

  <!-- Resultados -->
  <div class="sidebar-results" role="region" aria-label="Resultados">
    <div class="results-header">
      <p class="section-label">Resultados</p>
      {#if searched && !loading}
        <span class="results-count">{places.length}</span>
      {:else}
        <span class="results-count">—</span>
      {/if}
    </div>

    {#if loading}
      <div class="results-empty">
        <span class="spinner" aria-label="A carregar"></span>
      </div>
    {:else if !searched}
      <div class="results-empty">
        <svg
          width="32"
          height="32"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.5"
          stroke-linecap="round"
          stroke-linejoin="round"
          opacity="0.3"
        >
          <circle cx="11" cy="11" r="8" /><line
            x1="21"
            y1="21"
            x2="16.65"
            y2="16.65"
          />
        </svg>
        <p>Usa a pesquisa ou clica no mapa</p>
      </div>
    {:else if places.length === 0}
      <div class="results-empty">
        <svg
          width="32"
          height="32"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.5"
          stroke-linecap="round"
          stroke-linejoin="round"
          opacity="0.3"
        >
          <circle cx="11" cy="11" r="8" /><line
            x1="21"
            y1="21"
            x2="16.65"
            y2="16.65"
          />
        </svg>
        <p>Nenhum resultado encontrado</p>
      </div>
    {:else}
      <ul class="result-list">
        {#each places as place}
          <li>
            <button class="result-item" onclick={() => onPlaceClick(place)}>
              <div class="result-info-dot">
                <span
                  class="result-dot"
                  style="background: {CAT_COLORS[place.categoria]}"
                ></span>
                <span class="result-info">
                  <span class="result-nome">{place.nome}</span>
                  {#if place.morada}
                    <span class="result-morada">{place.morada}</span>
                  {/if}
                </span>
              </div>
              <div class="result-bottom">
                {#if place.distancia_m !== undefined || place.tempo_min !== undefined}
                  <span class="result-metrics">
                    <span>📍</span>
                    {#if place.distancia_m !== undefined}
                      {formatDistance(place.distancia_m)}
                    {/if}
                    {#if place.distancia_m !== undefined && place.tempo_min !== undefined}
                      ·
                    {/if}
                    {#if place.tempo_min !== undefined}
                      {place.tempo_min} min
                    {/if}
                  </span>
                  {#if place.estado}
                    <span class="result-estado-{place.estado}">
                      {place.estado === true ? "Aberto" : "Fechado"}
                    </span>
                  {/if}
                {/if}
              </div>
            </button>
          </li>
        {/each}
      </ul>
    {/if}
  </div>
</aside>

<style>
  .sidebar {
    position: fixed;
    top: var(--navbar-height);
    left: 0;
    bottom: 0;
    width: var(--sidebar-width);
    background: var(--bg-sidebar);
    border-right: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    transition:
      background-color var(--transition-slow),
      border-color var(--transition-slow);
    z-index: 50;
  }

  /* Expõe a variável para fora do componente */
  :global(:root) {
    --panel-width: var(--sidebar-width);
  }

  .sidebar-section {
    padding: 16px 16px 14px;
  }

  .sidebar-divider {
    height: 1px;
    background: var(--border);
    flex-shrink: 0;
  }

  .section-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 10px;
  }

  .search-wrapper {
    position: relative;
    display: flex;
    align-items: center;
  }

  .search-icon {
    position: absolute;
    left: 11px;
    color: var(--text-muted);
    pointer-events: none;
    display: flex;
  }

  .search-input {
    width: 100%;
    height: 38px;
    padding: 0 36px 0 36px;
    background: var(--bg-input);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    font-family: "Inter", sans-serif;
    font-size: 13.5px;
    color: var(--text-primary);
    transition:
      border-color var(--transition),
      box-shadow var(--transition);
    outline: none;
  }

  .search-input::placeholder {
    color: var(--text-muted);
  }

  .search-input:focus {
    border-color: var(--color-farmacia);
    box-shadow: 0 0 0 3px var(--color-farmacia-10);
  }

  .search-input::-webkit-search-cancel-button {
    display: none;
  }

  .search-clear {
    position: absolute;
    right: 10px;
    background: none;
    border: none;
    cursor: pointer;
    color: var(--text-muted);
    display: flex;
    padding: 2px;
    border-radius: var(--radius-sm);
    transition: color var(--transition);
  }

  .search-clear:hover {
    color: var(--text-primary);
  }

  .category-chips {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .chip {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    background: var(--bg-input);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    font-family: "Inter", sans-serif;
    font-size: 13px;
    font-weight: 500;
    color: var(--text-secondary);
    cursor: pointer;
    transition: all var(--transition);
    text-align: left;
  }

  .chip:hover {
    border-color: var(--chip-color);
    color: var(--text-primary);
  }

  .chip-active {
    background: color-mix(in srgb, var(--chip-color) 12%, transparent);
    border-color: color-mix(in srgb, var(--chip-color) 40%, transparent);
    color: var(--chip-color);
  }

  .chip-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--chip-color);
    flex-shrink: 0;
    transition: transform var(--transition);
  }

  .chip-active .chip-dot {
    transform: scale(1.2);
    box-shadow: 0 0 0 3px color-mix(in srgb, var(--chip-color) 20%, transparent);
  }

  .radius-buttons {
    display: flex;
    gap: 6px;
  }

  .radius-btn {
    flex: 1;
    padding: 7px 0;
    background: var(--bg-input);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    font-family: "Inter", sans-serif;
    font-size: 12.5px;
    font-weight: 500;
    color: var(--text-secondary);
    cursor: pointer;
    transition: all var(--transition);
  }

  .radius-btn:hover {
    border-color: var(--color-farmacia);
    color: var(--text-primary);
  }

  .radius-active {
    background: var(--color-farmacia-10);
    border-color: var(--color-farmacia);
    color: var(--color-farmacia);
    font-weight: 600;
  }

  .radius-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .spinner-sm {
    display: inline-block;
    width: 12px;
    height: 12px;
    border: 2px solid var(--border);
    border-top-color: var(--color-farmacia);
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
  }

  .geo-error {
    font-size: 11px;
    color: var(--color-red);
    margin-top: 6px;
  }

  .sidebar-results {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
  }

  .results-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;
  }

  .results-header .section-label {
    margin-bottom: 0;
  }

  .results-count {
    font-size: 12px;
    color: var(--text-muted);
    font-weight: 500;
  }

  .results-empty {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    padding: 32px 0;
    color: var(--text-muted);
    text-align: center;
  }

  .results-empty p {
    font-size: 12.5px;
    line-height: 1.5;
  }

  /* Spinner */
  .spinner {
    display: block;
    width: 28px;
    height: 28px;
    border: 3px solid var(--border);
    border-top-color: var(--color-farmacia);
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  /* Lista de resultados */
  .result-list {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .result-item {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
    width: 100%;
    padding: 10px 20px;
    background: var(--bg-card);
    border: 1px solid transparent;
    border-radius: var(--radius-md);
    cursor: pointer;
    text-align: left;
    transition:
      background var(--transition),
      border-color var(--transition);
  }

  .result-info {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .result-item:hover {
    background: var(--bg-input);
    border-color: var(--border);
  }

  .result-item:focus {
    background: var(--bg-input);
    border-color: var(--bg-farmacia);
    border-left: 5px;
    border-style: solid;
  }

  .result-info-dot {
    display: flex;
    gap: 10px;
    min-width: 0;
  }
  
  .result-dot {
    justify-content: left;
    width: 30px;
    height: 30px;
    border-radius: 20%;
    flex-shrink: 0;
    margin-top: 4px;
  }

  .result-info {
    width: auto;
    justify-content: right;
    display: flex;
    flex-direction: column;
    gap: 2px;
    min-width: 0;
  }

  .result-nome {
    font-family: "Inter", sans-serif;
    font-size: 15px;
    font-weight: 600;
    color: var(--text-primary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .result-morada {
    font-size: 11.5px;
    color: var(--text-secondary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .result-bottom {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    margin-top: 6px;
    opacity: 0.9;
  }

  .result-metrics {
    font-size: 11.5px;
    color: var(--text-primary);
    font-weight: 600;
  }

  .result-estado-aberto,
  .result-estado-Aberto {
    display: flex;
    color: var(--color-green);
    padding: 0px 10px;
    background-color: var(--bg-green-30);
    border: 2px solid var(--color-green);
    border-radius: 10px;
  }

  .result-estado-fechado,
  .result-estado-Fechado {
    display: flex;
    color: var(--color-red);
    background-color: var(--bg-red-30);
    padding: 0px 10px;
    border: 2px solid var(--color-red);
    border-radius: 10px;
  }
</style>
