<script lang="ts">
  // props e estado do componente
  let {
    onSearch = (_q: string) => {},
    onFiltersChange = (_f: Filters) => {},
  }: {
    onSearch?: (query: string) => void;
    onFiltersChange?: (filters: Filters) => void;
  } = $props();

  export interface Filters {
    categories: Set<Category>;
    time: number;
  }

  type Category = 'farmacia' | 'hospital' | 'restaurante';

  // Estado de pesquisa
  let searchQuery = $state('');

  // Estado dos filtros
  let activeCategories = $state<Set<Category>>(new Set(['farmacia', 'hospital', 'restaurante']));
  let activeTime = $state<number>(15);

  const CATEGORIES = [
    { id: 'farmacia' as Category,    label: 'Farmácias',    color: 'var(--color-farmacia)',    icon: '💊' },
    { id: 'hospital' as Category,    label: 'Hospitais',    color: 'var(--color-hospital)',    icon: '🏥' },
    { id: 'restaurante' as Category, label: 'Restaurantes', color: 'var(--color-restaurante)', icon: '🍽️' },
  ];

  const TIMES = [5, 15, 25];

  // avisa o componente pai sempre que os filtros mudam
  function toggleCategory(cat: Category) {
    const next = new Set(activeCategories);
    if (next.has(cat)) {
      if (next.size > 1) next.delete(cat); // pelo menos 1 ativa
    } else {
      next.add(cat);
    }
    activeCategories = next;
    emitFilters();
  }

  function setTime(t: number) {
    activeTime = t;
    emitFilters();
  }

  function emitFilters() {
    onFiltersChange({ categories: activeCategories, time: activeTime });
  }

  function handleSearch(e: Event) {
    e.preventDefault();
    onSearch(searchQuery);
  }

  function clearSearch() {
    searchQuery = '';
    onSearch('');
  }
</script>

<aside class="sidebar">
  <!-- Pesquisa -->
  <div class="sidebar-section">
    <form class="search-wrapper" onsubmit={handleSearch}>
      <span class="search-icon">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
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
        <button type="button" class="search-clear" onclick={clearSearch} aria-label="Limpar pesquisa">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
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
          onclick={() => setTime(t)}
          aria-pressed={activeTime === t}
        >
          {t} min
        </button>
      {/each}
    </div>
  </div>

  <div class="sidebar-divider"></div>

  <!-- Resultados (slot para a lista) -->
  <div class="sidebar-results" role="region" aria-label="Resultados">
    <div class="results-header">
      <p class="section-label">Resultados</p>
      <span class="results-count">—</span>
    </div>
    <div class="results-empty">
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" opacity="0.3">
        <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
      </svg>
      <p>Usa a pesquisa ou clica no mapa</p>
    </div>
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
    transition: background-color var(--transition-slow), border-color var(--transition-slow);
    z-index: 50;
  }

  /* Secções */
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

  /* campo de pesquisa */
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
    font-family: 'Inter', sans-serif;
    font-size: 13.5px;
    color: var(--text-primary);
    transition: border-color var(--transition), box-shadow var(--transition);
    outline: none;
  }

  .search-input::placeholder { color: var(--text-muted); }

  .search-input:focus {
    border-color: var(--color-farmacia);
    box-shadow: 0 0 0 3px var(--color-farmacia-10);
  }

  /* esconde o X nativo do browser no input search */
  .search-input::-webkit-search-cancel-button { display: none; }

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

  .search-clear:hover { color: var(--text-primary); }

  /* botões de categoria */
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
    font-family: 'Inter', sans-serif;
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

  /* botões de tempo a pé */
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
    font-family: 'Inter', sans-serif;
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

  /* Resultados */
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

  .results-header .section-label { margin-bottom: 0; }

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
</style>
