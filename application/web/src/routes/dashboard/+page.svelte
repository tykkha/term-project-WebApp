<script lang="ts">
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { getCurrentUser, authFetch } from '$lib/api';

    let isChecking = $state(true);
    let errorMessage = $state('');
    let debugInfo = $state('');

    onMount(async () => {
        const user = getCurrentUser();

        //Not logged in -> go to login
        if (!user) {
            goto('/login');
            return;
        }

        debugInfo = `Checking user ${user.uid}...`;

        try {
            //Check if user has a tutor profile by checking the Tutor table
            const tutorRes = await authFetch(`/api/tutors/by-user/${user.uid}`);

            debugInfo += `\nTutor check status: ${tutorRes.status}`;

            if (tutorRes.ok) {
                //Has tutor profile
                const tutorData = await tutorRes.json();
                debugInfo += `\nTutor found: tid=${tutorData.tid}`;
                console.log('Redirecting to tutor dashboard', tutorData);

                setTimeout(() => {
                    goto('/tutor-dashboard');
                }, 500);
            } else if (tutorRes.status === 404) {
                //No tutor profile - regular student
                debugInfo += '\nNo tutor profile - redirecting to student dashboard';
                console.log('Redirecting to student dashboard');

                setTimeout(() => {
                    goto('/student-dashboard');
                }, 500);
            } else {
                //Some other error
                errorMessage = `Unexpected response: ${tutorRes.status}`;
                isChecking = false;
            }
        } catch (err: any) {
            console.error('Dashboard routing error:', err);
            errorMessage = 'Failed to determine dashboard type';
            debugInfo += `\nError: ${err.message}`;
            isChecking = false;
        }
    });
</script>

<div class="min-h-screen bg-gray-50 flex items-center justify-center p-6">
    <div class="text-center max-w-md">
        {#if isChecking}
            <div class="animate-pulse">
                <div class="w-16 h-16 bg-[#231161] rounded-full mx-auto mb-4 flex items-center justify-center">
                    <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                </div>
                <p class="text-gray-600 font-medium">Loading your dashboard...</p>

                <!-- Debug info -->
                {#if debugInfo}
                    <div class="mt-4 bg-gray-100 rounded-lg p-3 text-left text-xs text-gray-700 font-mono">
                        {debugInfo}
                    </div>
                {/if}
            </div>
        {:else if errorMessage}
            <div class="bg-red-50 border border-red-200 rounded-lg p-6">
                <div class="text-red-600 mb-2">⚠️</div>
                <p class="text-red-700 font-medium mb-4">{errorMessage}</p>

                {#if debugInfo}
                    <div class="bg-red-100 rounded p-3 text-left text-xs text-red-800 font-mono mb-4">
                        {debugInfo}
                    </div>
                {/if}

                <div class="flex gap-2 justify-center">
                    <a
                            href="/student-dashboard"
                            class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 text-sm"
                    >
                        Student Dashboard
                    </a>
                    <a
                            href="/login"
                            class="px-4 py-2 bg-[#231161] text-white rounded-lg hover:bg-[#1a0d4a] text-sm"
                    >
                        Back to Login
                    </a>
                </div>
            </div>
        {/if}
    </div>
</div>