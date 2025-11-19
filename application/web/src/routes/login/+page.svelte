<script lang="ts">
	import { goto } from '$app/navigation';

	let email = $state('');
	let password = $state('');
	let rememberMe = $state(false);
	let errorMessage = $state('');

	function handleLogin() {
		errorMessage = '';

		if (!email || !password) {
			errorMessage = 'Please enter both email and password';
			return;
		}

		if (!email.includes('@')) {
			errorMessage = 'Please enter a valid email address';
			return;
		}

		// add authentication logic
		console.log('Login attempt:', { email, password, rememberMe });

		alert('Login functionality will be connected to backend in next milestone');
		goto('/dashboard');
	}
</script>

<div class="flex min-h-screen items-center justify-center bg-neutral-100 px-4 py-12">
	<div class="w-full max-w-md">
		<!--header-->
		<div class="mb-8 text-center">
			<h1 class="mb-2 text-4xl font-bold text-[#231161]">Gator Guides</h1>
			<p class="text-gray-600">Sign in to your account</p>
		</div>

		<!--Login form card-->
		<div class="rounded-2xl bg-white p-8 shadow-lg">
			<h2 class="mb-6 text-2xl font-bold text-[#231161]">Welcome Back</h2>

			<form
				onsubmit={(e) => {
					e.preventDefault();
					handleLogin();
				}}
			>
				<div class="mb-4">
					<label for="email" class="mb-2 block text-sm font-medium text-gray-700"
						>Email Address</label
					>
					<input
						id="email"
						type="email"
						bind:value={email}
						placeholder="you@sfsu.edu"
						class="w-full rounded-lg border border-gray-300 px-4 py-2.5 focus:border-[#231161] focus:outline-none focus:ring-2 focus:ring-[#231161] focus:ring-opacity-50"
					/>
				</div>

				<div class="mb-4">
					<label for="password" class="mb-2 block text-sm font-medium text-gray-700">Password</label
					>
					<input
						id="password"
						type="password"
						bind:value={password}
						placeholder="••••••••"
						class="w-full rounded-lg border border-gray-300 px-4 py-2.5 focus:border-[#231161] focus:outline-none focus:ring-2 focus:ring-[#231161] focus:ring-opacity-50"
					/>
				</div>

				{#if errorMessage}
					<div class="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-600">{errorMessage}</div>
				{/if}

				<div class="mb-6 flex items-center justify-between">
					<label class="flex items-center">
						<input
							type="checkbox"
							bind:checked={rememberMe}
							class="mr-2 h-4 w-4 rounded border-gray-300 text-[#231161] focus:ring-[#231161]"
						/>
						<span class="text-sm text-gray-700">Remember me</span>
					</label>
					<a href="/forgot-password" class="text-sm text-[#231161] hover:underline"
						>Forgot password?</a
					>
				</div>

				<button
					type="submit"
					class="w-full rounded-lg bg-[#231161] px-4 py-3 font-semibold text-white transition-colors hover:bg-[#1a0d4a] focus:outline-none focus:ring-2 focus:ring-[#231161] focus:ring-offset-2"
				>
					Sign In
				</button>

				<div class="mt-6 text-center">
					<p class="text-sm text-gray-600">
						Don't have an account?
						<a href="/register" class="font-medium text-[#231161] hover:underline">Sign up</a>
					</p>
				</div>

				<div class="mt-4 text-center">
					<a href="/" class="text-sm text-gray-600 hover:text-gray-800">← Back to home</a>
				</div>
			</form>
		</div>

		<!--additional info-->
		<div class="mt-6 text-center text-sm text-gray-600">
			<p>
				Need help? <a href="/support" class="text-[#231161] hover:underline">Contact support</a>
			</p>
		</div>
	</div>
</div>
