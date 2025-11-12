<script>
	import Tutorcard from '$lib/components/tutorcard.svelte';
	import Person from '../lib/components/person.svelte';
</script>

<div class="min-w-screen min-h-screen bg-neutral-100">
	<!-- #f2f2f2 -->
	<!-- #ffffff -->
	<!-- <h1 class="w-full py-8 text-center text-5xl font-bold">About Us</h1>
	<h1 class="w-full py-2 text-center text-4xl font-bold">Software Engineering class SFSU</h1>
	<h2 class="w-full py-2 text-center text-3xl font-bold">Fall 2025</h2>
	<h2 class="w-full py-2 text-center text-3xl font-bold">Section 01</h2>
	<h2 class="w-full py-2 text-center text-3xl font-bold">Team 09</h2> -->
	<!-- <div class="mx-auto flex w-full max-w-3xl justify-center gap-8 text-center">
		<Person
			url="/about/jason"
			name="Jason Javandel"
			github="https://github.com/CherryYeti"
			src="https://avatars.githubusercontent.com/u/53279269?v=4"
		/>
		<Person
			url="/about/connor"
			name="Connor Moore"
			github="https://github.com/tykkha"
			src="https://avatars.githubusercontent.com/tykkha"
		/>
		<Person
			url="/about/andy"
			name="Andy Yip"
			github="https://github.com/andyyip915"
			src="https://avatars.githubusercontent.com/u/120161192?v=4"
		/>
		<Person
			url="/about/Shirish"
			name="Shirish Maharjan"
			github="https://github.com/shirishsm5"
			src="https://avatars.githubusercontent.com/shirishsm5"
		/>
		<Person
			url="/about/manea"
			name="Manea Manea"
			github="https;//github.com/manea127"
			src="https://avatars.githubusercontent.com/manea127"
		/>
	</div> -->
	<!-- <Tutorcard
		tutor_name="Test"
		tutor_description="This is an example description for a tutor. This is an example description for a tutor. This is an example description for a tutor."
		tutor_img="https://avatars.githubusercontent.com/tykkha"
		tutor_subjects={['CSC415', 'CSC648']}
	/> -->
	<div class="mx-auto flex max-w-7xl flex-col gap-8 p-8 md:flex-row">
		<div class="w-full rounded-2xl bg-white p-4 drop-shadow-lg md:w-1/3">
			<h3 class="mb-4 text-2xl font-bold text-gray-800">Your Courses</h3>
			<p class="text-xl">CSC 415</p>
			<p class="text-xl">CSC 648</p>
			<p class="text-xl">JAPN 201</p>
		</div>
		<div class="w-full rounded-2xl bg-white p-4 drop-shadow-lg md:w-2/3">
			<h3 class="mb-4 text-2xl font-bold text-gray-800">Current Appointments</h3>
			<div class="flex w-full items-center justify-center">
				<p>You currently have no scheduled appointments.</p>
			</div>
		</div>
	</div>
</div>
