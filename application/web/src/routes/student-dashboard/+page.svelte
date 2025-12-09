<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import {
		getCurrentUser,
		logoutUser,
		authFetch,
		createSession,
		getTags,
		updateUser,
		uploadProfilePicture,
		type User,
		type Session
	} from '$lib/api';
	import ImageUpload from '$lib/components/ImageUpload.svelte';

	// ---- STATE ----
	let user = $state<User | null>(getCurrentUser());
	let profile = $state<any>(null);

	let tutors = $state<any[]>([]);
	let filteredTutors = $state<any[] | null>(null);

	let tutorCourses = $state<{ [key: number]: any[] }>({});
	let tutorCoursesLoading = $state<{ [key: number]: boolean }>({});
	let tutorCoursesError = $state<{ [key: number]: boolean }>({});
	let tags = $state<any[]>([]);
	let activeTagId = $state<number | null>(null);

	let upcomingSessions = $state<Session[]>([]);
	let pastSessions = $state<Session[]>([]);

	let isLoading = $state(true);
	let isLoggingOut = $state(false);
	let errorMessage = $state('');

	// ---- EDIT PROFILE ----
	let showEditProfile = $state(false);
	let editForm = $state({
		firstName: '',
		lastName: '',
		phone: '',
		studentId: '',
		bio: '',
		profilePicture: ''
	});
	let isEditSubmitting = $state(false);
	let editError = $state('');
	let editSuccess = $state('');
	let uploadingPhoto = $state(false);

	// ---- REVIEW MODAL ----
	let showReviewModal = $state(false);
	let reviewSession = $state<Session | null>(null);
	let reviewForm = $state({
		rating: 5,
		comment: ''
	});
	let isReviewSubmitting = $state(false);

	// ---- BOOKING ----
	let bookingStates = $state<{
		[key: number]: {
			isOpen: boolean;
			selectedCourse: number | null;
			selectedDay: string;
			selectedTime: number;
			isSubmitting: boolean;
			error: string;
			success: string;
		};
	}>({});

	// ---- HELPERS ----
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

	function hasTimeConflict(day: string, time: number): boolean {
		return upcomingSessions.some((session) => session.day === day && session.time === time);
	}

	function openBooking(tutorId: number) {
		bookingStates[tutorId] = {
			isOpen: true,
			selectedCourse: null,
			selectedDay: 'Monday',
			selectedTime: 14,
			isSubmitting: false,
			error: '',
			success: ''
		};
	}

	function closeBooking(tutorId: number) {
		if (bookingStates[tutorId]) {
			bookingStates[tutorId].isOpen = false;
		}
	}

	async function confirmBooking(tutorId: number) {
		const state = bookingStates[tutorId];
		if (!state || !user) return;

		state.error = '';
		state.success = '';

		if (!state.selectedCourse) {
			state.error = 'Please select a course';
			return;
		}

		if (hasTimeConflict(state.selectedDay, state.selectedTime)) {
			state.error = `You already have a session on ${state.selectedDay} at ${formatTime(
				state.selectedTime
			)}`;
			return;
		}

		state.isSubmitting = true;

		try {
			await createSession({
				uid: user.uid,
				tid: tutorId,
				tagsID: state.selectedCourse,
				day: state.selectedDay,
				time: state.selectedTime
			});

			state.success = 'Session booked successfully!';
			await loadSessions();

			setTimeout(() => {
				closeBooking(tutorId);
			}, 1500);
		} catch (err: any) {
			state.error = err?.message || 'Failed to book session';
		} finally {
			state.isSubmitting = false;
		}
	}

	async function cancelSessionById(sid: number) {
		try {
			const res = await authFetch(`/api/sessions/${sid}`, {
				method: 'DELETE'
			});

			if (!res.ok) {
				const body = await res.json().catch(() => null);
				console.error('Failed to cancel session', body || res.statusText);
				return;
			}

			await loadSessions();
		} catch (err) {
			console.error('Cancel session error:', err);
		}
	}

	function confirmCancelSession(session: Session) {
		const message = `Are you sure you want to cancel your ${session.course} session with ${session.tutor.name} on ${session.day} at ${formatTime(session.time)}?`;
		if (confirm(message)) {
			cancelSessionById((session as any).sid);
		}
	}

	async function loadTutorCourses(tid: number) {
		tutorCoursesLoading[tid] = true;
		tutorCoursesError[tid] = false;

		try {
			const res = await authFetch(`/api/tutors/${tid}/tags`);
			if (res.ok) {
				tutorCourses[tid] = await res.json();
				tutorCoursesError[tid] = false;
			} else {
				console.warn(`Could not load courses for tutor ${tid}: ${res.status}`);
				tutorCourses[tid] = [];
				tutorCoursesError[tid] = true;
			}
		} catch (err) {
			console.warn(`Could not load courses for tutor ${tid}:`, err);
			tutorCourses[tid] = [];
			tutorCoursesError[tid] = true;
		} finally {
			tutorCoursesLoading[tid] = false;
		}
	}

	async function loadSessions() {
		if (!user) return;

		try {
			const sessionsRes = await authFetch(`/api/users/${user.uid}/sessions`);
			if (sessionsRes.ok) {
				const allSessions = await sessionsRes.json();
				const now = new Date();

				upcomingSessions = allSessions.filter(
					(s: Session) => !s.concluded || new Date(s.concluded) > now
				);
				pastSessions = allSessions.filter(
					(s: Session) => s.concluded && new Date(s.concluded) <= now
				);
			}
		} catch (err) {
			console.error('Failed to load sessions:', err);
		}
	}

	function extractPhone(bio: string | null): string {
		if (!bio) return '';
		const match = bio.match(/Phone:\s*([^,|\n]+)/);
		return match ? match[1].trim() : '';
	}

	function extractStudentId(bio: string | null): string {
		if (!bio) return '';
		const match = bio.match(/Student ID:\s*([^,|\n]+)/);
		return match ? match[1].trim() : '';
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

			// Update form and profile
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
			const updatedBio = `Student ID: ${editForm.studentId}, Phone: ${editForm.phone}`;

			await updateUser(user!.uid, {
				firstName: editForm.firstName,
				lastName: editForm.lastName,
				bio: updatedBio
			});

			// Update UI immediately from form values
			profile = {
				...(profile ?? {}),
				firstName: editForm.firstName,
				lastName: editForm.lastName,
				bio: updatedBio,
				profilePicture: editForm.profilePicture
			};

			// Update header and local user
			if (user) {
				user.firstName = editForm.firstName;
				user.lastName = editForm.lastName;
				user.bio = updatedBio;
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

	function openReviewModal(session: Session) {
		reviewSession = session;
		reviewForm = { rating: 5, comment: '' };
		showReviewModal = true;
	}

	async function submitReview() {
		if (!reviewSession) return;

		isReviewSubmitting = true;

		try {
			const res = await authFetch(`/api/tutors/${reviewSession.tutor.tid}/reviews`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					uid: user?.uid,
					rating: reviewForm.rating,
					comment: reviewForm.comment
				})
			});

			if (!res.ok) {
				throw new Error('Failed to submit review');
			}

			showReviewModal = false;
			await loadDashboard();
		} catch (err: any) {
			console.error('Review error:', err);
		} finally {
			isReviewSubmitting = false;
		}
	}

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

	// ---- TAG FILTER ----
	function applyTagFilter(tagId: number | null) {
		activeTagId = tagId;

		if (tagId === null) {
			filteredTutors = tutors;
			return;
		}

		filteredTutors = tutors.filter((tutor) => {
			const courseList = tutorCourses[tutor.tid] || tutor.tags || tutor.courses || [];
			return courseList.some((tg: any) => tg.tagsID === tagId || tg.id === tagId);
		});
	}

	// ---- LOAD DASHBOARD ----
	async function loadDashboard() {
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
					phone: extractPhone(profile.bio),
					studentId: extractStudentId(profile.bio),
					bio: profile.bio || '',
					profilePicture: profile.profilePicture || ''
				};
			}
			const tutorRes = await authFetch(`/api/tutors/by-user/${user.uid}`);
			if (tutorRes.ok) {
				goto('/tutor-dashboard');
				return;
			}

			// 🔹 Load ALL tutors instead of only top tutors
			const tutorsRes = await authFetch('/api/tutors');
			if (tutorsRes.ok) {
				tutors = await tutorsRes.json();
				filteredTutors = tutors;

				for (const tutor of tutors) {
					await loadTutorCourses(tutor.tid);
				}
			} else {
				tutors = [];
				filteredTutors = [];
			}

			tags = await getTags();

			await loadSessions();
		} catch (err: any) {
			console.error('Error loading dashboard:', err);
			errorMessage = 'Failed to load dashboard';
		} finally {
			isLoading = false;
		}
	}

	onMount(() => {
		loadDashboard();
	});
