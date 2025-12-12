<script lang="ts">
    import { page } from '$app/state';
    import {parseDate} from '@ark-ui/svelte/date-picker';    

    const formatDate = (date: Date) => date.toISOString().split('T')[0];
    const formatDayName = (date: Date) => date.toLocaleDateString('en-US', { weekday: 'long' });

    // Tutor session variables  
    const tutorId = page.params.slug;
    let day = $state('');
    let location = $state('');
    let startSession = $state('');

    let sessionData = $state({
        uid: '',
        tid: tutorId,
        tags_id: '',
        day: '',
        time: ''
    });

    // temp data
    const locations = ['Burk Hall', 'Cesar Chavez Student Center', 'J. Paul Leonard Library'];

    // List up to the next 7 days to be scheduled
    const getNextSevenDays = () => {
        const dates = [];
        const today = new Date();
        
        // Generate dates for today and the next 6 days (7 days total)
        for (let i = 1; i < 8; i++) {
            const date = new Date(today);
            date.setDate(today.getDate() + i);
            
            dates.push({
                isoDate: formatDate(date), // e.g., "2025-11-29"
                dayName: formatDayName(date), // e.g., "Saturday"
                display: `${formatDayName(date)} (${date.getMonth() + 1}/${date.getDate()})` // e.g., "Saturday (11/29)"
            });
        }
        return dates;
    };
    const nextSevenDays = getNextSevenDays();

    // Create slots (hourly) for sessions
    const generateTimeSlots = (): string[] => {
        const slots: string[] = [];
        const startHour = 0;
        const endHour = 23; 

        // Loop through hours from 0 to 23 
        for (let h = startHour; h <= endHour; h++) {
            const hourStr = h.toString().padStart(2, '0');
            slots.push(`${hourStr}:00`);
        }

        return slots;
    };

    // Adds one hour to the starting session hour
    const getEndTime = (timeStr: string): string => {
        if (!timeStr) return '';
        
        const [hours, minutes] = timeStr.split(':').map(Number);
        
        // Create a Date object set to an arbitrary day, then add one hour
        const date = new Date(2000, 0, 1, hours, minutes);
        date.setHours(date.getHours() + 1);
        
        const newHours = date.getHours();
        const newMinutes = date.getMinutes();
        
        const newTimeStr = `${newHours.toString().padStart(2, '0')}:${newMinutes.toString().padStart(2, '0')}`;
        
        // Check if the calculated end time is within the allowed slots
        if (newHours > 21 || (newHours === 21 && newMinutes > 0)) {
            return '';
        }
        
        return newTimeStr;
    }
    const timeSlots = generateTimeSlots();

    // Automatically set endSession one hour after startSession changes
    let endSession = $derived(getEndTime(startSession));

    // Function to handle form submission
    async function handleSubmit () {
        console.log('Session Data:', sessionData);

        try {
            const response = await fetch ('sessions/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(sessionData),
            });
            
            const res = await response.json();
        } catch {

        }
        
    }

</script>

<!--Session page-->
<div class="min-h-screen min-w-screen bg-neutral-100">
    <div class="p-4">
        <a href="/tutor/{tutorId}" class="hover:underline">← Back to Tutor</a>
    </div>
   
	<div class="flex gap-8 p-8 justify-center">
        <!--Form card-->
        <div class="w-full rounded-2xl bg-white p-4 drop-shadow-lg md:w-6/12">
            <h2 class="text-3xl underline">Add a tutor session</h2>
            <form onsubmit={(e) => {
				e.preventDefault();
				handleSubmit();
			}}>
                <div class="flex-col">
                    <!--Session day and date-->
                    <label for="day" class="block text-xl">Day (Next 7 days)</label>
                    <select bind:value={sessionData.day} id="day" class="p-2 border border-gray-300 focus:outline-none focus:ring-1 focus:ring-[#231161] focus:border-[#231161] rounded-lg" required>
                        <option value="" disabled selected>Select a day</option>
                        {#each nextSevenDays as dayOption}
                            <option value={dayOption.dayName}>{dayOption.display}</option>
                        {/each}
                    </select>

                    <!--Session duration-->                        
                    <label for="time" class="block text-xl mt-4">Session Time (1-Hour Session)</label>
                    <div class="flex items-center gap-2">
                         <select bind:value={sessionData.time} id="start-time" class="p-2 border border-gray-300 focus:outline-none focus:ring-1 focus:ring-[#231161] focus:border-[#231161] rounded-lg" required>
                            <option value="" disabled selected>Start Time</option>
                            {#each timeSlots as time}
                                <option value={time}>{time}</option>
                            {/each}
                        </select>
                        <span class="text-lg">to</span>
                        <div class="p-2 border border-gray-300 focus:outline-none focus:ring-1 focus:ring-[#231161] focus:border-[#231161] rounded-lg">
                            {endSession || 'End Time'}
                        </div>
                        <input type="hidden" bind:value={endSession} name="endSession" required/>
                    </div>

                    <p class="text-sm text-gray-500 mt-1">The session end time is automatically set to one hour after the start time.</p>

                    <!--Location-->
                    <label for="location" class="block text-xl">Location</label> <!--TODO dropdown-->
                    <select bind:value={location} class="p-2 border border-gray-300 focus:outline-none focus:ring-1 focus:ring-[#231161] focus:border-[#231161] rounded-lg" required>
                        <option value="" disabled selected>Select a location</option>
                        {#each locations as location}
                            <option value={location}>{location}</option>
                        {/each}
                    </select>
                    
                    <button type="submit" onclick={handleSubmit} class="block mx-auto bg-[#231161] hover:bg-[#2d1982] text-white py-2 px-3 rounded">Submit</button>
                </div>
            </form>
        </div>
    </div>
</div>