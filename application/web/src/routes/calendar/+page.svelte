<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { getCurrentUser, authFetch, type User, type Session } from '$lib/api';

	let user = $state<User | null>(getCurrentUser());
	let sessions = $state<Session[]>([]);
	let isLoading = $state(true);
	let errorMessage = $state('');
	let currentWeekStart = $state(getMonday(new Date()));
	let isTutor = $state(false);
	let tutorId = $state<number | null>(null);

	// Derived state for filtered sessions
	let upcomingSessions = $derived(sessions.filter((s) => !s.concluded));
	let pastSessions = $derived(sessions.filter((s) => s.concluded));

	const daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
	const hours = Array.from({ length: 12 }, (_, i) => i + 9); // 9 AM to 8 PM

	function getMonday(date: Date): Date {
		const d = new Date(date);
		const day = d.getDay();
		const diff = d.getDate() - day + (day === 0 ? -6 : 1);
		d.setDate(diff);
		d.setHours(0, 0, 0, 0);
		return d;
	}

	function formatTime(hour: number): string {
		const period = hour >= 12 ? 'PM' : 'AM';
		const displayHour = hour > 12 ? hour - 12 : hour === 0 ? 12 : hour;
		return `${displayHour}:00 ${period}`;
	}

	function formatDateHeader(dayIndex: number): string {
		const date = new Date(currentWeekStart);
		date.setDate(date.getDate() + dayIndex);
		return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
	}

	function getWeekDateRange(): string {
		const start = new Date(currentWeekStart);
		const end = new Date(currentWeekStart);
		end.setDate(end.getDate() + 6);

		const startStr = start.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
		const endStr = end.toLocaleDateString('en-US', {
			month: 'short',
			day: 'numeric',
			year: 'numeric'
		});

		return `${startStr} - ${endStr}`;
	}

	function previousWeek() {
		const newDate = new Date(currentWeekStart);
		newDate.setDate(newDate.getDate() - 7);
		currentWeekStart = newDate;
	}

	function nextWeek() {
		const newDate = new Date(currentWeekStart);
		newDate.setDate(newDate.getDate() + 7);
		currentWeekStart = newDate;
	}

	function goToToday() {
		currentWeekStart = getMonday(new Date());
	}

	function getSessionsForSlot(day: string, hour: number): Session[] {
		return sessions.filter((s) => s.day === day && s.time === hour);
	}

	function getSessionColor(session: Session): string {
		if (session.concluded) {
			return 'bg-gray-200 border-gray-400 text-gray-700';
		}
		if (session.started) {
			return 'bg-green-100 border-green-500 text-green-800';
		}
		return 'bg-purple-100 border-[#231161] text-[#231161]';
	}

	function getSessionStatus(session: Session): string {
		if (session.concluded) return 'Completed';
		if (session.started) return 'In Progress';
		return 'Scheduled';
	}

	async function loadCalendarData() {
		if (!user) {
			goto('/login');
			return;
		}

		isLoading = true;
		errorMessage = '';

		try {
			// Check if user is a tutor
			const tutorRes = await authFetch(`/api/tutors/by-user/${user.uid}`);
			if (tutorRes.ok) {
				const tutorData = await tutorRes.json();
				isTutor = true;
				tutorId = tutorData.tid;

				// Load tutor sessions
				const tutorSessionsRes = await authFetch(`/api/tutors/${tutorData.tid}/sessions`);
				if (tutorSessionsRes.ok) {
					const tutorSessions = await tutorSessionsRes.json();
					sessions = tutorSessions;
				}
			} else {
				// Load student sessions
				const sessionsRes = await authFetch(`/api/users/${user.uid}/sessions`);
				if (sessionsRes.ok) {
					sessions = await sessionsRes.json();
				}
			}
		} catch (err: any) {
			console.error('Error loading calendar:', err);
			errorMessage = 'Failed to load calendar data';
		} finally {
			isLoading = false;
		}
	}

	onMount(() => {
		loadCalendarData();
	});
</script>

<svelte:head>
	<title>Calendar - Gator Guides</title>
</svelte:head>

