<script lang="ts">
	let props = $props();
</script>

<div class="flex flex-col items-center">
	<a href={props.url} aria-label={`Open ${props.name}'s page`}>
		<img src={props.src} class="h-auto w-32 rounded-full" alt={`${props.name} profile picture`} />
	</a>

	<p>{props.name}</p>
	<a
		href={props.github}
		class="underline decoration-orange-600 hover:cursor-pointer"
		target="_blank"
		rel="noopener noreferrer"
	>
		GitHub
	</a>
</div>
