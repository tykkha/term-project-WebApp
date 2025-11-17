<script lang="ts">
	import { page } from '$app/state';
	import { Avatar } from '@ark-ui/svelte/avatar';
</script>

<div class="min-w-screen flex flex-row gap-8 bg-neutral-100 p-16">
	<div class="w-full rounded-2xl bg-white p-6 shadow-lg">
		<div class="flex h-full w-full flex-row gap-8">
			<div class="flex h-full w-1/3 flex-col items-center">
				<h1>id: {page.params.slug}</h1>
				<Avatar.Root>
					<Avatar.Fallback>TN</Avatar.Fallback>
					<Avatar.Image
						src="https://i.pravatar.cc/3000?u=a"
						alt="avatar"
						class="h-96 w-96 rounded-full"
					/>
				</Avatar.Root>
				<h3 class="pt-16 text-3xl">Tutor Name</h3>
				<p class="px-8 pt-8 text-xl text-neutral-500">
					This is an example description for the tutor page. This is text that should be filled in
					by the person who created the tutor account.
				</p>
			</div>
			<div class="flex h-full w-1/3 flex-col items-center">
				<h2 class="text-4xl">Available Appointments</h2>
			</div>
			<div class="flex h-full w-1/3 flex-col items-center">
				<div class="h-1/2 w-full">
					<h2 class="text-4xl">Contact</h2>
					<div class="pt-4">
						<p class="text-xl">
							Email: <a href="mailto:tutoremail@sfsu.edu">tutoremail@sfsu.edu</a>
						</p>
					</div>
				</div>
				<div class="h-1/2 w-full">
					<h2 class="pb-8 text-4xl">Reviews</h2>
					<p class="text-xl">
						<span class="font-bold">Reviewer Name</span>: This was the best tutor ever!
					</p>
					<p class="text-xl">
						<span class="font-bold">Reviewer Name</span>: This was the worst tutor ever!
					</p>
				</div>
			</div>
		</div>
	</div>
</div>
