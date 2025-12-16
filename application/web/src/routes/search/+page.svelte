<script lang="ts">
	import { onMount } from 'svelte';
	import { Field } from '@ark-ui/svelte/field';
	import {
		Search as SearchIcon,
		Star,
		Calendar,
		Clock,
		User,
		BookOpen,
		Filter,
		X
	} from '@lucide/svelte';
	import { browser } from '$app/environment';
	import { goto } from '$app/navigation';
	import {
		searchTutors,
		getTags,
		getCurrentUser,
		authFetch,
		createSession,
		type SearchResult,
		type User as UserType,
		type Tag,
		type SessionLocation,
		SESSION_LOCATIONS
	} from '$lib/api';

	interface Tutor {
		tid: number;
		name: string;
		rating: number;
		email: string;
		courses: string[];
		bio: string | null;
		posts: { pid: number; course: string; content: string; timestamp: string }[];
		profile_tags: string[];
		status?: string;
	}

	// User state
	let user = $state<UserType | null>(getCurrentUser());

	// Search state
	let searchQuery = $state('');
	let searchResults = $state<Tutor[]>([]);
	let filteredResults = $state<Tutor[]>([]);
	let isLoading = $state(false);
	let errorMessage = $state('');
	let hasSearched = $state(false);

	// Filter state
	let tags = $state<Tag[]>([]);
	let selectedTagId = $state<number | null>(null);
	let minRating = $state<number>(0);
	let showFilters = $state(false);

	// Booking state
	let bookingTutorId = $state<number | null>(null);
	let bookingDay = $state('Monday');
	let bookingTime = $state(9);
	let bookingCourse = $state<number | null>(null);
	let bookingLocation = $state<SessionLocation>('Zoom');
	let isBooking = $state(false);
	let bookingError = $state('');
	let bookingSuccess = $state('');
	let tutorAvailability = $state<number[]>([]);
	let loadingAvailability = $state(false);

	const daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
	const hours = Array.from({ length: 12 }, (_, i) => i + 9); // 9 AM to 8 PM

	function formatTime(hour: number): string {
		const period = hour >= 12 ? 'PM' : 'AM';
		const displayHour = hour > 12 ? hour - 12 : hour === 0 ? 12 : hour;
		return `${displayHour}:00 ${period}`;
	}

	async function handleSearch() {
		isLoading = true;
		errorMessage = '';
		hasSearched = true;

		try {
			const data: SearchResult[] = await searchTutors(searchQuery);

			searchResults = data.map((t) => ({
				tid: t.tid,
				name: t.name,
				rating: t.rating ?? 0,
				email: t.email,
				courses: t.courses ?? [],
				bio: t.bio,
				posts: t.posts ?? [],
				profile_tags: t.profile_tags ?? [],
				status: (t as any).status
			}));

			applyFilters();
		} catch (error: any) {
			console.error('Search failed:', error);
			errorMessage = error?.message ?? 'Search failed. Please try again.';
			searchResults = [];
			filteredResults = [];
		} finally {
			isLoading = false;
		}
	}

	function applyFilters() {
		let results = [...searchResults];

		// Filter by tag/course
		if (selectedTagId !== null) {
			const selectedTag = tags.find(
				(t) => (t as any).tagsID === selectedTagId || t.id === selectedTagId
			);
			if (selectedTag) {
				const tagName = (selectedTag as any).tags || selectedTag.name;
				results = results.filter(
					(tutor) =>
						tutor.courses.some((c) => c.toLowerCase().includes(tagName.toLowerCase())) ||
						tutor.profile_tags.some((t) => t.toLowerCase().includes(tagName.toLowerCase()))
				);
			}
		}

		// Filter by minimum rating
		if (minRating > 0) {
			results = results.filter((tutor) => tutor.rating >= minRating);
		}

		filteredResults = results;
	}

	function clearFilters() {
		selectedTagId = null;
		minRating = 0;
		applyFilters();
	}

	async function loadAvailability(tid: number, day: string) {
		loadingAvailability = true;
		try {
			const res = await authFetch(`/api/tutors/${tid}/availability/day/${day}`);
			if (res.ok) {
				const data = await res.json();
				tutorAvailability = data.availableTimes || hours; // Default to all hours if no availability set
			} else {
				tutorAvailability = hours; // Default to all hours
			}
		} catch {
			tutorAvailability = hours;
		} finally {
			loadingAvailability = false;
		}
	}

	function openBooking(tutor: Tutor) {
		if (!user) {
			goto('/login');
			return;
		}
		bookingTutorId = tutor.tid;
		bookingDay = 'Monday';
		bookingTime = 9;
		bookingCourse = null;
		bookingLocation = 'Zoom';
		bookingError = '';
		bookingSuccess = '';
		loadAvailability(tutor.tid, 'Monday');
	}

	function closeBooking() {
		bookingTutorId = null;
		bookingDay = 'Monday';
		bookingTime = 9;
		bookingCourse = null;
		bookingLocation = 'Zoom';
		bookingError = '';
		bookingSuccess = '';
	}

	async function handleDayChange(day: string) {
		bookingDay = day;
		if (bookingTutorId) {
			await loadAvailability(bookingTutorId, day);
		}
	}

	async function confirmBooking() {
		if (!user || !bookingTutorId || !bookingCourse) return;

		isBooking = true;
		bookingError = '';
		bookingSuccess = '';

		try {
			await createSession({
				uid: user.uid,
				tid: bookingTutorId,
				tagsID: bookingCourse,
				day: bookingDay,
				time: bookingTime,
				location: bookingLocation
			});

			bookingSuccess = 'Session booked successfully! Redirecting to dashboard...';
			setTimeout(() => {
				goto('/student-dashboard');
			}, 2000);
		} catch (err: any) {
			bookingError = err?.message || 'Failed to book session';
		} finally {
			isBooking = false;
		}
	}

	function getTagIdFromCourse(courseName: string): number | null {
		const tag = tags.find(
			(t) => ((t as any).tags || t.name).toLowerCase() === courseName.toLowerCase()
		);
		return tag ? (tag as any).tagsID || tag.id : null;
	}

	// Load initial data
	onMount(async () => {
		// Load tags for filtering
		try {
			const res = await fetch('/api/tags');
			if (res.ok) {
				tags = await res.json();
			}
		} catch (e) {
			console.error('Failed to load tags:', e);
		}

		// Check URL for search query
		if (browser) {
			const urlParams = new URLSearchParams(window.location.search);
			if (urlParams.has('search')) {
				searchQuery = urlParams.get('search') ?? '';
				if (searchQuery.trim()) {
					handleSearch();
				}
			} else {
				// Load all tutors by default
				handleSearch();
			}
		}
	});

	// Re-apply filters when filter values change
	$effect(() => {
		if (hasSearched) {
			// Reference the reactive values to track them
			selectedTagId;
			minRating;
			applyFilters();
		}
	});
