<script lang="ts">
    import { page } from '$app/state';
    import { onMount } from 'svelte';
    import {
        getCurrentUser,
        authFetch,
        getTutorAvailability,
        addAvailabilitySlot,
        deleteAvailabilitySlot,
        type AvailabilitySlot,
		type User,
		type TutorResponse
    } from '$lib/api'; 
	import { goto } from '$app/navigation';
    

    // Pull tutor ID from URL
    const tutorId = page.params.slug;
    const tutorIdNum = Number(tutorId);

    // Check current user and tutor status
    let isTutor = $state(false); 
    let uData = $state<User | null>(getCurrentUser());
    let tData = $state<TutorResponse>();
    
    // Availability Data
    let availabilitySlots = $state<AvailabilitySlot[]>([]);
    let isLoading = $state(true);
    let error: string | null = $state(null);
    let successMessage: string | null = $state(null);

    // Form Data
    let newDay = $state(''); 
    let newStartTimeStr = $state(''); 
    let newEndTimeStr = $state(''); 
    let isSubmitting = $state(false);

    const formatDate = (date: Date) => date.toISOString().split('T')[0];
    const formatDayName = (date: Date) => date.toLocaleDateString('en-US', { weekday: 'long' });

    // List up to the next 7 days for availability setting
    const getNextDays = (count: number = 7) => {
        const dates = [];
        const today = new Date();

        for (let i = 0; i < count; i++) {
            const date = new Date(today);
            date.setDate(today.getDate() + i);

            dates.push({
                isoDate: formatDate(date), 
                dayName: formatDayName(date),
                display: `${formatDayName(date)} (${date.getMonth() + 1}/${date.getDate()})` 
            });
        }
        return dates;
    };
    const nextDaysOptions = getNextDays(7);

    // Generate hourly slots (04:00 to 20:00)
    const generateTimeSlots = (start: number = 4, end: number = 20): string[] => {
        const slots: string[] = [];
        for (let h = start; h <= end; h++) {
            slots.push(`${h.toString().padStart(2, '0')}:00`);
        }
        return slots;
    };
    const startTimeSlots = generateTimeSlots(4, 19); // Start times up to 20:00

    // Generate end time slots based on the selected start time + 1 hour
    const generateEndTimes = (startTimeStr: string): string[] => {
        if (!startTimeStr) return [];
        
        const startHour = parseInt(startTimeStr.split(':')[0], 10);
        const slots: string[] = [];
        const maxEndHour = 20; 

        for (let h = startHour + 1; h <= maxEndHour; h++) {
             slots.push(`${h.toString().padStart(2, '0')}:00`);
        }
        return slots;
    }
    let endTimeSlots = $derived(generateEndTimes(newStartTimeStr));

    // Reset end time if start time changes and the selected end time is no longer valid
    $effect(() => {
        if (!newStartTimeStr) {
            newEndTimeStr = '';
            return;
        }
        const validEndTimes = generateEndTimes(newStartTimeStr);
        if (!validEndTimes.includes(newEndTimeStr)) {
            // Reset to default/first valid option if current end time is invalid
            newEndTimeStr = validEndTimes.length > 0 ? validEndTimes[0] : '';
        }
    });

    // Sort slots by date and time
    const sortedSlots = $derived(
        [...availabilitySlots].sort((a, b) => {
            // Combine day and time for easy comparison
            const timeA = `${a.day}T${String(a.startTime).padStart(2, '0')}:00:00`;
            const timeB = `${b.day}T${String(b.startTime).padStart(2, '0')}:00:00`;
            return timeA.localeCompare(timeB);
        })
    );
    
    async function loadAvailability() {
        isLoading = true;
        error = null;
        try {
            const slots = await getTutorAvailability(tutorIdNum);
            availabilitySlots = slots.filter(slot => slot.isActive !== false); 
        } catch (err) {
            console.error("Failed to load availability:", err);
            error = "Could not load availability slots.";
            availabilitySlots = [];
        } finally {
            isLoading = false;
        }
    }

    $effect(() => {
        loadAvailability();
    });

    async function handleAddSlot(event: Event) {
        event.preventDefault(); 
        error = null;
        successMessage = null;
        isSubmitting = true;

        if (!newDay || !newStartTimeStr || !newEndTimeStr) {
            error = 'Please select a day, a start time, and an end time.';
            isSubmitting = false;
            return;
        }

        const startTimeHour = parseInt(newStartTimeStr.split(':')[0], 10);
        const endTimeHour = parseInt(newEndTimeStr.split(':')[0], 10);
        
        // Check that end time is after start time
        if (endTimeHour <= startTimeHour) {
             error = 'End time must be after the start time.';
             isSubmitting = false;
             return;
        }
        
        try {
            console.log('Adding slot:', { tutorIdNum, newDay, startTimeHour, endTimeHour });
            const newSlot = await addAvailabilitySlot(tutorIdNum, newDay, startTimeHour, endTimeHour);

            // Update local state with the new slot
            availabilitySlots = [...availabilitySlots, newSlot];

            // Success feedback and reset form
            successMessage = `Availability set for ${newDay} from ${newStartTimeStr} to ${newEndTimeStr}.`;
            newDay = '';
            newStartTimeStr = '';
            newEndTimeStr = ''; 

        } catch (err: any) {
            console.error('Error adding slot:', err);
            error = err?.message || 'Failed to add availability slot. Check for overlaps.';
        } finally {
            isSubmitting = false;
        }
    }

    async function handleDeleteSlot(availabilityID: number | undefined) {
        if (!availabilityID || !confirm('Are you sure you want to remove this availability slot?')) return;

        error = null;
        successMessage = null;
        
        try {
            await deleteAvailabilitySlot(tutorIdNum, availabilityID);
            availabilitySlots = availabilitySlots.filter(slot => slot.availabilityID !== availabilityID);
            successMessage = 'Availability slot removed successfully.';
            
        } catch (err: any) {
            console.error('Error deleting slot:', err);
            error = err?.message || 'Failed to remove availability slot.';
        }
    }

    async function validTutor() {
        const user = getCurrentUser();
        if (uData) {
            console.log('Current User Data:', uData);
            const tutorRes = await authFetch(`/api/tutors/by-user/${uData.uid}`);
            tData = await tutorRes.json();
            console.log('Current Tutor Data:', tData);
            if (tData?.tid == tutorIdNum) {
                console.log('User is the tutor for this page.');
                isTutor = true;
            } else {
                goto(`/tutor/${tutorIdNum}`);
            } 
        } else {
            console.log('No user logged in, redirecting to login page.');
            goto('/login');
        }
    }    

    const formatTimeHour = (hour: number) => `${String(hour).padStart(2, '0')}:00`;
    onMount(() => {
		validTutor();
	});
