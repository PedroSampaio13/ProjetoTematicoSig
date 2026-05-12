<script lang="ts">
  import '../app.css';
  import { theme } from '$lib/stores/theme';
  import favicon from '$lib/assets/favicon.svg';

  let { children } = $props();
</script>

<svelte:head>
  <link rel="icon" href={favicon} />
</svelte:head>

<div data-theme={$theme} id="app-root">
  {@render children()}
</div>

<style>
  #app-root {
    height: 100vh;
    width: 100vw;
    overflow: hidden;
    background-color: var(--bg-primary);
    color: var(--text-primary);
    transition: background-color var(--transition-slow), color var(--transition-slow);
  }
</style>
