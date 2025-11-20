<script lang="ts">
	import { goto } from '$app/navigation';

	//Form
	let formData = $state({
		//personal Information
		firstName: '',
		lastName: '',
		email: '',
		phone: '',
		studentId: '',

		//account Security
		password: '',
		confirmPassword: '',

		// Agreement
		agreeToTerms: false
	});

	let errorMessage = $state('');
	let successMessage = $state('');

	function validateForm(): boolean {
		errorMessage = '';

		if (!formData.firstName || !formData.lastName) {
			errorMessage = 'Please enter your full name';
			return false;
		}

		if (!formData.email.includes('@')) {
			errorMessage = 'Please enter a valid email address';
			return false;
		}

		if (!formData.studentId) {
			errorMessage = 'Please enter your student ID';
			return false;
		}

		if (formData.password.length < 8) {
			errorMessage = 'Password must be at least 8 characters long';
			return false;
		}

		if (formData.password !== formData.confirmPassword) {
			errorMessage = 'Passwords do not match';
			return false;
		}

		if (!formData.agreeToTerms) {
			errorMessage = 'Please agree to the terms and conditions';
			return false;
		}

		return true;
	}

	function handleSubmit() {
		if (!validateForm()) {
			return;
		}

		//Send data to backend API
		console.log('Form submitted:', formData);

		successMessage = 'Registration successful! Redirecting to login...';

		setTimeout(() => {
			goto('/');
		}, 2000);
	}
</script>

