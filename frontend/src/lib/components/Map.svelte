<script lang="ts">
	import { onMount } from 'svelte';

	import Map from 'ol/Map';
	import View from 'ol/View';

	import TileLayer from 'ol/layer/Tile';
	import OSM from 'ol/source/OSM';

	import 'ol/ol.css';

	let mapContainer: HTMLDivElement;

	onMount(() => {
		new Map({
			target: mapContainer,
			layers: [
				new TileLayer({
					source: new OSM()
				})
			],
			view: new View({
				center: [-850000, 4800000],
				zoom: 6.9
			})
		});
	});
</script>

<div bind:this={mapContainer} class="map"></div>

<style>
	.map {
		width: 100%;
		height: 100vh;
	}
</style>