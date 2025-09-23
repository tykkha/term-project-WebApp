<script>
	import Person from '../components/person.svelte';
</script>

<div class="min-w-screen min-h-screen bg-white">
	<h1 class="w-full pt-8 text-center text-5xl font-bold">About Us</h1>
	<div class="mx-auto flex w-full max-w-3xl justify-between text-center">
		<Person
			name="Jason Javandel"
			github="https://github.com/CherryYeti"
			src="https://avatars.githubusercontent.com/u/53279269?v=4"
		/>
		<Person 
			name="Connor Moore"
			github="https://github.com/tykkha"
			src="https://cdn.discordapp.com/attachments/748252014978269184/1420161031128485929/foeed0h3hsqf1.png?ex=68d46387&is=68d31207&hm=e319ba1f52ebe6fcd215cc2d59fba1d8ec796158d317aa5db1ac88745c538b7f&"
		/>
		<Person name="test" />
		<Person name="test" />
		<Person name="test" />
	</div>
</div>
