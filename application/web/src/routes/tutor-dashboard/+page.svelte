<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import {
		getCurrentUser,
		logoutUser,
		authFetch,
		updateUser,
		uploadProfilePicture,
		type User,
		type Session
	} from '$lib/api';
	import ImageUpload from '$lib/components/ImageUpload.svelte';

	let user = $state<User | null>(getCurrentUser());
	let profile = $state<any>(null);
	let tutorProfile = $state<any>(null);
	let upcomingSessions = $state<Session[]>([]);
	let pastSessions = $state<Session[]>([]);
	let isLoading = $state(true);
	let isLoggingOut = $state(false);
	let errorMessage = $state('');

	let totalSessions = $state(0);
	let thisWeekSessions = $state(0);
	let completedSessions = $state(0);

	// Edit Profile State
	let showEditProfile = $state(false);
	let editForm = $state({
		firstName: '',
		lastName: '',
		bio: '',
		profilePicture: ''
	});
	let isEditSubmitting = $state(false);
	let editError = $state('');
	let editSuccess = $state('');
	let uploadingPhoto = $state(false);

	async function handleLogout() {
		isLoggingOut = true;
		try {
			await logoutUser();
		} catch (error) {
			console.error('Logout error:', error);
		} finally {
			goto('/login');
		}
	}

	function openEditProfile() {
		showEditProfile = true;
		editError = '';
		editSuccess = '';
	}

	async function handleProfilePhotoUpload(file: File) {
		if (!user) return;

		uploadingPhoto = true;
		editError = '';

		try {
			const photoUrl = await uploadProfilePicture(user.uid, file);

			editForm.profilePicture = photoUrl;
			if (profile) {
				profile.profilePicture = photoUrl;
			}
			if (user) {
				user.profilePicture = photoUrl;
				localStorage.setItem('currentUser', JSON.stringify(user));
			}
		} catch (err: any) {
			editError = err?.message || 'Failed to upload profile picture';
		} finally {
			uploadingPhoto = false;
		}
	}

	async function handleEditProfile() {
		editError = '';
		editSuccess = '';

		if (!editForm.firstName || !editForm.lastName) {
			editError = 'First and last name are required';
			return;
		}

		isEditSubmitting = true;

		try {
			await updateUser(user!.uid, {
				firstName: editForm.firstName,
				lastName: editForm.lastName,
				bio: editForm.bio
			});

			profile = {
				...(profile ?? {}),
				firstName: editForm.firstName,
				lastName: editForm.lastName,
				bio: editForm.bio,
				profilePicture: editForm.profilePicture
			};

			if (user) {
				user.firstName = editForm.firstName;
				user.lastName = editForm.lastName;
				user.bio = editForm.bio;
				user.profilePicture = editForm.profilePicture;
				localStorage.setItem('currentUser', JSON.stringify(user));
			}

			editSuccess = 'Profile updated successfully!';
			setTimeout(() => {
				showEditProfile = false;
			}, 1500);
		} catch (err: any) {
			editError = err?.message || 'Failed to update profile';
		} finally {
			isEditSubmitting = false;
		}
	}

	// Helper: map weekday to index so we can sort Monday..Sunday
	function getDayIndex(day: string): number {
		const map: Record<string, number> = {
			Monday: 0,
			Tuesday: 1,
			Wednesday: 2,
			Thursday: 3,
			Friday: 4,
			Saturday: 5,
			Sunday: 6
		};
		return map[day] ?? 999;
	}

	// Helper: where is this session happening? (Milestone wants "place")
	function getSessionLocation(_session: Session): string {
		// DB does not store location yet; we can treat sessions as online.
		return 'Online';
	}

	async function loadTutorData() {
		if (!user) {
			goto('/login');
			return;
		}

		try {
			isLoading = true;
			errorMessage = '';

			const userRes = await authFetch(`/api/users/${user.uid}`);
			if (userRes.ok) {
				profile = await userRes.json();
				editForm = {
					firstName: profile.firstName || '',
					lastName: profile.lastName || '',
					bio: profile.bio || '',
					profilePicture: profile.profilePicture || ''
				};
			}

			const tutorRes = await authFetch(`/api/tutors/by-user/${user.uid}`);
			if (tutorRes.ok) {
				tutorProfile = await tutorRes.json();

				try {
					const sessionsRes = await authFetch(`/api/tutors/${tutorProfile.tid}/sessions`);
					if (sessionsRes.ok) {
						const allSessions = await sessionsRes.json();

						const now = new Date();

						// Split into upcoming vs past
						const upcoming = allSessions.filter(
							(s: Session) => !s.concluded || new Date(s.concluded) > now
						);
						const past = allSessions.filter(
							(s: Session) => s.concluded && new Date(s.concluded) <= now
						);

						// Chronological order for upcoming (Milestone 2 requirement)
						upcoming.sort((a: any, b: any) => {
							const dayDiff = getDayIndex(a.day) - getDayIndex(b.day);
							if (dayDiff !== 0) return dayDiff;
							return a.time - b.time;
						});

						// History: newest completed sessions first
						past.sort((a: any, b: any) => {
							const aDate = a.concluded ? new Date(a.concluded) : new Date(0);
							const bDate = b.concluded ? new Date(b.concluded) : new Date(0);
							return bDate.getTime() - aDate.getTime();
						});

						upcomingSessions = upcoming;
						pastSessions = past;

						// Stats
						totalSessions = allSessions.length;
						completedSessions = pastSessions.length;

						const oneWeekAgo = new Date();
						oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
						thisWeekSessions = allSessions.filter((s: Session) => {
							const sessionDate = s.started ? new Date(s.started) : new Date();
							return sessionDate >= oneWeekAgo;
						}).length;
					}
				} catch (err) {
					console.warn('Could not load sessions:', err);
				}
			} else {
				// Not a tutor → go to student dashboard
				goto('/student-dashboard');
				return;
			}
		} catch (err: any) {
			console.error('Error loading tutor dashboard:', err);
			errorMessage = 'Failed to load dashboard data';
		} finally {
			isLoading = false;
		}
	}

	onMount(() => {
		loadTutorData();
	});

	function formatTime(hour: number): string {
		const period = hour >= 12 ? 'PM' : 'AM';
		const displayHour = hour > 12 ? hour - 12 : hour === 0 ? 12 : hour;
		return `${displayHour}:00 ${period}`;
	}

	function formatDate(dateStr: string | null): string {
		if (!dateStr) return 'Not scheduled';
		const date = new Date(dateStr);
		return date.toLocaleDateString('en-US', {
			month: 'short',
			day: 'numeric',
			year: 'numeric'
		});
	}
