<script>
	import { Menu } from '@ark-ui/svelte';
</script>

<nav class="sticky top-0 z-50">
	<div class="flex h-20 items-center gap-8 bg-[#231161] p-8 text-white">
		<img
			src="/sfsu_logo_text_white.png"
			alt="San Francisco State University Logo"
			class="max-h-8"
		/>
		<h2 class="text-3xl font-bold">Gator Guides</h2>

		<div class="flex-1"></div>
		<p class="hover:cursor-pointer">Login</p>
		<p class="hover:cursor-pointer">Register</p>
	</div>

	<div class="flex w-full justify-center gap-8 bg-[#ffdc70] p-2 text-center text-black">
		<a href="/">Home</a>
		<a href="/calendar">Calendar</a>
		<a href="/glossary">Glossary</a>
		<a href="/appointments">Appointments</a>
	</div>

	<div class="flex w-full justify-center gap-8 bg-[#ff7070] p-2 text-center text-black">
		This website is solely for demonstration purposes. This is a project that was designed for a
		CSC648 class and is not real in any way.
	</div>
</nav>
