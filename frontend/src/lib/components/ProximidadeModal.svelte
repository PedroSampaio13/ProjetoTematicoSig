<script lang="ts">
  import { fade, scale } from 'svelte/transition';

  let { onResults, onCenter }: {
    onResults: (places: any[]) => void;
    onCenter: (lat: number, lon: number) => void;
  } = $props();

  let isOpen = $state(false);
  let categoria = $state<'farmacia' | 'hospital' | 'restaurante'>('farmacia');
  let tempo = $state(15);
  let loading = $state(false);
  let error = $state<string | null>(null);

  // Raio aproximado em graus de latitude para tempo a pé (~83m/min)
  const RADIUS_DEG: Record<number, number> = { 5: 0.004, 15: 0.012, 25: 0.020 };

  const categorias = [
    { id: 'farmacia',    label: 'Farmácia' },
    { id: 'hospital',    label: 'Hospital' },
    { id: 'restaurante', label: 'Restaurante' },
  ] as const;

  const tempos = [5, 15, 25] as const;

  function open() {
    isOpen = true;
    error = null;
  }

  function close() {
    isOpen = false;
    error = null;
    loading = false;
  }

  function handleBackdropClick(e: MouseEvent) {
    if ((e.target as HTMLElement).classList.contains('modal-backdrop')) close();
  }

  async function handleLocalizacao() {
    if (!navigator.geolocation) {
      error = 'Geolocalização não suportada neste browser.';
      return;
    }
    loading = true;
    error = null;

    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const userLat = pos.coords.latitude;
        const userLon = pos.coords.longitude;
        try {
          const res = await fetch(`http://localhost:8000/places/?categoria=${categoria}`);
          if (!res.ok) throw new Error();
          const all: any[] = await res.json();

          const radius = RADIUS_DEG[tempo];
          const nearby = all.filter((p) => {
            const dlat = p.lat - userLat;
            const dlon = p.lon - userLon;
            return Math.sqrt(dlat * dlat + dlon * dlon) <= radius;
          });

          onResults(nearby);
          onCenter(userLat, userLon);
          close();
        } catch {
          error = 'Erro ao carregar locais. Tente novamente.';
          loading = false;
        }
      },
      () => {
        error = 'Não foi possível obter a sua localização.';
        loading = false;
      },
      { timeout: 10000 }
    );
  }
</script>

<!-- Botão fixo no canto inferior esquerdo do mapa -->
<button class="proximity-fab" onclick={open} aria-label="Pesquisar perto de mim" title="Pesquisar perto de mim">
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/>
    <circle cx="12" cy="9" r="2.5"/>
  </svg>
</button>

