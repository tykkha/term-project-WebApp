<script lang="ts">
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import {
        authFetch,
        getCurrentUser,
        getTags,
        createSession,
        logoutUser,
        type User,
        type Tag,
        type Session as CreatedSession
    } from '$lib/api';

    type Session = {
        sid: number;
        tutor?: { tid: number; name: string };
        student?: { uid: number; name: string };
        course: string;
        day: string;
        time: number;
        started: string | null;
        concluded: string | null;
    };

    type TutorSummary = {
        tid: number;
        uid?: number;
        name: string;
        email?: string;
        rating?: number;
        status?: string;
        verificationStatus?: string;
        bio?: string | null;
    };

    let user = $state<User | null>(getCurrentUser());
    let profile = $state<any>(null);

    let upcomingSessions = $state<Session[]>([]);
    let previousSessions = $state<Session[]>([]);
    let topTutors = $state<TutorSummary[]>([]);
    let tags = $state<Tag[]>([]);

    let isLoading = $state(true);
    let errorMessage = $state('');
    let isLoggingOut = $state(false);

    // Booking state
    let bookingTutorId = $state<number | null>(null);
    let bookingTagId = $state<number | string | null>(null);
    let bookingDay = $state<string>('Monday');
    let bookingTime = $state<number | string>(12);
    let bookingError = $state('');
    let bookingMessage = $state('');
    let isBooking = $state(false);

    const daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    const timeOptions = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20];

    function formatTime(hour: number): string {
        if (hour === null || hour === undefined) return '';
        const h = Number(hour);
        const suffix = h >= 12 ? 'PM' : 'AM';
        const hour12 = ((h + 11) % 12) + 1;
        return `${hour12}:00 ${suffix}`;
    }

    function hasTimeConflict(day: string, time: number): boolean {
        return upcomingSessions.some(session =>
            session.day === day && session.time === time
        );
    }

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

    onMount(async () => {
        if (!user) {
            goto('/login');
            return;
        }

        isLoading = true;
        errorMessage = '';

        try {
            const [userRes, sessionsRes, topTutorRes, tagsRes] = await Promise.all([
                authFetch(`/api/users/${user.uid}`),
                authFetch(`/api/users/${user.uid}/sessions`),
                authFetch('/api/tutors/top'),
                getTags().then((t) => ({ ok: true, json: async () => t })).catch(() => ({ ok: false }))
            ]);

            if (userRes.ok) {
                profile = await userRes.json();
            }

            if (sessionsRes.ok) {
                const sessions: Session[] = await sessionsRes.json();
                upcomingSessions = sessions.filter((s) => s.concluded === null);
                previousSessions = sessions.filter((s) => s.concluded !== null);
            } else if (sessionsRes.status !== 404 && sessionsRes.status !== 403) {
                console.warn('Failed to load sessions', sessionsRes.status);
            }

            if (topTutorRes.ok) {
                topTutors = await topTutorRes.json();
            }

            if (tagsRes.ok) {
                tags = await tagsRes.json();
            }
        } catch (err: any) {
            console.error(err);
            errorMessage = err?.message ?? 'Failed to load dashboard data.';
        } finally {
            isLoading = false;
        }
    });

    function openBooking(tutor: TutorSummary) {
        if (!user) {
            errorMessage = 'You must be logged in to book a session.';
            return;
        }
        bookingTutorId = tutor.tid;
        bookingDay = 'Monday';
        bookingTime = 12;
        bookingTagId = tags.length ? tags[0].id : null;
        bookingError = '';
        bookingMessage = '';
    }

    function closeBooking() {
        bookingTutorId = null;
        bookingError = '';
        bookingMessage = '';
    }

    async function submitBooking() {
        if (!user || bookingTutorId === null || bookingTagId === null) {
            bookingError = 'Please select a tutor, course, day, and time.';
            return;
        }

        if (hasTimeConflict(bookingDay, Number(bookingTime))) {
            bookingError = `You already have a session booked on ${bookingDay} at ${formatTime(Number(bookingTime))}. Please choose a different time.`;
            return;
        }

        isBooking = true;
        bookingError = '';
        bookingMessage = '';

        try {
            const payload = {
                uid: user.uid,
                tid: bookingTutorId,
                tagsID: Number(bookingTagId),
                day: bookingDay,
                time: Number(bookingTime)
            };

            const newSession: CreatedSession = await createSession(payload);

            bookingMessage = 'Session booked successfully!';

            upcomingSessions = [
                ...upcomingSessions,
                {
                    sid: newSession.sid,
                    student: newSession.student,
                    tutor: newSession.tutor,
                    course: newSession.course,
                    day: newSession.day,
                    time: newSession.time,
                    started: newSession.started,
                    concluded: newSession.concluded
                }
            ];

            setTimeout(() => {
                closeBooking();
            }, 2000);
        } catch (err: any) {
            console.error(err);
            bookingError = err?.message ?? 'Failed to book session.';
        } finally {
            isBooking = false;
        }
    }
