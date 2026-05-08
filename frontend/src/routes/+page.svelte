<script lang="ts">
	import Map from '$lib/components/Map.svelte';

	let message = '';

	async function testar() {
		const res = await fetch('http://localhost:8000/test');
		const data = await res.json();

		message = data.message;
	}
</script>

<button on:click={testar}>
	Testar API
</button>

<p>{message}</p>

<Map />