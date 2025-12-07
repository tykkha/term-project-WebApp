<script lang="ts">
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { getCurrentUser, logoutUser, authFetch, type User, type Session } from '$lib/api';

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
        <div class="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
            <div>
                <h1 class="text-2xl font-bold">Gator Guides - Tutor Dashboard</h1>
                {#if user}
                    <p class="text-sm text-purple-200">
                        Welcome back, {user.firstName} {user.lastName}!
                    </p>
                {/if}
            </div>
            <div class="flex gap-3 items-center">
                <a href="/" class="text-sm text-purple-200 hover:text-white transition-colors">
                    Home
                </a>
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

    <main class="max-w-7xl mx-auto px-4 py-6 space-y-6">
        {#if isLoading}
            <div class="bg-white rounded-lg shadow p-8 text-center">
                <div class="animate-pulse">
                    <div class="w-16 h-16 bg-[#231161] rounded-full mx-auto mb-4"></div>
                    <p class="text-gray-600">Loading your tutor dashboard...</p>
                </div>
            </div>
        {:else if errorMessage}
            <div class="bg-red-50 border border-red-200 rounded-lg p-4">
                <p class="text-red-700">{errorMessage}</p>
            </div>
        {:else}
            <!-- STATS -->
            <section class="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div class="bg-white rounded-lg shadow p-6">
                    <p class="text-sm text-gray-600 mb-1">Total Sessions</p>
                    <p class="text-3xl font-bold text-[#231161]">{totalSessions}</p>
                </div>
                <div class="bg-white rounded-lg shadow p-6">
                    <p class="text-sm text-gray-600 mb-1">This Week</p>
                    <p class="text-3xl font-bold text-[#231161]">{thisWeekSessions}</p>
                </div>
                <div class="bg-white rounded-lg shadow p-6">
                    <p class="text-sm text-gray-600 mb-1">Completed</p>
                    <p class="text-3xl font-bold text-[#231161]">{completedSessions}</p>
                </div>
                <div class="bg-white rounded-lg shadow p-6">
                    <p class="text-sm text-gray-600 mb-1">Your Rating</p>
                    <div class="flex items-center gap-2">
                        <p class="text-3xl font-bold text-[#231161]">
                            {tutorProfile?.rating?.toFixed(1) || '0.0'}
                        </p>
                        <span class="text-yellow-500 text-2xl">⭐</span>
                    </div>
                </div>
            </section>

            <!-- TUTOR PROFILE -->
            <section class="bg-white rounded-lg shadow p-6">
                <h2 class="text-xl font-bold text-gray-800 mb-4">Your Tutor Profile</h2>
                {#if profile && tutorProfile}
                    <div class="grid md:grid-cols-2 gap-6">
                        <div class="space-y-3">
                            <div>
                                <p class="text-sm text-gray-600">Name</p>
                                <p class="text-lg font-semibold text-gray-800">
                                    {profile.firstName} {profile.lastName}
                                </p>
                            </div>
                            <div>
                                <p class="text-sm text-gray-600">Email</p>
                                <p class="text-gray-800">{profile.email}</p>
                            </div>
                            <div>
                                <p class="text-sm text-gray-600">Status</p>
                                <span
                                        class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium
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
                                        class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium
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
                        <div class="mt-4 pt-4 border-t">
                            <p class="text-sm text-gray-600 mb-1">Bio</p>
                            <p class="text-gray-800 whitespace-pre-wrap">{profile.bio}</p>
                        </div>
                    {/if}
                {/if}
            </section>

            <!-- UPCOMING SESSIONS (chronological) -->
            <section class="bg-white rounded-lg shadow p-6">
                <h2 class="text-xl font-bold text-gray-800 mb-4">Upcoming Sessions</h2>
                {#if upcomingSessions.length > 0}
                    <div class="space-y-3">
                        {#each upcomingSessions as session}
                            <div class="border border-purple-200 bg-purple-50 rounded-lg p-4">
                                <div class="flex items-center gap-2 mb-2">
                                    <span
                                            class="px-2 py-1 bg-purple-600 text-white text-xs font-semibold rounded"
                                    >
                                        Upcoming
                                    </span>
                                    <span class="text-sm font-medium text-gray-700">
                                        {session.course}
                                    </span>
                                </div>
                                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
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
                                    <p class="text-xs text-gray-600 mt-2">
                                        Started: {formatDate(session.started)}
                                    </p>
                                {/if}
                            </div>
                        {/each}
                    </div>
                {:else}
                    <p class="text-gray-500 text-center py-8">
                        No upcoming sessions scheduled.
                    </p>
                {/if}
            </section>

            <!-- PAST / COMPLETED SESSIONS -->
            {#if pastSessions.length > 0}
                <section class="bg-white rounded-lg shadow p-6">
                    <h2 class="text-xl font-bold text-gray-800 mb-4">Session History</h2>
                    <div class="space-y-3">
                        {#each pastSessions as session}
                            <div class="border border-gray-200 bg-gray-50 rounded-lg p-4">
                                <div class="flex items-center gap-2 mb-2">
                                    <span
                                            class="px-2 py-1 bg-gray-500 text-white text-xs font-semibold rounded"
                                    >
                                        Completed
                                    </span>
                                    <span class="text-sm font-medium text-gray-700">
                                        {session.course}
                                    </span>
                                </div>
                                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
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
