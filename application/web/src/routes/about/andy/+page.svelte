<script>
	import Person from '../../../lib/components/Person.svelte';
</script>

<div class="min-w-screen min-h-screen bg-neutral-100">
	<div class=" pt-32">
		<div
			class="mx-auto mb-8 flex w-full max-w-3xl justify-center rounded-2xl bg-white p-6 text-center shadow-lg"
		>
			<Person
				name="Andy Yip"
				github="https://github.com/andyyip915"
				src="https://avatars.githubusercontent.com/u/120161192?v=4"
				description={[
					"Hello, my name is Andy Yip. I am a fourth year student computer science major at San Francisco State University. The fields that I am interested in are datatbases engineering and cybersecurity.",
					"Some side interests that I have are videogame design and 3D modeling. Originally, these side interests had got me invested in acquring a computer science degree, though other fields of study have appeared to be more lucrative and stable. If I am given the chance, I would like to pursue these initial interests."
				]}
			/>
		</div>
	</div>
</div>