</script>

<div class="min-h-screen bg-gray-50">
    <header class="bg-[#231161] text-white shadow-lg">
        <div class="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
            <div>
                <h1 class="text-2xl font-bold">Gator Guides</h1>
                <p class="text-sm text-purple-200">
                    {#if user}
                        Welcome back, {user.firstName} {user.lastName}!
                    {:else}
                        Student Dashboard
                    {/if}
                </p>
            </div>
            <div class="flex gap-3 items-center">
                <a href="/" class="text-sm text-purple-200 hover:text-white transition-colors">Home</a>
                <button
                        onclick={handleLogout}
                        disabled={isLoggingOut}
                        class="px-4 py-2 bg-white text-[#231161] rounded-lg text-sm font-medium hover:bg-purple-50 transition-colors disabled:opacity-50"
                >
                    {isLoggingOut ? 'Logging out...' : 'Logout'}
                </button>
            </div>
        </div>
    </header>

    <main class="max-w-6xl mx-auto px-4 py-6 space-y-6">
        {#if isLoading}
            <div class="bg-white rounded-lg shadow p-6 text-center">
                <p class="text-gray-600">Loading your dashboard...</p>
            </div>
        {:else}
            {#if errorMessage}
                <div class="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
                    {errorMessage}
                </div>
            {/if}

            <section class="bg-white rounded-lg shadow p-6">
                <h2 class="text-xl font-bold text-gray-800 mb-4">My Profile</h2>
                {#if user && profile}
                    <div class="space-y-2">
                        <p class="text-lg font-semibold text-gray-800">
                            {profile.firstName} {profile.lastName}
                        </p>
                        <p class="text-gray-600">{profile.email}</p>
                        {#if profile.bio}
                            <p class="text-sm text-gray-600 mt-2 pt-2 border-t">{profile.bio}</p>
                        {/if}
                    </div>
                {/if}
            </section>

            <section class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="bg-white rounded-lg shadow p-6">
                    <h2 class="text-xl font-bold text-gray-800 mb-4">Upcoming Sessions</h2>
                    {#if upcomingSessions.length === 0}
                        <p class="text-gray-500 text-sm">
                            No upcoming sessions. Book a tutor below!
                        </p>
                    {:else}
                        <ul class="space-y-3">
                            {#each upcomingSessions as session}
                                <li class="border border-gray-200 rounded-lg p-4 bg-purple-50">
                                    <div class="flex justify-between items-start mb-2">
                                        <span class="font-semibold text-gray-800">{session.course}</span>
                                        <span class="text-xs bg-[#231161] text-white px-2 py-1 rounded">
                                            Upcoming
                                        </span>
                                    </div>
                                    <p class="text-sm text-gray-700 mb-1">
                                        <strong>Tutor:</strong> {session.tutor?.name ?? 'Unknown'}
                                    </p>
                                    <p class="text-sm text-gray-600">
                                        <strong>Time:</strong> {session.day} at {formatTime(session.time)}
                                    </p>
                                </li>
                            {/each}
                        </ul>
                    {/if}
                </div>

                <div class="bg-white rounded-lg shadow p-6">
                    <h2 class="text-xl font-bold text-gray-800 mb-4">Session History</h2>
                    {#if previousSessions.length === 0}
                        <p class="text-gray-500 text-sm">
                            No previous sessions yet.
                        </p>
                    {:else}
                        <ul class="space-y-3">
                            {#each previousSessions as session}
                                <li class="border border-gray-200 rounded-lg p-4 bg-gray-50">
                                    <div class="flex justify-between items-start mb-2">
                                        <span class="font-semibold text-gray-800">{session.course}</span>
                                        <span class="text-xs bg-green-600 text-white px-2 py-1 rounded">
                                            Completed
                                        </span>
                                    </div>
                                    <p class="text-sm text-gray-700 mb-1">
                                        <strong>Tutor:</strong> {session.tutor?.name ?? 'Unknown'}
                                    </p>
                                    <p class="text-sm text-gray-600">
                                        <strong>Time:</strong> {session.day} at {formatTime(session.time)}
                                    </p>
                                </li>
                            {/each}
                        </ul>
                    {/if}
                </div>
            </section>

            <section class="bg-white rounded-lg shadow p-6">
                <h2 class="text-xl font-bold text-gray-800 mb-4">Available Tutors</h2>

                {#if bookingError}
                    <div class="mb-4 rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
                        {bookingError}
                    </div>
                {/if}

                {#if bookingMessage}
                    <div class="mb-4 rounded-lg bg-green-50 border border-green-200 px-4 py-3 text-sm text-green-700">
                        {bookingMessage}
                    </div>
                {/if}

                {#if topTutors.length === 0}
                    <p class="text-gray-500 text-sm">No tutors available at the moment.</p>
                {:else}
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {#each topTutors as tutor}
                            <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                                <div class="mb-3">
                                    <p class="font-bold text-gray-800 text-lg mb-1">{tutor.name}</p>
                                    {#if tutor.email}
                                        <p class="text-xs text-gray-500 mb-2">{tutor.email}</p>
                                    {/if}
                                    {#if tutor.rating !== undefined}
                                        <div class="flex items-center gap-1 text-yellow-600 text-sm">
                                            <span>⭐</span>
                                            <span class="font-semibold">
                                                {tutor.rating?.toFixed ? tutor.rating.toFixed(1) : tutor.rating}/5
                                            </span>
                                        </div>
                                    {/if}
                                    {#if tutor.bio}
                                        <p class="text-xs text-gray-600 mt-2 line-clamp-2">{tutor.bio}</p>
                                    {/if}
                                </div>

                                <button
                                        type="button"
                                        class="w-full px-4 py-2 rounded-lg text-sm font-medium bg-[#231161] text-white hover:bg-[#1a0d4a] transition-colors"
                                        onclick={() => openBooking(tutor)}
                                >
                                    Book Session
                                </button>

                                {#if bookingTutorId === tutor.tid}
                                    <div class="mt-4 pt-4 border-t border-gray-200">
                                        <form onsubmit={(e) => { e.preventDefault(); submitBooking(); }} class="space-y-3">
                                            <div>
                                                <label class="block text-sm font-medium text-gray-700 mb-1">
                                                    Course
                                                </label>
                                                {#if tags.length === 0}
                                                    <p class="text-xs text-gray-500">No courses available</p>
                                                {:else}
                                                    <select
                                                            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-[#231161] focus:border-[#231161]"
                                                            bind:value={bookingTagId}
                                                    >
                                                        {#each tags as tag}
                                                            <option value={tag.id}>{tag.name}</option>
                                                        {/each}
                                                    </select>
                                                {/if}
                                            </div>

                                            <div class="grid grid-cols-2 gap-3">
                                                <div>
                                                    <label class="block text-sm font-medium text-gray-700 mb-1">
                                                        Day
                                                    </label>
                                                    <select
                                                            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-[#231161] focus:border-[#231161]"
                                                            bind:value={bookingDay}
                                                    >
                                                        {#each daysOfWeek as d}
                                                            <option value={d}>{d}</option>
                                                        {/each}
                                                    </select>
                                                </div>
                                                <div>
                                                    <label class="block text-sm font-medium text-gray-700 mb-1">
                                                        Time
                                                    </label>
                                                    <select
                                                            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-[#231161] focus:border-[#231161]"
                                                            bind:value={bookingTime}
                                                    >
                                                        {#each timeOptions as h}
                                                            <option value={h}>{formatTime(h)}</option>
                                                        {/each}
                                                    </select>
                                                </div>
                                            </div>

                                            <div class="flex gap-2">
                                                <button
                                                        type="button"
                                                        class="flex-1 px-4 py-2 rounded-lg text-sm font-medium border border-gray-300 text-gray-700 hover:bg-gray-50 transition-colors"
                                                        onclick={closeBooking}
                                                >
                                                    Cancel
                                                </button>
                                                <button
                                                        type="submit"
                                                        class="flex-1 px-4 py-2 rounded-lg text-sm font-medium bg-green-600 text-white hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                                        disabled={isBooking || tags.length === 0}
                                                >
                                                    {isBooking ? 'Booking...' : 'Confirm'}
                                                </button>
                                            </div>
                                        </form>
                                    </div>
                                {/if}
                            </div>
                        {/each}
                    </div>
                {/if}
            </section>
        {/if}
    </main>
</div>