<script>
	import { Dialog, Menu, Portal } from '@ark-ui/svelte';
	import { Avatar } from '@ark-ui/svelte/avatar';
	import { MenuIcon, XIcon } from '@lucide/svelte';

	let open = $state(false);
</script>

<nav class="sticky top-0 z-50">
	<div class="flex h-20 items-center gap-8 bg-[#231161] p-8 text-white">
		<a href="/">
			<img
				src="/sfsu_logo_text_white.png"
				alt="San Francisco State University Logo"
				class="max-h-8"
			/>
		</a>
		<h2 class="text-3xl font-bold">Gator Guides</h2>

		<div class="flex-1"></div>
		<div class="hidden gap-8 sm:flex sm:flex-row">
			<a href="/login">Login</a>
			<a href="/register">Resgister</a>
		</div>
		<div class="flex sm:hidden">
			<button class="hover:cursor-pointer" type="button" onclick={() => (open = !open)}
				><MenuIcon /></button
			>
		</div>
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
{#if open}
	<div class="fixed inset-0 z-50 h-screen w-screen bg-white">
		<div class="flex w-full flex-col gap-8 p-8">
			<button class="ml-auto hover:cursor-pointer" type="button" onclick={() => (open = !open)}>
				<XIcon />
			</button>

			<a href="/login">Login</a>
			<a href="/register">Resgister</a>
		</div>
	</div>
{/if}
