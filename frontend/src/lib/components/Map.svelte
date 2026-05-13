<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { theme } from '$lib/stores/theme';

  import OlMap from 'ol/Map';
  import View from 'ol/View';
  import TileLayer from 'ol/layer/Tile';
  import XYZ from 'ol/source/XYZ';
  import VectorLayer from 'ol/layer/Vector';
  import VectorSource from 'ol/source/Vector';
  import Feature from 'ol/Feature';
  import Point from 'ol/geom/Point';
  import { fromLonLat } from 'ol/proj';
  import { Style, Circle, Fill, Stroke, Text } from 'ol/style';
  import Overlay from 'ol/Overlay';
  import 'ol/ol.css';

  // Tiles por tema
  const TILES = {
    dark:  'https://{a-c}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
    light: 'https://{a-c}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
  };

  // Cores por categoria
  const CAT_COLORS: Record<string, string> = {
    farmacia:    '#16A85E',
    hospital:    '#2563EB',
    restaurante: '#D97706',
  };

  let mapContainer: HTMLDivElement;
  let popupEl: HTMLDivElement;
  let map: OlMap;
  let tileLayer: TileLayer<XYZ>;
  let vectorSource = new VectorSource();
  let popup: Overlay;

  // Popup state
  let popupData: { nome: string; categoria: string; morada?: string; aberto?: boolean } | null = $state(null);

  onMount(() => {
    tileLayer = new TileLayer({
      source: new XYZ({ url: TILES[$theme] }),
    });

    const vectorLayer = new VectorLayer({
      source: vectorSource,
    });

    popup = new Overlay({
      element: popupEl,
      positioning: 'bottom-center',
      stopEvent: false,
      offset: [0, -10],
    });

    map = new OlMap({
      target: mapContainer,
      layers: [tileLayer, vectorLayer],
      overlays: [popup],
      view: new View({
        center: fromLonLat([-8.2, 39.5]),
        zoom: 7,
        minZoom: 6,
        maxZoom: 18,
      }),
    });

    // Click em marcador → abrir popup
    map.on('click', (evt) => {
      const feature = map.forEachFeatureAtPixel(evt.pixel, f => f);
      if (feature) {
        const props = feature.getProperties();
        const geom = feature.getGeometry() as Point;
        popup.setPosition(geom.getCoordinates());
        popupData = {
          nome: props.nome ?? 'Local',
          categoria: props.categoria ?? 'farmacia',
          morada: props.morada,
          aberto: props.aberto,
        };
      } else {
        popupData = null;
        popup.setPosition(undefined);
      }
    });

    // Cursor pointer sobre marcadores
    map.on('pointermove', (evt) => {
      const hit = map.hasFeatureAtPixel(evt.pixel);
      (map.getTargetElement() as HTMLElement).style.cursor = hit ? 'pointer' : '';
    });
  });

  // Trocar tiles quando o tema muda
  $effect(() => {
    if (!tileLayer) return;
    tileLayer.setSource(new XYZ({ url: TILES[$theme] }));
  });

  // Expor função para adicionar marcadores
  export function addMarkers(places: Array<{
    id: string | number;
    nome: string;
    categoria: 'farmacia' | 'hospital' | 'restaurante';
    lat: number;
    lon: number;
    morada?: string;
    aberto?: boolean;
  }>) {
    vectorSource.clear();
    for (const p of places) {
      const color = CAT_COLORS[p.categoria];
      const feature = new Feature({
        geometry: new Point(fromLonLat([p.lon, p.lat])),
        nome: p.nome,
        categoria: p.categoria,
        morada: p.morada,
        aberto: p.aberto,
      });
      feature.setStyle(new Style({
        image: new Circle({
          radius: 9,
          fill: new Fill({ color }),
          stroke: new Stroke({ color: 'rgba(255,255,255,0.9)', width: 2 }),
        }),
      }));
      vectorSource.addFeature(feature);
    }
  }

  export function clearMarkers() {
    vectorSource.clear();
    popupData = null;
    popup?.setPosition(undefined);
  }

  export function focusPlace(place: {
    nome: string;
    categoria: string;
    morada?: string;
    lat: number;
    lon: number;
  }) {
    const coords = fromLonLat([place.lon, place.lat]);
    map.getView().animate({ center: coords, zoom: 15, duration: 600 });
    popup.setPosition(coords);
    popupData = {
      nome: place.nome,
      categoria: place.categoria,
      morada: place.morada,
    };
  }

  onDestroy(() => map?.dispose());