<div class="min-h-screen bg-neutral-100 py-8">
	<div class="mx-auto max-w-4xl px-4">
		<!--header -->
		<div class="mb-8 text-center">
			<h1 class="mb-2 text-4xl font-bold text-[#231161]">Student Registration</h1>
			<p class="text-gray-600">Create your account to find tutors and get help</p>
		</div>

		<!--form Container -->
		<form
				onsubmit={(e) => {
				e.preventDefault();
				handleSubmit();
			}}
				class="rounded-2xl bg-white p-8 shadow-lg"
		>
			<!--personal information section -->
			<section class="mb-8">
				<h2 class="mb-4 text-2xl font-bold text-gray-800">Personal Information</h2>
				<div class="grid gap-4 md:grid-cols-2">
					<div>
						<label for="firstName" class="mb-2 block text-sm font-medium text-gray-700">
							First Name <span class="text-red-500">*</span>
						</label>
						<input
								id="firstName"
								type="text"
								bind:value={formData.firstName}
								required
								class="w-full rounded-lg border border-gray-300 px-4 py-2.5 focus:border-[#231161] focus:outline-none focus:ring-2 focus:ring-[#231161] focus:ring-opacity-50"
						/>
					</div>
					<div>
						<label for="lastName" class="mb-2 block text-sm font-medium text-gray-700">
							Last Name <span class="text-red-500">*</span>
						</label>
						<input
								id="lastName"
								type="text"
								bind:value={formData.lastName}
								required
								class="w-full rounded-lg border border-gray-300 px-4 py-2.5 focus:border-[#231161] focus:outline-none focus:ring-2 focus:ring-[#231161] focus:ring-opacity-50"
						/>
					</div>
					<div>
						<label for="email" class="mb-2 block text-sm font-medium text-gray-700">
							SFSU Email <span class="text-red-500">*</span>
						</label>
						<input
								id="email"
								type="email"
								bind:value={formData.email}
								placeholder="you@sfsu.edu"
								required
								class="w-full rounded-lg border border-gray-300 px-4 py-2.5 focus:border-[#231161] focus:outline-none focus:ring-2 focus:ring-[#231161] focus:ring-opacity-50"
						/>
					</div>
					<div>
						<label for="phone" class="mb-2 block text-sm font-medium text-gray-700"
						>Phone Number</label
						>
						<input
								id="phone"
								type="tel"
								bind:value={formData.phone}
								placeholder="(123) 456-7890"
								class="w-full rounded-lg border border-gray-300 px-4 py-2.5 focus:border-[#231161] focus:outline-none focus:ring-2 focus:ring-[#231161] focus:ring-opacity-50"
						/>
					</div>
					<div class="md:col-span-2">
						<label for="studentId" class="mb-2 block text-sm font-medium text-gray-700">
							Student ID <span class="text-red-500">*</span>
						</label>
						<input
								id="studentId"
								type="text"
								bind:value={formData.studentId}
								placeholder="920123456"
								required
								class="w-full rounded-lg border border-gray-300 px-4 py-2.5 focus:border-[#231161] focus:outline-none focus:ring-2 focus:ring-[#231161] focus:ring-opacity-50"
						/>
					</div>
				</div>
			</section>

			<!--account security section -->
			<section class="mb-8">
				<h2 class="mb-4 text-2xl font-bold text-gray-800">Account Security</h2>
				<div class="grid gap-4 md:grid-cols-2">
					<div>
						<label for="password" class="mb-2 block text-sm font-medium text-gray-700">
							Password <span class="text-red-500">*</span>
						</label>
						<input
								id="password"
								type="password"
								bind:value={formData.password}
								placeholder="At least 8 characters"
								required
								class="w-full rounded-lg border border-gray-300 px-4 py-2.5 focus:border-[#231161] focus:outline-none focus:ring-2 focus:ring-[#231161] focus:ring-opacity-50"
						/>
					</div>
					<div>
						<label for="confirmPassword" class="mb-2 block text-sm font-medium text-gray-700">
							Confirm Password <span class="text-red-500">*</span>
						</label>
						<input
								id="confirmPassword"
								type="password"
								bind:value={formData.confirmPassword}
								placeholder="Re-enter password"
								required
								class="w-full rounded-lg border border-gray-300 px-4 py-2.5 focus:border-[#231161] focus:outline-none focus:ring-2 focus:ring-[#231161] focus:ring-opacity-50"
						/>
					</div>
				</div>
			</section>

			<!--terms and conditions -->
			<section class="mb-6">
				<label class="flex items-start gap-3">
					<input
							type="checkbox"
							bind:checked={formData.agreeToTerms}
							required
							class="mt-1 h-5 w-5 rounded border-gray-300 text-[#231161] focus:ring-[#231161]"
					/>
					<span class="text-sm text-gray-700">
						I agree to the <a href="/terms" class="text-[#231161] hover:underline"
					>Terms and Conditions</a
					>
						and
						<a href="/privacy" class="text-[#231161] hover:underline">Privacy Policy</a>
						<span class="text-red-500">*</span>
					</span>
				</label>
			</section>

			<!--messages -->
			{#if errorMessage}
				<div class="mb-4 rounded-lg bg-red-50 p-4 text-red-600">{errorMessage}</div>
			{/if}

			{#if successMessage}
				<div class="mb-4 rounded-lg bg-green-50 p-4 text-green-600">{successMessage}</div>
			{/if}

			<!-- Submit Button -->
			<div class="flex gap-4">
				<a
						href="/"
						class="flex-1 rounded-lg border-2 border-gray-300 px-6 py-3 text-center font-semibold text-gray-700 transition-colors hover:bg-gray-50"
				>
					Cancel
				</a>
				<button
						type="submit"
						class="flex-1 rounded-lg bg-[#231161] px-6 py-3 font-semibold text-white transition-colors hover:bg-[#1a0d4a] focus:outline-none focus:ring-2 focus:ring-[#231161] focus:ring-offset-2"
				>
					Register
				</button>
			</div>

			<!--login link -->
			<div class="mt-6 text-center">
				<p class="text-sm text-gray-600">
					Already have an account?
					<a href="/login" class="font-medium text-[#231161] hover:underline">Sign in</a>
				</p>
				<p class="mt-2 text-sm text-gray-600">
					Want to become a tutor?
					<a href="/tutor-register" class="font-medium text-[#231161] hover:underline"
					>Tutor Registration</a
					>
				</p>
			</div>
		</form>
	</div>
</div>