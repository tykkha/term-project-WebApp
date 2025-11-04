<script>
	import { Menu } from '@ark-ui/svelte';
</script>

<nav>
	<div class="fixed inset-x-0 top-0 z-50 flex h-20 items-center gap-8 bg-[#231161] p-8 text-white">
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
	<div class="mt-20 flex w-full justify-center gap-8 bg-[#ffdc70] p-2 text-center text-black">
		<p>Home</p>
		<p>Glossary</p>
		<p>Calendar</p>
		<p>Appointments</p>
	</div>
</nav>
