<script lang="ts">
	import { goto } from '$app/navigation';
	import {
		registerUser,
		createTutorProfile,
		addTutorTags,
		getCourseTagIds,
		type RegisterPayload
	} from '$lib/api';
	import ImageUpload from '$lib/components/ImageUpload.svelte';

	let form = $state({
		firstName: '',
		lastName: '',
		email: '',
		phone: '',
		studentId: '',
		password: '',
		confirmPassword: '',
		major: '',
		gpa: '',
		graduationYear: '',
		shortBio: '',
		subjects: [] as string[],
		agreeToTerms: false,
		profilePicture: ''
	});

	let currentSubject = $state('');
	let errorMessage = $state('');
	let successMessage = $state('');
	let isSubmitting = $state(false);

	function handleImageUpload(url: string) {
		form.profilePicture = url;
	}

	const suggestedSubjects = [
		'CSC 101',
		'CSC 210',
		'CSC 220',
		'CSC 230',
		'CSC 256',
		'CSC 340',
		'CSC 413',
		'CSC 415',
		'CSC 648',
		'MATH 226',
		'MATH 227',
		'MATH 228'
	];

	function addSubject() {
		const trimmed = currentSubject.trim();
		if (trimmed && !form.subjects.includes(trimmed)) {
			form.subjects = [...form.subjects, trimmed];
		}
		currentSubject = '';
	}

	function removeSubject(subject: string) {
		form.subjects = form.subjects.filter((s) => s !== subject);
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

		if (!form.major) {
			errorMessage = 'Please enter your major.';
			return false;
		}

		if (!form.gpa) {
			errorMessage = 'Please enter your GPA.';
			return false;
		} else {
			const gpaNum = parseFloat(form.gpa);
			if (Number.isNaN(gpaNum) || gpaNum < 0 || gpaNum > 4.0) {
				errorMessage = 'Please enter a valid GPA between 0.0 and 4.0.';
				return false;
			}
		}

		if (form.subjects.length === 0) {
			errorMessage = 'Please add at least one subject you can tutor.';
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

		try {
			//Pack tutor-specific info into bio
			const tutorBio = `${form.shortBio || ''}\n\nMajor: ${form.major}\nGPA: ${form.gpa}\nGraduation: ${form.graduationYear || 'N/A'}\nStudent ID: ${form.studentId}${form.phone ? `\nPhone: ${form.phone}` : ''}`;

			//Register user account
			console.log('Step 1: Registering user...');
			const registerResponse = await registerUser({
				firstName: form.firstName,
				lastName: form.lastName,
				email: form.email,
				password: form.password,
				profilePicture: form.profilePicture || null,
				bio: tutorBio
			});

			console.log('User registered:', registerResponse);

			//Auto-login to get session token
			console.log('Step 2: Auto-logging in...');
			const loginResponse = await fetch('/api/login', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					email: form.email,
					password: form.password
				})
			});

			if (!loginResponse.ok) {
				throw new Error('Auto-login failed after registration');
			}

			const loginData = await loginResponse.json();
			const sessionID = loginData.sessionID;
			const uid = loginData.user.uid;

			console.log('Auto-login successful, uid:', uid);

			//Create tutor profile
			console.log('Step 3: Creating tutor profile...');
			const tutorResponse = await createTutorProfile(uid, sessionID);
			console.log('Tutor profile created:', tutorResponse);

			//Add subject tags
			console.log('Step 4: Adding subject tags...');
			const tagIds = getCourseTagIds(form.subjects);
			if (tagIds.length > 0) {
				await addTutorTags(tutorResponse.tid, tagIds, sessionID);
				console.log('Tags added successfully');
			} else {
				console.warn('No valid tag IDs found for subjects:', form.subjects);
			}

			successMessage = 'Tutor registration successful! Redirecting to login...';

			setTimeout(() => {
				goto('/login');
			}, 2000);
		} catch (err: any) {
			console.error('Registration error:', err);
			errorMessage = err?.message ?? 'Tutor registration failed. Please try again.';
		} finally {
			isSubmitting = false;
		}
	}
