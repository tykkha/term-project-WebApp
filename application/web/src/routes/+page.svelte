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
			src="https://cdn.discordapp.com/attachments/748252014978269184/1420161031128485929/foeed0h3hsqf1.png?ex=68d46387&is=68d31207&hm=e319ba1f52ebe6fcd215cc2d59fba1d8ec796158d317aa5db1ac88745c538b7f&"
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
		<Person name="test" />
	</div>
</div>
