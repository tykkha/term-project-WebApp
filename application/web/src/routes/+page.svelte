<script>
	import Person from '../components/person.svelte';
</script>

<div class="min-w-screen min-h-screen bg-white">
	<h1 class="w-full py-8 text-center text-5xl font-bold">About Us</h1>
	<h1 class="w-full py-2 text-center text-4xl font-bold">Software Engineering class SFSU</h1>
	<h2 class="w-full py-2 text-center text-3xl font-bold">Fall 2025</h2>
	<h2 class="w-full py-2 text-center text-3xl font-bold">Section 01</h2>
	<h2 class="w-full py-2 text-center text-3xl font-bold">Team 09</h2>
	<div class="mx-auto flex w-full max-w-3xl justify-center gap-8 text-center">
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
	</div>
</div>
