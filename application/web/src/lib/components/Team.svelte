<script lang="ts">
	import { goto } from '$app/navigation';
	let props = $props();
</script>

<div
	class="mb-8 w-full cursor-pointer rounded-2xl bg-white p-6 shadow-lg transition-all hover:scale-110"
	role="link"
	tabindex="0"
	aria-label={`Open ${props.name}'s page`}
	onclick={() => {
		void goto(props.url);
	}}
	onkeydown={(e) => {
		if (e.key === 'Enter' || e.key === ' ') {
			e.preventDefault();
			void goto(props.url);
		}
	}}
>
	<div class="flex flex-col items-center">
		<a href={props.url} aria-label={`Open ${props.name}'s page`}>
			<img src={props.src} class="h-auto w-32 rounded-full" alt={`${props.name} profile picture`} />
		</a>

		<p class="py-2 text-xl">{props.name}</p>

		<p class="text-neutral-500">{props.position}</p>
	</div>
</div>