<div class="min-h-screen bg-gray-50">
	<!-- Header -->
	<div class="bg-[#231161] px-4 py-6 text-white">
		<div class="mx-auto max-w-7xl">
			<h1 class="text-3xl font-bold">My Calendar</h1>
			{#if user}
				<p class="mt-1 text-purple-200">
					{isTutor ? 'Tutor' : 'Student'} Schedule for {user.firstName}
					{user.lastName}
				</p>
			{/if}
		</div>
	</div>

	<main class="mx-auto max-w-7xl px-4 py-6">
		{#if !user}
			<div class="rounded-lg bg-white p-8 text-center shadow">
				<h2 class="mb-4 text-xl font-semibold text-gray-800">Please Log In</h2>
				<p class="mb-4 text-gray-600">You need to be logged in to view your calendar.</p>
				<a
					href="/login"
					class="inline-block rounded-lg bg-[#231161] px-6 py-3 text-white hover:bg-[#1a0d4a]"
				>
					Go to Login
				</a>
			</div>
		{:else if isLoading}
			<div class="rounded-lg bg-white p-8 text-center shadow">
				<div class="animate-pulse">
					<div class="mx-auto mb-4 h-16 w-16 rounded-full bg-[#231161]"></div>
					<p class="text-gray-600">Loading your calendar...</p>
				</div>
			</div>
		{:else if errorMessage}
			<div class="rounded-lg border border-red-200 bg-red-50 p-4">
				<p class="text-red-700">{errorMessage}</p>
			</div>
		{:else}
			<!-- Calendar Controls -->
			<div
				class="mb-6 flex flex-wrap items-center justify-between gap-4 rounded-lg bg-white p-4 shadow"
			>
				<div class="flex items-center gap-2">
					<button
						onclick={previousWeek}
						class="rounded-lg border border-gray-300 px-4 py-2 text-gray-700 hover:bg-gray-50"
					>
						← Previous
					</button>
					<button
						onclick={goToToday}
						class="rounded-lg bg-[#231161] px-4 py-2 text-white hover:bg-[#1a0d4a]"
					>
						Today
					</button>
					<button
						onclick={nextWeek}
						class="rounded-lg border border-gray-300 px-4 py-2 text-gray-700 hover:bg-gray-50"
					>
						Next →
					</button>
				</div>
				<div class="text-lg font-semibold text-gray-800">
					{getWeekDateRange()}
				</div>
			</div>

			<!-- Legend -->
			<div class="mb-4 flex flex-wrap gap-4 rounded-lg bg-white p-4 shadow">
				<div class="flex items-center gap-2">
					<div class="h-4 w-4 rounded border-2 border-[#231161] bg-purple-100"></div>
					<span class="text-sm text-gray-600">Scheduled</span>
				</div>
				<div class="flex items-center gap-2">
					<div class="h-4 w-4 rounded border-2 border-green-500 bg-green-100"></div>
					<span class="text-sm text-gray-600">In Progress</span>
				</div>
				<div class="flex items-center gap-2">
					<div class="h-4 w-4 rounded border-2 border-gray-400 bg-gray-200"></div>
					<span class="text-sm text-gray-600">Completed</span>
				</div>
			</div>

			<!-- Calendar Grid -->
			<div class="overflow-x-auto rounded-lg bg-white shadow">
				<div class="min-w-[800px]">
					<!-- Header Row -->
					<div class="grid grid-cols-8 border-b bg-gray-50">
						<div class="border-r p-3 text-center text-sm font-medium text-gray-500">Time</div>
						{#each daysOfWeek as day, index}
							<div class="border-r p-3 text-center last:border-r-0">
								<div class="font-semibold text-gray-800">{day}</div>
								<div class="text-sm text-gray-500">{formatDateHeader(index)}</div>
							</div>
						{/each}
					</div>

					<!-- Time Slots -->
					{#each hours as hour}
						<div class="grid grid-cols-8 border-b last:border-b-0">
							<div class="border-r bg-gray-50 p-3 text-center text-sm font-medium text-gray-500">
								{formatTime(hour)}
							</div>
							{#each daysOfWeek as day}
								{@const slotSessions = getSessionsForSlot(day, hour)}
								<div class="relative min-h-[80px] border-r p-1 last:border-r-0">
									{#each slotSessions as session}
										<div class="mb-1 rounded border-l-4 p-2 text-xs {getSessionColor(session)}">
											<div class="font-semibold">{session.course}</div>
											<div class="truncate">
												{#if isTutor}
													{session.student?.name || 'Student'}
												{:else}
													{session.tutor?.name || 'Tutor'}
												{/if}
											</div>
											<div class="mt-1 text-[10px] opacity-75">
												{getSessionStatus(session)}
											</div>
										</div>
									{/each}
								</div>
							{/each}
						</div>
					{/each}
				</div>
			</div>

			<!-- Sessions Summary -->
			<div class="mt-6 grid gap-6 md:grid-cols-2">
				<!-- Upcoming Sessions -->
				<div class="rounded-lg bg-white p-6 shadow">
					<h2 class="mb-4 text-lg font-bold text-gray-800">Upcoming Sessions</h2>
					{#if upcomingSessions.length > 0}
						<div class="space-y-3">
							{#each upcomingSessions.slice(0, 5) as session}
								<div class="rounded-lg border border-purple-200 bg-purple-50 p-3">
									<div class="flex items-start justify-between">
										<div>
											<div class="font-semibold text-[#231161]">{session.course}</div>
											<div class="text-sm text-gray-600">
												{#if isTutor}
													with {session.student?.name || 'Student'}
												{:else}
													with {session.tutor?.name || 'Tutor'}
												{/if}
											</div>
											<div class="mt-1 text-sm text-gray-500">
												{session.day} at {formatTime(session.time)}
											</div>
										</div>
										{#if session.started}
											<span class="rounded-full bg-green-100 px-2 py-1 text-xs text-green-700">
												In Progress
											</span>
										{/if}
									</div>
								</div>
							{/each}
						</div>
					{:else}
						<p class="text-gray-500">No upcoming sessions scheduled.</p>
					{/if}
				</div>

				<!-- Past Sessions -->
				<div class="rounded-lg bg-white p-6 shadow">
					<h2 class="mb-4 text-lg font-bold text-gray-800">Recent Completed Sessions</h2>
					{#if pastSessions.length > 0}
						<div class="space-y-3">
							{#each pastSessions.slice(0, 5) as session}
								<div class="rounded-lg border border-gray-200 bg-gray-50 p-3">
									<div class="flex items-start justify-between">
										<div>
											<div class="font-semibold text-gray-700">{session.course}</div>
											<div class="text-sm text-gray-600">
												{#if isTutor}
													with {session.student?.name || 'Student'}
												{:else}
													with {session.tutor?.name || 'Tutor'}
												{/if}
											</div>
											<div class="mt-1 text-sm text-gray-500">
												{session.day} at {formatTime(session.time)}
											</div>
										</div>
										<span class="rounded-full bg-gray-200 px-2 py-1 text-xs text-gray-600">
											Completed
										</span>
									</div>
								</div>
							{/each}
						</div>
					{:else}
						<p class="text-gray-500">No completed sessions yet.</p>
					{/if}
				</div>
			</div>

			<!-- Quick Actions -->
			<div class="mt-6 rounded-lg bg-white p-6 shadow">
				<h2 class="mb-4 text-lg font-bold text-gray-800">Quick Actions</h2>
				<div class="flex flex-wrap gap-4">
					{#if isTutor}
						<a
							href="/tutor-dashboard"
							class="rounded-lg bg-[#231161] px-6 py-3 text-white hover:bg-[#1a0d4a]"
						>
							Go to Tutor Dashboard
						</a>
					{:else}
						<a
							href="/student-dashboard"
							class="rounded-lg bg-[#231161] px-6 py-3 text-white hover:bg-[#1a0d4a]"
						>
							Go to Student Dashboard
						</a>
						<a
							href="/search"
							class="rounded-lg border border-[#231161] px-6 py-3 text-[#231161] hover:bg-purple-50"
						>
							Find a Tutor
						</a>
					{/if}
				</div>
			</div>
		{/if}
	</main>
</div>
