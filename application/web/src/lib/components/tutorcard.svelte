<script lang="ts">
	let props = $props();
</script>

<div class=" mx-auto flex w-full max-w-3xl items-center justify-center">
	<div class="flex flex-row rounded-3xl bg-[#f2f2f3] p-2">
		<img src={props.tutor_img} class="h-64 w-64 rounded-full" alt="{props.tutor_name}'s profile" />
		<div class="flex flex-col">
			<p>{props.tutor_name}</p>
			<p>{props.tutor_description}</p>
		</div>
		<div class="m-2 rounded-xl bg-[#d7d7d7]">
			<h2 class="p-2">Subjects</h2>
		</div>
	</div>
</div>