</script>

<div class="flex min-h-screen items-center justify-center bg-neutral-100 p-6">
	<div class="w-full max-w-3xl rounded-2xl border border-gray-100 bg-white p-8 shadow-xl">
		<h1 class="mb-2 text-center text-3xl font-bold text-[#231161]">Apply as a tutor</h1>
		<p class="mb-6 text-center text-sm text-gray-600">
			Share your skills with other Gators. Fill out your academic info so we can verify you.
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

		<form class="space-y-5" onsubmit={handleSubmit}>
			<!-- Name -->
			<div class="grid gap-4 md:grid-cols-2">
				<div>
					<label for="firstName" class="mb-1 block text-sm font-medium text-gray-700"
						>First name</label
					>
					<input
						id="firstName"
						type="text"
						bind:value={form.firstName}
						class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-[#231161] focus:outline-none focus:ring-2 focus:ring-[#231161]/30"
						required
					/>
				</div>
				<div>
					<label for="lastName" class="mb-1 block text-sm font-medium text-gray-700"
						>Last name</label
					>
					<input
						id="lastName"
						type="text"
						bind:value={form.lastName}
						class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-[#231161] focus:outline-none focus:ring-2 focus:ring-[#231161]/30"
						required
					/>
				</div>
			</div>

			<!-- Contact -->
			<div class="grid gap-4 md:grid-cols-2">
				<div>
					<label for="email" class="mb-1 block text-sm font-medium text-gray-700">SFSU Email</label>
					<input
						id="email"
						type="email"
						bind:value={form.email}
						placeholder="your.name@sfsu.edu"
						class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-[#231161] focus:outline-none focus:ring-2 focus:ring-[#231161]/30"
						required
					/>
				</div>
				<div>
					<label for="phone" class="mb-1 block text-sm font-medium text-gray-700"
						>Phone (optional)</label
					>
					<input
						id="phone"
						type="tel"
						bind:value={form.phone}
						class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-[#231161] focus:outline-none focus:ring-2 focus:ring-[#231161]/30"
					/>
				</div>
			</div>

			<!-- Student & academic info -->
			<div class="grid gap-4 md:grid-cols-3">
				<div>
					<label for="studentId" class="mb-1 block text-sm font-medium text-gray-700"
						>Student ID</label
					>
					<input
						id="studentId"
						type="text"
						bind:value={form.studentId}
						class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-[#231161] focus:outline-none focus:ring-2 focus:ring-[#231161]/30"
						required
					/>
				</div>
				<div>
					<label for="major" class="mb-1 block text-sm font-medium text-gray-700">Major</label>
					<input
						id="major"
						type="text"
						bind:value={form.major}
						placeholder="e.g. Computer Science"
						class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-[#231161] focus:outline-none focus:ring-2 focus:ring-[#231161]/30"
						required
					/>
				</div>
				<div>
					<label for="gpa" class="mb-1 block text-sm font-medium text-gray-700">GPA</label>
					<input
						id="gpa"
						type="text"
						bind:value={form.gpa}
						placeholder="e.g. 3.5"
						class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-[#231161] focus:outline-none focus:ring-2 focus:ring-[#231161]/30"
						required
					/>
				</div>
			</div>

			<div class="grid gap-4 md:grid-cols-2">
				<div>
					<label for="graduationYear" class="mb-1 block text-sm font-medium text-gray-700"
						>Expected graduation year (optional)</label
					>
					<input
						id="graduationYear"
						type="text"
						bind:value={form.graduationYear}
						placeholder="e.g. 2027"
						class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-[#231161] focus:outline-none focus:ring-2 focus:ring-[#231161]/30"
					/>
				</div>
			</div>

			<!-- Profile Picture Upload -->
			<div>
				<ImageUpload label="Profile Picture (optional)" onUpload={handleImageUpload} />
			</div>

			<!-- Subjects -->
			<div>
				<label for="currentSubject" class="mb-1 block text-sm font-medium text-gray-700"
					>Subjects you can tutor</label
				>
				<div class="mb-2 flex flex-wrap items-center gap-2">
					<input
						id="currentSubject"
						type="text"
						bind:value={currentSubject}
						placeholder="e.g. CSC 413"
						class="min-w-[160px] flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-[#231161] focus:outline-none focus:ring-2 focus:ring-[#231161]/30"
						onkeydown={(e) => {
							if (e.key === 'Enter') {
								e.preventDefault();
								addSubject();
							}
						}}
					/>
					<button
						type="button"
						onclick={addSubject}
						class="rounded-lg bg-[#231161] px-3 py-2 text-xs font-semibold text-white hover:bg-[#2d1982]"
					>
						Add
					</button>
				</div>
				{#if suggestedSubjects.length}
					<p class="mb-2 text-xs text-gray-500">
						Quick add:
						{#each suggestedSubjects as subj}
							<button
								type="button"
								onclick={() => {
									currentSubject = subj;
									addSubject();
								}}
								class="mr-1 mt-1 inline-flex items-center rounded-full bg-gray-100 px-2 py-1 text-[11px] text-gray-700 hover:bg-gray-200"
							>
								+ {subj}
							</button>
						{/each}
					</p>
				{/if}
				{#if form.subjects.length > 0}
					<div class="mt-1 flex flex-wrap gap-2">
						{#each form.subjects as subject}
							<span
								class="inline-flex items-center gap-1 rounded-full bg-[#231161]/10 px-3 py-1 text-xs text-[#231161]"
							>
								{subject}
								<button type="button" onclick={() => removeSubject(subject)} class="text-[10px]">
									✕
								</button>
							</span>
						{/each}
					</div>
				{:else}
					<p class="mt-1 text-xs text-gray-500">
						Add at least one subject you feel confident tutoring.
					</p>
				{/if}
			</div>

			<!-- Bio -->
			<div>
				<label for="shortBio" class="mb-1 block text-sm font-medium text-gray-700"
					>Short tutor bio (optional)</label
				>
				<textarea
					id="shortBio"
					bind:value={form.shortBio}
					rows={3}
					placeholder="Tell students about your experience, courses you've excelled in, and how you like to help."
					class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-[#231161] focus:outline-none focus:ring-2 focus:ring-[#231161]/30"
				></textarea>
			</div>

			<!-- Password -->
			<div class="grid gap-4 md:grid-cols-2">
				<div>
					<label for="password" class="mb-1 block text-sm font-medium text-gray-700">Password</label
					>
					<input
						id="password"
						type="password"
						bind:value={form.password}
						class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-[#231161] focus:outline-none focus:ring-2 focus:ring-[#231161]/30"
						required
					/>
					<p class="mt-1 text-xs text-gray-500">At least 8 characters.</p>
				</div>
				<div>
					<label for="confirmPassword" class="mb-1 block text-sm font-medium text-gray-700"
						>Confirm password</label
					>
					<input
						id="confirmPassword"
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
					I certify that the information above is accurate and understand that my SFSU academic
					record may be used to verify my eligibility to tutor.
				</span>
			</label>

			<button
				type="submit"
				class="mt-4 w-full rounded-lg bg-[#231161] px-4 py-2.5 text-sm font-semibold text-white hover:bg-[#2d1982] disabled:bg-[#231161]/60"
				disabled={isSubmitting}
			>
				{#if isSubmitting}
					Submitting application...
				{:else}
					Submit tutor application
				{/if}
			</button>
		</form>

		<p class="mt-4 text-center text-xs text-gray-600">
			Already have an account?
			<a href="/login" class="text-[#231161] hover:underline">Sign in</a>.
		</p>
	</div>
</div>
