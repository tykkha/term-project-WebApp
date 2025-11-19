<script>
	import Team from '$lib/components/Team.svelte';
</script>

<div class="min-w-screen min-h-screen bg-neutral-100 pt-16">
	<div class="mx-auto flex w-full max-w-7xl flex-row gap-16">
		<div class="w-1/2 pt-32">
			<h1 class="text-5xl text-gray-600">Connecting students with tutors</h1>

			<p class="pt-16 text-2xl">
				Here at GatorGuides, our focus is to connect students and tutors with each other to help
				boost success.
			</p>
		</div>
		<div class="w-1/2">
			<img
				class="h-auto w-full"
				src="/landing.jpg"
				alt="A student sitting at a desk, writing in a notebook"
			/>
		</div>
	</div>
	<div class="mx-auto flex w-full flex-col gap-8 bg-neutral-100 px-8 pt-[1024px] md:flex-row">
		<div class="mb-8 w-full rounded-2xl bg-white p-6 shadow-lg">
			<h3 class="text-2xl">"A lorem ipsum review will go here"</h3>
			<p class="text-right text-xl">- Satisfied Customer</p>
		</div>
		<div class="mb-8 w-full rounded-2xl bg-white p-6 shadow-lg">
			<h3 class="text-2xl">"A lorem ipsum review will go here"</h3>
			<p class="text-right text-xl">- Satisfied Customer</p>
		</div>
		<div class="mb-8 w-full rounded-2xl bg-white p-6 shadow-lg">
			<h3 class="text-2xl">"A lorem ipsum review will go here"</h3>
			<p class="text-right text-xl">- Satisfied Customer</p>
		</div>
	</div>
	<div
		class="mx-auto flex min-h-screen w-full flex-col items-center justify-center gap-8 bg-neutral-100 px-8"
	>
		<h1 class="w-full text-center text-5xl font-bold">Meet the Team</h1>
		<div class="pt-15 mx-auto flex w-full flex-col justify-center gap-8 text-center md:flex-row">
			<Team
				name="Jason Javandel"
				src="https://avatars.githubusercontent.com/u/53279269?v=4"
				position="Team Lead"
				url="/about/jason"
			/>
			<Team
				name="Andy Yip"
				src="https://avatars.githubusercontent.com/u/120161192?v=4"
				position="Frontend Lead"
				url="/about/andy"
			/>
			<Team
				name="Connor Moore"
				src="https://avatars.githubusercontent.com/u/100100421?v=4"
				position="Database Lead"
				url="/about/connor"
			/>
			<Team
				name="Manea"
				src="https://avatars.githubusercontent.com/u/127?v=4"
				position="Backend Lead"
				url="/about/manea"
			/>
			<Team
				name="Shirish Maharjan"
				src="https://avatars.githubusercontent.com/shirishsm5"
				position="Github Lead"
				url="/about/shirish"
			/>
		</div>
	</div>
</div>
