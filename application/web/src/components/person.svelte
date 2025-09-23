<script lang="ts">
	let props = $props();
</script>

<div class="flex flex-col">
	<img src={props.src} class="h-auto max-w-32 rounded-full" alt="{props.name} profile picture" />
	<p>{props.name}</p>
	<a
		href={props.github}
		class="underline decoration-orange-600 hover:cursor-pointer"
		target="_blank">Github</a
	>
</div>