</script>

<div class="min-h-screen min-w-screen bg-neutral-100">
    <div class="p-4">
        <a href="/tutor/{tutorIdNum}" class="hover:underline text-[#231161]">← Back to Tutor Profile</a>
    </div>

    <div class="flex gap-8 p-8 justify-center">
        <div class="w-full max-w-4xl rounded-2xl bg-white p-6 drop-shadow-xl">
            <h2 class="text-3xl font-semibold text-[#231161] mb-6">Manage Your Availability</h2>
            <p class="text-gray-600 mb-6">
                Set the days and times you are available for tutoring. The available time range is between 4:00 and 21:00.
            </p>

            {#if error}
                <div class="p-3 mb-4 bg-red-100 border border-red-400 text-red-700 rounded-lg" role="alert">
                    {error}
                </div>
            {/if}
            {#if successMessage}
                <div class="p-3 mb-4 bg-green-100 border border-green-400 text-green-700 rounded-lg" role="alert">
                    {successMessage}
                </div>
            {/if}

            <div class="mb-8 border-b pb-6">
                <h3 class="text-2xl font-medium text-[#231161] mb-4">➕ Add New Availability Slot</h3>
                <form onsubmit={handleAddSlot} class="flex flex-col gap-4 sm:flex-row sm:items-end">
                    <div class="flex-1 w-full sm:w-auto">
                        <label for="newDay" class="block text-sm font-medium">Select Day</label>
                        <select
                            bind:value={newDay}
                            id="newDay"
                            class="w-full p-3 border border-gray-300 rounded-lg transition"
                            required
                        >
                            <option value="" disabled selected>Select a day</option>
                            {#each nextDaysOptions as dayOption}
                                <option value={dayOption.dayName}>{dayOption.dayName}</option>
                            {/each}
                        </select>
                    </div>

                    <div class="w-full sm:w-auto flex items-end gap-2">
                        <div>
                            <label for="newStartTime" class="block text-sm font-medium">Start Time</label>
                            <select
                                bind:value={newStartTimeStr}
                                id="newStartTime"
                                class="p-3 border border-gray-300 rounded-lg"
                                required
                            >
                                <option value="" disabled selected>Start</option>
                                {#each startTimeSlots as time}
                                    <option value={time}>{time}</option>
                                {/each}
                            </select>
                        </div>
                        
                        <span class="text-lg pb-3">to</span>

                        <div>
                            <label for="newEndTime" class="block text-sm font-medium">End Time</label>
                            <select
                                bind:value={newEndTimeStr}
                                id="newEndTime"
                                class="p-3 border border-gray-300 rounded-lg"
                                required
                                disabled={!newStartTimeStr || endTimeSlots.length === 0}
                            >
                                <option value="" disabled selected>End</option>
                                {#each endTimeSlots as time}
                                    <option value={time}>{time}</option>
                                {/each}
                            </select>
                        </div>
                    </div>

                    <button
                        type="submit"
                        class="w-full sm:w-auto flex items-center justify-center gap-2 bg-[#231161] hover:bg-[#2d1982] text-white py-3 px-6 rounded-xl text-md font-semibold transition-colors disabled:opacity-50"
                        disabled={isSubmitting || !newDay || !newStartTimeStr || !newEndTimeStr}
                    >
                       {isSubmitting ? 'Adding...' : 'Add Slot'}
                    </button>
                </form>
            </div>


            <div class="flex justify-between items-center mb-4">
                <h3 class="text-2xl font-medium text-[#231161]">Available Slots</h3>
                <button 
                    onclick={loadAvailability} 
                    disabled={isLoading || isSubmitting}
                    class="flex items-center gap-1 text-sm text-[#231161] hover:text-[#2d1982] disabled:opacity-50 transition"
                >
                    {isLoading ? 'Refreshing...' : 'Refresh'}
                </button>
            </div>

            {#if isLoading}
                <div class="text-center py-8 text-gray-500">Loading your current availability...</div>
            {:else if sortedSlots.length === 0}
                <div class="p-6 bg-yellow-50 border border-yellow-200 text-yellow-800 rounded-lg text-center">
                    You have no availability slots set. Use the form above to add some!
                </div>
            {:else}
                <ul class="space-y-3">
                    {#each sortedSlots as slot (slot.availabilityID)}
                        <li class="flex justify-between items-center p-4 bg-gray-50 border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition">
                            <div class="flex flex-col">
                                <span class="text-lg font-semibold text-gray-800">
                                    {slot.day}
                                </span>
                                <span class="text-md text-gray-600">
                                    {formatTimeHour(slot.startTime)} to {formatTimeHour(slot.endTime)}
                                </span>
                            </div>
                            <button 
                                onclick={() => handleDeleteSlot(slot.availabilityID)}
                                class="p-2 text-red-600 hover:bg-red-100 rounded-full transition"
                            >
                                X
                            </button>
                        </li>
                    {/each}
                </ul>
            {/if}
        </div>
    </div>
</div>