</script>

<div class="min-h-screen bg-gray-50">
	<header class="bg-[#231161] text-white shadow-lg">
		<div class="mx-auto flex max-w-7xl items-center justify-between px-4 py-4">
			<div>
				<h1 class="text-2xl font-bold">Gator Guides - Tutor Dashboard</h1>
				{#if user}
					<p class="text-sm text-purple-200">
						Welcome back, {user.firstName}
						{user.lastName}!
					</p>
				{/if}
			</div>
			<div class="flex items-center gap-3">
				<a href="/" class="text-sm text-purple-200 transition-colors hover:text-white"> Home </a>
				<button
					onclick={handleLogout}
					disabled={isLoggingOut}
					class="rounded-lg bg-white px-4 py-2 text-sm font-medium text-[#231161] transition-colors hover:bg-purple-50 disabled:opacity-50"
				>
					{isLoggingOut ? 'Logging out...' : 'Logout'}
				</button>
			</div>
		</div>
	</header>

	<main class="mx-auto max-w-7xl space-y-6 px-4 py-6">
		{#if isLoading}
			<div class="rounded-lg bg-white p-8 text-center shadow">
				<div class="animate-pulse">
					<div class="mx-auto mb-4 h-16 w-16 rounded-full bg-[#231161]"></div>
					<p class="text-gray-600">Loading your tutor dashboard...</p>
				</div>
			</div>
		{:else if errorMessage}
			<div class="rounded-lg border border-red-200 bg-red-50 p-4">
				<p class="text-red-700">{errorMessage}</p>
			</div>
		{:else}
			<!-- STATS -->
			<section class="grid grid-cols-1 gap-4 md:grid-cols-4">
				<div class="rounded-lg bg-white p-6 shadow">
					<p class="mb-1 text-sm text-gray-600">Total Sessions</p>
					<p class="text-3xl font-bold text-[#231161]">{totalSessions}</p>
				</div>
				<div class="rounded-lg bg-white p-6 shadow">
					<p class="mb-1 text-sm text-gray-600">This Week</p>
					<p class="text-3xl font-bold text-[#231161]">{thisWeekSessions}</p>
				</div>
				<div class="rounded-lg bg-white p-6 shadow">
					<p class="mb-1 text-sm text-gray-600">Completed</p>
					<p class="text-3xl font-bold text-[#231161]">{completedSessions}</p>
				</div>
				<div class="rounded-lg bg-white p-6 shadow">
					<p class="mb-1 text-sm text-gray-600">Your Rating</p>
					<div class="flex items-center gap-2">
						<p class="text-3xl font-bold text-[#231161]">
							{tutorProfile?.rating?.toFixed(1) || '0.0'}
						</p>
						<span class="text-2xl text-yellow-500">⭐</span>
					</div>
				</div>
			</section>

			<!-- TUTOR PROFILE -->
			<section class="rounded-lg bg-white p-6 shadow">
				<div class="mb-4 flex items-center justify-between">
					<h2 class="text-xl font-bold text-gray-800">Your Tutor Profile</h2>
					<button
						onclick={openEditProfile}
						class="rounded-lg bg-[#231161] px-4 py-2 text-sm text-white hover:bg-[#1a0d4a]"
					>
						Edit Profile
					</button>
				</div>
				{#if profile && tutorProfile}
					<div class="mb-6 flex items-start gap-6">
						{#if profile.profilePicture}
							<img
								src={profile.profilePicture}
								alt="{profile.firstName} {profile.lastName}"
								class="h-24 w-24 rounded-full border-2 border-[#231161] object-cover"
							/>
						{:else}
							<div
								class="flex h-24 w-24 items-center justify-center rounded-full border-2 border-[#231161] bg-purple-100"
							>
								<span class="text-3xl font-bold text-[#231161]">
									{profile.firstName?.[0]}{profile.lastName?.[0]}
								</span>
							</div>
						{/if}
						<div class="flex-1">
							<p class="mb-1 text-2xl font-bold text-gray-800">
								{profile.firstName}
								{profile.lastName}
							</p>
							<p class="text-gray-600">{profile.email}</p>
						</div>
					</div>
					<div class="grid gap-6 md:grid-cols-2">
						<div class="space-y-3">
							<div>
								<p class="text-sm text-gray-600">Status</p>
								<span
									class="inline-flex items-center rounded-full px-3 py-1 text-sm font-medium
                                        {tutorProfile.status === 'available'
										? 'bg-green-100 text-green-800'
										: 'bg-gray-100 text-gray-800'}"
								>
									{tutorProfile.status || 'available'}
								</span>
							</div>
						</div>
						<div class="space-y-3">
							<div>
								<p class="text-sm text-gray-600">Verification Status</p>
								<span
									class="inline-flex items-center rounded-full px-3 py-1 text-sm font-medium
                                        {tutorProfile.verificationStatus === 'approved'
										? 'bg-blue-100 text-blue-800'
										: 'bg-yellow-100 text-yellow-800'}"
								>
									{tutorProfile.verificationStatus || 'pending'}
								</span>
							</div>
							<div>
								<p class="text-sm text-gray-600">Rating</p>
								<div class="flex items-center gap-2">
									<span class="text-yellow-500">⭐</span>
									<span class="font-semibold text-gray-800">
										{tutorProfile.rating?.toFixed(1) || '0.0'}/5.0
									</span>
								</div>
							</div>
						</div>
					</div>

					{#if profile.bio}
						<div class="mt-4 border-t pt-4">
							<p class="mb-1 text-sm text-gray-600">Bio</p>
							<p class="whitespace-pre-wrap text-gray-800">{profile.bio}</p>
						</div>
					{/if}
				{/if}
			</section>

			<!-- UPCOMING SESSIONS (chronological) -->
			<section class="rounded-lg bg-white p-6 shadow">
				<h2 class="mb-4 text-xl font-bold text-gray-800">Upcoming Sessions</h2>
				{#if upcomingSessions.length > 0}
					<div class="space-y-3">
						{#each upcomingSessions as session}
							<div class="rounded-lg border border-purple-200 bg-purple-50 p-4">
								<div class="mb-2 flex items-center gap-2">
									<span class="rounded bg-purple-600 px-2 py-1 text-xs font-semibold text-white">
										Upcoming
									</span>
									<span class="text-sm font-medium text-gray-700">
										{session.course}
									</span>
								</div>
								<div class="grid grid-cols-1 gap-4 text-sm md:grid-cols-3">
									<div>
										<p class="text-gray-600">Student</p>
										<p class="font-semibold text-gray-800">
											{session.student.name}
										</p>
									</div>
									<div>
										<p class="text-gray-600">Schedule</p>
										<p class="font-semibold text-gray-800">
											{session.day} at {formatTime(session.time)}
										</p>
									</div>
									<div>
										<p class="text-gray-600">Location</p>
										<p class="font-semibold text-gray-800">
											{getSessionLocation(session)}
										</p>
									</div>
								</div>
								{#if session.started}
									<p class="mt-2 text-xs text-gray-600">
										Started: {formatDate(session.started)}
									</p>
								{/if}
							</div>
						{/each}
					</div>
				{:else}
					<p class="py-8 text-center text-gray-500">No upcoming sessions scheduled.</p>
				{/if}
			</section>

			<!-- PAST / COMPLETED SESSIONS -->
			{#if pastSessions.length > 0}
				<section class="rounded-lg bg-white p-6 shadow">
					<h2 class="mb-4 text-xl font-bold text-gray-800">Session History</h2>
					<div class="space-y-3">
						{#each pastSessions as session}
							<div class="rounded-lg border border-gray-200 bg-gray-50 p-4">
								<div class="mb-2 flex items-center gap-2">
									<span class="rounded bg-gray-500 px-2 py-1 text-xs font-semibold text-white">
										Completed
									</span>
									<span class="text-sm font-medium text-gray-700">
										{session.course}
									</span>
								</div>
								<div class="grid grid-cols-1 gap-4 text-sm md:grid-cols-3">
									<div>
										<p class="text-gray-600">Student</p>
										<p class="font-semibold text-gray-800">
											{session.student.name}
										</p>
									</div>
									<div>
										<p class="text-gray-600">Completed</p>
										<p class="font-semibold text-gray-800">
											{formatDate(session.concluded)}
										</p>
									</div>
									<div>
										<p class="text-gray-600">Location</p>
										<p class="font-semibold text-gray-800">
											{getSessionLocation(session)}
										</p>
									</div>
								</div>
							</div>
						{/each}
					</div>
				</section>
			{/if}
		{/if}
	</main>
</div>

<!-- EDIT PROFILE MODAL -->
{#if showEditProfile}
	<div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
		<div class="max-h-[90vh] w-full max-w-md overflow-y-auto rounded-lg bg-white p-6">
			<h3 class="mb-4 text-xl font-bold text-gray-800">Edit Profile</h3>

			<div class="space-y-4">
				<!-- Profile Picture -->
				<div>
					<label for="profile-picture-upload" class="mb-2 block text-sm font-medium text-gray-700">
						Profile Picture
					</label>
					{#if editForm.profilePicture}
						<div class="mb-3">
							<img
								src={editForm.profilePicture}
								alt="Current profile"
								class="h-24 w-24 rounded-full border-2 border-gray-200 object-cover"
							/>
						</div>
					{/if}
					<input
						type="file"
						accept="image/*"
						disabled={uploadingPhoto || isEditSubmitting}
						onchange={async (e) => {
							const file = e.currentTarget.files?.[0];
							if (file) await handleProfilePhotoUpload(file);
						}}
						class="block w-full text-sm file:mr-4 file:rounded-lg file:border-0 file:bg-[#231161] file:px-4 file:py-2 file:text-white hover:file:bg-[#2d1982] disabled:file:bg-gray-400"
					/>
					{#if uploadingPhoto}
						<p class="mt-2 text-sm text-gray-600">Uploading...</p>
					{/if}
				</div>

				<div>
					<label class="mb-1 block text-sm font-medium text-gray-700" for="tutor-first-name"
						>First Name</label
					>
					<input
						id="tutor-first-name"
						type="text"
						bind:value={editForm.firstName}
						class="w-full rounded-lg border border-gray-300 px-3 py-2"
					/>
				</div>

				<div>
					<label class="mb-1 block text-sm font-medium text-gray-700" for="tutor-last-name"
						>Last Name</label
					>
					<input
						id="tutor-last-name"
						type="text"
						bind:value={editForm.lastName}
						class="w-full rounded-lg border border-gray-300 px-3 py-2"
					/>
				</div>

				<div>
					<label class="mb-1 block text-sm font-medium text-gray-700" for="tutor-bio">Bio</label>
					<textarea
						id="tutor-bio"
						bind:value={editForm.bio}
						rows="4"
						class="w-full rounded-lg border border-gray-300 px-3 py-2"
						placeholder="Tell students about yourself..."
					></textarea>
				</div>

				{#if editError}
					<p class="text-sm text-red-600">{editError}</p>
				{/if}

				{#if editSuccess}
					<p class="text-sm text-green-600">{editSuccess}</p>
				{/if}

				<div class="flex gap-3 pt-4">
					<button
						onclick={() => (showEditProfile = false)}
						disabled={isEditSubmitting}
						class="flex-1 rounded-lg bg-gray-200 px-4 py-2 text-gray-700 hover:bg-gray-300 disabled:opacity-50"
					>
						Cancel
					</button>
					<button
						onclick={handleEditProfile}
						disabled={isEditSubmitting}
						class="flex-1 rounded-lg bg-[#231161] px-4 py-2 text-white hover:bg-[#1a0d4a] disabled:opacity-50"
					>
						{isEditSubmitting ? 'Saving...' : 'Save Changes'}
					</button>
				</div>
			</div>
		</div>
	</div>
{/if}