<!-- Modal -->
{#if isOpen}
  <!-- svelte-ignore a11y_click_events_have_key_events -->
  <!-- svelte-ignore a11y_no_static_element_interactions -->
  <div class="modal-backdrop" onclick={handleBackdropClick} transition:fade={{ duration: 180 }}>
    <div class="modal-content" transition:scale={{ duration: 200, start: 0.94 }}>
      <!-- Cabeçalho -->
      <div class="modal-header">
        <div class="modal-title-row">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="modal-icon">
            <circle cx="12" cy="12" r="3"/>
            <path d="M12 2v3M12 19v3M2 12h3M19 12h3"/>
          </svg>
          <h2 class="modal-title">Pesquisar perto de mim</h2>
        </div>
        <button class="modal-close" onclick={close} aria-label="Fechar">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>

      <!-- Categoria -->
      <div class="field">
        <label class="field-label">Categoria</label>
        <div class="chip-group">
          {#each categorias as cat}
            <button
              class="chip cat-chip cat-{cat.id}"
              class:chip-active={categoria === cat.id}
              onclick={() => categoria = cat.id}
            >
              {cat.label}
            </button>
          {/each}
        </div>
      </div>

      <!-- Tempo a pé -->
      <div class="field">
        <label class="field-label">Distância a pé</label>
        <div class="chip-group">
          {#each tempos as t}
            <button
              class="chip time-chip"
              class:chip-active={tempo === t}
              onclick={() => tempo = t}
            >
              {t} min
            </button>
          {/each}
        </div>
      </div>

      <!-- Erro -->
      {#if error}
        <p class="modal-error" transition:fade={{ duration: 150 }}>{error}</p>
      {/if}

      <!-- Botão principal -->
      <button class="btn-location" onclick={handleLocalizacao} disabled={loading}>
        {#if loading}
          <span class="spinner"></span>
          A obter localização…
        {:else}
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="3"/>
            <path d="M12 2v3M12 19v3M2 12h3M19 12h3"/>
          </svg>
          Usar a minha localização
        {/if}
      </button>
    </div>
  </div>
{/if}

<style>
  /* ── Botão flutuante ── */
  .proximity-fab {
    position: fixed;
    bottom: 24px;
    left: calc(var(--sidebar-width) + 24px);
    z-index: 50;
    width: 44px;
    height: 44px;
    border-radius: var(--radius-md);
    border: 1px solid var(--border);
    background: var(--bg-secondary);
    color: var(--color-farmacia);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    box-shadow: var(--shadow-md);
    transition: all var(--transition);
  }

  .proximity-fab:hover {
    color: var(--color-farmacia);
    border-color: var(--color-farmacia);
    background: var(--color-farmacia-10);
    transform: scale(1.06);
  }

  /* ── Fundo escurecido ── */
  .modal-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.45);
    z-index: 300;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 16px;
  }

  /* ── Modal ── */
  .modal-content {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: var(--radius-xl);
    box-shadow: var(--shadow-lg);
    padding: 24px;
    width: 100%;
    max-width: 380px;
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  .modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .modal-title-row {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .modal-icon {
    color: var(--color-farmacia);
    flex-shrink: 0;
  }

  .modal-title {
    font-family: 'Sora', sans-serif;
    font-size: 15px;
    font-weight: 700;
    color: var(--text-primary);
  }

  .modal-close {
    background: none;
    border: none;
    cursor: pointer;
    color: var(--text-muted);
    padding: 5px;
    border-radius: var(--radius-sm);
    display: flex;
    transition: all var(--transition);
  }

  .modal-close:hover {
    color: var(--text-primary);
    background: var(--bg-hover);
  }

  /* ── Campos do formulário ── */
  .field {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .field-label {
    font-size: 12px;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .chip-group {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }

  .chip {
    padding: 7px 14px;
    border-radius: var(--radius-full);
    border: 1px solid var(--border);
    background: var(--bg-input);
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    font-weight: 500;
    color: var(--text-secondary);
    cursor: pointer;
    transition: all var(--transition);
  }

  .chip:hover {
    border-color: var(--text-muted);
    color: var(--text-primary);
  }

  /* Chips de categoria — cor muda consoante o tipo activo */
  .cat-chip.cat-farmacia.chip-active    { background: var(--color-farmacia-10);    color: var(--color-farmacia);    border-color: var(--color-farmacia); }
  .cat-chip.cat-hospital.chip-active    { background: var(--color-hospital-10);    color: var(--color-hospital);    border-color: var(--color-hospital); }
  .cat-chip.cat-restaurante.chip-active { background: var(--color-restaurante-10); color: var(--color-restaurante); border-color: var(--color-restaurante); }

  .time-chip.chip-active {
    background: var(--color-farmacia-10);
    color: var(--color-farmacia);
    border-color: var(--color-farmacia);
    font-weight: 700;
  }

  /* ── Erro ── */
  .modal-error {
    font-size: 12.5px;
    color: #EF4444;
    background: rgba(239, 68, 68, 0.08);
    border: 1px solid rgba(239, 68, 68, 0.2);
    border-radius: var(--radius-md);
    padding: 8px 12px;
    line-height: 1.4;
  }

  /* ── Botão principal ── */
  .btn-location {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    width: 100%;
    padding: 12px;
    background: var(--color-farmacia);
    color: white;
    border: none;
    border-radius: var(--radius-md);
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: opacity var(--transition);
  }

  .btn-location:hover:not(:disabled) { opacity: 0.88; }
  .btn-location:disabled { opacity: 0.55; cursor: not-allowed; }

  /* ── Animação de carregamento ── */
  .spinner {
    width: 15px;
    height: 15px;
    border: 2px solid rgba(255,255,255,0.35);
    border-top-color: white;
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
    flex-shrink: 0;
  }

  @keyframes spin { to { transform: rotate(360deg); } }
</style>
