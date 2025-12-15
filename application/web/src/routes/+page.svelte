<script>
	import Team from '$lib/components/Team.svelte';
</script>

<div class="min-w-screen min-h-screen bg-neutral-100 pt-8 md:pt-16">
	<div
		class="mx-auto flex w-full max-w-7xl flex-col-reverse gap-8 px-4 md:flex-row md:gap-16 md:px-8"
	>
		<div class="w-full pt-8 md:w-1/2 md:pt-32">
			<h1 class="text-3xl text-gray-600 md:text-5xl">Connecting students with tutors</h1>

			<p class="pt-8 text-lg md:pt-16 md:text-2xl">
				Here at GatorGuides, our focus is to connect students and tutors with each other to help
				boost success.
			</p>

			<div class="mt-8 flex flex-col gap-4 sm:flex-row">
				<a
					href="/search"
					class="rounded-lg bg-[#231161] px-6 py-3 text-center font-medium text-white transition-colors hover:bg-[#1a0d4a]"
				>
					Find a Tutor
				</a>
				<a
					href="/register"
					class="rounded-lg border border-[#231161] px-6 py-3 text-center font-medium text-[#231161] transition-colors hover:bg-purple-50"
				>
					Get Started
				</a>
			</div>
		</div>
		<div class="w-full md:w-1/2">
			<img
				class="h-auto w-full rounded-lg shadow-lg"
				src="/landing.jpg"
				alt="A student sitting at a desk, writing in a notebook"
			/>
		</div>
	</div>

	<div class="mx-auto w-full px-4 pt-16 md:px-8 md:pt-32">
		<h2 class="mb-8 text-center text-2xl font-bold text-gray-800 md:text-3xl">
			What Our Students Say
		</h2>
		<div class="mx-auto flex max-w-7xl flex-col gap-6 md:flex-row md:gap-8">
			<div class="w-full rounded-2xl bg-white p-6 shadow-lg">
				<div class="mb-3 flex text-yellow-500">
					<span>★</span><span>★</span><span>★</span><span>★</span><span>★</span>
				</div>
				<h3 class="text-lg md:text-xl">
					"GatorGuides helped me raise my grade in CSC 648 from a C to an A-. My tutor was patient
					and really knew how to explain complex topics in a way I could understand."
				</h3>
				<p class="mt-4 text-right text-gray-600">— Maria S., Computer Science Major</p>
			</div>
			<div class="w-full rounded-2xl bg-white p-6 shadow-lg">
				<div class="mb-3 flex text-yellow-500">
					<span>★</span><span>★</span><span>★</span><span>★</span><span>★</span>
				</div>
				<h3 class="text-lg md:text-xl">
					"I was struggling with Calculus II and thought I'd have to drop the class. After just
					three sessions with my tutor, I finally understood integration. Lifesaver!"
				</h3>
				<p class="mt-4 text-right text-gray-600">— Kevin T., Engineering Student</p>
			</div>
			<div class="w-full rounded-2xl bg-white p-6 shadow-lg">
				<div class="mb-3 flex text-yellow-500">
					<span>★</span><span>★</span><span>★</span><span>★</span><span>☆</span>
				</div>
				<h3 class="text-lg md:text-xl">
					"The scheduling system is so convenient. I can book sessions around my work schedule, and
					my tutor is always prepared. Best tutoring experience I've had at SFSU."
				</h3>
				<p class="mt-4 text-right text-gray-600">— Ashley R., Biology Major</p>
			</div>
		</div>
	</div>

	<div class="mx-auto mt-16 w-full max-w-7xl px-4 md:mt-24 md:px-8">
		<div
			class="grid grid-cols-2 gap-4 rounded-2xl bg-[#231161] p-6 text-white md:grid-cols-4 md:gap-8 md:p-8"
		>
			<div class="text-center">
				<p class="text-2xl font-bold md:text-4xl">500+</p>
				<p class="text-sm text-purple-200 md:text-base">Students Helped</p>
			</div>
			<div class="text-center">
				<p class="text-2xl font-bold md:text-4xl">50+</p>
				<p class="text-sm text-purple-200 md:text-base">Expert Tutors</p>
			</div>
			<div class="text-center">
				<p class="text-2xl font-bold md:text-4xl">30+</p>
				<p class="text-sm text-purple-200 md:text-base">Subjects Covered</p>
			</div>
			<div class="text-center">
				<p class="text-2xl font-bold md:text-4xl">4.8</p>
				<p class="text-sm text-purple-200 md:text-base">Average Rating</p>
			</div>
		</div>
	</div>

	<div
		class="mx-auto flex w-full flex-col items-center justify-center gap-8 px-4 py-16 md:px-8 md:py-32"
	>
		<h1 class="w-full text-center text-3xl font-bold md:text-5xl">Meet the Team</h1>
		<div
			class="mx-auto grid w-full max-w-6xl grid-cols-2 gap-4 pt-8 text-center sm:grid-cols-3 md:grid-cols-5 md:gap-8"
		>
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
