<script lang="ts">
	import { goto } from '$app/navigation';
	import { registerUser, type RegisterPayload } from '$lib/api';
	import ImageUpload from '$lib/components/ImageUpload.svelte';

	let form = $state({
		firstName: '',
		lastName: '',
		email: '',
		phone: '',
		studentId: '',
		password: '',
		confirmPassword: '',
		agreeToTerms: false,
		profilePicture: ''
	});

	let errorMessage = $state('');
	let successMessage = $state('');
	let isSubmitting = $state(false);

	function handleImageUpload(url: string) {
		form.profilePicture = url;
	}

	function validateForm(): boolean {
		errorMessage = '';

		if (!form.firstName || !form.lastName) {
			errorMessage = 'Please enter your first and last name.';
			return false;
		}

		if (!form.email.endsWith('@sfsu.edu')) {
			errorMessage = 'Please use a valid SFSU email (@sfsu.edu).';
			return false;
		}

		if (!form.studentId) {
			errorMessage = 'Student ID is required.';
			return false;
		}

		if (form.password.length < 8) {
			errorMessage = 'Password must be at least 8 characters long.';
			return false;
		}

		if (form.password !== form.confirmPassword) {
			errorMessage = 'Passwords do not match.';
			return false;
		}

		if (!form.agreeToTerms) {
			errorMessage = 'You must agree to the terms and conditions.';
			return false;
		}

		return true;
	}

	async function handleSubmit(event: SubmitEvent) {
		event.preventDefault();

		if (!validateForm()) return;

		isSubmitting = true;
		errorMessage = '';
		successMessage = '';

		const payload: RegisterPayload = {
			firstName: form.firstName,
			lastName: form.lastName,
			email: form.email,
			password: form.password,
			profilePicture: form.profilePicture || null,
			// extra info stored in bio so backend still validates
			bio: `Student ID: ${form.studentId}, Phone: ${form.phone}`
		};

		try {
			await registerUser(payload);
			successMessage = 'Registration successful! Redirecting to login...';

			setTimeout(() => goto('/login'), 1500);
		} catch (err: any) {
			console.error(err);
			errorMessage = err?.message ?? 'Registration failed.';
		} finally {
			isSubmitting = false;
		}
	}
</script>

<div class="flex min-h-screen items-center justify-center bg-neutral-100 p-6">
	<div class="w-full max-w-2xl rounded-2xl border border-gray-100 bg-white p-8 shadow-xl">
		<h1 class="mb-2 text-center text-3xl font-bold text-[#231161]">Create your student account</h1>
		<p class="mb-6 text-center text-sm text-gray-600">
			Sign up with your SFSU email to start booking tutoring sessions.
		</p>

		{#if errorMessage}
			<div class="mb-4 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
				{errorMessage}
			</div>
		{/if}

		{#if successMessage}
			<div
				class="mb-4 rounded-lg border border-green-200 bg-green-50 px-3 py-2 text-sm text-green-700"
			>
				{successMessage}
			</div>
		{/if}

		<form class="space-y-4" on:submit|preventDefault={handleSubmit}>
			<div class="grid gap-4 md:grid-cols-2">
				<div>
					<label class="mb-1 block text-sm font-medium text-gray-700">First name</label>
					<input
						type="text"
						bind:value={form.firstName}
						class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-[#231161] focus:outline-none focus:ring-2 focus:ring-[#231161]/30"
						required
					/>
				</div>
				<div>
					<label class="mb-1 block text-sm font-medium text-gray-700">Last name</label>
					<input
						type="text"
						bind:value={form.lastName}
						class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-[#231161] focus:outline-none focus:ring-2 focus:ring-[#231161]/30"
						required
					/>
				</div>
			</div>

			<div class="grid gap-4 md:grid-cols-2">
				<div>
					<label class="mb-1 block text-sm font-medium text-gray-700">SFSU Email</label>
					<input
						type="email"
						bind:value={form.email}
						placeholder="your.name@sfsu.edu"
						class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-[#231161] focus:outline-none focus:ring-2 focus:ring-[#231161]/30"
						required
					/>
				</div>
				<div>
					<label class="mb-1 block text-sm font-medium text-gray-700">Phone (optional)</label>
					<input
						type="tel"
						bind:value={form.phone}
						class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-[#231161] focus:outline-none focus:ring-2 focus:ring-[#231161]/30"
					/>
				</div>
			</div>

			<!-- Profile Picture Upload -->
			<div>
				<ImageUpload label="Profile Picture (optional)" onUpload={handleImageUpload} />
			</div>

			<div class="grid gap-4 md:grid-cols-2">
				<div>
					<label class="mb-1 block text-sm font-medium text-gray-700">Student ID</label>
					<input
						type="text"
						bind:value={form.studentId}
						class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-[#231161] focus:outline-none focus:ring-2 focus:ring-[#231161]/30"
						required
					/>
				</div>
			</div>

			<div class="grid gap-4 md:grid-cols-2">
				<div>
					<label class="mb-1 block text-sm font-medium text-gray-700">Password</label>
					<input
						type="password"
						bind:value={form.password}
						class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-[#231161] focus:outline-none focus:ring-2 focus:ring-[#231161]/30"
						required
					/>
					<p class="mt-1 text-xs text-gray-500">At least 8 characters.</p>
				</div>
				<div>
					<label class="mb-1 block text-sm font-medium text-gray-700">Confirm password</label>
					<input
						type="password"
						bind:value={form.confirmPassword}
						class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-[#231161] focus:outline-none focus:ring-2 focus:ring-[#231161]/30"
						required
					/>
				</div>
			</div>

			<label class="mt-2 flex items-start gap-2 text-xs text-gray-600">
				<input
					type="checkbox"
					bind:checked={form.agreeToTerms}
					class="mt-0.5 h-4 w-4 rounded border-gray-300 text-[#231161] focus:ring-[#231161]"
				/>
				<span>
					I agree to the GatorGuides terms of use and understand that my SFSU account may be used
					for verification.
				</span>
			</label>

			<button
				type="submit"
				class="mt-4 w-full rounded-lg bg-[#231161] px-4 py-2.5 text-sm font-semibold text-white hover:bg-[#2d1982] disabled:bg-[#231161]/60"
				disabled={isSubmitting}
			>
				{#if isSubmitting}
					Creating account...
				{:else}
					Create student account
				{/if}
			</button>
		</form>

		<p class="mt-4 text-center text-xs text-gray-600">
			Already have an account?
			<a href="/login" class="text-[#231161] hover:underline">Sign in</a>.
		</p>
	</div>
</div>