</script>

<div class="min-h-screen bg-gray-50">
	<header class="bg-[#231161] text-white shadow-lg">
		<div class="mx-auto flex max-w-7xl items-center justify-between px-4 py-4">
			<div>
				<h1 class="text-2xl font-bold">Gator Guides</h1>
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
					<p class="text-gray-600">Loading your dashboard...</p>
				</div>
			</div>
		{:else if errorMessage}
			<div class="rounded-lg border border-red-200 bg-red-50 p-4">
				<p class="text-red-700">{errorMessage}</p>
			</div>
		{:else}
			<!-- PROFILE -->
			<section class="rounded-lg bg-white p-6 shadow">
				<div class="mb-4 flex items-center justify-between">
					<h2 class="text-xl font-bold text-gray-800">Your Profile</h2>
					<button
						onclick={openEditProfile}
						class="rounded-lg bg-[#231161] px-4 py-2 text-sm text-white hover:bg-[#1a0d4a]"
					>
						Edit Profile
					</button>
				</div>
				{#if profile}
					<div class="flex items-start gap-4">
						{#if profile.profilePicture}
							<img
								src={profile.profilePicture}
								alt="{profile.firstName} {profile.lastName}"
								class="h-20 w-20 rounded-full border-2 border-[#231161] object-cover"
							/>
						{:else}
							<div
								class="flex h-20 w-20 items-center justify-center rounded-full border-2 border-[#231161] bg-purple-100"
							>
								<span class="text-2xl font-bold text-[#231161]">
									{profile.firstName?.[0]}{profile.lastName?.[0]}
								</span>
							</div>
						{/if}
						<div class="flex-1 space-y-2">
							<p class="text-lg font-semibold text-gray-800">
								{profile.firstName}
								{profile.lastName}
							</p>
							<p class="text-gray-600">{profile.email}</p>
							{#if extractStudentId(profile.bio)}
								<p class="text-sm text-gray-600">
									Student ID: {extractStudentId(profile.bio)}
								</p>
							{/if}
							{#if extractPhone(profile.bio)}
								<p class="text-sm text-gray-600">
									Phone: {extractPhone(profile.bio)}
								</p>
							{/if}
						</div>
					</div>
				{/if}
			</section>

			<!-- UPCOMING SESSIONS -->
			{#if upcomingSessions.length > 0}
				<section class="rounded-lg bg-white p-6 shadow">
					<h2 class="mb-4 text-xl font-bold text-gray-800">Upcoming Sessions</h2>
					<div class="space-y-3">
						{#each upcomingSessions as session}
							<div class="rounded-lg border border-purple-200 bg-purple-50 p-4">
								<div class="mb-2 flex items-center justify-between">
									<div class="flex items-center gap-2">
										<span class="rounded bg-purple-600 px-2 py-1 text-xs font-semibold text-white"
											>Upcoming</span
										>
										<span class="text-sm font-medium text-gray-700">{session.course}</span>
									</div>
									<button
										type="button"
										class="rounded bg-red-600 px-3 py-1 text-xs text-white hover:bg-red-700"
										onclick={() => confirmCancelSession(session)}
									>
										Cancel
									</button>
								</div>
								<div class="grid grid-cols-2 gap-4 text-sm">
									<div>
										<p class="text-gray-600">Tutor</p>
										<p class="font-semibold text-gray-800">
											{session.tutor.name}
										</p>
									</div>
									<div>
										<p class="text-gray-600">Schedule</p>
										<p class="font-semibold text-gray-800">
											{session.day} at {formatTime(session.time)}
										</p>
									</div>
								</div>
							</div>
						{/each}
					</div>
				</section>
			{/if}

			<!-- PAST SESSIONS -->
			{#if pastSessions.length > 0}
				<section class="rounded-lg bg-white p-6 shadow">
					<h2 class="mb-4 text-xl font-bold text-gray-800">Past Sessions</h2>
					<div class="space-y-3">
						{#each pastSessions as session}
							<div class="rounded-lg border border-gray-200 bg-gray-50 p-4">
								<div class="mb-2 flex items-center gap-2">
									<span class="rounded bg-gray-500 px-2 py-1 text-xs font-semibold text-white"
										>Completed</span
									>
									<span class="text-sm font-medium text-gray-700">{session.course}</span>
								</div>
								<div class="grid grid-cols-2 gap-4 text-sm">
									<div>
										<p class="text-gray-600">Tutor</p>
										<p class="font-semibold text-gray-800">
											{session.tutor.name}
										</p>
									</div>
									<div>
										<p class="text-gray-600">Completed</p>
										<p class="font-semibold text-gray-800">
											{formatDate(session.concluded)}
										</p>
									</div>
								</div>
								<div class="mt-3 border-t pt-3">
									<button
										onclick={() => openReviewModal(session)}
										class="rounded bg-yellow-600 px-4 py-2 text-sm text-white hover:bg-yellow-700"
									>
										Rate Tutor
									</button>
								</div>
							</div>
						{/each}
					</div>
				</section>
			{/if}

			<!-- AVAILABLE TUTORS + TAG FILTER -->
			<section class="rounded-lg bg-white p-6 shadow">
				<div class="mb-4 flex items-center justify-between">
					<h2 class="text-xl font-bold text-gray-800">Available Tutors</h2>
				</div>

				{#if tags.length > 0}
					<div class="mb-4">
						<p class="mb-2 text-xs text-gray-600">Filter by course / tag:</p>
						<div class="flex flex-wrap gap-2">
							<button
								type="button"
								class="rounded-full border px-3 py-1 text-xs font-medium
                                {activeTagId === null
									? 'border-[#231161] bg-[#231161] text-white'
									: 'border-gray-300 bg-white text-gray-700'}"
								onclick={() => applyTagFilter(null)}
							>
								All
							</button>

							{#each tags as tag}
								<button
									type="button"
									class="rounded-full border px-3 py-1 text-xs font-medium
                                    {activeTagId === (tag.tagsID ?? tag.id)
										? 'border-[#231161] bg-[#231161] text-white'
										: 'border-gray-300 bg-white text-gray-700'}"
									onclick={() => applyTagFilter(tag.tagsID ?? tag.id)}
								>
									{tag.tags ?? tag.name}
								</button>
							{/each}
						</div>
					</div>
				{/if}

				{#if (filteredTutors ?? tutors).length > 0}
					<div class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
						{#each filteredTutors ?? tutors as tutor}
							<div class="rounded-lg border border-gray-200 p-4">
								<div class="mb-3">
									<p class="font-semibold text-gray-800">{tutor.name}</p>
									<div class="mt-1 flex items-center gap-1 text-sm text-yellow-600">
										<span>⭐</span>
										<span>{tutor.rating?.toFixed(1) || '0.0'}</span>
									</div>

									{#if tutorCoursesLoading[tutor.tid]}
										<p class="mt-2 text-xs text-gray-500">Loading courses...</p>
									{:else if tutorCoursesError[tutor.tid]}
										<p class="mt-2 text-xs text-red-600">⚠️ Courses unavailable</p>
									{:else if tutorCourses[tutor.tid] && tutorCourses[tutor.tid].length > 0}
										<div class="mt-2">
											<p class="mb-1 text-xs text-gray-600">Teaches:</p>
											<div class="flex flex-wrap gap-1">
												{#each tutorCourses[tutor.tid] as course}
													<span class="rounded bg-purple-100 px-2 py-1 text-xs text-purple-800">
														{course.name}
													</span>
												{/each}
											</div>
										</div>
									{/if}
								</div>

								{#if tutorCoursesError[tutor.tid]}
									<button
										disabled
										class="w-full cursor-not-allowed rounded-lg bg-gray-300 px-4 py-2 text-sm text-gray-500"
									>
										Booking Unavailable
									</button>
								{:else if !bookingStates[tutor.tid]?.isOpen}
									<button
										onclick={() => openBooking(tutor.tid)}
										class="w-full rounded-lg bg-[#231161] px-4 py-2 text-sm font-medium text-white hover:bg-[#1a0d4a]"
									>
										Book Session
									</button>
								{:else}
									<div class="space-y-3">
										<div>
											<label class="mb-1 block text-xs text-gray-600" for={`course-${tutor.tid}`}
												>Course</label
											>
											<select
												id={`course-${tutor.tid}`}
												bind:value={bookingStates[tutor.tid].selectedCourse}
												class="w-full rounded border border-gray-300 px-3 py-2 text-sm"
											>
												<option value={null}>Select course</option>
												{#each tutorCourses[tutor.tid] || [] as course}
													<option value={course.id}>
														{course.name}
													</option>
												{/each}
											</select>
										</div>

										<div>
											<label class="mb-1 block text-xs text-gray-600" for={`day-${tutor.tid}`}
												>Day</label
											>
											<select
												id={`day-${tutor.tid}`}
												bind:value={bookingStates[tutor.tid].selectedDay}
												class="w-full rounded border border-gray-300 px-3 py-2 text-sm"
											>
												<option>Monday</option>
												<option>Tuesday</option>
												<option>Wednesday</option>
												<option>Thursday</option>
												<option>Friday</option>
											</select>
										</div>

										<div>
											<label class="mb-1 block text-xs text-gray-600" for={`time-${tutor.tid}`}
												>Time</label
											>
											<select
												id={`time-${tutor.tid}`}
												bind:value={bookingStates[tutor.tid].selectedTime}
												class="w-full rounded border border-gray-300 px-3 py-2 text-sm"
											>
												{#each Array(9) as _, i}
													<option value={9 + i}>
														{formatTime(9 + i)}
													</option>
												{/each}
											</select>
										</div>

										{#if bookingStates[tutor.tid].error}
											<p class="text-xs text-red-600">
												{bookingStates[tutor.tid].error}
											</p>
										{/if}

										{#if bookingStates[tutor.tid].success}
											<p class="text-xs text-green-600">
												{bookingStates[tutor.tid].success}
											</p>
										{/if}

										<div class="flex gap-2">
											<button
												onclick={() => closeBooking(tutor.tid)}
												disabled={bookingStates[tutor.tid].isSubmitting}
												class="flex-1 rounded bg-gray-200 px-3 py-2 text-sm text-gray-700 hover:bg-gray-300 disabled:opacity-50"
											>
												Cancel
											</button>
											<button
												onclick={() => confirmBooking(tutor.tid)}
												disabled={bookingStates[tutor.tid].isSubmitting}
												class="flex-1 rounded bg-[#231161] px-3 py-2 text-sm text-white hover:bg-[#1a0d4a] disabled:opacity-50"
											>
												{bookingStates[tutor.tid].isSubmitting ? 'Booking...' : 'Confirm'}
											</button>
										</div>
									</div>
								{/if}
							</div>
						{/each}
					</div>
				{:else}
					<p class="py-8 text-center text-gray-500">No tutors available at the moment.</p>
				{/if}
			</section>
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
					<label class="mb-2 block text-sm font-medium text-gray-700"> Profile Picture </label>
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
					<label class="mb-1 block text-sm font-medium text-gray-700" for="first-name-input"
						>First Name</label
					>
					<input
						id="first-name-input"
						type="text"
						bind:value={editForm.firstName}
						class="w-full rounded-lg border border-gray-300 px-3 py-2"
					/>
				</div>

				<div>
					<label class="mb-1 block text-sm font-medium text-gray-700" for="last-name-input"
						>Last Name</label
					>
					<input
						id="last-name-input"
						type="text"
						bind:value={editForm.lastName}
						class="w-full rounded-lg border border-gray-300 px-3 py-2"
					/>
				</div>

				<div>
					<label class="mb-1 block text-sm font-medium text-gray-700" for="phone-input">Phone</label
					>
					<input
						id="phone-input"
						type="tel"
						bind:value={editForm.phone}
						class="w-full rounded-lg border border-gray-300 px-3 py-2"
					/>
				</div>

				<div>
					<label class="mb-1 block text-sm font-medium text-gray-700" for="student-id-input"
						>Student ID</label
					>
					<input
						id="student-id-input"
						type="text"
						bind:value={editForm.studentId}
						class="w-full rounded-lg border border-gray-300 px-3 py-2"
					/>
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

<!-- REVIEW MODAL -->
{#if showReviewModal && reviewSession}
	<div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
		<div class="w-full max-w-md rounded-lg bg-white p-6">
			<h3 class="mb-4 text-xl font-bold text-gray-800">Rate Your Tutor</h3>
			<p class="mb-4 text-sm text-gray-600">
				How was your session with {reviewSession.tutor.name}?
			</p>

			<div class="space-y-4">
				<div>
					<label class="mb-2 block text-sm font-medium text-gray-700">Rating</label>
					<div class="flex gap-2">
						{#each [1, 2, 3, 4, 5] as star}
							<button
								type="button"
								onclick={() => (reviewForm.rating = star)}
								class="text-3xl {star <= reviewForm.rating ? 'text-yellow-500' : 'text-gray-300'}"
							>
								★
							</button>
						{/each}
					</div>
				</div>

				<div>
					<label class="mb-1 block text-sm font-medium text-gray-700" for="review-comment"
						>Comment</label
					>
					<textarea
						id="review-comment"
						bind:value={reviewForm.comment}
						rows="4"
						placeholder="Share your experience..."
						class="w-full rounded-lg border border-gray-300 px-3 py-2"
					></textarea>
				</div>

				<div class="flex gap-3 pt-4">
					<button
						type="button"
						onclick={() => (showReviewModal = false)}
						disabled={isReviewSubmitting}
						class="flex-1 rounded-lg bg-gray-200 px-4 py-2 text-gray-700 hover:bg-gray-300 disabled:opacity-50"
					>
						Cancel
					</button>
					<button
						type="button"
						onclick={submitReview}
						disabled={isReviewSubmitting}
						class="flex-1 rounded-lg bg-yellow-600 px-4 py-2 text-white hover:bg-yellow-700 disabled:opacity-50"
					>
						{isReviewSubmitting ? 'Submitting...' : 'Submit Review'}
					</button>
				</div>
			</div>
		</div>
	</div>
{/if}
