<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';
	import Navbar from '$lib/components/navbar.svelte';
	import Footer from '$lib/components/footer.svelte';
	import LoginModal from '$lib/components/LoginModal.svelte';
	import { page } from '$app/stores';
	import { browser } from '$app/environment';

	let { children } = $props();

	let loginModalOpen = $state(false);

	// Check if user was logged in before
	let isLoggedIn = $state(browser && sessionStorage.getItem('isLoggedIn') === 'true');

	let lastPath = $state('');

	//show popup immediately on every route change
	$effect(() => {
		const currentPath = $page.url.pathname;

		//if route changed and not logged in
		if (currentPath !== lastPath && !isLoggedIn) {
			loginModalOpen = false;
		}

		lastPath = currentPath;
	});

	function handleLogin(userData: any) {
		isLoggedIn = true;
		loginModalOpen = false;

		// Save login state in browser
		if (browser) {
			sessionStorage.setItem('isLoggedIn', 'true');
		}

		console.log('User logged in:', userData);
	}

	function handleLogout() {
		isLoggedIn = false;
		loginModalOpen = true;

		// Clear login state from browser
		if (browser) {
			sessionStorage.removeItem('isLoggedIn');
		}
	}
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<Navbar />
{@render children?.()}
<Footer />

<!--login popup-->
{#if !isLoggedIn}
	<LoginModal bind:isOpen={loginModalOpen} onLogin={handleLogin} />
{/if}
