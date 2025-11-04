<script lang="ts">
	let props = $props();
</script>

<div class=" mx-auto flex w-full max-w-3xl items-center justify-center">
	<div class="flex flex-row rounded-3xl bg-[#f2f2f3] p-8">
		<img
			src={props.tutor_img}
			class=" mr-8 h-64 w-64 rounded-full"
			alt="{props.tutor_name}'s profile"
		/>
		<div class="mr-8 flex flex-col">
			<p class="pb-4 text-3xl underline decoration-[#231161] decoration-8 underline-offset-4">
				{props.tutor_name}
			</p>
			<p>{props.tutor_description}</p>
			<div class="mt-4 rounded-xl bg-[#d7d7d7] p-2 px-6">
				<h2 class="underline-offset-6 pb-2 text-xl underline decoration-[#231161] decoration-4">
					Subjects
				</h2>
				{#each props.tutor_subjects as subject}
					<p>{subject}</p>
				{/each}
				<p></p>
			</div>
		</div>
	</div>
</div>
