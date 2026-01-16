<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';
	import Navbar from '$lib/components/Navbar.svelte';
	import Footer from '$lib/components/Footer.svelte';
	import LoginModal from '$lib/components/LoginModal.svelte';
	import { page } from '$app/stores';
	import { browser } from '$app/environment';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	let { children } = $props();

	let loginModalOpen = $state(false);

	// Check if user was logged in before
	let isLoggedIn = $state(browser && sessionStorage.getItem('isLoggedIn') === 'true');

	let lastPath = $state('');

	// Handle hash-based routing for GitHub Pages
	onMount(() => {
		// Intercept all link clicks and convert to hash-based routing
		document.addEventListener('click', (e) => {
			const target = e.target as HTMLElement;
			const link = target.closest('a[href]') as HTMLAnchorElement;
			
			if (link && link.href && !link.href.includes('http') && !link.href.includes('#')) {
				e.preventDefault();
				const path = new URL(link.href).pathname;
				const cleanPath = path.replace('/csc648-fa25-145-team09', '');
				window.location.hash = cleanPath;
				goto(cleanPath, { replaceState: true });
			}
		});

		// Handle hash navigation on page load
		if (window.location.hash && !window.location.hash.startsWith('#%2F')) {
			const hashPath = window.location.hash.slice(1);
			if (!window.location.pathname.endsWith(hashPath)) {
				goto(hashPath, { replaceState: true });
			}
		}
	});

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
