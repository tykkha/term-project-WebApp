<script>
	import Person from '../../../lib/components/Person.svelte';
</script>

<div class="min-w-screen min-h-screen bg-neutral-100">
	<div class=" pt-32">
		<div
			class="mx-auto mb-8 flex w-full max-w-3xl justify-center rounded-2xl bg-white p-6 text-center shadow-lg"
		>
			<Person
				name="Connor Moore"
				github="https://github.com/tykkha"
				src="https://avatars.githubusercontent.com/u/100100421?v=4"
				description={[
					"Howdy! My name is Connor M and I'm a senior at SF State University majoring in computer science with a focus on backend and database development.",
					'Believe it or not, I focused more on electrical engineering in my earlier years of junior high and high school through their robotics programs, but it also introduced me to programming as a means of connecting software and the hardware we worked to construct for competitions and sparked the passion for doing what I do today.', 
					"As much as I love software development and databases, I also like to keep a good life balance by enjoying my other hobbies such as gardening, coffee brewing, and going on adventures with my friends even if it's just to downtown San Francisco."
				]}
			/>
		</div>
	</div>
</div>
