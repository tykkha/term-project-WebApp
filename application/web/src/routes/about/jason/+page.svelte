<script>
	import Person from '../../../lib/components/Person.svelte';
</script>

<div class="min-w-screen min-h-screen bg-neutral-100">
	<div class=" pt-32">
		<div
			class="mx-auto mb-8 flex w-full max-w-3xl justify-center rounded-2xl bg-white p-6 text-center shadow-lg"
		>
			<Person
				name="Jason Javandel"
				github="https://github.com/CherryYeti"
				src="https://avatars.githubusercontent.com/u/53279269?v=4"
				description={[
					"Hello! I am a fourth year college student who believes in open source projects. I am majoring in computer science, and I love creating! I've been an avid linux user and advocate for the last 5 years, and I love working in Python and more recently, Zig. I started making websites when I was around 12, and since, I have learned how to work in React and Svelte. I am proud to be entirely self-taught.",
					'Other than websites, I have spent considerable time learning Jetpack Compose and Flutter, both are frameworks for building native apps for Android. I am one of the few people I know who loves writing documentation, as I find it extremely rewarding to make things easier for other people to understand.',
					"When I'm not coding, I enjoy maintaining my homelab and using applications with Docker. I'm currently expanding my skills towards learning Proxmox and Kubernetes. Outside of tech, you'll find me playing Final Fantasy, studying Japanese, or getting up at 6 AM to watch Formula 1 races. PST baby! がんばれ、広島カープ！"
				]}
			/>
		</div>
	</div>
</div>