</script>

<svelte:head>
	<title>Search Tutors - Gator Guides</title>
</svelte:head>

<div class="min-h-screen bg-gray-50">
	<!-- Header -->
	<div class="bg-[#231161] px-4 py-6 text-white">
		<div class="mx-auto max-w-7xl">
			<h1 class="text-3xl font-bold">Find a Tutor</h1>
			<p class="mt-1 text-purple-200">Search by course, subject, or tutor name</p>
		</div>
	</div>

	<main class="mx-auto max-w-7xl px-4 py-6">
		<!-- Search Box -->
		<section class="mb-6 rounded-lg bg-white p-6 shadow">
			<div class="flex flex-col gap-4 sm:flex-row">
				<div class="relative flex-1">
					<SearchIcon class="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
					<input
						type="text"
						bind:value={searchQuery}
						onkeydown={(e) => {
							if (e.key === 'Enter') {
								e.preventDefault();
								handleSearch();
							}
						}}
						placeholder="Search by course code (e.g., CSC 648) or tutor name..."
						class="w-full rounded-lg border border-gray-300 bg-white py-3 pl-10 pr-4 focus:border-[#231161] focus:outline-none focus:ring-2 focus:ring-[#231161]/20"
					/>
				</div>
				<button
					onclick={handleSearch}
					disabled={isLoading}
					class="flex items-center justify-center gap-2 rounded-lg bg-[#231161] px-6 py-3 font-medium text-white transition-colors hover:bg-[#1a0d4a] disabled:opacity-50"
				>
					<SearchIcon class="h-5 w-5" />
					{isLoading ? 'Searching...' : 'Search'}
				</button>
				<button
					onclick={() => (showFilters = !showFilters)}
					class="flex items-center justify-center gap-2 rounded-lg border border-gray-300 px-4 py-3 text-gray-700 transition-colors hover:bg-gray-50"
				>
					<Filter class="h-5 w-5" />
					Filters
				</button>
			</div>

			<!-- Filters Panel -->
			{#if showFilters}
				<div class="mt-4 border-t pt-4">
					<div class="flex flex-wrap items-end gap-4">
						<!-- Course Filter -->
						<div class="min-w-[200px] flex-1">
							<label class="mb-1 block text-sm font-medium text-gray-700">Course/Subject</label>
							<select
								bind:value={selectedTagId}
								class="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-[#231161] focus:outline-none"
							>
								<option value={null}>All Courses</option>
								{#each tags as tag}
									<option value={(tag as any).tagsID || tag.id}>
										{(tag as any).tags || tag.name}
									</option>
								{/each}
							</select>
						</div>

						<!-- Rating Filter -->
						<div class="min-w-[150px]">
							<label class="mb-1 block text-sm font-medium text-gray-700">Minimum Rating</label>
							<select
								bind:value={minRating}
								class="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-[#231161] focus:outline-none"
							>
								<option value={0}>Any Rating</option>
								<option value={3}>3+ Stars</option>
								<option value={4}>4+ Stars</option>
								<option value={4.5}>4.5+ Stars</option>
							</select>
						</div>

						<!-- Clear Filters -->
						<button
							onclick={clearFilters}
							class="flex items-center gap-1 rounded-lg border border-gray-300 px-4 py-2 text-gray-600 hover:bg-gray-50"
						>
							<X class="h-4 w-4" />
							Clear
						</button>
					</div>
				</div>
			{/if}
		</section>

		<!-- Error Message -->
		{#if errorMessage}
			<div class="mb-6 rounded-lg border border-red-200 bg-red-50 p-4">
				<p class="text-red-700">{errorMessage}</p>
			</div>
		{/if}

		<!-- Results Count -->
		{#if hasSearched && !isLoading}
			<div class="mb-4 text-sm text-gray-600">
				Found {filteredResults.length} tutor{filteredResults.length !== 1 ? 's' : ''}
				{#if searchQuery}
					for "{searchQuery}"
				{/if}
			</div>
		{/if}

		<!-- Loading State -->
		{#if isLoading}
			<div class="rounded-lg bg-white p-8 text-center shadow">
				<div class="animate-pulse">
					<div class="mx-auto mb-4 h-16 w-16 rounded-full bg-[#231161]"></div>
					<p class="text-gray-600">Searching for tutors...</p>
				</div>
			</div>
		{:else if filteredResults.length > 0}
			<!-- Search Results -->
			<div class="space-y-4">
				{#each filteredResults as tutor}
					<div class="rounded-lg bg-white p-6 shadow transition-shadow hover:shadow-md">
						<div class="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
							<!-- Tutor Info -->
							<div class="flex-1">
								<div class="mb-2 flex items-center gap-3">
									<a
										href="/tutor/{tutor.tid}"
										class="text-xl font-semibold text-[#231161] hover:underline"
									>
										{tutor.name}
									</a>
									<div
										class="flex items-center gap-1 rounded-full bg-yellow-100 px-2 py-1 text-sm text-yellow-700"
									>
										<Star class="h-4 w-4 fill-yellow-500 text-yellow-500" />
										{tutor.rating?.toFixed(1) || '0.0'}
									</div>
									{#if tutor.status === 'available'}
										<span class="rounded-full bg-green-100 px-2 py-1 text-xs text-green-700">
											Available
										</span>
									{/if}
								</div>

								{#if tutor.email}
									<p class="mb-2 text-sm text-gray-600">{tutor.email}</p>
								{/if}

								{#if tutor.bio}
									<p class="mb-3 text-gray-700">{tutor.bio}</p>
								{/if}

								<!-- Courses/Tags -->
								{#if tutor.courses.length > 0 || tutor.profile_tags.length > 0}
									<div class="mb-3">
										<div class="flex items-center gap-2 text-sm text-gray-600">
											<BookOpen class="h-4 w-4" />
											<span>Teaches:</span>
										</div>
										<div class="mt-1 flex flex-wrap gap-2">
											{#each [...new Set([...tutor.courses, ...tutor.profile_tags])] as course}
												<span class="rounded-full bg-purple-100 px-3 py-1 text-sm text-purple-800">
													{course}
												</span>
											{/each}
										</div>
									</div>
								{/if}

								<!-- Recent Posts Preview -->
								{#if tutor.posts.length > 0}
									<div class="mt-3 border-t pt-3">
										<p class="mb-2 text-sm font-medium text-gray-700">Recent Activity:</p>
										<div class="space-y-2">
											{#each tutor.posts.slice(0, 2) as post}
												<div class="rounded bg-gray-50 p-2 text-sm">
													<span class="font-medium text-[#231161]">{post.course}</span>
													<p class="text-gray-600">
														{post.content.slice(0, 100)}{post.content.length > 100 ? '...' : ''}
													</p>
												</div>
											{/each}
										</div>
									</div>
								{/if}
							</div>

							<!-- Action Buttons -->
							<div class="flex flex-col gap-2">
								<a
									href="/tutor/{tutor.tid}"
									class="rounded-lg border border-[#231161] px-4 py-2 text-center text-sm font-medium text-[#231161] transition-colors hover:bg-purple-50"
								>
									View Profile
								</a>
								<button
									onclick={() => openBooking(tutor)}
									class="flex items-center justify-center gap-2 rounded-lg bg-[#231161] px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-[#1a0d4a]"
								>
									<Calendar class="h-4 w-4" />
									Book Session
								</button>
							</div>
						</div>
					</div>
				{/each}
			</div>
		{:else if hasSearched}
			<!-- No Results -->
			<div class="rounded-lg bg-white p-8 text-center shadow">
				<User class="mx-auto mb-4 h-16 w-16 text-gray-300" />
				<h3 class="mb-2 text-lg font-semibold text-gray-800">No tutors found</h3>
				<p class="text-gray-600">Try adjusting your search terms or filters to find more tutors.</p>
			</div>
		{/if}

		<!-- Quick Links -->
		<section class="mt-8 rounded-lg bg-white p-6 shadow">
			<h2 class="mb-4 text-lg font-bold text-gray-800">Popular Subjects</h2>
			<div class="flex flex-wrap gap-2">
				{#each tags.slice(0, 12) as tag}
					<button
						onclick={() => {
							searchQuery = (tag as any).tags || tag.name;
							handleSearch();
						}}
						class="rounded-full border border-gray-300 px-4 py-2 text-sm text-gray-700 transition-colors hover:border-[#231161] hover:bg-purple-50 hover:text-[#231161]"
					>
						{(tag as any).tags || tag.name}
					</button>
				{/each}
			</div>
		</section>
	</main>
</div>

<!-- Booking Modal -->
{#if bookingTutorId !== null}
	{@const tutor = filteredResults.find((t) => t.tid === bookingTutorId)}
	{#if tutor}
		<div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
			<div class="max-h-[90vh] w-full max-w-md overflow-y-auto rounded-lg bg-white p-6">
				<div class="mb-4 flex items-center justify-between">
					<h3 class="text-xl font-bold text-gray-800">Book a Session</h3>
					<button onclick={closeBooking} class="text-gray-500 hover:text-gray-700">
						<X class="h-6 w-6" />
					</button>
				</div>

				<p class="mb-4 text-gray-600">
					Booking with <span class="font-semibold text-[#231161]">{tutor.name}</span>
				</p>

				<div class="space-y-4">
					<!-- Course Selection -->
					<div>
						<label class="mb-1 block text-sm font-medium text-gray-700">Select Course</label>
						<select
							bind:value={bookingCourse}
							class="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-[#231161] focus:outline-none"
						>
							<option value={null}>Choose a course...</option>
							{#each [...new Set([...tutor.courses, ...tutor.profile_tags])] as course}
								{@const tagId = getTagIdFromCourse(course)}
								{#if tagId}
									<option value={tagId}>{course}</option>
								{/if}
							{/each}
						</select>
					</div>

					<!-- Day Selection -->
					<div>
						<label class="mb-1 block text-sm font-medium text-gray-700">Select Day</label>
						<select
							bind:value={bookingDay}
							onchange={(e) => handleDayChange((e.target as HTMLSelectElement).value)}
							class="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-[#231161] focus:outline-none"
						>
							{#each daysOfWeek as day}
								<option value={day}>{day}</option>
							{/each}
						</select>
					</div>

					<!-- Time Selection -->
					<div>
						<label class="mb-1 block text-sm font-medium text-gray-700">Select Time</label>
						{#if loadingAvailability}
							<p class="text-sm text-gray-500">Loading availability...</p>
						{:else}
							<select
								bind:value={bookingTime}
								class="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-[#231161] focus:outline-none"
							>
								{#each tutorAvailability as hour}
									<option value={hour}>{formatTime(hour)}</option>
								{/each}
							</select>
							{#if tutorAvailability.length === 0}
								<p class="mt-1 text-sm text-red-600">No available times for this day</p>
							{/if}
						{/if}
					</div>

					<!-- Location Selection -->
					<div>
						<label class="mb-1 block text-sm font-medium text-gray-700">Select Location</label>
						<select
							bind:value={bookingLocation}
							class="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-[#231161] focus:outline-none"
						>
							{#each SESSION_LOCATIONS as loc}
								<option value={loc}>{loc}</option>
							{/each}
						</select>
					</div>

					<!-- Error/Success Messages -->
					{#if bookingError}
						<div class="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
							{bookingError}
						</div>
					{/if}

					{#if bookingSuccess}
						<div class="rounded-lg border border-green-200 bg-green-50 p-3 text-sm text-green-700">
							{bookingSuccess}
						</div>
					{/if}

					<!-- Action Buttons -->
					<div class="flex gap-3 pt-4">
						<button
							onclick={closeBooking}
							disabled={isBooking}
							class="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-gray-700 transition-colors hover:bg-gray-50 disabled:opacity-50"
						>
							Cancel
						</button>
						<button
							onclick={confirmBooking}
							disabled={isBooking || !bookingCourse || tutorAvailability.length === 0}
							class="flex-1 rounded-lg bg-[#231161] px-4 py-2 text-white transition-colors hover:bg-[#1a0d4a] disabled:opacity-50"
						>
							{isBooking ? 'Booking...' : 'Confirm Booking'}
						</button>
					</div>
				</div>
			</div>
		</div>
	{/if}
{/if}