</script>

<div class="map-wrapper">
  <div bind:this={mapContainer} class="map"></div>

  <!-- Popup de detalhe -->
  <div bind:this={popupEl} class="popup" class:popup-visible={popupData !== null}>
    {#if popupData}
      <div class="popup-inner">
        <div class="popup-header">
          <span class="popup-dot" style="background: {CAT_COLORS[popupData.categoria]}"></span>
          <strong class="popup-nome">{popupData.nome}</strong>
          <button class="popup-close" onclick={() => { popupData = null; popup.setPosition(undefined); }} aria-label="Fechar">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        {#if popupData.morada}
          <p class="popup-morada">{popupData.morada}</p>
        {/if}
        {#if popupData.aberto !== undefined}
          <span class="popup-badge" class:badge-open={popupData.aberto} class:badge-closed={!popupData.aberto}>
            {popupData.aberto ? 'Aberto' : 'Fechado'}
          </span>
        {/if}
      </div>
    {/if}
  </div>
</div>

<style>
  .map-wrapper {
    position: relative;
    width: 100%;
    height: 100%;
  }

  .map {
    width: 100%;
    height: 100%;
  }

  /* Popup */
  .popup {
    position: absolute;
    pointer-events: none;
    opacity: 0;
    transform: translateY(4px);
    transition: opacity 0.2s ease, transform 0.2s ease;
  }

  .popup-visible {
    opacity: 1;
    transform: translateY(0);
    pointer-events: auto;
  }

  .popup-inner {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-popup);
    padding: 12px 14px;
    min-width: 200px;
    max-width: 260px;
  }

  .popup-header {
    display: flex;
    align-items: center;
    gap: 7px;
    margin-bottom: 6px;
  }

  .popup-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
  }

  .popup-nome {
    font-family: 'Sora', sans-serif;
    font-size: 13px;
    font-weight: 600;
    color: var(--text-primary);
    flex: 1;
    line-height: 1.3;
  }

  .popup-close {
    background: none;
    border: none;
    cursor: pointer;
    color: var(--text-muted);
    padding: 2px;
    border-radius: 4px;
    display: flex;
    transition: color var(--transition);
  }

  .popup-close:hover { color: var(--text-primary); }

  .popup-morada {
    font-size: 12px;
    color: var(--text-secondary);
    margin-bottom: 8px;
    line-height: 1.4;
  }

  .popup-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: var(--radius-full);
    font-size: 11px;
    font-weight: 600;
  }

  .badge-open  { background: var(--color-farmacia-10);    color: var(--color-farmacia); }
  .badge-closed{ background: rgba(239,68,68,0.1); color: #EF4444; }

  /* Override estilos do OpenLayers para combinar com o tema */
  :global(.ol-attribution) { display: none !important; }
  :global(.ol-zoom) {
    bottom: 24px !important;
    right: 24px !important;
    top: auto !important;
    left: auto !important;
  }
  :global(.ol-zoom button) {
    background: var(--bg-secondary) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    width: 32px !important;
    height: 32px !important;
    font-size: 18px !important;
    box-shadow: var(--shadow-sm) !important;
    transition: background var(--transition) !important;
  }
  :global(.ol-zoom button:hover) {
    background: var(--bg-hover) !important;
  }
  :global(.ol-zoom-in) { margin-bottom: 4px !important; }
</style>