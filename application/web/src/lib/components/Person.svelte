<script lang="ts">
	import { Github } from '@lucide/svelte';

	let props = $props();
</script>

<div class="flex flex-col items-center">
	<a href={props.url} aria-label={`Open ${props.name}'s page`}>
		<img src={props.src} class="h-auto w-72 rounded-full" alt={`${props.name} profile picture`} />
	</a>

	<p class="text-6xl font-bold">{props.name}</p>
	<a href={props.github} class="" target="_blank" rel="noopener noreferrer">
		<button
			class="rounded-2xl py-4 text-neutral-500 transition-all hover:cursor-pointer hover:text-neutral-950"
		>
			<Github />
		</button>
	</a>
	{#if props.description}
		{#each props.description as description}
			<p class="w-full py-2 text-left indent-8 text-lg">{description}</p>
		{/each}
	{/if}
</div>
