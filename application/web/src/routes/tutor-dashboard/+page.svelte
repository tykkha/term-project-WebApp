<script lang="ts">
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import {
        getCurrentUser,
        logoutUser,
        authFetch,
        updateUser,
        uploadProfilePicture,
        getTutorAvailability,
        addAvailabilitySlot,
        deleteAvailabilitySlot,
        type User,
        type Session,
        type AvailabilitySlot
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

    let isAdmin = $state(false);
    let pendingTutors = $state<any[]>([]);
    let approvalLoading = $state<{ [key: number]: boolean }>({});

    // ---- AVAILABILITY STATE ----
    let availabilitySlots = $state<AvailabilitySlot[]>([]);
    let isLoadingAvailability = $state(false);
    let showAddAvailability = $state(false);
    let newSlot = $state({
        day: 'Monday',
        startTime: 9,
        endTime: 10
    });
    let isAddingSlot = $state(false);
    let availabilityError = $state('');
    let availabilitySuccess = $state('');
    let deletingSlotId = $state<number | null>(null);

    const daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    const hours = Array.from({ length: 15 }, (_, i) => i + 8); // 8 AM to 10 PM

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

    function getSessionLocation(session: Session): string {
        return (session as any).location || 'Zoom';
    }

    // ---- AVAILABILITY FUNCTIONS ----
    async function loadAvailability() {
        if (!tutorProfile?.tid) return;

        isLoadingAvailability = true;
        try {
            availabilitySlots = await getTutorAvailability(tutorProfile.tid);
        } catch (err) {
            console.error('Failed to load availability:', err);
        } finally {
            isLoadingAvailability = false;
        }
    }

    async function handleAddSlot() {
        if (!tutorProfile?.tid) return;

        availabilityError = '';
        availabilitySuccess = '';

        if (newSlot.startTime >= newSlot.endTime) {
            availabilityError = 'End time must be after start time';
            return;
        }

        // Check for overlapping slots
        const overlapping = availabilitySlots.find(
            (slot) =>
                slot.day === newSlot.day &&
                ((newSlot.startTime >= slot.startTime && newSlot.startTime < slot.endTime) ||
                    (newSlot.endTime > slot.startTime && newSlot.endTime <= slot.endTime) ||
                    (newSlot.startTime <= slot.startTime && newSlot.endTime >= slot.endTime))
        );

        if (overlapping) {
            availabilityError = `This overlaps with existing slot: ${overlapping.day} ${formatTime(overlapping.startTime)} - ${formatTime(overlapping.endTime)}`;
            return;
        }

        isAddingSlot = true;

        try {
            await addAvailabilitySlot(tutorProfile.tid, newSlot.day, newSlot.startTime, newSlot.endTime);
            availabilitySuccess = 'Availability slot added!';
            await loadAvailability();

            // Reset form
            newSlot = { day: 'Monday', startTime: 9, endTime: 10 };

            setTimeout(() => {
                showAddAvailability = false;
                availabilitySuccess = '';
            }, 1500);
        } catch (err: any) {
            availabilityError = err?.message || 'Failed to add availability slot';
        } finally {
            isAddingSlot = false;
        }
    }

    async function handleDeleteSlot(slot: AvailabilitySlot) {
        if (!tutorProfile?.tid || !slot.availabilityID) return;

        const confirmed = confirm(
            `Remove availability for ${slot.day} ${formatTime(slot.startTime)} - ${formatTime(slot.endTime)}?`
        );
        if (!confirmed) return;

        deletingSlotId = slot.availabilityID;

        try {
            await deleteAvailabilitySlot(tutorProfile.tid, slot.availabilityID);
            await loadAvailability();
        } catch (err: any) {
            alert(err?.message || 'Failed to delete slot');
        } finally {
            deletingSlotId = null;
        }
    }

    // Group slots by day for display
    function getSlotsByDay() {
        const grouped: Record<string, AvailabilitySlot[]> = {};
        for (const day of daysOfWeek) {
            grouped[day] = availabilitySlots
                .filter((s) => s.day === day)
                .sort((a, b) => a.startTime - b.startTime);
        }
        return grouped;
    }

    async function loadPendingTutors() {
        try {
            // Get ALL tutors instead of /pending endpoint
            const res = await authFetch('/api/tutors');
            if (res.ok) {
                const allTutors = await res.json();

                // Filter for pending tutors on frontend
                pendingTutors = allTutors.filter((tutor: any) => tutor.verificationStatus === 'pending');
            }
        } catch (err) {
            console.error('Load pending tutors error:', err);
        }
    }

    async function approveTutor(tid: number) {
        approvalLoading[tid] = true;
        try {
            const res = await authFetch(`/api/tutors/${tid}/approve`, {
                method: 'PUT'
            });

            if (res.ok) {
                await loadPendingTutors();
            } else {
                const body = await res.json().catch(() => null);
                alert(body?.detail || 'Failed to approve tutor');
            }
        } catch (err) {
            console.error('Approve tutor error:', err);
            alert('Failed to approve tutor');
        } finally {
            approvalLoading[tid] = false;
        }
    }

    async function rejectTutor(tid: number) {
        approvalLoading[tid] = true;
        try {
            const res = await authFetch(`/api/tutors/${tid}/reject`, {
                method: 'PUT'
            });

            if (res.ok) {
                await loadPendingTutors();
            } else {
                const body = await res.json().catch(() => null);
                alert(body?.detail || 'Failed to reject tutor');
            }
        } catch (err) {
            console.error('Reject tutor error:', err);
            alert('Failed to reject tutor');
        } finally {
            approvalLoading[tid] = false;
        }
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

                console.log('Profile data:', profile);
                console.log('Profile type:', profile.type);
                console.log('Profile Type (capital):', profile.Type);

                if (profile.type === 'admin' || profile.Type === 'admin') {
                    console.log('User is admin!');
                    isAdmin = true;
                    await loadPendingTutors();
                } else {
                    console.log('User is NOT admin');
                }

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

                // Load availability after we have the tutor profile
                await loadAvailability();

                try {
                    const sessionsRes = await authFetch(`/api/tutors/${tutorProfile.tid}/sessions`);
                    if (sessionsRes.ok) {
                        const allSessions = await sessionsRes.json();

                        const now = new Date();

                        const upcoming = allSessions.filter(
                            (s: Session) => !s.concluded || new Date(s.concluded) > now
                        );
                        const past = allSessions.filter(
                            (s: Session) => s.concluded && new Date(s.concluded) <= now
                        );

                        upcoming.sort((a: any, b: any) => {
                            const dayDiff = getDayIndex(a.day) - getDayIndex(b.day);
                            if (dayDiff !== 0) return dayDiff;
                            return a.time - b.time;
                        });

                        past.sort((a: any, b: any) => {
                            const aDate = a.concluded ? new Date(a.concluded) : new Date(0);
                            const bDate = b.concluded ? new Date(b.concluded) : new Date(0);
                            return bDate.getTime() - aDate.getTime();
                        });

                        upcomingSessions = upcoming;
                        pastSessions = past;

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
                <a href="/calendar" class="text-sm text-purple-200 transition-colors hover:text-white">
                    Calendar
                </a>
                <a href="/messages" class="text-sm text-purple-200 transition-colors hover:text-white">
                    Messages
                </a>
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
            {#if isAdmin && pendingTutors.length > 0}
                <section class="rounded-lg border-2 border-yellow-400 bg-yellow-50 p-6 shadow-lg">
                    <div class="mb-4 flex items-center gap-3">
                        <span class="text-2xl">🛡️</span>
                        <h2 class="text-xl font-bold text-gray-800">
                            Pending Tutor Approvals ({pendingTutors.length})
                        </h2>
                    </div>

                    <div class="space-y-3">
                        {#each pendingTutors as tutor}
                            <div class="rounded-lg border border-yellow-300 bg-white p-4">
                                <div class="mb-2 flex items-center justify-between">
                                    <div>
                                        <p class="font-semibold text-gray-800">{tutor.name}</p>
                                        <p class="text-xs text-gray-600">
                                            ID: {tutor.tid} | Email: {tutor.email}
                                        </p>
                                    </div>
                                    <span class="rounded bg-yellow-600 px-2 py-1 text-xs font-semibold text-white">
                                        PENDING
                                    </span>
                                </div>

                                <div class="mb-2 text-sm">
                                    <span class="text-gray-600">Rating: </span>
                                    <span class="font-semibold">⭐ {tutor.rating?.toFixed(1) || '0.0'}</span>
                                </div>

                                {#if tutor.tags && tutor.tags.length > 0}
                                    <div class="mb-3">
                                        <p class="mb-1 text-xs text-gray-600">Teaches:</p>
                                        <div class="flex flex-wrap gap-1">
                                            {#each tutor.tags as tag}
                                                <span class="rounded bg-purple-100 px-2 py-1 text-xs text-purple-800">
                                                    {tag.name}
                                                </span>
                                            {/each}
                                        </div>
                                    </div>
                                {/if}

                                <div class="flex gap-2 border-t pt-3">
                                    <button
                                        onclick={() => approveTutor(tutor.tid)}
                                        disabled={approvalLoading[tutor.tid]}
                                        class="flex-1 rounded-lg bg-green-600 px-3 py-2 text-sm font-medium text-white hover:bg-green-700 disabled:opacity-50"
                                    >
                                        {approvalLoading[tutor.tid] ? '...' : '✅ Approve'}
                                    </button>
                                    <button
                                        onclick={() => rejectTutor(tutor.tid)}
                                        disabled={approvalLoading[tutor.tid]}
                                        class="flex-1 rounded-lg bg-red-600 px-3 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-50"
                                    >
                                        {approvalLoading[tutor.tid] ? '...' : '❌ Reject'}
                                    </button>
                                </div>
                            </div>
                        {/each}
                    </div>

                    <div class="mt-3 rounded bg-blue-50 p-2 text-xs text-blue-800">
                        ℹ️ Admin only - regular tutors don't see this
                    </div>
                </section>
            {/if}

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

            <!-- AVAILABILITY MANAGER SECTION -->
            <section class="rounded-lg bg-white p-6 shadow">
                <div class="mb-4 flex items-center justify-between">
                    <div>
                        <h2 class="text-xl font-bold text-gray-800">Your Availability</h2>
                        <p class="text-sm text-gray-600">
                            Set the times when students can book sessions with you
                        </p>
                    </div>
                    <button
                        onclick={() => {
                            showAddAvailability = true;
                            availabilityError = '';
                            availabilitySuccess = '';
                        }}
                        class="rounded-lg bg-[#231161] px-4 py-2 text-sm text-white hover:bg-[#1a0d4a]"
                    >
                        + Add Time Slot
                    </button>
                </div>

                {#if isLoadingAvailability}
                    <div class="py-8 text-center">
                        <p class="text-gray-500">Loading availability...</p>
                    </div>
                {:else if availabilitySlots.length === 0}
                    <div class="rounded-lg border-2 border-dashed border-gray-300 py-12 text-center">
                        <p class="mb-2 text-gray-500">No availability set yet</p>
                        <p class="text-sm text-gray-400">
                            Add time slots so students know when they can book sessions
                        </p>
                    </div>
                {:else}
                    <div class="space-y-4">
                        {#each daysOfWeek as day}
                            {@const daySlots = getSlotsByDay()[day]}
                            {#if daySlots.length > 0}
                                <div class="rounded-lg border border-gray-200 p-4">
                                    <h3 class="mb-3 font-semibold text-gray-800">{day}</h3>
                                    <div class="flex flex-wrap gap-2">
                                        {#each daySlots as slot}
                                            <div
                                                class="flex items-center gap-2 rounded-lg bg-green-100 px-3 py-2 text-sm"
                                            >
                                                <span class="text-green-800">
                                                    {formatTime(slot.startTime)} - {formatTime(slot.endTime)}
                                                </span>
                                                <button
                                                    onclick={() => handleDeleteSlot(slot)}
                                                    disabled={deletingSlotId === slot.availabilityID}
                                                    class="text-red-500 hover:text-red-700 disabled:opacity-50"
                                                    title="Remove slot"
                                                >
                                                    {#if deletingSlotId === slot.availabilityID}
                                                        <span class="inline-block h-4 w-4 animate-spin rounded-full border-2 border-red-500 border-t-transparent"></span>
                                                    {:else}
                                                        ✕
                                                    {/if}
                                                </button>
                                            </div>
                                        {/each}
                                    </div>
                                </div>
                            {/if}
                        {/each}
                    </div>

                    <div class="mt-4 rounded-lg bg-blue-50 p-3 text-sm text-blue-800">
                        💡 Tip: Students can only book sessions during your available time slots
                    </div>
                {/if}
            </section>

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

<!-- ADD AVAILABILITY MODAL -->
{#if showAddAvailability}
    <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
        <div class="w-full max-w-md rounded-lg bg-white p-6">
            <h3 class="mb-4 text-xl font-bold text-gray-800">Add Availability Slot</h3>

            <div class="space-y-4">
                <div>
                    <label class="mb-1 block text-sm font-medium text-gray-700" for="avail-day">Day</label>
                    <select
                        id="avail-day"
                        bind:value={newSlot.day}
                        class="w-full rounded-lg border border-gray-300 px-3 py-2"
                    >
                        {#each daysOfWeek as day}
                            <option value={day}>{day}</option>
                        {/each}
                    </select>
                </div>

                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="mb-1 block text-sm font-medium text-gray-700" for="avail-start"
                            >Start Time</label
                        >
                        <select
                            id="avail-start"
                            bind:value={newSlot.startTime}
                            class="w-full rounded-lg border border-gray-300 px-3 py-2"
                        >
                            {#each hours as hour}
                                <option value={hour}>{formatTime(hour)}</option>
                            {/each}
                        </select>
                    </div>

                    <div>
                        <label class="mb-1 block text-sm font-medium text-gray-700" for="avail-end"
                            >End Time</label
                        >
                        <select
                            id="avail-end"
                            bind:value={newSlot.endTime}
                            class="w-full rounded-lg border border-gray-300 px-3 py-2"
                        >
                            {#each hours as hour}
                                {#if hour > newSlot.startTime}
                                    <option value={hour}>{formatTime(hour)}</option>
                                {/if}
                            {/each}
                            <option value={23}>{formatTime(23)}</option>
                        </select>
                    </div>
                </div>

                <div class="rounded-lg bg-gray-50 p-3 text-sm text-gray-600">
                    Preview: <span class="font-medium">{newSlot.day}</span> from
                    <span class="font-medium">{formatTime(newSlot.startTime)}</span> to
                    <span class="font-medium">{formatTime(newSlot.endTime)}</span>
                </div>

                {#if availabilityError}
                    <p class="text-sm text-red-600">{availabilityError}</p>
                {/if}

                {#if availabilitySuccess}
                    <p class="text-sm text-green-600">{availabilitySuccess}</p>
                {/if}

                <div class="flex gap-3 pt-4">
                    <button
                        onclick={() => (showAddAvailability = false)}
                        disabled={isAddingSlot}
                        class="flex-1 rounded-lg bg-gray-200 px-4 py-2 text-gray-700 hover:bg-gray-300 disabled:opacity-50"
                    >
                        Cancel
                    </button>
                    <button
                        onclick={handleAddSlot}
                        disabled={isAddingSlot || newSlot.startTime >= newSlot.endTime}
                        class="flex-1 rounded-lg bg-[#231161] px-4 py-2 text-white hover:bg-[#1a0d4a] disabled:opacity-50"
                    >
                        {isAddingSlot ? 'Adding...' : 'Add Slot'}
                    </button>
                </div>
            </div>
        </div>
    </div>
{/if}
