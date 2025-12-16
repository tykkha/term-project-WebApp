<script>
	import { Dialog, Field, Menu, Portal } from '@ark-ui/svelte';
	import { MenuIcon, SearchIcon, XIcon } from '@lucide/svelte';
	import { goto } from '$app/navigation';
	import { getCurrentUser, logoutUser } from '$lib/api';

	let searchQuery = $state('');
	let open = $state(false);
	let currentUser = $state(getCurrentUser());
	let isLoggingOut = $state(false);

	async function handleSearch() {
		console.log(searchQuery);
		goto(`search?search=${searchQuery}`);
	}

	async function handleLogout() {
		isLoggingOut = true;
		try {
			await logoutUser();
			currentUser = null;
			goto('/');
		} catch (error) {
			console.error('Logout error:', error);
		} finally {
			isLoggingOut = false;
		}
	}
</script>

<nav class="sticky top-0 z-50">
	<div class="flex h-20 items-center gap-2 bg-[#231161] p-8 text-white md:gap-8">
		<a href="/">
			<img
				src="/sfsu_logo_text_white.png"
				alt="San Francisco State University Logo"
				class="hidden max-h-8 md:block"
			/>
		</a>
		<a href="/">
			<h2 class="text-3xl font-bold">Gator Guides</h2>
		</a>
		<div class="flex-1"></div>
		<div class="hidden items-center gap-8 md:flex md:flex-row">
			<Field.Root class="flex items-center justify-center gap-4">
				<input
					type="text"
					bind:value={searchQuery}
					onkeydown={(e) => {
						if (e.key === 'Enter') {
							e.preventDefault();
							handleSearch();
						}
					}}
					placeholder="Search"
					class="w-full rounded-lg border border-gray-300 bg-white px-4 py-2 text-black focus:border-[#231161] focus:outline-none"
				/>
			</Field.Root>
			{#if currentUser}
				<span class="text-sm">Welcome, {currentUser.firstName}!</span>
				<button
					onclick={handleLogout}
					disabled={isLoggingOut}
					class="rounded-lg bg-white px-4 py-2 text-sm font-medium text-[#231161] transition-colors hover:bg-purple-50 disabled:opacity-50"
				>
					{isLoggingOut ? 'Logging out...' : 'Logout'}
				</button>
			{:else}
				<a href="/login">Login</a>
				<a href="/register">Register</a>
			{/if}
		</div>
		<div class="flex md:hidden">
			<button class="hover:cursor-pointer" type="button" onclick={() => (open = !open)}
				><MenuIcon /></button
			>
		</div>
	</div>

	<div class="flex w-full justify-center gap-8 bg-[#ffdc70] p-2 text-center text-black">
		<a href="/">Home</a>
		<a href="/calendar">Calendar</a>
		<a href="/messages">Messages</a>
		<a href="/dashboard">Dashboard</a>
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
			<Field.Root class="flex items-center justify-center gap-4">
				<input
					type="text"
					bind:value={searchQuery}
					onkeydown={(e) => {
						if (e.key === 'Enter') {
							e.preventDefault();
							handleSearch();
						}
					}}
					placeholder="Search"
					class="w-full rounded-lg border bg-white px-4 py-2 text-black focus:outline-none"
				/>
			</Field.Root>
			{#if currentUser}
				<span class="text-xl">Welcome, {currentUser.firstName}!</span>
				<button
					onclick={handleLogout}
					disabled={isLoggingOut}
					class="rounded-lg bg-[#231161] px-4 py-2 text-3xl text-white transition-colors hover:bg-[#1a0d4a] disabled:opacity-50"
				>
					{isLoggingOut ? 'Logging out...' : 'Logout'}
				</button>
			{:else}
				<a href="/login" class="text-3xl">Login</a>
				<a href="/register" class="text-3xl">Register</a>
			{/if}
		</div>
	</div>
{/if}
